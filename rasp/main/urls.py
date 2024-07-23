from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_rasp_main, name='class_rasp'),
    path('exam_rasp/', views.exam_rasp_main, name='exam_rasp'),
    path('class_pdf/', views.class_pdf, name='class_pdf'),
    path('exam_pdf/', views.exam_pdf, name='exam_pdf'),
]
