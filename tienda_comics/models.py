import uuid

from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Editorial(models.Model):
    nombre = models.CharField("nombre", max_length=150, unique=True)

    class Meta:
        verbose_name = "editorial"
        verbose_name_plural = "editoriales"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Comic(models.Model):
    titulo = models.CharField("título", max_length=200)
    editorial = models.ForeignKey(
        Editorial,
        on_delete=models.CASCADE,
        related_name="comics",
        verbose_name="editorial",
    )
    portada = models.ImageField("portada", upload_to="portadas/")
    precio = models.DecimalField(
        "precio (CLP)",
        max_digits=10,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    numero_tomo = models.PositiveIntegerField(
        "número de tomo",
        validators=[MinValueValidator(1)],
    )
    tapa_dura = models.BooleanField("tapa dura", default=False)
    stock = models.PositiveIntegerField("stock", default=0)
    disponible_venta = models.BooleanField("disponible para la venta", default=True)

    class Meta:
        verbose_name = "cómic"
        verbose_name_plural = "cómics"
        ordering = ["titulo", "numero_tomo"]

    def __str__(self):
        return f"{self.titulo} (tomo {self.numero_tomo})"


class Reserva(models.Model):
    comic = models.ForeignKey(
        Comic,
        on_delete=models.CASCADE,
        related_name="reservas",
        verbose_name="cómic",
    )
    nombre = models.CharField("nombre", max_length=150)
    correo = models.EmailField("correo electrónico")
    rut = models.CharField("RUT", max_length=12)
    cantidad = models.PositiveIntegerField(
        "cantidad de ejemplares",
        validators=[MinValueValidator(1)],
    )
    fecha_hora = models.DateTimeField("fecha y hora de reserva", default=timezone.now)
    codigo = models.UUIDField("código", default=uuid.uuid4, unique=True, editable=False)

    class Meta:
        verbose_name = "reserva"
        verbose_name_plural = "reservas"
        ordering = ["-fecha_hora"]

    def __str__(self):
        return f"Reserva {self.codigo} - {self.nombre} ({self.comic})"
