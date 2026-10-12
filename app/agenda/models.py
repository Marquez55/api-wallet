from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models


color_hex_validator = RegexValidator(
    regex=r'^#[0-9A-Fa-f]{6}$',
    message='Usa un color hexadecimal con el formato #RRGGBB.',
)


class AgendaEvento(models.Model):
    class Tipo(models.TextChoices):
        TAREA = 'tarea', 'Tarea'
        ACTIVIDAD = 'actividad', 'Actividad'
        CITA = 'cita', 'Cita'

    class Estado(models.TextChoices):
        PROGRAMADO = 'programado', 'Programado'
        COMPLETADO = 'completado', 'Completado'
        CANCELADO = 'cancelado', 'Cancelado'

    class EstadoMeet(models.TextChoices):
        NO_CONECTADO = 'no_conectado', 'Google no conectado'
        PENDIENTE = 'pendiente', 'Pendiente de sincronizar'
        CREADO = 'creado', 'Evento de Google creado'
        ERROR = 'error', 'Error de sincronización'

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='eventos_agenda',
    )
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, default='')
    tipo = models.CharField(max_length=12, choices=Tipo.choices, default=Tipo.ACTIVIDAD)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    todo_el_dia = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#5D87FF', validators=[color_hex_validator])
    color_secundario = models.CharField(max_length=7, default='#ECF2FF', validators=[color_hex_validator])
    ubicacion = models.CharField(max_length=300, blank=True, default='')
    estado = models.CharField(max_length=12, choices=Estado.choices, default=Estado.PROGRAMADO)
    asistentes = models.JSONField(default=list, blank=True)
    recordatorio_minutos = models.PositiveSmallIntegerField(null=True, blank=True)

    # Campos preparados para sincronizar Google Calendar y guardar el enlace de Meet.
    google_calendar_id = models.CharField(max_length=255, blank=True, default='')
    google_event_id = models.CharField(max_length=255, blank=True, default='')
    meet_url = models.URLField(max_length=500, blank=True, default='')
    meet_estado = models.CharField(
        max_length=16,
        choices=EstadoMeet.choices,
        default=EstadoMeet.NO_CONECTADO,
    )
    meet_error = models.TextField(blank=True, default='')
    meet_sincronizado_en = models.DateTimeField(null=True, blank=True)

    activo = models.BooleanField(default=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['fecha_inicio', 'id']
        indexes = [
            models.Index(fields=['usuario', 'fecha_inicio', 'activo'], name='agenda_usr_start_active_idx'),
            models.Index(fields=['usuario', 'tipo', 'activo'], name='agenda_usr_type_active_idx'),
        ]

    def __str__(self):
        return f'{self.titulo} ({self.fecha_inicio:%Y-%m-%d %H:%M})'
