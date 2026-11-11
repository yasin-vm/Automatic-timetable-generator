from django.db import models

from django.conf import settings


class Class(models.Model):
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return self.class_name


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.teacher_name


class Subject(models.Model):
    subject_code = models.CharField(max_length=70)
    subject_name = models.CharField(max_length=100)
    weekly_hours = models.IntegerField()
    is_lab = models.BooleanField(default=False)
    requires_consecutive = models.BooleanField(default=False)
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject_name


class SubjectAllocation(models.Model):
    class_ref = models.ForeignKey(Class, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    mode = models.CharField(
    choices=[('REG','Regular'), ('REM','Remedial')],
    max_length=5
)

    def __str__(self):
        return f"{self.class_ref} - {self.subject} - {self.teacher}"


class UserProfile(models.Model):

    ROLE_CHOICES = [
        ('HOD', 'HOD'),
        ('TEACHER', 'Teacher'),
        ('STUDENT', 'Student'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES
    )

    teacher = models.OneToOneField(
        Teacher,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    class_ref = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.role}"
