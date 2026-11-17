from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from tienda_comics import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.catalogo, name="catalogo"),
    path("comics/<int:pk>/", views.detalle_comic, name="detalle_comic"),
    path("reserva/<int:id_comic>/", views.reserva_comic, name="reserva_comic"),
    path("reservas/", views.historial_reservas, name="historial_reservas"),
    path(
        "reserva/comprobante/<uuid:codigo>/",
        views.comprobante_reserva,
        name="comprobante_reserva",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
