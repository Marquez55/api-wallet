from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.agenda.models import AgendaEvento
from app.agenda.serializers import AgendaEventoSerializer


class AgendaEventoListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        eventos = AgendaEvento.objects.filter(usuario=request.user, activo=True)
        inicio = request.query_params.get('inicio')
        fin = request.query_params.get('fin')

        if inicio or fin:
            inicio_dt = parse_datetime(inicio) if inicio else None
            fin_dt = parse_datetime(fin) if fin else None
            if not inicio_dt or not fin_dt or fin_dt <= inicio_dt:
                return Response(
                    {'detail': 'Envía un rango válido en los parámetros inicio y fin.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            eventos = eventos.filter(fecha_inicio__lt=fin_dt, fecha_fin__gte=inicio_dt)

        serializer = AgendaEventoSerializer(eventos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = AgendaEventoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgendaEventoDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_evento(self, request, pk):
        return get_object_or_404(AgendaEvento, pk=pk, usuario=request.user, activo=True)

    def get(self, request, pk):
        return Response(AgendaEventoSerializer(self.get_evento(request, pk)).data)

    def put(self, request, pk):
        evento = self.get_evento(request, pk)
        serializer = AgendaEventoSerializer(evento, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        evento = self.get_evento(request, pk)
        serializer = AgendaEventoSerializer(evento, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        evento = self.get_evento(request, pk)
        evento.activo = False
        evento.save(update_fields=['activo', 'actualizado_en'])
        return Response(status=status.HTTP_204_NO_CONTENT)
