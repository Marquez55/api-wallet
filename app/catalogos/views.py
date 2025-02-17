from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from app.catalogos.models import AnioUsuario, Mes, TipoIngreso, Categoria, Subcategoria
from app.user.models import Rol
from django.contrib.auth.models import User
from app.catalogos.serializers import AnioUsuarioSerializer, CategoriaSerializer, SubcategoriaSerializer
from django.db import transaction



class RolesListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de roles activos
        """
        roles = Rol.objects.filter(activo=True).values("id", "clave", "descripcion", "activo")

        res = {"roles": list(roles)}
        return Response(data=res, status=status.HTTP_200_OK)


class TipoIngresoAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de todos tipo de ingresos, mensual, quincenal, otros.
        """
        # Obtener todos los registros del modelo Anios
        Tipoingresos = TipoIngreso.objects.all().values("id", "ingreso", "activo")

        res = {"tingresos": list(Tipoingresos)}
        return Response(data=res, status=status.HTTP_200_OK)

class TipoListView(APIView):
    def get(self, request):
        """
        Listado de tipo ingreso e egreso.
        """
        tipos = Tipo.objects.filter(activo=True)  # Obtener solo los tipos activos
        serializer = TipoSerializer(tipos, many=True)
        return Response(serializer.data)


class MesesAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de todos los meses.
        """
        # Obtener todos los registros del modelo Mes
        meses = Mes.objects.all().values("id", "mes", "activo")

        res = {"meses": list(meses)}
        return Response(data=res, status=status.HTTP_200_OK)

class CatalogoAniosAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Listado de todos los años del usuario.
        """
        anios = AnioUsuario.objects.filter(usuario=request.user)
        serializer = AnioUsuarioSerializer(anios, many=True)
        return Response({"anios": serializer.data}, status=status.HTTP_200_OK)




class AnioDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, anio_id):
        """
        Obtiene los detalles de un año por su ID para el usuario autenticado.
        """
        try:
            anio_usuario = AnioUsuario.objects.get(usuario=request.user, id=anio_id)
            serializer = AnioUsuarioSerializer(anio_usuario)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AnioUsuario.DoesNotExist:
            return Response(
                {"error": "El año solicitado no existe o no pertenece al usuario."},
                status=status.HTTP_404_NOT_FOUND
            )


class CrearAnioAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """
        Creación de años.
        """
        # Asocia directamente el usuario del request
        serializer = AnioUsuarioSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # Guarda el año asociándolo con el usuario autenticado
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ActivarAnioAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, anio_id):
        """
        Activa o desactiva un año específico.
        """
        try:
            anio_usuario = AnioUsuario.objects.get(usuario=request.user, id=anio_id)

            if anio_usuario.activo:
                anio_usuario.activo = False
                anio_usuario.save()
                message = f"Año {anio_usuario.anio} desactivado correctamente."
            else:
                # Si está inactivo, activarlo
                anio_usuario.activar()
                message = f"Año {anio_usuario.anio} activado correctamente."

            return Response({"message": message}, status=status.HTTP_200_OK)

        except AnioUsuario.DoesNotExist:
            return Response(
                {"error": "El año solicitado no existe o no pertenece al usuario."},
                status=status.HTTP_404_NOT_FOUND
            )



class ActualizarAnioAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, anio_id):
        """
        Actualiza un año específico del usuario autenticado.
        """
        try:
            anio_usuario = AnioUsuario.objects.get(usuario=request.user, id=anio_id)
            serializer = AnioUsuarioSerializer(anio_usuario, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except AnioUsuario.DoesNotExist:
            return Response(
                {"error": "El año solicitado no existe o no pertenece al usuario."},
                status=status.HTTP_404_NOT_FOUND
            )




#Servicios para Categorias


class CategoriaListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
           Listado de Categorias
        """
        categorias = Categoria.objects.filter(usuario=request.user, activo=True)
        serializer = CategoriaSerializer(categorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """
            Creación de Categorias
        """
        serializer = CategoriaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(usuario=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoriaUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        """
          Actualización de categorias
        """
        try:
            categoria = Categoria.objects.get(pk=pk, usuario=request.user)
        except Categoria.DoesNotExist:
            return Response({"error": "Categoria no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Validar que no haya más de 5 categorías favoritas
        if request.data.get("favorito", None) is True:  # Si se intenta marcar como favorito
            favoritas_count = Categoria.objects.filter(usuario=request.user, favorito=True).count()
            if favoritas_count >= 5:
                return Response(
                    {"error": "No puedes tener más de 5 categorías marcadas como favoritas."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = CategoriaSerializer(categoria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @transaction.atomic
    def delete(self, request, pk):
        """
            Eliminar una categoría y sus subcategorías asociadas lógicamente
            Si la categoría está marcada como favorita, se desmarcará antes de eliminarla.
        """
        try:
            categoria = Categoria.objects.get(pk=pk, usuario=request.user, activo=True)
        except Categoria.DoesNotExist:
            return Response({"error": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

            # Desmarcar como favorita antes de eliminar
        if categoria.favorito:
            categoria.favorito = False
            categoria.save(update_fields=["favorito"])

        # Eliminar lógicamente la categoría
        categoria.eliminar_logicamente()

        # Obtener todas las subcategorías activas asociadas a la categoría
        subcategorias = Subcategoria.objects.filter(categoria=categoria, activo=True)

        # Eliminar lógicamente todas las subcategorías asociadas
        subcategorias.update(activo=False)

        return Response({"message": "Categoría y sus subcategorías eliminadas correctamente."},
                        status=status.HTTP_204_NO_CONTENT)


#Servicios para Subcategorias

class SubcategoriaListCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, categoria_id):
        """
            Listado de Subcategorias
        """
        try:
            categoria = Categoria.objects.get(pk=categoria_id, usuario=request.user)
        except Categoria.DoesNotExist:
            return Response({"error": "Categoria no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        subcategorias = Subcategoria.objects.filter(categoria=categoria, activo=True)
        serializer = SubcategoriaSerializer(subcategorias, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, categoria_id):
        """
          Creación de Subcategorias
        """
        try:
            categoria = Categoria.objects.get(pk=categoria_id, usuario=request.user)
        except Categoria.DoesNotExist:
            return Response({"error": "Categoría no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubcategoriaSerializer(data=request.data, context={'request': request, 'categoria': categoria})
        if serializer.is_valid():
            serializer.save()  # 'categoria' se asigna en el serializer
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SubcategoriaUpdateDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        """
            Actualización de subcategorias
        """
        try:
            subcategoria = Subcategoria.objects.get(pk=pk, usuario=request.user)
        except Subcategoria.DoesNotExist:
            return Response({"error": "Subcategoria no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        serializer = SubcategoriaSerializer(subcategoria, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """
            Eliminar una subcategorias
        """
        try:
            subcategoria = Subcategoria.objects.get(pk=pk, usuario=request.user)
        except Subcategoria.DoesNotExist:
            return Response({"error": "Subcategoria no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        subcategoria.eliminar_logicamente()
        return Response({"message": "Subcategoria eliminada lógicamente."}, status=status.HTTP_204_NO_CONTENT)