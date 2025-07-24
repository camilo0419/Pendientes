# pendientes_kathe/tareas/populate_db.py

import os
import django

# Configura el entorno de Django
# Esto es crucial para que el script pueda acceder a tus modelos
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pendientes_kathe.settings')
django.setup()

from tareas.models import Aseguradora, TipoOperacion, Ramo

def populate_initial_data():
    print("Iniciando el llenado de datos iniciales...")

    # --- Datos para Aseguradoras ---
    aseguradoras_data = [
        "Allianz", "Axa Colpatria", "BBVA", "Berkley", "Chubb",
        "Confianza", "HDI", "Mapfre", "Nacional de Seguros", "SBS",
        "Seguros Bolívar", "Seguros del Estado", "Seguros Mundial",
        "Solidaria", "Solunion", "Sura", "Zurich"
    ]

    # Itera y crea Aseguradoras, si no existen
    for nombre in aseguradoras_data:
        aseguradora, created = Aseguradora.objects.get_or_create(nombre=nombre)
        if created:
            print(f"Aseguradora '{aseguradora.nombre}' creada.")
        else:
            print(f"Aseguradora '{aseguradora.nombre}' ya existe.")

    # --- Datos para Tipos de Operación ---
    tipos_operacion_data = [
        "Actualización de datos", "Autoinspección y/o inspección", "Cancelación",
        "Certificación y/o endoso", "Cobro", "Cotización", "Modificación",
        "Otros", "Póliza nueva", "Prórroga", "Siniestros"
    ]

    # Itera y crea Tipos de Operacion, si no existen
    for nombre in tipos_operacion_data:
        tipo_op, created = TipoOperacion.objects.get_or_create(nombre=nombre)
        if created:
            print(f"Tipo de Operación '{tipo_op.nombre}' creado.")
        else:
            print(f"Tipo de Operación '{tipo_op.nombre}' ya existe.")

    # --- Datos para Ramos ---
    ramos_data = [
        "Agrícola", "Aviación", "Cadena de abastecimiento", "Copropiedades",
        "Crédito", "Cyber", "Energía Solar", "IRF", "Manejo", "MEC y RCE",
        "Multiriesgo", "Navegación", "Obras civiles terminadas", "Protección legal",
        "RC Clínicas y hospitales", "RC D&O", "RC Drones", "RC Hidrocarburos",
        "RC Medicos", "RC Parqueaderos", "RC PLO", "RC Profesional",
        "RC Sombrilla", "RC Talleres", "Transporte de mercancías",
        "Transporte específico", "Trasporte de valores", "TRC y RCE",
        "TRM y RCE", "Vivienda Segura y/o decenal"
    ]

    # Itera y crea Ramos, si no existen
    for nombre in ramos_data:
        ramo, created = Ramo.objects.get_or_create(nombre=nombre)
        if created:
            print(f"Ramo '{ramo.nombre}' creado.")
        else:
            print(f"Ramo '{ramo.nombre}' ya existe.")

    print("Llenado de datos iniciales completado.")

if __name__ == '__main__':
    populate_initial_data()