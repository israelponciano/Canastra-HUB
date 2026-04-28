from django.urls import path
from . import views
 
app_name = 'hubs'
 
urlpatterns = [
    path('', views.listar_hubs, name='listar_hubs'),
    path('<str:nome_hub>/', views.hub_detalhe, name='hub_detalhe'),
    # path("agro/", views.agro, name="agro"),
    # path("apicultura/", views.apicultura, name="apicultura"),
    # path("queijo/", views.queijo, name="queijo"),
    # path("calcados/", views.calcados, name="calcados"),
    # path("milho/", views.milho, name="milho"),
    # path("graos/", views.graos, name="graos"),
    # path("sobre/", views.sobre, name="sobre"),
    # path("espacos_hub/", views.espacos_hub, name="espacos_hub"),
    # path("parceiros/", views.parceiros, name="parceiros"),
]

    