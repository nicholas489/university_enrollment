from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Course, Section, Instructor, Student
from .forms import InstructorLoginForm, StudentLoginForm

# Create your views here.
def home(request):
    return render(request, 'university/home.html')

def course_list(request):
    courses = Course.objects.select_related('department').all()
    return render(request, 'university/course_list.html', {'courses': courses})


def section_list(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    sections = Section.objects.filter(course=course)
    return render(
        request,
        'university/section_list.html',
        {'course': course, 'sections': sections}
    )
    
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
                # if check_password(password, student.password):
                if password == student.password:
                    request.session['student_id'] = student.id
                    messages.success(request, f"Welcome, {student.first_name}!")
                    return redirect('student_dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
    # User made a GET Request to just retrieve the login page
    else:
        form = StudentLoginForm()

    return render(request, 'university/student_login.html', {'form': form})

def student_dashboard(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('student_login')

    student = Student.objects.get(id=student_id)
    return render(
        request,
        'university/student_dashboard.html',
        {'student': student}
    )
    
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
                # if check_password(password, instructor.password):
                if password == instructor.password:
                    # store instructor id in session
                    request.session['instructor_id'] = instructor.id
                    messages.success(request, f"Welcome, {instructor.first_name}!")
                    return redirect('instructor_dashboard')
                else:
                    messages.error(request, "Invalid email or password.")
    # User made a GET Request to just retrieve the login page
    else:
        form = InstructorLoginForm()

    return render(request, 'university/instructor_login.html', {'form': form})

def instructor_dashboard(request):
    instructor_id = request.session.get('instructor_id')
    if not instructor_id:
        return redirect('instructor_login')

    instructor = Instructor.objects.get(id=instructor_id)
    return render(
        request,
        'university/instructor_dashboard.html',
        {'instructor': instructor}
    )

def logout(request):
    # Safely remove instructor_id from session if present
    request.session.pop('instructor_id', None)
    request.session.pop('student_id', None)
    # Clear any prior messages
    storage = messages.get_messages(request)
    storage.used = True
    
    messages.success(request, "You have been logged out.")
    return redirect('home')