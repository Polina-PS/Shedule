from django.urls import path
from . import views

app_name = 'check'  # Пространство имен для приложения "check"

urlpatterns = [
    path('load', views.load_file_get, name='check_page'),  # GET запрос
    path('load_post', views.load_file_post, name='check_page_post'),  # POST запрос
    path('list_folders/', views.list_folders, name='list_folders'),
    path('list_files/<str:folder>/', views.list_files, name='list_files'),
    path('download/<str:folder>/<str:filename>/', views.download_file, name='download_file'),
    path('download_xml/<str:folder>/<str:filename>/', views.download_file_xml, name='download_file_xml'),
    path('schedule_check/<str:folder>/', views.schedule_check, name='schedule_check'),
    path('list_files/<str:folder>/report/', views.report, name='report'),
    path('rasp_to_db/', views.rasp_to_db, name='rasp_to_db'),
]

