from django.shortcuts import render
from django.http import HttpResponse
from django.http import FileResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.files.storage import FileSystemStorage
from .models import MyFiles
from .utils import parser_class_rasp_xls, parser_exam_rasp, parser_sved, parser_workload, check_xml_class, \
    check_xml_exam, class_to_db, exam_to_db
from django.conf import settings
import os


@staff_member_required
def load_file_get(request):
    # Обработка GET запроса
    return render(request, 'check/load_file.html')


@staff_member_required
def load_file_post(request):
    file = request.FILES.get('file')
    category = request.POST.get('type')  # Получаем выбранную категорию из формы
    semester = request.POST.get('semester')
    year = request.POST.get('year')
    directories = {
        'autumn_spring': [
            os.path.join(settings.MEDIA_ROOT, 'upl_files', f'{year}_autumn'),
            os.path.join(settings.MEDIA_ROOT, 'upl_files', f'{year}_spring')
        ],
        'autumn': os.path.join(settings.MEDIA_ROOT, 'upl_files', f'{year}_autumn'),
        'spring': os.path.join(settings.MEDIA_ROOT, 'upl_files', f'{year}_spring')
    }
    pdf_directories = {
        'class_pdf': os.path.join(settings.MEDIA_ROOT, 'pdf_files', f'{year}_{semester}'),
        'exam_pdf': os.path.join(settings.MEDIA_ROOT, 'pdf_files', f'{year}_{semester}')
    }
    if file is not None and category != 'empty' and semester in directories and year != 'empty':
        if category in ['class_pdf', 'exam_pdf']:
            fs = FileSystemStorage(location=pdf_directories[category])
            filename = fs.save(file.name, file)
            MyFiles.objects.create(file=filename, file_type=category, year=year, semester=semester,
                                   directory_path=pdf_directories[category])
        else:
            if isinstance(directories[semester], list):
                for directory in directories[semester]:
                    fs = FileSystemStorage(location=directory)
                    filename = fs.save(file.name, file)
                    MyFiles.objects.create(file=filename, file_type=category, year=year, semester=semester, directory_path = directory)
            else:
                fs = FileSystemStorage(location=directories[semester])
                filename = fs.save(file.name, file)
                MyFiles.objects.create(file=filename, file_type=category, year=year, semester=semester, directory_path=directories[semester])
    return render(request, 'check/load_file.html')


@staff_member_required
def list_folders(request):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'upl_files')
    folders = [name for name in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, name))]
    return render(request, 'check/list_folders.html', {'folders': folders})


@staff_member_required
def list_files(request, folder):

    folder_path = os.path.join(settings.MEDIA_ROOT, 'upl_files', folder)
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        year, semester = folder.split('_')
        files = [{'folder': folder, 'file_name': f, 'year': year, 'semester': semester} for f in os.listdir(folder_path)
                 if os.path.isfile(os.path.join(folder_path, f))]

        my_files = []

        for file_info in files:
            my_file = MyFiles.objects.filter(file__endswith=file_info['file_name']).filter(
                file_type__in=['class_rasp', 'exam_rasp']).first()

            if my_file:
                my_file.file_name = file_info['file_name']
                my_file.year = file_info['year']
                my_file.semester = file_info['semester']

                if my_file.file_type == 'class_rasp':
                    my_file.name_button = 'Проверить расписание занятий'
                elif my_file.file_type == 'exam_rasp':
                    my_file.name_button = 'Проверить расписание экзаменов'

                my_files.append(my_file)
        return render(request, 'check/list_files.html', {'folder': folder, 'files': files, 'my_files': my_files})
    else:
        return HttpResponse("Директория не найдена")


@staff_member_required
def download_file(request, folder, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'upl_files', folder, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse("Файл не найден")


@staff_member_required
def download_file_xml(request, folder, filename):
    file_path = os.path.join(settings.MEDIA_ROOT, 'create_xml', folder, filename)
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    else:
        return HttpResponse("Файл не найден")


@staff_member_required
def report(request, folder):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'create_xml', folder)
    files = []

    my_files = MyFiles.objects.filter(directory_path=folder_path, file_type='success').values_list('file', flat=True)
    print(my_files)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        for filename in os.listdir(folder_path):
            if filename == 'report_class_rasp.xml' or filename == 'report_exam_rasp.xml':
                files.append(filename)

    return render(request, 'check/report.html', {'folder': folder, 'files': files, 'my_files': my_files})


@staff_member_required
def rasp_to_db(request):
    file_name = request.GET.get('file_name')  # название report
    folder = request.GET.get('folder')
    year_semester = folder.split('_')
    year = year_semester[0]
    semester = year_semester[1]
    my_file = MyFiles.objects.filter(file=file_name, year=year, semester=semester).first()
    directory_path = my_file.directory_path  # путь до xml

    if file_name == 'report_class_rasp.xml':
        class_to_db(directory_path, year, semester)
    elif file_name == 'report_exam_rasp.xml':
        exam_to_db(directory_path, year, semester)

    return render(request, 'check/rasp_to_db.html')


@staff_member_required
def schedule_check(request, folder):
    filename = request.GET.get('filename', None)
    type_file = request.GET.get('file_type', None)
    year, semester = folder.split('_')
    file_semester = semester
    print(type_file)
    folder_path = os.path.join(settings.MEDIA_ROOT, 'upl_files', folder)
    file_path = os.path.join(folder_path, filename)
    my_files = MyFiles.objects.filter(directory_path=folder_path)
    # создание всех xml
    output_folder = None
    report_name = None
    parsed_data = []

    if type_file == 'class_rasp':
        output = parser_class_rasp_xls(file_path, filename, folder, type_file)
        if output:
            output_folder = output[0]
            folder = output[1]
        print('filename')
        print(filename)
    elif type_file == 'exam_rasp':
        output = parser_exam_rasp(file_path, filename, folder, type_file)
        if output:
            output_folder = output[0]
            folder = output[1]
        print('filename')
        print(filename)

    for file in my_files.values():
        file_path = os.path.join(file['directory_path'], file['file'])
        print('file_path')
        print(file_path)
        file_type = file['file_type']

        if file_type == 'sved':
            parsed_data.append(parser_sved(file_path, folder, file_type))
        elif file_type == 'workload':
            parsed_data.append(parser_workload(file_path, folder, file_type, file_semester))

    # проведение проверки определенного расписания
    for file in my_files.values():
        file_path = os.path.join(file['directory_path'], file['file'])
        print('Проверка xml')
        print(file['file'])
        file_type = file['file_type']

        if file_type == type_file:
            if file_type == 'class_rasp':
                report_name = check_xml_class(output_folder, folder)
            elif file_type == 'exam_rasp':
                report_name = check_xml_exam(output_folder, folder)

    return render(request, 'check/schedule_check.html', {'folder': folder, 'report_name': report_name})


