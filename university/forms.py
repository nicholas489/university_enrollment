from django import forms
from .models import Department, Instructor, Course

# -------------------------
# Authentication Forms
# -------------------------
class InstructorLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )


class StudentLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )


class AdminLoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )


# -------------------------
# Admin Forms
# -------------------------
class AdminCreateCourseForm(forms.Form):
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label="Department")
    instructor = forms.ModelChoiceField(queryset=Instructor.objects.all(), label="Instructor")
    course_code = forms.CharField(max_length=10, label="Course Code")
    course_name = forms.CharField(max_length=100, label="Course Name")
    # description = forms.CharField(
    #     max_length=100,
    #     label="Course Description"
    # )
    total_capacity = forms.IntegerField(min_value=1, label="Capacity per Section")
    num_sections = forms.IntegerField(min_value=1, label="Number of Sections")

    # def __init__(self, *args, **kwargs):
    #     # Optional: pass department_id to filter instructors
    #     department_id = kwargs.pop('department_id', None)
    #     super().__init__(*args, **kwargs)
    #     if department_id:
    #         self.fields['instructor'].queryset = Instructor.objects.filter(department_id=department_id)
    #     else:
    #         # Initially empty queryset until department is selected
    #         self.fields['instructor'].queryset = Instructor.objects.none()