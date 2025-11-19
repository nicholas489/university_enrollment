from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.management import call_command
from django.db import transaction, IntegrityError
from django.db.models import Avg, Count
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from decimal import Decimal, InvalidOperation
import statistics
from .models import (
    Admin,
    Course,
    Department,
    GraduateStudent, 
    Section, 
    Instructor, 
    Student, 
    Enrollment, 
    Grade,
    UndergraduateStudent,
    Wait,
    Waitlist
)
from .forms import InstructorLoginForm, StudentLoginForm
from .decorators import student_required, instructor_required

TABLES_CONFIG = [
    {"id": "admin", "label": "Admin", "model": Admin},
    {"id": "department", "label": "Department", "model": Department},
    {"id": "student", "label": "Student", "model": Student},
    {"id": "undergraduate", "label": "UndergraduateStudent", "model": UndergraduateStudent},
    {"id": "graduate", "label": "GraduateStudent", "model": GraduateStudent},
    {"id": "instructor", "label": "Instructor", "model": Instructor},
    {"id": "course", "label": "Course", "model": Course},
    {"id": "section", "label": "Section", "model": Section},
    {"id": "enrollment", "label": "Enrollment", "model": Enrollment},
    {"id": "grade", "label": "Grade", "model": Grade},
    {"id": "waitlist", "label": "Waitlist", "model": Waitlist},
    {"id": "wait", "label": "Wait", "model": Wait},
]


def home(request):
    # If already logged in as student/instructor/admin, go to appropriate dashboard
    if request.session.get('student_id'):
        return redirect('student_dashboard')
    if request.session.get('instructor_id'):
        return redirect('instructor_dashboard')
    
    return render(request, 'university/home.html')

# Student Views
def student_login(request):
    if request.method == "POST":
        form = StudentLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                student = Student.objects.get(email=email)
            except Student.DoesNotExist:
                messages.error(request, "Invalid email or password.")
            else:
                # clear any prior instructor session that may exist
                request.session.pop('instructor_id', None)
                
                if password == student.password:
                    request.session['student_id'] = student.id
                    messages.success(request, f"Welcome, {student.first_name}!")
                    return redirect('student_dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
    # User made a GET Request to just retrieve the login page
    else:
        # If student is already logged in, return to dashboard
        if request.session.get('student_id'):
            return redirect('student_dashboard')
        form = StudentLoginForm()

    return render(request, 'university/student_login.html', {'form': form})

@student_required
def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)

    # Get all enrollments for this student, along with related course & instructor
    enrollments = (
        Enrollment.objects
        .filter(student=student)
        .select_related('section__course', 'section__instructor')
    )

    # Get grades for this student in these sections
    section_ids = enrollments.values_list('section_id', flat=True)
    grades = Grade.objects.filter(student=student, section_id__in=section_ids)

    # Map section_id -> grade object
    grade_by_section = {g.section_id: g for g in grades}

    # Build rows for the template
    enrollment_rows = []
    for enrollment in enrollments:
        section = enrollment.section
        course = section.course
        instructor = section.instructor
        grade = grade_by_section.get(section.id)  # might be None

        enrollment_rows.append({
            "course_code": course.course_code,
            "course_name": course.course_name,
            "section_id": section.id,
            "term": section.term,
            "instructor_name": f"{instructor.first_name} {instructor.last_name}",
            "lab_grade": getattr(grade, 'lab_grade', None),
            "assignment_grade": getattr(grade, 'assignment_grade', None),
            "midterm_grade": getattr(grade, 'midterm_grade', None),
            "final_grade": getattr(grade, 'final_grade', None),
        })

    return render(
        request,
        'university/student_dashboard.html',
        {
            'student': student,
            'enrollment_rows': enrollment_rows,
        }
    )

@student_required
def student_available_courses(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)

    # Sections the student is already enrolled in
    enrolled_section_ids = Enrollment.objects.filter(student=student).values_list(
        'section_id', flat=True
    )

    # Sections not yet enrolled in
    sections = (
        Section.objects
        .exclude(id__in=enrolled_section_ids)
        .select_related('course', 'instructor', 'course__department')
        .order_by('course__course_code', 'section_number')
    )

    return render(
        request,
        'university/student_available_courses.html',
        {
            'student': student,
            'sections': sections,
        }
    )

@student_required
def student_add_course(request, section_id):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    section = get_object_or_404(Section, id=section_id)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('student_available_courses')

    # Already enrolled?
    if Enrollment.objects.filter(student=student, section=section).exists():
        messages.info(request, "You are already enrolled in this section.")
        return redirect('student_dashboard')

    # If section has space: enroll normally
    if section.current_capacity < section.total_capacity:
        try:
            with transaction.atomic():
                Enrollment.objects.create(
                    student=student,
                    section=section,
                    admin=section.admin,  # or student.admin if you prefer
                )
                section.current_capacity += 1
                section.save()  # recalculates remaining_capacity
            messages.success(
                request,
                f"You have been enrolled in {section.course.course_code} "
                f"Section {section.section_number} ({section.term})."
            )
        except IntegrityError:
            messages.error(request, "An error occurred while enrolling. Please try again.")
        return redirect('student_dashboard')

    # ---- Section is full → WAITLIST LOGIC ----

    # Check if student is already on a waitlist for this section
    existing_wait = Wait.objects.filter(
        student=student,
        waitlist__section=section,
    ).first()

    if existing_wait:
        messages.info(
            request,
            "You are already on the waitlist for this section."
        )
        return redirect('student_dashboard')

    try:
        with transaction.atomic():
            # Get or create a waitlist for this section (single waitlist per section)
            waitlist, created = Waitlist.objects.get_or_create(
                section=section,
                waitlist_id=1,  # assuming one waitlist per section
                defaults={
                    "spaces_left": 10,  # default capacity; adjust if you like
                    "admin": section.admin,
                },
            )

            # If you want to enforce max waitlist size:
            if waitlist.spaces_left <= 0:
                messages.error(
                    request,
                    "Course and its waitlist are currently full. Please try another section."
                )
                return redirect('student_dashboard')

            # Create wait entry
            Wait.objects.create(
                student=student,
                waitlist=waitlist,
                admin=section.admin,
            )

            # Decrement waitlist spaces_left
            if waitlist.spaces_left > 0:
                waitlist.spaces_left -= 1
                waitlist.save()

        messages.success(
            request,
            "Course requested to be added is currently full. "
            "You will be added to the waitlist. Please check back for when you're "
            "successfully enrolled."
        )
    except IntegrityError:
        messages.error(request, "An error occurred while adding you to the waitlist.")

    return redirect('student_dashboard')

@student_required
def student_drop_course(request, section_id):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    section = get_object_or_404(Section, id=section_id)

    if request.method != "POST":
        messages.error(request, "Invalid request method.")
        return redirect('student_dashboard')

    try:
        with transaction.atomic():
            # Find the enrollment for this student + section
            enrollment = Enrollment.objects.select_for_update().get(
                student=student,
                section=section,
            )

            # Delete the enrollment
            enrollment.delete()

            # Decrease section capacity (no auto-promotion from waitlist)
            if section.current_capacity > 0:
                section.current_capacity -= 1
                section.save()  # will recalc remaining_capacity in save()

        messages.success(
            request,
            f"You have dropped {section.course.course_code} "
            f"Section {section.section_number} ({section.term})."
        )
    except Enrollment.DoesNotExist:
        messages.error(request, "You are not enrolled in this section.")

    return redirect('student_dashboard')
    
def instructor_login(request):
    if request.method == "POST":
        form = InstructorLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            try:
                instructor = Instructor.objects.get(email=email)
            except Instructor.DoesNotExist:
                messages.error(request, "Invalid email or password.")
            else:
                # clear any student session that may exist
                request.session.pop('student_id', None)
                
                if password == instructor.password:
                    # store instructor id in session
                    request.session['instructor_id'] = instructor.id
                    messages.success(request, f"Welcome, {instructor.first_name}!")
                    return redirect('instructor_dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
    # User made a GET Request to just retrieve the login page
    else:
        if request.session.get('instructor_id'):
            return redirect('instructor_dashboard')
        form = InstructorLoginForm()

    return render(request, 'university/instructor_login.html', {'form': form})

@instructor_required
def instructor_dashboard(request):
    instructor_id = request.session.get('instructor_id')
    if not instructor_id:
        return redirect('instructor_login')

    instructor = Instructor.objects.get(id=instructor_id)

    # All sections taught by this instructor
    sections = (
        Section.objects
        .filter(instructor=instructor)
        .select_related('course')
        .prefetch_related('enrollments__student', 'grades__student')
    )

    section_rows = []

    for section in sections:
        # Map student_id -> Grade object for this section
        grades_by_student = {g.student_id: g for g in section.grades.all()}

        students_data = []
        for enrollment in section.enrollments.all():
            student = enrollment.student
            grade = grades_by_student.get(student.id)

            students_data.append({
                "student_name": f"{student.first_name} {student.last_name}",
                "student_email": student.email,
                "lab_grade": getattr(grade, 'lab_grade', None),
                "assignment_grade": getattr(grade, 'assignment_grade', None),
                "midterm_grade": getattr(grade, 'midterm_grade', None),
                "final_grade": getattr(grade, 'final_grade', None),
            })

        section_rows.append({
            "section_id": section.id,
            "course_code": section.course.course_code,
            "course_name": section.course.course_name,
            "section_number": section.section_number,
            "term": section.term,
            "students": students_data,
        })

    return render(
        request,
        'university/instructor_dashboard.html',
        {
            'instructor': instructor,
            'section_rows': section_rows,
        }
    )

@instructor_required
def instructor_edit_grades(request, section_id):
    instructor_id = request.session.get('instructor_id')
    if not instructor_id:
        return redirect('instructor_login')

    instructor = Instructor.objects.get(id=instructor_id)
    section = get_object_or_404(Section, id=section_id)

    # Ensure this instructor actually teaches this section
    if section.instructor_id != instructor.id:
        messages.error(request, "You are not authorized to edit grades for this section.")
        return redirect('instructor_dashboard')

    enrollments = (
        Enrollment.objects
        .filter(section=section)
        .select_related('student')
    )

    # Map (student_id) -> Grade object
    grades = Grade.objects.filter(section=section, student__in=[e.student for e in enrollments])
    grades_by_student = {g.student_id: g for g in grades}

    if request.method == "POST":
        # Process grade updates
        for enrollment in enrollments:
            student = enrollment.student
            key_prefix = f"{enrollment.id}"

            lab_raw = request.POST.get(f"lab_grade_{key_prefix}", "").strip()
            assignment_raw = request.POST.get(f"assignment_grade_{key_prefix}", "").strip()
            midterm_raw = request.POST.get(f"midterm_grade_{key_prefix}", "").strip()
            final_raw = request.POST.get(f"final_grade_{key_prefix}", "").strip()

            def parse_decimal(value):
                if value == "":
                    return None
                try:
                    return Decimal(value)
                except InvalidOperation:
                    return None  # you could also collect errors if you want

            lab = parse_decimal(lab_raw)
            assignment = parse_decimal(assignment_raw)
            midterm = parse_decimal(midterm_raw)
            final = parse_decimal(final_raw)

            grade = grades_by_student.get(student.id)

            if grade is None:
                # Create new grade row if any field has a value
                if any(v is not None for v in (lab, assignment, midterm, final)):
                    grade = Grade.objects.create(
                        student=student,
                        section=section,
                        course=section.course,
                        admin=section.admin,
                        lab_grade=lab,
                        assignment_grade=assignment,
                        midterm_grade=midterm,
                        final_grade=final,
                    )
                    grades_by_student[student.id] = grade
            else:
                # Update existing grade
                grade.lab_grade = lab
                grade.assignment_grade = assignment
                grade.midterm_grade = midterm
                grade.final_grade = final
                grade.save()

        messages.success(request, "Grades updated successfully.")
        return redirect('instructor_dashboard')

    # GET: build rows for display in form
    rows = []
    for enrollment in enrollments:
        student = enrollment.student
        g = grades_by_student.get(student.id)

        rows.append({
            "enrollment_id": enrollment.id,
            "student_name": f"{student.first_name} {student.last_name}",
            "student_email": student.email,
            "lab_grade": getattr(g, 'lab_grade', None),
            "assignment_grade": getattr(g, 'assignment_grade', None),
            "midterm_grade": getattr(g, 'midterm_grade', None),
            "final_grade": getattr(g, 'final_grade', None),
        })

    return render(
        request,
        'university/instructor_edit_grades.html',
        {
            'instructor': instructor,
            'section': section,
            'rows': rows,
        }
    )

def tables_menu(request):
    return render(request, 'university/tables_menu.html')

def create_tables_page(request):
    """
    Recreates tables for the 'university' app by re-applying migrations.
    Does NOT populate data.
    """
    if request.method == "POST":
        # Re-apply all migrations for the app (recreate tables)
        call_command('migrate', 'university')

        messages.success(
            request,
            "Tables have been created (migrations applied) for the 'university' app."
        )
        return redirect('create_tables_page')

    return render(request, 'university/tables_create.html')

def populate_tables_page(request):
    """
    Populates tables with mock data by running the seed_mock_data command.
    Assumes tables already exist.
    """
    if request.method == "POST":
        call_command('seed_mock_data')

        messages.success(
            request,
            "Tables have been populated with mock data (seed_mock_data)."
        )
        return redirect('populate_tables_page')

    return render(request, 'university/tables_populate.html')

def drop_tables_page(request):
    """
    Drops (unapplies migrations for) the 'university' app, which effectively
    drops all its tables. This uses Django's migration system so migration state stays in sync.
    """
    if request.method == "POST":
        # This will:
        # - Unapply all migrations for the 'university' app
        # - Drop its tables
        call_command('migrate', 'university', 'zero')
        messages.success(
            request,
            "All tables for the 'university' app have been dropped (migrated to zero)."
        )
        return redirect('drop_tables_page')

    return render(request, 'university/tables_drop.html')

def query_tables_page(request):
    # ----- Query 1: Instructor average final grade per course (> 80) -----
    q1_queryset = (
        Grade.objects
        .select_related('section__course', 'section__instructor')
        .values(
            'section__instructor__first_name',
            'section__instructor__last_name',
            'section__course__course_code',
        )
        .annotate(avg_final=Avg('final_grade'))
        .filter(avg_final__gt=80)
        .order_by(
            'section__instructor__last_name',
            'section__instructor__first_name',
            'section__course__course_code',
        )
    )
    query1_rows = list(q1_queryset)

    # ----- Query 2: Instructors & courses with students also in Abhari's CPS109 -----
    abhari_students = Student.objects.filter(
        enrollments__section__instructor__last_name='Abhari',
        enrollments__section__course__course_code='CPS109',
    ).distinct()

    q2_queryset = (
        Enrollment.objects
        .filter(student__in=abhari_students)
        .select_related('section__course', 'section__instructor')
        .values(
            'section__instructor__first_name',
            'section__instructor__last_name',
            'section__course__course_code',
        )
        .distinct()
        .order_by(
            'section__instructor__last_name',
            'section__instructor__first_name',
            'section__course__course_code',
        )
    )
    query2_rows = list(q2_queryset)

    # ----- Query 3: Min/Max/Avg/Var/StdDev of final grades per course -----
    query3_rows = []
    for course in Course.objects.all().order_by('course_code'):
        finals = list(
            Grade.objects
            .filter(course=course)
            .values_list('final_grade', flat=True)
        )
        if not finals:
            continue

        min_g = min(finals)
        max_g = max(finals)
        avg_g = round(statistics.mean(finals), 2)

        if len(finals) > 1:
            var_g = round(statistics.pvariance(finals), 2)
            std_g = round(statistics.pstdev(finals), 2)
        else:
            var_g = 0
            std_g = 0

        query3_rows.append({
            "course_code": course.course_code,
            "min_grade": min_g,
            "max_grade": max_g,
            "avg_grade": avg_g,
            "var_grade": var_g,
            "stddev_grade": std_g,
        })

    # ----- Query 4: Courses with no students enrolled -----
    q4_queryset = (
        Course.objects
        .annotate(total_enrollments=Count('sections__enrollments', distinct=True))
        .filter(total_enrollments=0)
        .values('course_code', 'course_name')
        .order_by('course_code')
    )
    query4_rows = list(q4_queryset)

    # ----- Query 5: Student counts in CPS109 and CPS205 -----
    q5_queryset = (
        Course.objects
        .filter(course_code__in=['CPS109', 'CPS205'])
        .annotate(
            student_count=Count('sections__enrollments__student', distinct=True)
        )
        .values('course_code', 'student_count')
        .order_by('course_code')
    )
    query5_rows = list(q5_queryset)

    return render(
        request,
        'university/tables_query.html',
        {
            "query1_rows": query1_rows,
            "query2_rows": query2_rows,
            "query3_rows": query3_rows,
            "query4_rows": query4_rows,
            "query5_rows": query5_rows,
        }
    )

def logout(request):
    # Safely remove entity ids from session if they're present
    request.session.pop('instructor_id', None)
    request.session.pop('student_id', None)
    # Clear any prior messages
    storage = messages.get_messages(request)
    storage.used = True
    
    messages.success(request, "You have been logged out.")
    return redirect('home')