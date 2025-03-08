from django.db import models
from django.contrib.auth.models import User

class Professor(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    name = models.CharField(max_length=100)

class Module(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    year = models.IntegerField()
    semester = models.IntegerField()
    professors = models.ManyToManyField(Professor)

    class Meta:
        unique_together = ['code', 'year', 'semester']

    def __str__(self):
        return f"{self.name} ({self.code}, {self.year}, Semester: {self.semester})"

class Rating(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    professor = models.ForeignKey('Professor', on_delete=models.CASCADE)
    module = models.ForeignKey('Module', on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ['student', 'professor', 'module']

    def __str__(self):
        return f"{self.student} rated {self.professor} in {self.module} with {self.rating}"


