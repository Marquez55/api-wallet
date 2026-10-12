from django.contrib import admin

from app.agenda.models import AgendaEvento


@admin.register(AgendaEvento)
class AgendaEventoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'usuario', 'tipo', 'fecha_inicio', 'fecha_fin', 'estado', 'meet_estado', 'activo')
    list_filter = ('tipo', 'estado', 'meet_estado', 'activo')
    search_fields = ('titulo', 'descripcion', 'usuario__username', 'usuario__email')
