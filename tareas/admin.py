# tareas/admin.py

from django.contrib import admin
from .models import Tarea, Cliente, TipoOperacion, Aseguradora, Ramo, NotaGestion # Eliminado SolicitudAsunto
from django.utils import timezone
from django import forms # Necesario para los forms personalizados en el admin

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(TipoOperacion)
class TipoOperacionAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Aseguradora)
class AseguradoraAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Ramo)
class RamoAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)


# Inline para NotaGestion en TareaAdmin
class NotaGestionInline(admin.TabularInline):
    model = NotaGestion
    extra = 1
    fields = ['nota_texto', 'usuario_creacion', 'fecha_registro']
    readonly_fields = ['usuario_creacion', 'fecha_registro']

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        
        # Definir el formulario personalizado para NotaGestion dentro de get_formset
        class NotaGestionAdminForm(formset.form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if not self.instance.pk: # Si es una nueva nota
                    self.initial['usuario_creacion'] = request.user
                    self.initial['fecha_registro'] = timezone.now()
                
                # Deshabilitar el campo usuario_creacion si no es superuser ni 'kathe'
                if 'usuario_creacion' in self.fields and not request.user.is_superuser and request.user.username != 'kathe':
                    self.fields['usuario_creacion'].widget.attrs['disabled'] = 'disabled'
                    # Asegurarse de que el campo no sea requerido si está deshabilitado y ya tiene un valor
                    if self.instance.usuario_creacion:
                        self.fields['usuario_creacion'].required = False
                    # Quitar los botones de añadir/cambiar/borrar/ver relacionados para el campo deshabilitado
                    self.fields['usuario_creacion'].widget.can_add_related = False
                    self.fields['usuario_creacion'].widget.can_change_related = False
                    self.fields['usuario_creacion'].widget.can_delete_related = False
                    self.fields['usuario_creacion'].widget.can_view_related = False
            
            # Sobreescribir el método save para asegurar que usuario_creacion se guarde correctamente
            # cuando el campo está deshabilitado para el usuario final (Django no lo incluye en form.cleaned_data)
            def save(self, commit=True):
                instance = super().save(commit=False)
                if 'usuario_creacion' in self.fields and self.fields['usuario_creacion'].widget.attrs.get('disabled') == 'disabled':
                    # Si el campo está deshabilitado, y es una nueva instancia, se asegura de asignar el usuario actual.
                    # Si es una instancia existente, no se modifica su usuario_creacion.
                    if not instance.pk: # Nueva nota
                        instance.usuario_creacion = self.initial.get('usuario_creacion')
                if commit:
                    instance.save()
                return instance

        formset.form = NotaGestionAdminForm
        return formset


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'fecha_solicitud_cliente', 'tomador', 'tipo_operacion',
        'aseguradora', 'ramo', 'numero_poliza',
        'responsable',
        'propietario', 'estado', 'fecha_actualizacion',
        'asunto' # NUEVO: Mostrar el campo asunto en la lista de tareas del admin
    )
    list_filter = ('estado', 'tipo_operacion', 'aseguradora', 'ramo', 'propietario', 'responsable')
    search_fields = (
        'tomador__nombre', 'ramo__nombre', 'numero_poliza', 'aseguradora__nombre',
        'tipo_operacion__nombre',
        'responsable__first_name', 'responsable__last_name',
        'propietario__username',
        'asunto', # NUEVO: Buscar en el campo asunto de Tarea
        # 'solicitudes_asunto__asunto_texto', # ELIMINADO: Ya no existe este modelo
        'notas_gestion__nota_texto',
        'numero_radicado_cia', 'numero_aus_ticket', 'grupo_empresarial'
    )
    date_hierarchy = 'fecha_solicitud_cliente'
    ordering = ('-fecha_creacion',)

    inlines = [NotaGestionInline] # ELIMINADO: SolicitudAsuntoInline

    raw_id_fields = ('tomador', 'tipo_operacion', 'aseguradora', 'ramo', 'propietario', 'responsable')

    fieldsets = (
        (None, {
            'fields': (
                ('fecha_solicitud_cliente', 'fecha_envio_cliente'),
                ('tomador', 'tipo_operacion', 'aseguradora', 'ramo'),
                ('numero_poliza', 'grupo_empresarial'),
                ('numero_radicado_cia', 'numero_aus_ticket'),
                ('responsable', 'estado', 'propietario'),
                'asunto', # NUEVO: Incluir el campo asunto en el fieldset principal
                'descripcion', # Asumo que 'descripcion' es un campo de Tarea y quieres que esté visible
            )
        }),
        ('Fechas del Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.propietario:
            obj.propietario = request.user
        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        if formset.model == NotaGestion:
            instances = formset.save(commit=False)
            for instance in instances:
                if not instance.pk:
                    instance.usuario_creacion = request.user
                    instance.fecha_registro = timezone.now()
                instance.save()
            for obj_to_delete in formset.deleted_objects:
                obj_to_delete.delete()
            formset.save_m2m()
        else:
            super().save_formset(request, form, formset, change)