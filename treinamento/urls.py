from django.urls import path
from . import views

app_name = 'treinamento'

urlpatterns = [
    #public
    path('', views.listar_treinamentos, name='listar_treinamentos'),

    #admin/empresa
    path('criar/', views.criar_treinamento, name='cadastro_treinamentos'),
    path('<int:treinamento_id>/editar/', views.editar_treinamento, name='editar_treinamento'),
    path('<int:treinamento_id>/remover/', views.remover_treinamento, name='remover_treinamento'),
    path('<int:treinamento_id>/inscritos/', views.gerenciar_inscricoes, name='gerenciar_inscricoes'),
    path('<int:treinamento_id>/exportar/', views.exportar_csv, name='exportar_csv'),
    path('inscricao/<int:inscricao_id>/presenca/', views.atualizar_presenca, name='atualizar_presenca'),
    path('inscricao/<int:inscricao_id>/remover/', views.remover_inscricao, name='remover_inscricao'),

    #usuario
    path('<int:treinamento_id>/inscrever/', views.inscrever, name='inscrever'),
    path('<int:treinamento_id>/cancelar/', views.cancelar_inscricao, name='cancelar'),
]