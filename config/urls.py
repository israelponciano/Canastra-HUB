from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include('core.urls')),  
    path('empresa/', include('empresa.urls')),  
    path('usuario/', include('usuario.urls')),
    path('vagas/', include('vagas.urls'))
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)