from django.contrib import admin
from .models import LogAcao

@admin.register(LogAcao)
class LogAcaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'tipo_acao', 'ip', 'descricao_resumida')
    list_filter = ('tipo_acao', 'data_hora', 'usuario')
    search_fields = ('descricao', 'usuario__email', 'ip')
    readonly_fields = ('usuario', 'tipo_acao', 'descricao', 'data_hora', 'ip')

    def descricao_resumida(self, obj):
        return obj.descricao[:50] + '...' if len(obj.descricao) > 50 else obj.descricao
    descricao_resumida.short_description = 'Descrição'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False



#python manage.py makemigrations
#python manage.py migrate