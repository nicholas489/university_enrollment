from django.core.management.base import BaseCommand
from university.models import (
    Admin,
    Department,
    Student,
    UndergraduateStudent,
    GraduateStudent,
    Instructor,
    Course,
    Section,
    Enrollment,
    Grade,
    Waitlist,
    Wait,
)


class Command(BaseCommand):
    help = "Seed the Database with Mock Data."

    def handle(self, *args, **options):
        # --- Admin ---
        admin1, _ = Admin.objects.get_or_create(
            id=1,
            defaults={
                "username": "admin1",
                "password": "adminpass",  # for dev only!
                "first_name": "System",
                "last_name": "Admin",
            },
        )

        # --- Departments ---
        cs_dept, _ = Department.objects.get_or_create(
            id=1,
            defaults={
                "name": "Computer Science",
                "office": "ENG101",
                "email": "cps@torontomu.ca",
                "admin": admin1,
            },
        )

        math_dept, _ = Department.objects.get_or_create(
            id=2,
            defaults={
                "name": "Mathematics",
                "office": "ENG202",
                "email": "math@torontomu.ca",
                "admin": admin1,
            },
        )

        # --- Students ---
        s100, _ = Student.objects.get_or_create(
            id=100,
            defaults={
                "email": "john.jason@torontomu.ca",
                "password": "jason1234",
                "first_name": "John",
                "last_name": "Jason",
                "admin": admin1,
            },
        )

        s101, _ = Student.objects.get_or_create(
            id=101,
            defaults={
                "email": "jane.smith@torontomu.ca",
                "password": "jane1234",
                "first_name": "Jane",
                "last_name": "Smith",
                "admin": admin1,
            },
        )

        s102, _ = Student.objects.get_or_create(
            id=102,
            defaults={
                "email": "michael.matt@torontomu.ca",
                "password": "michael1234",
                "first_name": "Michael",
                "last_name": "Matt",
                "admin": admin1,
            },
        )

        s103, _ = Student.objects.get_or_create(
            id=103,
            defaults={
                "email": "vanessa.sarah@torontomu.ca",
                "password": "vanessa1234",
                "first_name": "Vanessa",
                "last_name": "Sarah",
                "admin": admin1,
            },
        )

        # --- Undergrad & Graduate ---
        UndergraduateStudent.objects.get_or_create(
            student=s100,
            defaults={
                "major": "Computer Science",
                "year": 2,  # ug_year
            },
        )

        GraduateStudent.objects.get_or_create(
            student=s101,
            defaults={
                "degree": "MSc Computer Science",
                "g_year": 1,
            },
        )

        UndergraduateStudent.objects.get_or_create(
            student=s102,
            defaults={
                "major": "Mathematics",
                "year": 3,
            },
        )

        GraduateStudent.objects.get_or_create(
            student=s103,
            defaults={
                "degree": "MSc Mathematics",
                "g_year": 2,
            },
        )

        # --- Instructors ---
        inst_abhari, _ = Instructor.objects.get_or_create(
            id=200,
            defaults={
                "first_name": "Abdolreza",
                "last_name": "Abhari",
                "email": "abhari@torontomu.ca",
                "password": "abdolreza1234",
                "office": "ENG201",
                "department": cs_dept,
                "admin": admin1,
            },
        )

        inst_ufkes, _ = Instructor.objects.get_or_create(
            id=201,
            defaults={
                "first_name": "Alex",
                "last_name": "Ufkes",
                "email": "aufkes@torontomu.ca",
                "password": "alex1234",
                "office": "ENG301",
                "department": math_dept,
                "admin": admin1,
            },
        )

        # --- Courses ---
        cps109, _ = Course.objects.get_or_create(
            id=300,
            defaults={
                "course_code": "CPS109",
                "course_name": "Computer Science I",
                "department": cs_dept,
                "admin": admin1,
            },
        )

        cps205, _ = Course.objects.get_or_create(
            id=301,
            defaults={
                "course_code": "CPS205",
                "course_name": "Data Structures",
                "department": cs_dept,
                "admin": admin1,
            },
        )

        mth101, _ = Course.objects.get_or_create(
            id=302,
            defaults={
                "course_code": "MTH101",
                "course_name": "Calculus I",
                "department": math_dept,
                "admin": admin1,
            },
        )

        mth210, _ = Course.objects.get_or_create(
            id=303,
            defaults={
                "course_code": "MTH210",
                "course_name": "Linear Algebra",
                "department": math_dept,
                "admin": admin1,
            },
        )

        # --- Sections ---
        # Note: in Django we use a Section FK instead of (course_id, section_number) columns.
        sec_cps109_1, _ = Section.objects.get_or_create(
            course=cps109,
            section_number=1,
            term="Fall 2025",
            defaults={
                "total_capacity": 50,
                "current_capacity": 2,
                "remaining_capacity": 48,  # will be recomputed in save()
                "instructor": inst_abhari,
                "admin": admin1,
            },
        )
        sec_cps109_1.save()

        sec_cps205_1, _ = Section.objects.get_or_create(
            course=cps205,
            section_number=1,
            term="Fall 2025",
            defaults={
                "total_capacity": 40,
                "current_capacity": 1,
                "remaining_capacity": 39,
                "instructor": inst_abhari,
                "admin": admin1,
            },
        )
        sec_cps205_1.save()

        sec_mth101_1, _ = Section.objects.get_or_create(
            course=mth101,
            section_number=1,
            term="Fall 2025",
            defaults={
                "total_capacity": 60,
                "current_capacity": 3,
                "remaining_capacity": 57,
                "instructor": inst_ufkes,
                "admin": admin1,
            },
        )
        sec_mth101_1.save()

        sec_mth210_1, _ = Section.objects.get_or_create(
            course=mth210,
            section_number=1,
            term="Fall 2025",
            defaults={
                "total_capacity": 35,
                "current_capacity": 0,
                "remaining_capacity": 35,
                "instructor": inst_ufkes,
                "admin": admin1,
            },
        )
        sec_mth210_1.save()

        # --- Enrollments ---
        Enrollment.objects.get_or_create(
            id=400,
            student=s100,
            section=sec_cps109_1,
            defaults={"admin": admin1},
        )

        Enrollment.objects.get_or_create(
            id=401,
            student=s101,
            section=sec_cps109_1,
            defaults={"admin": admin1},
        )

        Enrollment.objects.get_or_create(
            id=402,
            student=s102,
            section=sec_cps205_1,
            defaults={"admin": admin1},
        )

        Enrollment.objects.get_or_create(
            id=403,
            student=s103,
            section=sec_mth101_1,
            defaults={"admin": admin1},
        )

        Enrollment.objects.get_or_create(
            id=404,
            student=s100,
            section=sec_mth101_1,
            defaults={"admin": admin1},
        )

        Enrollment.objects.get_or_create(
            id=405,
            student=s101,
            section=sec_mth101_1,
            defaults={"admin": admin1},
        )

        # --- Grades ---
        Grade.objects.get_or_create(
            id=1,
            student=s100,
            section=sec_cps109_1,
            course=cps109,
            admin=admin1,
            defaults={
                "lab_grade": 85,
                "assignment_grade": 90,
                "midterm_grade": 88,
                "final_grade": 92,
            },
        )

        Grade.objects.get_or_create(
            id=2,
            student=s101,
            section=sec_cps109_1,
            course=cps109,
            admin=admin1,
            defaults={
                "lab_grade": 88,
                "assignment_grade": 85,
                "midterm_grade": 84,
                "final_grade": 89,
            },
        )

        Grade.objects.get_or_create(
            id=3,
            student=s102,
            section=sec_cps205_1,
            course=cps205,
            admin=admin1,
            defaults={
                "lab_grade": 92,
                "assignment_grade": 89,
                "midterm_grade": 95,
                "final_grade": 94,
            },
        )

        Grade.objects.get_or_create(
            id=4,
            student=s103,
            section=sec_mth101_1,
            course=mth101,
            admin=admin1,
            defaults={
                "lab_grade": 75,
                "assignment_grade": 78,
                "midterm_grade": 72,
                "final_grade": 80,
            },
        )

        Grade.objects.get_or_create(
            id=5,
            student=s100,
            section=sec_mth101_1,
            course=mth101,
            admin=admin1,
            defaults={
                "lab_grade": 90,
                "assignment_grade": 88,
                "midterm_grade": 86,
                "final_grade": 91,
            },
        )

        Grade.objects.get_or_create(
            id=6,
            student=s101,
            section=sec_mth101_1,
            course=mth101,
            admin=admin1,
            defaults={
                "lab_grade": 82,
                "assignment_grade": 85,
                "midterm_grade": 80,
                "final_grade": 83,
            },
        )

        # --- Waitlists ---
        # Oracle: waitlist(id, waitlist_capacity, spaces_left, course_id, section_number, admin_id)
        # Django: Waitlist(section, waitlist_id, spaces_left, admin)
        wl_cps205, _ = Waitlist.objects.get_or_create(
            section=sec_cps205_1,
            waitlist_id=1,  # corresponds to Oracle "id" = 1
            defaults={
                "spaces_left": 4,  # capacity=5 not stored in current model
                "admin": admin1,
            },
        )

        wl_mth210, _ = Waitlist.objects.get_or_create(
            section=sec_mth210_1,
            waitlist_id=2,  # corresponds to Oracle "id" = 2
            defaults={
                "spaces_left": 4,
                "admin": admin1,
            },
        )

        # --- Wait entries ---
        Wait.objects.get_or_create(
            id=500,
            student=s100,
            waitlist=wl_cps205,
            defaults={"admin": admin1},
        )

        Wait.objects.get_or_create(
            id=501,
            student=s101,
            waitlist=wl_mth210,
            defaults={"admin": admin1},
        )

        self.stdout.write(self.style.SUCCESS("Mock data seeded successfully."))
