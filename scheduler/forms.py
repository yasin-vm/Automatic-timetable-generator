
from django import forms
from .models import Teacher, Class, Subject, SubjectAllocation


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['teacher_name', 'department']

        widgets = {
            'teacher_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter teacher name'
            }),
            'department': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter department'
            }),
        }

class ClassForm(forms.ModelForm):
    class Meta:
        model = Class
        fields = ['class_name']


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = [
            'subject_code',
            'subject_name',
            'weekly_hours',
            'is_lab',
            'requires_consecutive',
            'class_ref'
        ]


class SubjectAllocationForm(forms.ModelForm):
    class Meta:
        model = SubjectAllocation
        fields = [
            'class_ref',
            'subject',
            'teacher',
            'mode'
        ]

