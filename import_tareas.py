import os
import django
import pandas as pd
from datetime import datetime
from django.db import transaction
import sys

# Añade la ruta del directorio actual al sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

# Configurar Django ANTES de importar CUALQUIER modelo de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pendienteskathe.settings')
django.setup()

# AHORA que Django está configurado, puedes importar tus modelos.
from django.contrib.auth.models import User
from tareas.models import Tarea

# Ruta del archivo Excel
archivo_excel = 'data/datos.xlsx'

# Leer el archivo Excel
df = pd.read_excel(archivo_excel)

print("Columnas leídas del Excel:", df.columns.tolist())

# Renombrar la columna 'Propietaria' a 'propietario' para que coincida con el modelo de Django
df.rename(columns={'Propietaria': 'propietario'}, inplace=True)

# Convertir las columnas de fecha
# APLICAR errors='coerce' también a fecha_solicitud_cliente
df['fecha_solicitud_cliente'] = pd.to_datetime(df['fecha_solicitud_cliente'], errors='coerce').dt.date
df['fecha_envio_cliente'] = pd.to_datetime(df['fecha_envio_cliente'], errors='coerce').dt.date

print("Iniciando importación de datos...")
# Usamos transaction.atomic() para asegurar la integridad de los datos.
# Eliminamos el try-except dentro del bucle temporalmente para que el primer error
# detenga la ejecución y muestre la traza completa, facilitando el diagnóstico.
with transaction.atomic():
    for index, fila in df.iterrows():
        # Manejar 'solicitud_asunto' si es NaN
        solicitud_asunto_val = fila.get('solicitud_asunto', '')
        if pd.isna(solicitud_asunto_val):
            solicitud_asunto_val = ''
        solicitud_asunto_val = str(solicitud_asunto_val)

        # Manejar 'notas_gestion' si es NaN
        notas_gestion = fila.get('notas_gestion', '')
        if pd.isna(notas_gestion):
            notas_gestion = ''
            
        # NUEVA CORRECCIÓN: Manejar fecha_solicitud_cliente si es NaT
        fecha_solicitud = fila['fecha_solicitud_cliente']
        if pd.isna(fecha_solicitud):
            fecha_solicitud = None

        # Manejar fecha_envio_cliente si es NaT
        fecha_envio = fila['fecha_envio_cliente']
        if pd.isna(fecha_envio):
            fecha_envio = None

        # Obtener el usuario. Si no existe, User.objects.get lanzará DoesNotExist
        propietario_obj = User.objects.get(username=fila['propietario'])

        tarea = Tarea(
            fecha_solicitud_cliente=fecha_solicitud, # Usar el valor manejado
            fecha_envio_cliente=fecha_envio,         # Usar el valor manejado
            tipo_operacion=fila['tipo_operacion'],
            aseguradora=str(fila['aseguradora']).strip(),
            ramo=str(fila['ramo']).strip(),
            numero_poliza=fila['numero_poliza'],
            tomador=fila['tomador'],
            grupo_empresarial=fila['grupo_empresarial'],
            solicitud_asunto=solicitud_asunto_val,
            numero_radicado_cia=fila['numero_radicado_cia'],
            numero_aus_ticket=fila['numero_aus_ticket'],
            solicitado_por=fila['solicitado_por'],
            notas_gestion=notas_gestion,
            propietario=propietario_obj
        )
        tarea.save()
        print(f"Tarea creada: {tarea}")

print("Proceso de importación finalizado.")