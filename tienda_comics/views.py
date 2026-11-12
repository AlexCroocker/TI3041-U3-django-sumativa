from django.shortcuts import get_object_or_404, render

from .models import Comic, Editorial


def catalogo(request):
    comics = Comic.objects.filter(disponible_venta=True).select_related("editorial")
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
