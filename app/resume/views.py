from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from app.catalogos.models import AnioUsuario, Mes, Categoria, Subcategoria, Tipo, TipoIngreso
from app.cashflow.models import Ingresos, Egresos
from django.db.models import Sum



class EgresosFavoritosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve la suma de los egresos por categoría favorita del usuario en el año activo.
        """
        # Obtener el año activo del usuario
        anio_activo = AnioUsuario.objects.filter(usuario=request.user, activo=True).first()
        if not anio_activo:
            return Response({"error": "No tienes un año activo configurado."}, status=400)

        # Obtener las categorías marcadas como favoritas
        categorias_favoritas = Categoria.objects.filter(usuario=request.user, favorito=True, activo=True)
        if not categorias_favoritas.exists():
            return Response({"error": "No tienes categorías favoritas configuradas."}, status=400)

        # Filtrar los egresos en el año activo y sumarizar por categoría
        egresos = (
            Egresos.objects.filter(
                usuario=request.user,
                anio=anio_activo,
                categoria__in=categorias_favoritas,
                activo=True,
            )
            .values("categoria__nombre")
            .annotate(total=Sum("monto"))
        )

        return Response(egresos, status=200)