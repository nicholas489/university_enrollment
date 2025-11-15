from django.contrib import admin
from .models import (
    Admin as AdminModel,
    Department,
    Student,
    UndergraduateStudent,
    GraduateStudent,
    Instructor,
    Course,
    Section,
    Grade,
    Enrollment,
    Waitlist,
    Wait
)

# Register your models here.
@admin.register(AdminModel)
class AdminAdmin(admin.ModelAdmin):
    list_display = ("username", "first_name", "last_name")
    search_fields = ("username", "first_name", "last_name")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "office", "email", "admin")
    search_fields = ("name", "email")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "admin")
    search_fields = ("first_name", "last_name", "email")


@admin.register(UndergraduateStudent)
class UndergraduateStudentAdmin(admin.ModelAdmin):
    list_display = ("student", "major", "year")


@admin.register(GraduateStudent)
class GraduateStudentAdmin(admin.ModelAdmin):
    list_display = ("student", "degree", "g_year")


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "department", "admin")
    search_fields = ("first_name", "last_name", "email")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("course_code", "course_name", "department", "admin")
    search_fields = ("course_code", "course_name")


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "section_number",
        "term",
        "instructor",
        "total_capacity",
        "current_capacity",
        "remaining_capacity",
        "admin",
    )
    list_filter = ("term", "course")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "section", "lab_grade", "assignment_grade",
                    "midterm_grade", "final_grade", "admin")
    list_filter = ("section",)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "section", "admin")
    list_filter = ("section", "admin")


@admin.register(Waitlist)
class WaitlistAdmin(admin.ModelAdmin):
    list_display = ("section", "waitlist_id", "spaces_left", "admin")


@admin.register(Wait)
class WaitAdmin(admin.ModelAdmin):
    list_display = ("student", "waitlist", "admin")