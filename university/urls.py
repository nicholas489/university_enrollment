from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    # Student authentication + dashboard
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.logout, name='student_logout'),
    
    # Student Course Enrollment
    path(
        'student/courses/available/',
        views.student_available_courses,
        name='student_available_courses'
    ),
    path(
        'student/courses/add/<int:section_id>/',
        views.student_add_course,
        name='student_add_course'
    ),
    
    # Student Drop Course
    path(
        'student/courses/drop/<int:section_id>/',
        views.student_drop_course,
        name='student_drop_course'
    ),
    
    # Instructor authentication + dashboard
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/logout/', views.logout, name='logout'),
    
    path(
        'instructor/sections/<int:section_id>/grades/',
        views.instructor_edit_grades,
        name='instructor_edit_grades'
    ),
]