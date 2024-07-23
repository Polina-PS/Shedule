from django.contrib import admin
from .models import MyFiles, Faculty, Qualification, Group, Weekday, Discipline, LessonType, \
    Department, Position, Teacher, Classroom, LessonTime, Subgroup, Lesson, ExamTime, Exam


@admin.register(MyFiles)
class MyFilesAdmin(admin.ModelAdmin):
    list_display = ['file', 'file_type', 'year', 'semester', 'directory_path']


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['faculty']


@admin.register(Qualification)
class QualificationAdmin(admin.ModelAdmin):
    list_display = ['qualification']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['group', 'faculty', 'course', 'qualification', 'num_students']


@admin.register(Weekday)
class WeekdayAdmin(admin.ModelAdmin):
    list_display = ['weekday']


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ['discipline']


@admin.register(LessonType)
class LessonTypeAdmin(admin.ModelAdmin):
    list_display = ['lesson_type']


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['department', 'department_number']


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ['position']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'short_name', 'position', 'department']


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ['center_number', 'classroom', 'num_seats']


@admin.register(LessonTime)
class LessonTimeAdmin(admin.ModelAdmin):
    list_display = ['lesson_number', 'start_time', 'end_time']


@admin.register(Subgroup)
class SubgroupAdmin(admin.ModelAdmin):
    list_display = ['group', 'subgroup_number']


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['id', 'week_number', 'weekday', 'lesson_number', 'discipline', 'lesson_type',
                    'teacher', 'classroom', 'start_date', 'end_date', 'groups_list', 'subgroups_list']

    def subgroups_list(self, obj):
        return ', '.join([str(sg) for sg in obj.subgroup.all()])
    subgroups_list.short_description = 'Подгруппы'

    def groups_list(self, obj):
        groups = obj.subgroup.all().values_list('group', flat=True).distinct()
        return ', '.join([str(Group.objects.get(id=g)) for g in groups])
    groups_list.short_description = 'Группы'


@admin.register(ExamTime)
class ExamTimeAdmin(admin.ModelAdmin):
    list_display = ['start_time']


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ['lesson', 'exam_date', 'start_time']
