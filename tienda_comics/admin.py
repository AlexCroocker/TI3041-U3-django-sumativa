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
        "precio",
        "stock",
        "disponible_venta",
    )
    list_filter = ("editorial", "tapa_dura", "disponible_venta")
    search_fields = ("titulo", "editorial__nombre")


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "comic", "nombre", "correo", "rut", "cantidad", "fecha_hora")
    list_filter = ("fecha_hora",)
    search_fields = ("codigo", "comic__titulo", "nombre", "correo", "rut")
    readonly_fields = ("codigo",)
