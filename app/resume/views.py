from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from app.catalogos.models import AnioUsuario, Mes, Categoria, Subcategoria, Tipo, TipoIngreso
from app.cashflow.models import Ingresos, Egresos
from django.db.models import Sum, Value, DecimalField
from django.db.models.functions import Coalesce


class EgresosFavoritosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve la suma de los egresos por categoría favorita del usuario en el año activo,
        incluyendo el porcentaje que representa cada categoría.
        Siempre devuelve las 5 categorías favoritas configuradas, con total=0 si no hay egresos.
        Si no hay categorías favoritas configuradas o no hay un año activo, completa con "En espera".
        """

        anio_activo = AnioUsuario.objects.filter(usuario=request.user, activo=True).first()
        if not anio_activo:

            respuesta = [{"categoria__nombre": "En espera", "total": 0, "porcentaje": 0} for _ in range(5)]
            return Response(respuesta, status=200)


        categorias_favoritas = Categoria.objects.filter(
            usuario=request.user, favorito=True, activo=True
        )


        if not categorias_favoritas.exists():
            respuesta = [{"categoria__nombre": "En espera", "total": 0, "porcentaje": 0} for _ in range(5)]
            return Response(respuesta, status=200)


        egresos_totales = Egresos.objects.filter(
            usuario=request.user,
            anio=anio_activo,
            categoria__in=categorias_favoritas,
            activo=True,
        ).aggregate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))["total"]


        if egresos_totales == 0:
            respuesta = [
                {"categoria__nombre": categoria.nombre, "total": 0, "porcentaje": 0}
                for categoria in categorias_favoritas
            ]

            # Completar con "En espera" si hay menos de 5 categorías favoritas
            placeholders_faltantes = 5 - len(respuesta)
            respuesta += [{"categoria__nombre": "En espera", "total": 0, "porcentaje": 0} for _ in range(placeholders_faltantes)]

            return Response(respuesta, status=200)


        egresos = (
            Egresos.objects.filter(
                usuario=request.user,
                anio=anio_activo,
                categoria__in=categorias_favoritas,
                activo=True,
            )
            .values("categoria__nombre")
            .annotate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))
        )


        egresos_dict = {e["categoria__nombre"]: e["total"] for e in egresos}

        # Crear la respuesta final con las categorías favoritas
        respuesta = [
            {
                "categoria__nombre": categoria.nombre,
                "total": egresos_dict.get(categoria.nombre, 0),
                "porcentaje": min(int((egresos_dict.get(categoria.nombre, 0) / egresos_totales) * 100), 100),
            }
            for categoria in categorias_favoritas
        ]


        placeholders_faltantes = 5 - len(respuesta)
        respuesta += [{"categoria__nombre": "En espera", "total": 0, "porcentaje": 0} for _ in range(placeholders_faltantes)]

        return Response(respuesta, status=200)



class IngresosEgresosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve la suma de ingresos, egresos y la diferencia (restante) del usuario en el año activo.
        Si no hay un año activo, retorna 0 para todos los valores.
        """

        anio_activo = AnioUsuario.objects.filter(usuario=request.user, activo=True).first()
        if not anio_activo:
            # Si no hay un año activo, devolver valores por defecto
            return Response(
                {
                    "anio": None,
                    "ingresos": 0,
                    "egresos": 0,
                    "restante": 0
                },
                status=200
            )


        ingresos_total = (
            Ingresos.objects.filter(usuario=request.user, anio=anio_activo, activo=True)
            .aggregate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))
            ["total"]
        )


        egresos_total = (
            Egresos.objects.filter(usuario=request.user, anio=anio_activo, activo=True)
            .aggregate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))
            ["total"]
        )


        restante = ingresos_total - egresos_total


        respuesta = {
            "anio": anio_activo.anio,
            "ingresos": ingresos_total,
            "egresos": egresos_total,
            "restante": restante
        }

        return Response(respuesta, status=200)



class IngresosEgresosMensualesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve los ingresos y egresos mensuales del usuario en el año activo.
        Si no hay un año activo, retorna 0 para todos los valores.
        """
        anio_activo = AnioUsuario.objects.filter(usuario=request.user, activo=True).first()
        if not anio_activo:
            # Si no hay un año activo, devolver 0 para todos los meses
            meses = Mes.objects.all().order_by("id")  # Aseguramos el orden de enero a diciembre
            respuesta = {mes.id: {"ingresos": 0, "egresos": 0} for mes in meses}
            respuesta_final = {mes.mes[:3]: valores for mes, valores in zip(meses, respuesta.values())}
            return Response({"anio": None, "mensual": respuesta_final}, status=200)

        meses = Mes.objects.all().order_by("id")
        respuesta_mensual = {mes.id: {"ingresos": 0, "egresos": 0} for mes in meses}

        # Obtener ingresos y egresos mensuales
        ingresos_mensuales = (
            Ingresos.objects.filter(usuario=request.user, anio=anio_activo, activo=True)
            .values("mes__id")  # Usar el ID del mes
            .annotate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))
        )

        egresos_mensuales = (
            Egresos.objects.filter(usuario=request.user, anio=anio_activo, activo=True)
            .values("mes__id")  # Usar el ID del mes
            .annotate(total=Coalesce(Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())))
        )

        # Asignar los valores a respuesta_mensual
        for ingreso in ingresos_mensuales:
            mes_id = ingreso["mes__id"]
            if mes_id in respuesta_mensual:
                respuesta_mensual[mes_id]["ingresos"] = ingreso["total"]

        for egreso in egresos_mensuales:
            mes_id = egreso["mes__id"]
            if mes_id in respuesta_mensual:
                respuesta_mensual[mes_id]["egresos"] = egreso["total"]

        # Opcional: Convertir a nombre de mes ([:3]) para la respuesta final
        respuesta_mensual_final = {mes.mes[:3]: respuesta_mensual[mes.id] for mes in meses}

        # Respuesta final
        return Response({"anio": anio_activo.anio, "mensual": respuesta_mensual_final}, status=200)




class IngresosMensualesSalarioAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Devuelve los ingresos mensuales clasificados como salario (excluyendo id 4)
        y el total general (incluyendo id 4) clasificado como 'otros'.
        """

        anio_activo = AnioUsuario.objects.filter(usuario=request.user, activo=True).first()
        if not anio_activo:
            meses = Mes.objects.all().order_by("id")
            respuesta = {mes.id: {"salario": 0} for mes in meses}
            respuesta_final = {mes.mes[:3]: respuesta[mes.id] for mes in meses}  # Convertir ID a nombres de meses
            return Response(
                {
                    "anio": None,
                    "mensual": respuesta_final,
                    "total_salario": 0,
                    "otros": 0,
                },
                status=200,
            )

        meses = Mes.objects.all().order_by("id")

        # Crear la respuesta inicial basada en los IDs de los meses
        respuesta_mensual = {mes.id: {"salario": 0} for mes in meses}

        # Excluir el tipo de ingreso con id=4
        tipos_salario = TipoIngreso.objects.exclude(id=4)

        # Obtener los ingresos mensuales por tipos de salario
        ingresos_mensuales = (
            Ingresos.objects.filter(
                usuario=request.user,
                anio=anio_activo,
                activo=True,
                tipoingreso__in=tipos_salario,  # Filtrar por tipos válidos
            )
            .values("mes__id")  # Usar ID del mes
            .annotate(
                total_salario=Coalesce(
                    Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())
                )
            )
        )

        # Obtener los totales generales
        total_salario = (
            Ingresos.objects.filter(
                usuario=request.user,
                anio=anio_activo,
                activo=True,
                tipoingreso__in=tipos_salario,
            )
            .aggregate(
                total=Coalesce(
                    Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())
                )
            )["total"]
        )

        total_otros = (
            Ingresos.objects.filter(
                usuario=request.user,
                anio=anio_activo,
                activo=True,
                tipoingreso_id=4,  # Filtrar únicamente por id 4
            )
            .aggregate(
                total=Coalesce(
                    Sum("monto", output_field=DecimalField()), Value(0, output_field=DecimalField())
                )
            )["total"]
        )

        # Asignar los ingresos mensuales al diccionario
        for ingreso in ingresos_mensuales:
            mes_id = ingreso["mes__id"]  # Usar el ID del mes
            if mes_id in respuesta_mensual:
                respuesta_mensual[mes_id]["salario"] = ingreso["total_salario"]

        # Convertir el diccionario a una estructura con nombres de los meses
        respuesta_mensual_final = {mes.mes[:3]: respuesta_mensual[mes.id] for mes in meses}

        return Response(
            {
                "anio": anio_activo.anio,
                "mensual": respuesta_mensual_final,
                "total_salario": total_salario,
                "otros": total_otros,
            },
            status=200,
        )