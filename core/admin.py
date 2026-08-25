from django.contrib import admin

# Register your models here.
from django.contrib import admin

from core.models import LogAcao


@admin.register(LogAcao)
class LogAcaoAdmin(admin.ModelAdmin):
    list_display = ('data_hora', 'usuario', 'tipo_acao', 'ip')
    list_filter = ('tipo_acao',)
    search_fields = ('usuario__email', 'descricao', 'ip')
    date_hierarchy = 'data_hora'

    def has_add_permission(self, request):
        return False  # log só é criado via código, nunca manualmente

    def has_change_permission(self, request, obj=None):
        return False  # ninguém edita um log

    def has_delete_permission(self, request, obj=None):
        return False  # ninguém deleta um log