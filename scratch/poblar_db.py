import json
from database.crud import upsert_productos

def poblar_datos_prueba():
    """Lee el archivo de muestra y realiza el upsert en la base de datos de Docker."""
    print("Leyendo archivo de muestra scratch/muestra_productos.json...")
    try:
        with open("scratch/muestra_productos.json", "r", encoding="utf-8") as f:
            productos = json.load(f)
        
        print(f"Detectados {len(productos)} productos listos para insertar.")
        upsert_productos(productos)
        print("Sincronización de prueba completada de forma exitosa.")
    except FileNotFoundError:
        print("Error: No se encontró el archivo scratch/muestra_productos.json. Asegúrate de correr ver_datos.py primero.")
    except Exception as e:
        print(f"Error al poblar los datos: {e}")

if __name__ == "__main__":
    poblar_datos_prueba()
