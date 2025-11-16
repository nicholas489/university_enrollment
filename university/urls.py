from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('sections/<int:course_id>/', views.section_list, name='section_list'),
]