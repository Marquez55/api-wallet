from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from app.proyect.serializer import (
    ProyectoSerializer,
    PagoProyectoSerializer,
    PresupuestoSerializer,
    PresupuestoCategoriaSerializer,
    PresupuestoPartidaSerializer
)
from app.proyect.models import (
    Proyecto,
    PagoProyecto,
    Presupuesto,
    PresupuestoCategoria,
    PresupuestoPartida
)




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


class PresupuestoListView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        presupuestos = Presupuesto.objects.filter(usuario=request.user, activo=True).order_by('nombre')
        serializer = PresupuestoSerializer(presupuestos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PresupuestoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PresupuestoDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        try:
            return Presupuesto.objects.get(pk=pk, usuario=request.user, activo=True)
        except Presupuesto.DoesNotExist:
            return None

    def get(self, request, pk):
        presupuesto = self.get_object(request, pk)
        if not presupuesto:
            return Response({"error": "Presupuesto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PresupuestoSerializer(presupuesto)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        presupuesto = self.get_object(request, pk)
        if not presupuesto:
            return Response({"error": "Presupuesto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PresupuestoSerializer(presupuesto, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        presupuesto = self.get_object(request, pk)
        if not presupuesto:
            return Response({"error": "Presupuesto no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        presupuesto.eliminar_logicamente()
        return Response({"message": "Presupuesto eliminado correctamente."}, status=status.HTTP_200_OK)


class PresupuestoCategoriaListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, presupuesto_id):
        categorias = PresupuestoCategoria.objects.filter(
            presupuesto_id=presupuesto_id,
            presupuesto__usuario=request.user,
            activo=True
        ).order_by('orden', 'nombre')
        serializer = PresupuestoCategoriaSerializer(categorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, presupuesto_id):
        try:
            presupuesto = Presupuesto.objects.get(pk=presupuesto_id, usuario=request.user, activo=True)
        except Presupuesto.DoesNotExist:
            return Response({"error": "Presupuesto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['presupuesto'] = presupuesto.id
        serializer = PresupuestoCategoriaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PresupuestoCategoriaDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        try:
            return PresupuestoCategoria.objects.get(pk=pk, usuario=request.user, activo=True)
        except PresupuestoCategoria.DoesNotExist:
            return None

    def put(self, request, pk):
        categoria = self.get_object(request, pk)
        if not categoria:
            return Response({"error": "Categoría de presupuesto no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PresupuestoCategoriaSerializer(categoria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        categoria = self.get_object(request, pk)
        if not categoria:
            return Response({"error": "Categoría de presupuesto no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        categoria.eliminar_logicamente()
        return Response({"message": "Categoría de presupuesto eliminada correctamente."}, status=status.HTTP_200_OK)


class PresupuestoPartidaListCreateView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, presupuesto_id):
        partidas = PresupuestoPartida.objects.filter(
            presupuesto_id=presupuesto_id,
            presupuesto__usuario=request.user,
            activo=True
        ).order_by('categoria_id', 'concepto')
        serializer = PresupuestoPartidaSerializer(partidas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, presupuesto_id):
        try:
            presupuesto = Presupuesto.objects.get(pk=presupuesto_id, usuario=request.user, activo=True)
        except Presupuesto.DoesNotExist:
            return Response({"error": "Presupuesto no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['presupuesto'] = presupuesto.id
        serializer = PresupuestoPartidaSerializer(data=data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PresupuestoPartidaDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, request, pk):
        try:
            return PresupuestoPartida.objects.get(pk=pk, usuario=request.user, activo=True)
        except PresupuestoPartida.DoesNotExist:
            return None

    def put(self, request, pk):
        partida = self.get_object(request, pk)
        if not partida:
            return Response({"error": "Partida no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PresupuestoPartidaSerializer(partida, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        partida = self.get_object(request, pk)
        if not partida:
            return Response({"error": "Partida no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        partida.eliminar_logicamente()
        return Response({"message": "Partida eliminada correctamente."}, status=status.HTTP_200_OK)
