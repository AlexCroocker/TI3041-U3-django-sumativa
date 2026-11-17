from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReservaForm
from .models import Comic, Editorial, Reserva


def catalogo(request):
    comics = Comic.objects.select_related("editorial").all()
    busqueda = request.GET.get("q", "").strip()
    editorial_id = request.GET.get("editorial", "").strip()

    if busqueda:
        comics = comics.filter(titulo__icontains=busqueda)

    if editorial_id:
        if editorial_id.isdecimal():
            comics = comics.filter(editorial_id=editorial_id)
        else:
            comics = comics.none()

    return render(
        request,
        "tienda_comics/catalogo.html",
        {
            "comics": comics,
            "editoriales": Editorial.objects.all(),
            "busqueda": busqueda,
            "editorial_seleccionada": editorial_id,
        },
    )


def detalle_comic(request, pk):
    comic = get_object_or_404(
        Comic.objects.select_related("editorial"),
        pk=pk,
        disponible_venta=True,
    )
    return render(request, "tienda_comics/detalle_comic.html", {"comic": comic})


def reserva_comic(request, id_comic):
    comic = get_object_or_404(Comic, pk=id_comic, disponible_venta=True)

    if comic.stock <= 0:
        return render(
            request,
            "tienda_comics/reservar_comic.html",
            {
                "comic": comic,
                "form": ReservaForm(initial={"id_comic": comic.id}),
                "agotado": True,
            },
        )

    if request.method == "POST":
        form = ReservaForm(request.POST)
        if form.is_valid():
            cantidad = form.cleaned_data["cantidad"]
            with transaction.atomic():
                comic_actualizado = Comic.objects.select_for_update().get(pk=comic.pk)
                if cantidad > comic_actualizado.stock:
                    form.add_error(
                        "cantidad",
                        f"Solo quedan {comic_actualizado.stock} ejemplar(es) disponibles.",
                    )
                    return render(
                        request,
                        "tienda_comics/reservar_comic.html",
                        {"comic": comic_actualizado, "form": form},
                    )

                reserva = Reserva.objects.create(
                    comic=comic_actualizado,
                    nombre=form.cleaned_data["nombre"],
                    correo=form.cleaned_data["email"],
                    rut=form.cleaned_data["rut"],
                    cantidad=cantidad,
                )
                comic_actualizado.stock -= cantidad
                comic_actualizado.save(update_fields=["stock"])

            return redirect("comprobante_reserva", codigo=reserva.codigo)
    else:
        form = ReservaForm(initial={"id_comic": comic.id})

    return render(
        request,
        "tienda_comics/reservar_comic.html",
        {"comic": comic, "form": form},
    )


def comprobante_reserva(request, codigo):
    reserva = get_object_or_404(
        Reserva.objects.select_related("comic", "comic__editorial"),
        codigo=codigo,
    )
    return render(
        request,
        "tienda_comics/reservar_comic.html",
        {"comprobante": True, "reserva": reserva},
    )


def historial_reservas(request):
    reservas = Reserva.objects.select_related("comic").all()
    return render(request, "tienda_comics/historial_reservas.html", {"reservas": reservas})