from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')),  
    path('empresa/', include('empresa.urls')),  
    path('usuario/', include('usuario.urls')),

]
