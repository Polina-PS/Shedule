from django.shortcuts import render
from django.conf import settings
import os
from check.models import MyFiles, Faculty, Qualification, Group, Weekday, Discipline, LessonType, \
    Department, Position, Teacher, Classroom, LessonTime, Subgroup, Lesson, Exam


def get_courses_for_faculty(faculty):
    courses = set()
    groups = Group.objects.filter(faculty=faculty)
    for group in groups:
        courses.add(group.course)
    return sorted(list(courses))


def get_faculties_by_qualification(qualification_name):
    qualification = Qualification.objects.get(qualification=qualification_name)
    faculties = Faculty.objects.filter(group__qualification=qualification).distinct()
    return faculties


def get_groups_by_course(course, qualification=None, faculty=None):
    groups = Group.objects.filter(course=course)
    if qualification is not None:
        groups = groups.filter(qualification=qualification)
    if faculty is not None:
        groups = groups.filter(faculty=faculty)
    return groups


def get_group_schedule(group):
    lessons = Lesson.objects.filter(subgroup__group=group)
    schedule = []
    for lesson in lessons:
        schedule.append({
            'week_number': lesson.week_number,
            'day_of_week': lesson.weekday.weekday,  # Получение дня недели
            'lesson_number': lesson.lesson_number.lesson_number,
            'start_time': lesson.lesson_number.start_time.strftime('%H:%M'),
            'end_time': lesson.lesson_number.end_time.strftime('%H:%M'),
            'teacher': lesson.teacher.short_name,  # Получение короткого имени учителя
            'classroom': lesson.classroom.classroom,  # Получение номера аудитории
        })
    return schedule


def class_rasp_main(request):
    qualifications = Qualification.objects.all()
    faculties = []
    selected_faculty = None
    groups = []
    courses = []
    selected_course = None
    group_schedules = []
    teacher_schedules = []
    departments = []
    teachers = []
    teacher = None
    group = None

    qualification_name = request.GET.get('qualification')
    faculty_id = request.GET.get('faculty')
    course = request.GET.get('course')
    group_id = request.GET.get('group')
    department_id = request.GET.get('department')
    teacher_id = request.GET.get('teacher_id')

    qualification = None

    if request.method == 'POST':
        print("post получен")
        form_data = request.POST
        search_query = form_data.get('search_query')
        search_type = form_data.get('search_type')

        if search_type == 'group':
            # Обработка поиска по группе
            group = Group.objects.get(group=search_query)
            # Вывод расписания для группы
            lessons = Lesson.objects.filter(subgroup__group=group).distinct().select_related(
                'weekday', 'lesson_number', 'discipline', 'lesson_type', 'teacher', 'classroom'
            )
            # Организуем данные в словарь по дням недели и парам для каждой недели
            schedule_table_odd = {}
            schedule_table_even = {}

            for lesson in lessons:
                day = lesson.weekday.weekday  # Имя или ID дня недели
                lesson_num = lesson.lesson_number.lesson_number  # Номер урока

                if lesson.week_number == 1:
                    if day not in schedule_table_odd:
                        schedule_table_odd[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                    schedule_table_odd[day][lesson_num - 1].append(lesson)
                elif lesson.week_number == 2:
                    if day not in schedule_table_even:
                        schedule_table_even[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                    schedule_table_even[day][lesson_num - 1].append(lesson)
                elif lesson.week_number == 0:
                    if day not in schedule_table_odd:
                        schedule_table_odd[day] = [[] for _ in range(6)]
                    schedule_table_odd[day][lesson_num - 1].append(lesson)
                    if day not in schedule_table_even:
                        schedule_table_even[day] = [[] for _ in range(6)]
                    schedule_table_even[day][lesson_num - 1].append(lesson)

            group_schedules = {
                "odd": schedule_table_odd,
                "even": schedule_table_even
            }

        elif search_type == 'teacher':
            # Обработка поиска по преподавателю
            teacher = Teacher.objects.get(short_name__icontains=search_query)
            # Вывод расписания для преподавателя
            lessons = Lesson.objects.filter(teacher=teacher).distinct().select_related(
                'weekday', 'lesson_number', 'discipline', 'lesson_type', 'classroom'
            ).prefetch_related('subgroup__group')

            # Организуем данные в словарь по дням недели и парам для каждой недели
            schedule_table_odd = {}
            schedule_table_even = {}

            for lesson in lessons:
                day = lesson.weekday.weekday  # Имя или ID дня недели
                lesson_num = lesson.lesson_number.lesson_number  # Номер урока

                if lesson.week_number == 1:
                    if day not in schedule_table_odd:
                        schedule_table_odd[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                    schedule_table_odd[day][lesson_num - 1].append(lesson)
                elif lesson.week_number == 2:
                    if day not in schedule_table_even:
                        schedule_table_even[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                    schedule_table_even[day][lesson_num - 1].append(lesson)
                elif lesson.week_number == 0:
                    if day not in schedule_table_odd:
                        schedule_table_odd[day] = [[] for _ in range(6)]
                    schedule_table_odd[day][lesson_num - 1].append(lesson)
                    if day not in schedule_table_even:
                        schedule_table_even[day] = [[] for _ in range(6)]
                    schedule_table_even[day][lesson_num - 1].append(lesson)

            teacher_schedules = {
                "odd": schedule_table_odd,
                "even": schedule_table_even
            }

    if qualification_name:
        qualification = Qualification.objects.get(qualification=qualification_name)
        faculties = Faculty.objects.filter(group__qualification=qualification).distinct()

    if faculty_id:
        selected_faculty = Faculty.objects.get(id=faculty_id)
        courses = Group.objects.filter(qualification=qualification,
                                       faculty=selected_faculty
                                       ).values_list('course', flat=True).distinct()

    if course:
        selected_course = course
        groups = Group.objects.filter(qualification=qualification,
                                      faculty=selected_faculty,
                                      course=selected_course)

    if group_id:
        group = Group.objects.get(id=group_id)
        subgroups = Subgroup.objects.filter(group=group)
        lessons = Lesson.objects.filter(subgroup__in=subgroups).distinct().select_related(
            'weekday', 'lesson_number', 'discipline', 'lesson_type', 'teacher', 'classroom'
        )

        # Организуем данные в словарь по дням недели и парам для каждой недели
        schedule_table_odd = {}
        schedule_table_even = {}

        for lesson in lessons:
            day = lesson.weekday.weekday  # Имя или ID дня недели
            lesson_num = lesson.lesson_number.lesson_number  # Номер урока

            if lesson.week_number == 1:
                if day not in schedule_table_odd:
                    schedule_table_odd[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                schedule_table_odd[day][lesson_num - 1].append(lesson)
            elif lesson.week_number == 2:
                if day not in schedule_table_even:
                    schedule_table_even[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                schedule_table_even[day][lesson_num - 1].append(lesson)
            elif lesson.week_number == 0:
                if day not in schedule_table_odd:
                    schedule_table_odd[day] = [[] for _ in range(6)]
                schedule_table_odd[day][lesson_num - 1].append(lesson)
                if day not in schedule_table_even:
                    schedule_table_even[day] = [[] for _ in range(6)]
                schedule_table_even[day][lesson_num - 1].append(lesson)

        group_schedules = {
            "odd": schedule_table_odd,
            "even": schedule_table_even
        }

    if 'teacher' in request.GET:
        departments = Department.objects.all()

    if department_id:
        departments = Department.objects.all()
        teachers = Teacher.objects.filter(department_id=department_id)

    if teacher_id:
        teacher = Teacher.objects.get(id=teacher_id)
        lessons = Lesson.objects.filter(teacher=teacher).distinct().select_related(
            'weekday', 'lesson_number', 'discipline', 'lesson_type', 'classroom'
        ).prefetch_related('subgroup__group')
        departments = Department.objects.all()
        teachers = Teacher.objects.filter(department_id=teacher.department_id)

        # Организуем данные в словарь по дням недели и парам для каждой недели
        schedule_table_odd = {}
        schedule_table_even = {}

        for lesson in lessons:
            day = lesson.weekday.weekday  # Имя или ID дня недели
            lesson_num = lesson.lesson_number.lesson_number  # Номер урока

            if lesson.week_number == 1:
                if day not in schedule_table_odd:
                    schedule_table_odd[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                schedule_table_odd[day][lesson_num - 1].append(lesson)
            elif lesson.week_number == 2:
                if day not in schedule_table_even:
                    schedule_table_even[day] = [[] for _ in range(6)]  # Предполагаем максимум 6 уроков в день
                schedule_table_even[day][lesson_num - 1].append(lesson)
            elif lesson.week_number == 0:
                if day not in schedule_table_odd:
                    schedule_table_odd[day] = [[] for _ in range(6)]
                schedule_table_odd[day][lesson_num - 1].append(lesson)
                if day not in schedule_table_even:
                    schedule_table_even[day] = [[] for _ in range(6)]
                schedule_table_even[day][lesson_num - 1].append(lesson)

        teacher_schedules = {
            "odd": schedule_table_odd,
            "even": schedule_table_even
        }

    return render(request, 'main/class_rasp_main.html', {
        'qualifications': qualifications,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'courses': list(sorted(set(courses))),  # Remove duplicates and sort them
        'selected_course': selected_course,
        'groups': groups,
        'group_schedules': group_schedules,
        'departments': departments,
        'teachers': teachers,
        'teacher_schedules': teacher_schedules,
        'valid_subgroup_numbers': [1, 2],  # Добавляем допустимые номера подгрупп
        'teacher': teacher,
        'group': group,
    })


def exam_rasp_main(request):
    qualifications = Qualification.objects.all()
    faculties = []
    selected_faculty = None
    groups = []
    courses = []
    selected_course = None
    exam_info = []
    exam_info_teacher = []
    departments = []
    teachers = []
    teacher = None
    group = None

    qualification_name = request.GET.get('qualification')
    faculty_id = request.GET.get('faculty')
    course = request.GET.get('course')
    group_id = request.GET.get('group')
    department_id = request.GET.get('department')
    teacher_id = request.GET.get('teacher_id')
    qualification = None

    if request.method == 'POST':
        print("post получен")
        form_data = request.POST
        search_query = form_data.get('search_query')
        search_type = form_data.get('search_type')

        if search_type == 'group':
            # Обработка поиска по группе
            group = Group.objects.get(group=search_query)
            subgroups = Subgroup.objects.filter(group=group)
            # Вывод расписания для группы
            exams = Exam.objects.filter(lesson__subgroup__in=subgroups)
            for exam in exams:
                exam_info.append({
                    'exam_date': exam.exam_date,
                    'start_time': exam.start_time.start_time,
                    'discipline': exam.lesson.discipline.discipline,
                    'teacher': exam.lesson.teacher.short_name
                })

        elif search_type == 'teacher':
            # Обработка поиска по преподавателю
            teacher = Teacher.objects.get(short_name__icontains=search_query)
            exams = Exam.objects.filter(lesson__teacher=teacher)
            for exam in exams:
                groups = [subgroup.group.group for subgroup in exam.lesson.subgroup.all()]
                exam_info_teacher.append({
                    'exam_date': exam.exam_date,
                    'start_time': exam.start_time.start_time,
                    'discipline': exam.lesson.discipline.discipline,
                    'groups': ', '.join(groups)
                })

    if qualification_name:
        qualification = Qualification.objects.get(qualification=qualification_name)
        faculties = Faculty.objects.filter(group__qualification=qualification).distinct()
    if faculty_id:
        selected_faculty = Faculty.objects.get(id=faculty_id)
        courses = Group.objects.filter(qualification=qualification,
                                       faculty=selected_faculty
                                       ).values_list('course', flat=True).distinct()
    if course:
        selected_course = course
        groups = Group.objects.filter(qualification=qualification,
                                      faculty=selected_faculty,
                                      course=selected_course)
    if group_id:
        group = Group.objects.get(id=group_id)
        subgroups = Subgroup.objects.filter(group=group)
        exams = Exam.objects.filter(lesson__subgroup__in=subgroups)
        for exam in exams:
            exam_info.append({
                'exam_date': exam.exam_date,
                'start_time': exam.start_time.start_time,
                'discipline': exam.lesson.discipline.discipline,
                'teacher': exam.lesson.teacher.short_name
            })

    if 'teacher' in request.GET:
        departments = Department.objects.all()
    if department_id:
        departments = Department.objects.all()
        teachers = Teacher.objects.filter(department_id=department_id)

    if teacher_id:
        teacher = Teacher.objects.get(id=teacher_id)
        exams = Exam.objects.filter(lesson__teacher=teacher)
        for exam in exams:
            groups = [subgroup.group.group for subgroup in exam.lesson.subgroup.all()]
            exam_info_teacher.append({
                'exam_date': exam.exam_date,
                'start_time': exam.start_time.start_time,
                'discipline': exam.lesson.discipline.discipline,
                'groups': ', '.join(groups)
            })
        departments = Department.objects.all()
        teachers = Teacher.objects.filter(department_id=teacher.department_id)

    return render(request, 'main/exam_rasp_main.html', {
        'qualifications': qualifications,
        'faculties': faculties,
        'selected_faculty': selected_faculty,
        'courses': list(sorted(set(courses))),
        'selected_course': selected_course,
        'groups': groups,
        'exam_info': exam_info,
        'exam_info_teacher': exam_info_teacher,
        'departments': departments,
        'teachers': teachers,
        'teacher': teacher,
        'group': group,
    })


def class_pdf(request):
    files = MyFiles.objects.filter(directory_path=os.path.join(settings.MEDIA_ROOT, 'pdf_files', '2023-2024_autumn'),
                                   file_type='class_pdf')
    return render(request, 'main/class_pdf.html', {'files': files})


def exam_pdf(request):
    files = MyFiles.objects.filter(directory_path=os.path.join(settings.MEDIA_ROOT, 'pdf_files', '2023-2024_autumn'),
                                   file_type='exam_pdf')
    return render(request, 'main/exam_pdf.html', {'files': files})

