from django import forms


def rut_valido(rut):
    rut = rut.strip().upper()
    if not rut:
        return False

    if "-" not in rut:
        return False

    cuerpo, dv = rut.rsplit("-", 1)
    cuerpo = cuerpo.replace(".", "")

    if not cuerpo.isdigit():
        return False
    if len(cuerpo) < 2 or len(cuerpo) > 8:
        return False

    dv = dv.strip()
    if dv not in {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "K"}:
        return False

    suma = 0
    multiplo = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplo
        multiplo += 1
        if multiplo == 8:
            multiplo = 2

    resto = 11 - (suma % 11)
    if resto == 11:
        dv_calculado = "0"
    elif resto == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(resto)

    return dv_calculado == dv


class ReservaForm(forms.Form):
    id_comic = forms.IntegerField(widget=forms.HiddenInput())
    nombre = forms.CharField(
        max_length=100,
        label="Nombre",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
            }
        ),
    )
    email = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
            }
        ),
    )
    rut = forms.CharField(
        max_length=12,
        label="RUT",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "",
            }
        ),
    )
    cantidad = forms.IntegerField(
        min_value=1,
        max_value=3,
        label="Cantidad",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
                "min": 1,
                "max": 3,
                "step": 1,
                "placeholder": "",
            }
        ),
    )

    def clean_rut(self):
        rut = self.cleaned_data["rut"].strip()
        if not rut_valido(rut):
            raise forms.ValidationError("El RUT ingresado no es válido.")
        return rut

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad < 1 or cantidad > 3:
            raise forms.ValidationError("La cantidad debe estar entre 1 y 3 ejemplares.")
        return cantidad