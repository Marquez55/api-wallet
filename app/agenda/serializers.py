from rest_framework import serializers

from app.agenda.models import AgendaEvento


class AgendaEventoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgendaEvento
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'fecha_inicio', 'fecha_fin',
            'todo_el_dia', 'color', 'color_secundario', 'ubicacion', 'estado',
            'asistentes', 'recordatorio_minutos', 'google_calendar_id',
            'google_event_id', 'meet_url', 'meet_estado', 'meet_error',
            'meet_sincronizado_en', 'creado_en', 'actualizado_en',
        ]
        read_only_fields = [
            'google_calendar_id', 'google_event_id', 'meet_url', 'meet_estado',
            'meet_error', 'meet_sincronizado_en', 'creado_en', 'actualizado_en',
        ]

    def validate(self, attrs):
        start = attrs.get('fecha_inicio', getattr(self.instance, 'fecha_inicio', None))
        end = attrs.get('fecha_fin', getattr(self.instance, 'fecha_fin', None))
        if start and end and end <= start:
            raise serializers.ValidationError({'fecha_fin': 'La fecha de término debe ser posterior al inicio.'})
        return attrs
