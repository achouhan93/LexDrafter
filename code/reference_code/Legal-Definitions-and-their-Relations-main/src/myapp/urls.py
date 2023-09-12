from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('result/', views.result, name='result'),
    path('annotations/', views.annotations_page, name='annotations'),
    path('download/', views.download_definitions_file, name='download_definitions_file'),
    path('download-annotations/', views.download_annotations, name='download_annotations'),
    path('download-sentences/', views.download_sentences, name='download_sentences'),
    path('download-relations/', views.download_relations, name='download_relations'),
    path('graph/', views.graph, name='graph'),
]