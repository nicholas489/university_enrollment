from django.db import models

# Create your models here.
class Admin(models.Model):
    # Admin Table
    # (admin_id PK, username, password, first_name, last_name)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # in real apps use Django auth/password hashing
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Department(models.Model):
    # Department Table
    # (dept_id PK, name, office, email, admin_id FK)
    name = models.CharField(max_length=200)
    office = models.CharField(max_length=100, blank=True)
    email = models.EmailField()
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='departments'
    )

    def __str__(self):
        return self.name


class Student(models.Model):
    # Student Table
    # (student_id PK, email, first_name, last_name, admin_id FK)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='students'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"


class UndergraduateStudent(models.Model):
    # Undergraduate Student Table
    # (student_id PK & FK, major, year)
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='undergraduate'
    )
    major = models.CharField(max_length=200)
    year = models.PositiveSmallIntegerField()  # e.g. 1, 2, 3, 4

    def __str__(self):
        return f"Undergrad {self.student} - {self.major} (Year {self.year})"


class GraduateStudent(models.Model):
    # Graduate Student Table
    # (student_id PK & FK, degree, g_year)
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='graduate'
    )
    degree = models.CharField(max_length=200)  # e.g. MSc, PhD
    g_year = models.PositiveSmallIntegerField()  # year in the program

    def __str__(self):
        return f"Grad {self.student} - {self.degree} (Year {self.g_year})"


class Instructor(models.Model):
    # Instructor Table
    # (instructor_id PK, first_name, last_name, email, office, department_id FK, admin_id FK)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    office = models.CharField(max_length=100, blank=True)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='instructors'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='instructors'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Course(models.Model):
    # Course Table
    # (course_id PK, course_code, course_name, department_id FK, admin_id FK)
    course_code = models.CharField(max_length=20, unique=True)
    course_name = models.CharField(max_length=255)
    department = models.ForeignKey(
        Department, on_delete=models.PROTECT, related_name='courses'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='courses'
    )

    def __str__(self):
        return f"{self.course_code} - {self.course_name}"


class Section(models.Model):
    # Section Table
    # Conceptually: (course_id PK₁, section_number PK₂, term, total_capacity,
    #  current_capacity, remaining_capacity, instructor_id FK, admin_id FK)
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='sections'
    )
    section_number = models.PositiveIntegerField()
    term = models.CharField(max_length=50)  # e.g. "Fall 2025"
    total_capacity = models.PositiveIntegerField()
    current_capacity = models.PositiveIntegerField(default=0)
    remaining_capacity = models.PositiveIntegerField()
    instructor = models.ForeignKey(
        Instructor, on_delete=models.PROTECT, related_name='sections'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='sections'
    )

    class Meta:
        # Emulate composite PK (course_id, section_number) as unique constraint
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'section_number'],
                name='unique_course_section_number'
            )
        ]

    def save(self, *args, **kwargs):
        # Auto-update remaining capacity if not manually set
        if self.total_capacity is not None:
            self.remaining_capacity = self.total_capacity - self.current_capacity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.course.course_code} - Sec {self.section_number} ({self.term})"


class Grade(models.Model):
    # Grade Table
    # (grade_id PK, lab_grade, assignment_grade, midterm_grade, final_grade,
    #  admin_id FK, course_id FK, section_number FK, student_id FK)
    lab_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    assignment_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    midterm_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    final_grade = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )

    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='grades'
    )
    course = models.ForeignKey(
        Course, on_delete=models.PROTECT, related_name='grades'
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='grades'
    )
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='grades'
    )

    class Meta:
        unique_together = ('section', 'student')

    def __str__(self):
        return f"Grade for {self.student} in {self.section}"


class Enrollment(models.Model):
    # Enrollment Table
    # (enrollment_id PK, student_id FK, course_id FK, section_number FK, admin_id FK)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='enrollments'
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='enrollments'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='enrollments'
    )

    class Meta:
        unique_together = ('student', 'section')

    def __str__(self):
        return f"Enrollment: {self.student} -> {self.section}"


class Waitlist(models.Model):
    # Waitlist Table
    # Conceptually: (course_id PK₁, section_number PK₂, waitlist_id PK₃,
    #  spaces_left, admin_id FK)
    # Implemented with a single PK plus constraints.
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name='waitlists'
    )
    waitlist_id = models.PositiveIntegerField()
    spaces_left = models.PositiveIntegerField()
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='waitlists'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['section', 'waitlist_id'],
                name='unique_section_waitlist'
            )
        ]

    def __str__(self):
        return f"Waitlist {self.waitlist_id} for {self.section}"


class Wait(models.Model):
    # Wait Table
    # (wait_id PK, student_id FK, course_id FK, section_number FK,
    #  waitlist_id FK, admin_id FK)
    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name='wait_entries'
    )
    waitlist = models.ForeignKey(
        Waitlist, on_delete=models.CASCADE, related_name='entries'
    )
    admin = models.ForeignKey(
        Admin, on_delete=models.PROTECT, related_name='wait_entries'
    )

    class Meta:
        unique_together = ('student', 'waitlist')

    def __str__(self):
        return f"{self.student} on {self.waitlist}"
