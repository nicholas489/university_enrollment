from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Course, Section

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