from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Universal logout (for students, instructors, admin)
    path('logout/', views.logout_view, name='logout'),

    # Student authentication + dashboard
    path('student/login/', views.student_login, name='student_login'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/logout/', views.logout_view, name='student_logout'),

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
    path(
        'student/courses/drop/<int:section_id>/',
        views.student_drop_course,
        name='student_drop_course'
    ),

    # Instructor authentication + dashboard
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/logout/', views.logout_view, name='instructor_logout'),

    # Instructor grade editing
    path(
        'instructor/sections/<int:section_id>/grades/',
        views.instructor_edit_grades,
        name='instructor_edit_grades'
    ),

    # Admin authentication + dashboard
    path('admin/login/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', views.logout_view, name='admin_logout'),

    # Admin functionalities
    path('admin/create_course/', views.admin_create_course, name='admin_create_course'),
    path('admin/waitlist/', views.admin_waitlist, name='admin_waitlist'),

    # Tables Menu
    path('tables_menu/', views.tables_menu, name='tables_menu'),
    path('tables_menu/drop_tables/', views.drop_tables_page, name='drop_tables_page'),
    path('tables_menu/create_tables/', views.create_tables_page, name='create_tables_page'),
    path('tables_menu/populate_tables/', views.populate_tables_page, name='populate_tables_page'),
    path('tables_menu/query_tables/', views.query_tables_page, name='query_tables_page'),
]