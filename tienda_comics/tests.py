from django.core.exceptions import ValidationError
from django.test import TestCase

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
