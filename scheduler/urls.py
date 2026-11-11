from django.urls import path
from scheduler.views import hod_dashboard
from .views import (
    timetable_view,
    home_view,
    hod_login,
    teacher_login,
    student_login,
)
from .views import (
    teacher_list,
    add_teacher,
    edit_teacher,
    delete_teacher
)
from .views import (
    subject_list,
    add_subject,
    edit_subject,
    delete_subject
)
from .views import (
    class_list,
    add_class,
    edit_class,
    delete_class
)
from .views import (
    allocation_list,
    add_allocation,
    edit_allocation,
    delete_allocation
)

urlpatterns = [
    path('', home_view, name='home'),
    path('generate/', timetable_view, name='generate'),

    path('hod-login/', hod_login, name='hod_login'),
    path('teacher-login/', teacher_login, name='teacher_login'),
    path('student-login/', student_login, name='student_login'),
    path('hod-dashboard/', hod_dashboard, name='hod_dashboard'),
    path('teachers/', teacher_list, name='teacher_list'),
    path('teachers/add/', add_teacher, name='add_teacher'),
    path('teachers/edit/<int:pk>/', edit_teacher, name='edit_teacher'),
    path('teachers/delete/<int:pk>/', delete_teacher, name='delete_teacher'),
    path('subjects/', subject_list, name='subject_list'),
    path('subjects/add/', add_subject, name='add_subject'),
    path('subjects/edit/<int:pk>/', edit_subject, name='edit_subject'),
    path('subjects/delete/<int:pk>/', delete_subject, name='delete_subject'),
    path('classes/', class_list, name='class_list'),
    path('classes/add/', add_class, name='add_class'),
    path('classes/edit/<int:pk>/', edit_class, name='edit_class'),
    path('classes/delete/<int:pk>/', delete_class, name='delete_class'),
    path('allocations/', allocation_list, name='allocation_list'),

    path('allocations/add/', add_allocation, name='add_allocation'),

    path('allocations/edit/<int:pk>/', edit_allocation, name='edit_allocation'),

    path('allocations/delete/<int:pk>/', delete_allocation, name='delete_allocation'),
]