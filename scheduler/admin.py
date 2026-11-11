from django.contrib import admin
from .models import Teacher, Class, Subject, SubjectAllocation

admin.site.register(Teacher)
admin.site.register(Class)
admin.site.register(Subject)
admin.site.register(SubjectAllocation)