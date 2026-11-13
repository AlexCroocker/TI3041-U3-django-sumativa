from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import TestCase

from .admin import ComicAdmin, ReservaAdmin
from .models import Comic, Editorial, Reserva


class CatalogoYReservasTests(TestCase):
    def setUp(self):
        self.editorial = Editorial.objects.create(nombre="Editorial de prueba")
        self.comic = Comic.objects.create(
            titulo="Aventura",
            editorial=self.editorial,
            portada="portadas/aventura.jpg",
            precio=5000,
            numero_tomo=1,
            stock=3,
        )
        self.reserva = Reserva.objects.create(
            comic=self.comic,
            nombre="Ana Pérez",
            correo="ana@example.com",
            rut="12.345.678-9",
            cantidad=1,
        )

    def test_registros_tienen_nombres_legibles(self):
        self.assertEqual(str(self.editorial), "Editorial de prueba")
        self.assertEqual(str(self.comic), "Aventura (tomo 1)")
        self.assertIn("Ana Pérez", str(self.reserva))

    def test_eliminar_editorial_elimina_comics_y_reservas(self):
        self.editorial.delete()

        self.assertFalse(Comic.objects.exists())
        self.assertFalse(Reserva.objects.exists())

    def test_eliminar_comic_elimina_sus_reservas(self):
        self.comic.delete()

        self.assertTrue(Editorial.objects.filter(pk=self.editorial.pk).exists())
        self.assertFalse(Reserva.objects.exists())

    def test_nombre_de_editorial_no_se_puede_repetir(self):
        editorial_duplicada = Editorial(nombre=self.editorial.nombre)

        with self.assertRaises(ValidationError):
            editorial_duplicada.full_clean()

    def test_reserva_debe_indicar_al_menos_un_ejemplar(self):
        reserva_sin_ejemplares = Reserva(
            comic=self.comic,
            nombre="Ana Pérez",
            correo="ana@example.com",
            rut="12.345.678-9",
            cantidad=0,
        )

        with self.assertRaises(ValidationError):
            reserva_sin_ejemplares.full_clean()

    def test_admin_formatea_precio_en_pesos_chilenos(self):
        comic_admin = ComicAdmin(Comic, admin.site)

        self.assertEqual(comic_admin.precio_formateado(self.comic), "$5.000")

    def test_admin_agrega_puntos_al_rut_sin_puntos(self):
        reserva_admin = ReservaAdmin(Reserva, admin.site)
        ejemplos = (
            ("2188945-1", "2.188.945-1"),
            ("21889451-1", "21.889.451-1"),
        )

        for rut, rut_esperado in ejemplos:
            with self.subTest(rut=rut):
                self.reserva.rut = rut
                self.assertEqual(reserva_admin.rut_formateado(self.reserva), rut_esperado)


class CatalogoPublicoTests(TestCase):
    def setUp(self):
        self.editorial = Editorial.objects.create(nombre="Editorial principal")
        self.otra_editorial = Editorial.objects.create(nombre="Otra editorial")
        self.comic = Comic.objects.create(
            titulo="Aventura espacial",
            editorial=self.editorial,
            portada="portadas/aventura-espacial.jpg",
            precio=12500,
            numero_tomo=2,
            tapa_dura=True,
            stock=4,
        )
        self.otro_comic = Comic.objects.create(
            titulo="Aventura medieval",
            editorial=self.otra_editorial,
            portada="portadas/aventura-medieval.jpg",
            precio=8000,
            numero_tomo=1,
            stock=2,
        )
        self.comic_no_disponible = Comic.objects.create(
            titulo="Edición agotada",
            editorial=self.editorial,
            portada="portadas/agotada.jpg",
            precio=3000,
            numero_tomo=1,
            stock=0,
            disponible_venta=False,
        )

    def test_inicio_lista_solo_disponibles_y_formatea_precios_en_clp(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aventura espacial")
        self.assertContains(response, "Editorial principal")
        self.assertContains(response, "$12.500 CLP")
        self.assertNotContains(response, "Edición agotada")
        self.assertContains(response, 'aria-label="Menú principal"')

    def test_busqueda_y_editorial_se_pueden_combinar(self):
        response = self.client.get(
            "/",
            {"q": "Aventura", "editorial": self.editorial.pk},
        )

        self.assertContains(response, "Aventura espacial")
        self.assertNotContains(response, "Aventura medieval")
        self.assertNotContains(response, "Edición agotada")

    def test_filtro_por_editorial_muestra_solo_sus_comics(self):
        response = self.client.get("/", {"editorial": self.otra_editorial.pk})

        self.assertContains(response, "Aventura medieval")
        self.assertNotContains(response, "Aventura espacial")

    def test_detalle_muestra_datos_del_comic_disponible(self):
        response = self.client.get(f"/comics/{self.comic.pk}/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Editorial principal")
        self.assertContains(response, "Número de tomo")
        self.assertContains(response, "$12.500 CLP")
        self.assertContains(response, "Tapa dura")
        self.assertContains(response, "Stock")

    def test_detalle_de_comic_inexistente_o_no_disponible_responde_404(self):
        for pk in (self.comic_no_disponible.pk, self.comic.pk + 100):
            with self.subTest(pk=pk):
                response = self.client.get(f"/comics/{pk}/")
                self.assertEqual(response.status_code, 404)

    def test_editorial_invalida_no_muestra_todos_los_comics(self):
        response = self.client.get("/", {"editorial": "no-es-un-id"})

        self.assertNotContains(response, "Aventura espacial")
        self.assertNotContains(response, "Aventura medieval")
