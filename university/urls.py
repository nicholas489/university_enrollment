from django.urls import path
from . import views

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('sections/<int:course_id>/', views.section_list, name='section_list'),
]