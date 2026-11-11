from django.shortcuts import render, get_object_or_404
from .solver import generate_timetable
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Teacher
from .forms import TeacherForm
from .models import Subject
from .forms import SubjectForm
from .models import Class
from .forms import ClassForm
from .models import SubjectAllocation
from .forms import SubjectAllocationForm

def timetable_view(request):
    timetable = generate_timetable()
    return render(request, "timetable.html", {
        "timetable": timetable
    })
def home_view(request):
    return render(request, "home.html")


def role_login(request, role):
    if request.user.is_authenticated:
        if hasattr(request.user, 'profile'):
            if request.user.profile.role == role:
                return redirect(f'{role.lower()}_dashboard')
            logout(request)

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            try:
                profile = user.profile

                if profile.role == role:
                    login(request, user)
                    return redirect(f'{role.lower()}_dashboard')

                messages.error(request, 'You are not authorized for this portal.')

            except UserProfile.DoesNotExist:
                messages.error(request, 'User role is not configured.')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html', {'role': role})


def hod_login(request):
    return role_login(request, 'HOD')


def teacher_login(request):
    return role_login(request, 'TEACHER')


def student_login(request):
    return role_login(request, 'STUDENT')

@login_required
def hod_dashboard(request):
    if not hasattr(request.user, 'profile'):
        return HttpResponseForbidden("Access denied")

    if request.user.profile.role != 'HOD':
        return HttpResponseForbidden("Access denied")

    return render(request, 'hod_dashboard.html')

# HOD access protection
def hod_required(view_func):
    from functools import wraps

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not hasattr(request.user, 'profile'):
            return HttpResponseForbidden("Access denied")

        if request.user.profile.role != 'HOD':
            return HttpResponseForbidden("Only HOD can access this page")

        return view_func(request, *args, **kwargs)

    return wrapper


# View all teachers
@hod_required
def teacher_list(request):
    teachers = Teacher.objects.all()

    return render(request, 'teacher_list.html', {
        'teachers': teachers
    })


# Add a teacher
@hod_required
def add_teacher(request):

    if request.method == 'POST':
        form = TeacherForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher added successfully!')
            return redirect('teacher_list')

    else:
        form = TeacherForm()

    return render(request, 'teacher_form.html', {
        'form': form,
        'title': 'Add Teacher'
    })


# Edit teacher details
@hod_required
def edit_teacher(request, pk):

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        form = TeacherForm(request.POST, instance=teacher)

        if form.is_valid():
            form.save()
            messages.success(request, 'Teacher updated successfully!')
            return redirect('teacher_list')

    else:
        form = TeacherForm(instance=teacher)

    return render(request, 'teacher_form.html', {
        'form': form,
        'title': 'Edit Teacher'
    })


# Delete a teacher
@hod_required
def delete_teacher(request, pk):

    teacher = get_object_or_404(Teacher, pk=pk)

    if request.method == 'POST':
        teacher.delete()
        messages.success(request, 'Teacher deleted successfully!')
        return redirect('teacher_list')

    return render(request, 'teacher_confirm_delete.html', {
        'teacher': teacher
    })

# View all subjects
@hod_required
def subject_list(request):

    subjects = Subject.objects.select_related('class_ref').all()

    return render(request, 'subject_list.html', {
        'subjects': subjects
    })


# Add a subject
@hod_required
def add_subject(request):

    if request.method == 'POST':
        form = SubjectForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Subject added successfully!')
            return redirect('subject_list')

    else:
        form = SubjectForm()

    return render(request, 'subject_form.html', {
        'form': form,
        'title': 'Add Subject'
    })


# Edit subject
@hod_required
def edit_subject(request, pk):

    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)

        if form.is_valid():
            form.save()
            messages.success(request, 'Subject updated successfully!')
            return redirect('subject_list')

    else:
        form = SubjectForm(instance=subject)

    return render(request, 'subject_form.html', {
        'form': form,
        'title': 'Edit Subject'
    })


# Delete subject
@hod_required
def delete_subject(request, pk):

    subject = get_object_or_404(Subject, pk=pk)

    if request.method == 'POST':
        subject.delete()
        messages.success(request, 'Subject deleted successfully!')
        return redirect('subject_list')

    return render(request, 'subject_confirm_delete.html', {
        'subject': subject
    })

# View all classes
@hod_required
def class_list(request):
    classes = Class.objects.all()

    return render(request, 'class_list.html', {
        'classes': classes
    })


# Add a class
@hod_required
def add_class(request):

    if request.method == 'POST':
        form = ClassForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Class added successfully!')
            return redirect('class_list')

    else:
        form = ClassForm()

    return render(request, 'class_form.html', {
        'form': form,
        'title': 'Add Class'
    })


# Edit a class
@hod_required
def edit_class(request, pk):

    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        form = ClassForm(request.POST, instance=class_obj)

        if form.is_valid():
            form.save()
            messages.success(request, 'Class updated successfully!')
            return redirect('class_list')

    else:
        form = ClassForm(instance=class_obj)

    return render(request, 'class_form.html', {
        'form': form,
        'title': 'Edit Class'
    })


# Delete a class
@hod_required
def delete_class(request, pk):

    class_obj = get_object_or_404(Class, pk=pk)

    if request.method == 'POST':
        class_obj.delete()
        messages.success(request, 'Class deleted successfully!')
        return redirect('class_list')

    return render(request, 'class_confirm_delete.html', {
        'class_obj': class_obj
    })

# View all allocations
@hod_required
def allocation_list(request):

    allocations = SubjectAllocation.objects.select_related(
        'class_ref',
        'subject',
        'teacher'
    ).all()

    return render(request, 'allocation_list.html', {
        'allocations': allocations
    })


# Add an allocation
@hod_required
def add_allocation(request):

    if request.method == 'POST':
        form = SubjectAllocationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Teacher allocated successfully!'
            )
            return redirect('allocation_list')

    else:
        form = SubjectAllocationForm()

    return render(request, 'allocation_form.html', {
        'form': form,
        'title': 'Allocate Teacher'
    })


# Edit an allocation
@hod_required
def edit_allocation(request, pk):

    allocation = get_object_or_404(
        SubjectAllocation,
        pk=pk
    )

    if request.method == 'POST':
        form = SubjectAllocationForm(
            request.POST,
            instance=allocation
        )

        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Allocation updated successfully!'
            )
            return redirect('allocation_list')

    else:
        form = SubjectAllocationForm(instance=allocation)

    return render(request, 'allocation_form.html', {
        'form': form,
        'title': 'Edit Allocation'
    })


# Delete an allocation
@hod_required
def delete_allocation(request, pk):

    allocation = get_object_or_404(
        SubjectAllocation,
        pk=pk
    )

    if request.method == 'POST':
        allocation.delete()
        messages.success(
            request,
            'Allocation deleted successfully!'
        )
        return redirect('allocation_list')

    return render(request, 'allocation_confirm_delete.html', {
        'allocation': allocation
    })

