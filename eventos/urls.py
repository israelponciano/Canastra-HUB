from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # Público
    path('', views.listar_eventos, name='listar_eventos'),
    path('<int:evento_id>/', views.detalhe_evento, name='detalhe_evento'),
    
    

    # Empresa / Admin — CRUD
    path('criar/', views.criar_evento, name='criar_evento'),
    path('<int:evento_id>/editar/', views.editar_evento, name='editar_evento'),
    path('<int:evento_id>/remover/', views.remover_evento, name='remover_evento'),
    path('<int:evento_id>/inscritos/', views.gerenciar_inscricoes, name='gerenciar_inscricoes'),
    path('<int:evento_id>/exportar/', views.exportar_csv, name='exportar_csv'),

    # Presença / inscrição (gestão)
    path('inscricao/<int:inscricao_id>/presenca/', views.atualizar_presenca, name='atualizar_presenca'),
    path('inscricao/<int:inscricao_id>/remover/', views.remover_inscricao, name='remover_inscricao'),

    # Usuário
    path('<int:evento_id>/inscrever/', views.inscrever, name='inscrever'),
    path('<int:evento_id>/cancelar/', views.cancelar_inscricao, name='cancelar_inscricao'),
]