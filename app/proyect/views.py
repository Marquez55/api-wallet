from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from app.proyect.serializer import ProyectoSerializer, PagoProyectoSerializer
from app.proyect.models import Proyecto, PagoProyecto




class ProyectListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de proyectos activos del usuario autenticado
        """
        proyecto = Proyecto.objects.filter(usuario=request.user, activo=True)
        serializer = ProyectoSerializer(proyecto, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
        Creación de un nuevo proyecto
        """
        serializer = ProyectoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProyectDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        try:
            return Proyecto.objects.get(pk=pk, usuario=request.user, activo=True)
        except Proyecto.DoesNotExist:
            return None

    def get(self, request, pk):
        """
        Detalle de un proyecto
        """
        proyecto = self.get_object(request, pk)
        if not proyecto:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProyectoSerializer(proyecto)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """
        Actualización de un proyecto
        """
        proyecto = self.get_object(request, pk)
        if not proyecto:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProyectoSerializer(proyecto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Eliminación lógica de un proyecto
        """
        proyecto = self.get_object(request, pk)
        if not proyecto:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        proyecto.eliminar_logicamente()
        return Response({"message": "Proyecto eliminado correctamente."}, status=status.HTTP_200_OK)


class PagoProyectoListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, proyecto_id):
        """
        Listado de pagos activos de un proyecto
        """
        pagos = PagoProyecto.objects.filter(
            proyecto_id=proyecto_id, proyecto__usuario=request.user, activo=True
        )
        serializer = PagoProyectoSerializer(pagos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, proyecto_id):
        """
        Crear un pago para un proyecto
        """
        try:
            proyecto = Proyecto.objects.get(pk=proyecto_id, usuario=request.user, activo=True)
        except Proyecto.DoesNotExist:
            return Response({"error": "Proyecto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['proyecto'] = proyecto.id
        serializer = PagoProyectoSerializer(data=data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PagoProyectoDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        try:
            return PagoProyecto.objects.get(pk=pk, usuario=request.user, activo=True)
        except PagoProyecto.DoesNotExist:
            return None

    def put(self, request, pk):
        """
        Actualización de un pago
        """
        pago = self.get_object(request, pk)
        if not pago:
            return Response({"error": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PagoProyectoSerializer(pago, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
        Eliminación lógica de un pago
        """
        pago = self.get_object(request, pk)
        if not pago:
            return Response({"error": "Pago no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        pago.eliminar_logicamente()
        return Response({"message": "Pago eliminado correctamente."}, status=status.HTTP_200_OK)
