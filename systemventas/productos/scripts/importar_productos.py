import csv
from django.core.exceptions import ValidationError
from productos.models import Producto

def run(*args):
    if len(args) == 0:
        print("ERROR: Debes proporcionar la ruta del archivo CSV")
        return

    ruta_csv = args[0]

    try:
        with open(ruta_csv, newline='', encoding='utf-8') as csvfile:
            lector = csv.DictReader(csvfile)

            for fila in lector:
                try:
                    Producto.objects.create(
                        nombre=fila['nombre'],
                        descripcion=fila['descripcion'],
                        precio=fila['precio'],
                        stock=fila['stock'],
                        stock_minimo=fila['stock_minimo'],
                    )
                    print(f"✔ Producto cargado: {fila['nombre']}")

                except ValidationError as e:
                    print(f"⚠ Error validando fila: {fila} - {e}")

                except Exception as e:
                    print(f"❌ Error creando producto para fila {fila}: {e}")

    except FileNotFoundError:
        print("❌ No se encontró el archivo CSV.")
