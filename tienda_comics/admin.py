from django.contrib import admin
from .models import Comic, Editorial, Reserva


@admin.register(Editorial)
class EditorialAdmin(admin.ModelAdmin):
    list_display = ("nombre",)
    search_fields = ("nombre",)


@admin.register(Comic)
class ComicAdmin(admin.ModelAdmin):
    list_display = (
        "titulo",
        "numero_tomo",
        "editorial",
        "precio_formateado",
        "stock",
        "tapa_dura",
        "disponible_venta",
        "tiene_reservas",
    )
    list_filter = ("editorial", "tapa_dura")
    search_fields = ("titulo", "editorial__nombre")

    @admin.display(description="Precio")
    def precio_formateado(self, obj):
        return f"${obj.precio:,.0f}".replace(",", ".")

    @admin.display(boolean=True, description="En reserva")
    def tiene_reservas(self, obj):
        return obj.reservas.exists()


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "comic",
        "nombre",
        "correo",
        "rut_formateado",
        "cantidad",
        "fecha_hora",
    )
    list_filter = ("comic",)
    search_fields = ("codigo", "comic__titulo", "nombre", "correo", "rut")
    readonly_fields = ("codigo",)

    @admin.display(description="RUT")
    def rut_formateado(self, obj):
        numero, separador, digito_verificador = obj.rut.rpartition("-")
        numero = numero.replace(".", "")
        if (
            not separador
            or not numero.isdecimal()
            or len(digito_verificador) != 1
            or not (digito_verificador.isdecimal() or digito_verificador.lower() == "k")
        ):
            return obj.rut

        numero_formateado = f"{int(numero):,}".replace(",", ".")
        return f"{numero_formateado}-{digito_verificador}"
