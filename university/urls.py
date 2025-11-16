from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('sections/<int:course_id>/', views.section_list, name='section_list'),
    
    # Instructor authentication
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/logout/', views.logout, name='logout'),
    
    # Student authentication
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.logout, name='student_logout'),
]