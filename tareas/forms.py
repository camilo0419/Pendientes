from django import forms
from django.forms import inlineformset_factory
from .models import Tarea, NotaGestion, Cliente, TipoOperacion, Aseguradora, Ramo 
from django.contrib.auth.models import User
from django.utils import timezone 

class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = [
            'fecha_solicitud_cliente',
            'tomador',
            'tipo_operacion',
            'aseguradora',
            'ramo',
            'numero_poliza',
            'grupo_empresarial',
            'numero_radicado_cia',
            'numero_aus_ticket',
            'responsable',
            'estado',
            'fecha_envio_cliente',
            'propietario',
            'asunto' 
        ]
        widgets = {
            'fecha_solicitud_cliente': forms.DateInput(
                attrs={'class': 'form-control datepicker-input'} # Ahora solo la clase
            ),
            'fecha_envio_cliente': forms.DateInput(
                attrs={'class': 'form-control datepicker-input'} # Ahora solo la clase
            ),
            'asunto': forms.Textarea(attrs={'rows': 4, 'class': 'form-control', 'placeholder': 'Describe el asunto principal de la tarea...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si es una nueva tarea y no se ha inicializado 'fecha_solicitud_cliente', establecerla a la fecha actual
        if not self.instance.pk and not self.initial.get('fecha_solicitud_cliente'):
             self.initial['fecha_solicitud_cliente'] = timezone.now().date() 
        
        # Añadir clases de Bootstrap y Select2 a los campos por defecto para estilos consistentes
        for field_name, field in self.fields.items():
            # Añadir 'form-control' si no es un Checkbox ni ya tiene 'datepicker-input' o 'form-select'
            if isinstance(field.widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.Textarea)):
                if 'class' not in field.widget.attrs or 'form-control' not in field.widget.attrs.get('class', ''):
                    current_classes = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = (current_classes + ' form-control').strip()
            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field.widget, forms.Select):
                # Asegúrate de que los selects tengan 'form-select' y 'select2-enabled'
                field.widget.attrs.update({'class': 'form-select select2-enabled'})


class NotaGestionForm(forms.ModelForm):
    class Meta:
        model = NotaGestion
        fields = ['nota_texto'] 
        widgets = {
            'nota_texto': forms.Textarea(attrs={'rows': 3, 'cols': 60, 'class': 'form-control', 'placeholder': 'Escribe la nota de gestión...'}),
        }

NotaGestionFormSet = inlineformset_factory(Tarea, NotaGestion, form=NotaGestionForm, extra=1, can_delete=True)