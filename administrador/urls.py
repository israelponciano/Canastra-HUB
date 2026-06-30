from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'administrador'

urlpatterns = [
    path("", views.areaAdm, name="areaAdm"),
    
    # gerencia os hubs
    path("cadastrarHub/", views.cadastrarHub, name="cadastrarHub"),
    path("gerenciarHubs/", views.gerenciarHubs, name="gerenciarHubs"),
    path("alterarHub/", views.alterarHub, name="alterarHub"),
    path("deletaHub/<int:noticia_id>", views.deletaHub, name="deletaHub"),

    # gerencia as noticias
    path("cadastrarNoticias/", views.cadastrarNoticias, name="cadastrarNoticias"),
    path("gerenciarNoticias/", views.gerenciarNoticias, name="gerenciarNoticias"),
    path("alterarNoticias/", views.alterarNoticias, name="alterarNoticias"),
    path("deletaNoticias/<int:noticia_id>", views.deletaNoticias, name="deletaNoticias"),
  
    #gerencia os usuários
    path("listar_usuarios/", views.listar_usuarios, name="listar_usuarios"),
    path("detalhe_usuario/<int:usuario_id>/", views.detalhe_usuario, name="detalhe_usuario"),
    path("desativar_usuario/<int:usuario_id>/", views.desativar_usuario, name="desativar_usuario"),
    path("alterar_status_usuario/<int:usuario_id>/", views.alterar_status_usuario, name="alterar_status_usuario"),
    
    #gerencia os eventos 
    path("gerenciarEventos/", views.gerenciarEventos, name="gerenciarEventos"),  
    path("evento/<int:evento_id>/status/", views.alterar_status_evento, name="alterar_status_evento"),
    path("evento/<int:evento_id>/inscritos/", views.inscritos_evento, name="inscritos_evento"),   
    path("removerEvento/<int:evento_id>/", views.removerEvento, name="removerEvento"),
    path("alterarStatusEvento/<int:evento_id>/", views.alterar_status_evento, name="alterar_status_evento"),
    
    #gerencia os treinamentos
    path("gerenciarTreinamentos/", views.gerenciarTreinamentos, name="gerenciarTreinamentos"),
    path("treinamento/<int:treinamento_id>/status/", views.alterar_status_treinamento, name="alterar_status_treinamento"),
]

