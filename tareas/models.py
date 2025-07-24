# tareas/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# --- Nuevos modelos (quedan igual) ---
class Cliente(models.Model):
    nombre = models.CharField(max_length=200, unique=True)
    # Si quieres añadir email y teléfono, deberían ir aquí:
    # email = models.EmailField(blank=True, null=True, verbose_name="Correo Electrónico")
    # telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Número de Teléfono")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class TipoOperacion(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Tipo de Operación"
        verbose_name_plural = "Tipos de Operación"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

class Aseguradora(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Aseguradora"
        verbose_name_plural = "Aseguradoras"
        ordering = ['nombre']

    # === LÍNEA CORREGIDA AQUÍ ===
    def __str__(self):
        return self.nombre

class Ramo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Ramo"
        verbose_name_plural = "Ramos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

# --- Modelo Tarea (modificado) ---
class Tarea(models.Model):
    # Campos existentes de Tarea
    #titulo = models.CharField(max_length=200, verbose_name="Título de la Tarea") # Añadí verbose_name para consistencia
    
    # === CAMPO 'ASUNTO' MOVido Y RENOMBRADO ===
    asunto = models.TextField(verbose_name="Asunto/Descripción Principal")

    #descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción Adicional")
    
    # Campos de fechas
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    fecha_actualizacion = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")
    fecha_solicitud_cliente = models.DateField(verbose_name="Fecha de Solicitud (Cliente)")
    fecha_envio_cliente = models.DateField(blank=True, null=True, verbose_name="Fecha de Envío (Cliente)")

    # Foreign Keys a los nuevos modelos
    tomador = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tomador (Cliente)")
    tipo_operacion = models.ForeignKey(TipoOperacion, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tipo de Operación")
    aseguradora = models.ForeignKey(Aseguradora, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Aseguradora")
    ramo = models.ForeignKey(Ramo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Ramo")

    # Otros campos existentes
    numero_poliza = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número de Póliza")
    grupo_empresarial = models.CharField(max_length=200, blank=True, null=True, verbose_name="Grupo Empresarial")
    numero_radicado_cia = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número Radicado Compañía")
    numero_aus_ticket = models.CharField(max_length=100, blank=True, null=True, verbose_name="Número AUS Ticket")
    responsable = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='tareas_responsable', verbose_name="Responsable")

    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Completada', 'Completada'),
        ('Anulada', 'Anulada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente', verbose_name="Estado")

    propietario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Propietario Asignado")

    # Campo para eliminación lógica
    eliminado_logicamente = models.BooleanField(default=False, verbose_name="Eliminado Lógicamente")

    class Meta:
        verbose_name = "Tarea"
        verbose_name_plural = "Tareas"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Tarea #{self.id} - {self.asunto[:50]}{'...' if len(self.asunto) > 50 else ''}"

# --- Modelo SolicitudAsunto (ELIMINADO) ---
# Este modelo se elimina. Si tenías este modelo, BÓRRALO de tu archivo.
# class SolicitudAsunto(models.Model):
#    ...

# --- Modelo NotaGestion (queda igual) ---
class NotaGestion(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name='notas_gestion')
    nota_texto = models.TextField(verbose_name="Texto de la Nota")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    usuario_creacion = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Usuario de Creación")

    class Meta:
        verbose_name = "Nota de Gestión"
        verbose_name_plural = "Notas de Gestión"
        ordering = ['fecha_registro']

    def __str__(self):
        return f"Nota para Tarea {self.tarea.id}: {self.nota_texto[:50]}..."