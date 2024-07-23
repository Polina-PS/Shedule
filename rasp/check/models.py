from django.db import models


class MyFiles(models.Model):
    file = models.FileField(upload_to='upl_files')
    file_type = models.CharField(max_length=50)
    year = models.CharField(max_length=50)
    semester = models.CharField(max_length=50)
    directory_path = models.CharField(max_length=150)

    def get_file_path(self):
        return self.file.path


class Faculty(models.Model):
    faculty = models.CharField(max_length=200)

    def __str__(self):
        return self.faculty


class Qualification(models.Model):
    qualification = models.CharField(max_length=100)

    def __str__(self):
        return self.qualification


class Group(models.Model):
    group = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    course = models.IntegerField()
    qualification = models.ForeignKey(Qualification, on_delete=models.CASCADE)
    num_students = models.IntegerField()

    class Meta:
        ordering = ['group']

    def __str__(self):
        return self.group


class Weekday(models.Model):
    weekday = models.CharField(max_length=100)

    def __str__(self):
        return self.weekday


class Discipline(models.Model):
    discipline = models.CharField(max_length=100)

    class Meta:
        ordering = ['discipline']

    def __str__(self):
        return self.discipline


class LessonType(models.Model):
    lesson_type = models.CharField(max_length=100)

    def __str__(self):
        return self.lesson_type


class Department(models.Model):
    department = models.CharField(max_length=100)
    department_number = models.IntegerField()

    def __str__(self):
        return str(self.department_number)


class Position(models.Model):
    position = models.CharField(max_length=100)

    def __str__(self):
        return self.position


class Teacher(models.Model):
    full_name = models.CharField(max_length=100, default='')
    short_name = models.CharField(max_length=100, default='')
    position = models.ForeignKey(Position, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        ordering = ['short_name']

    def __str__(self):
        return self.short_name


class Classroom(models.Model):
    center_number = models.IntegerField()
    classroom = models.IntegerField()
    num_seats = models.IntegerField(null=True)

    class Meta:
        unique_together = ('center_number', 'classroom')

    def __str__(self):
        return str(self.classroom)


class LessonTime(models.Model):
    lesson_number = models.IntegerField()
    start_time = models.TimeField(auto_now=False, auto_now_add=False)
    end_time = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return str(self.lesson_number)


class Subgroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subgroup_number = models.IntegerField()

    class Meta:
        ordering = ['group', 'subgroup_number']

    def __str__(self):
        return str(self.subgroup_number)


class Lesson(models.Model):
    week_number = models.IntegerField()
    weekday = models.ForeignKey(Weekday, on_delete=models.CASCADE)
    lesson_number = models.ForeignKey(LessonTime, on_delete=models.CASCADE)
    subgroup = models.ManyToManyField(Subgroup)
    discipline = models.ForeignKey(Discipline, on_delete=models.CASCADE)
    lesson_type = models.ForeignKey(LessonType, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        ordering = ['weekday']

    def __str__(self):
        return str(self.discipline)


class ExamTime(models.Model):
    start_time = models.TimeField()

    def __str__(self):
        return str(self.start_time)


class Exam(models.Model):
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE)
    exam_date = models.DateField()
    start_time = models.ForeignKey(ExamTime, on_delete=models.CASCADE)

    class Meta:
        ordering = ['exam_date', 'start_time']


