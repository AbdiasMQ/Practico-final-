import csv
from django.core.exceptions import ValidationError
from clientes.models import Cliente


def run(*args):
    if len(args) == 0:
        print("ERROR: Debes especificar la ruta del archivo CSV")
        return

    ruta_csv = args[0]

    try:
        with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
            lector = csv.DictReader(csvfile)

            for fila in lector:
                try:
                    Cliente.objects.create(
                        nombre=fila['nombre'],
                        apellido=fila['apellido'],
                        dni=fila['dni'],
                        telefono=fila['telefono'],
                        email=fila['email'],
                        direccion=fila.get('direccion', 'Sin dirección')  # por si no lo incluís en el CSV
                    )
                    print(f"✔ Cliente cargado: {fila['nombre']} {fila['apellido']}")

                except ValidationError as e:
                    print(f"⚠ Error validando fila: {fila} - {e}")

                except Exception as e:
                    print(f"❌ Error creando cliente para fila {fila}: {e}")

    except FileNotFoundError:
        print("❌ No se encontró el archivo CSV.")
