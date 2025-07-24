# tareas/views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import Tarea, NotaGestion, Cliente, TipoOperacion, Aseguradora, Ramo
from .forms import TareaForm, NotaGestionFormSet, NotaGestionForm
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string

@login_required
def lista_tareas(request):
    query = request.GET.get('q', '')
    tareas_query = Tarea.objects.filter(eliminado_logicamente=False)

    if query:
        # Añadir búsqueda por ID de tarea si es un número
        if query.isdigit():
            tareas_query = tareas_query.filter(
                Q(id=query) | # Permite buscar por el ID de la tarea
                Q(tomador__nombre__icontains=query) |
                Q(tipo_operacion__nombre__icontains=query) |
                Q(aseguradora__nombre__icontains=query) |
                Q(ramo__nombre__icontains=query) |
                Q(numero_poliza__icontains=query) |
                Q(numero_radicado_cia__icontains=query) |
                Q(numero_aus_ticket__icontains=query) |
                Q(propietario__first_name__icontains=query) |
                Q(propietario__last_name__icontains=query) |
                Q(responsable__first_name__icontains=query) |
                Q(responsable__last_name__icontains=query) |
                Q(estado__icontains=query) |
                Q(asunto__icontains=query)
            ).distinct()
        else:
            tareas_query = tareas_query.filter(
                Q(tomador__nombre__icontains=query) |
                Q(tipo_operacion__nombre__icontains=query) |
                Q(aseguradora__nombre__icontains=query) |
                Q(ramo__nombre__icontains=query) |
                Q(numero_poliza__icontains=query) |
                Q(numero_radicado_cia__icontains=query) |
                Q(numero_aus_ticket__icontains=query) |
                Q(propietario__first_name__icontains=query) |
                Q(propietario__last_name__icontains=query) |
                Q(responsable__first_name__icontains=query) |
                Q(responsable__last_name__icontains=query) |
                Q(estado__icontains=query) |
                Q(asunto__icontains=query)
            ).distinct()

    tareas_query = tareas_query.order_by('-fecha_solicitud_cliente')

    paginator = Paginator(tareas_query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'tareas/lista_tareas.html', {'page_obj': page_obj, 'query': query})

@login_required
def nueva_tarea(request):
    is_new_task = True

    if request.method == 'POST':
        form = TareaForm(request.POST)
        nota_formset = NotaGestionFormSet(request.POST, prefix='nota')

        if form.is_valid() and nota_formset.is_valid():
            with transaction.atomic():
                tarea = form.save(commit=False)
                if not tarea.propietario:
                    tarea.propietario = request.user
                tarea.save()

                nota_formset.instance = tarea
                notas_to_save = nota_formset.save(commit=False)
                for nota in notas_to_save:
                    if not nota.usuario_creacion:
                        nota.usuario_creacion = request.user
                    nota.save()
                for obj in nota_formset.deleted_objects:
                    obj.delete()

            messages.success(request, 'Tarea creada exitosamente!')
            return redirect('lista_tareas')
        else:
            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = TareaForm(initial={'propietario': request.user})
        nota_formset = NotaGestionFormSet(prefix='nota')

    context = {
        'form': form,
        'nota_formset': nota_formset,
        'is_new_task': is_new_task
    }
    return render(request, 'tareas/tarea_form.html', context)


@login_required
def editar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    is_new_task = False

    if tarea.estado == 'Completada':
        messages.warning(request, 'No puedes editar una tarea que ha sido marcada como "Completada". Si necesitas editarla, desmárcala como completada primero.')
        return redirect('detalle_tarea', pk=tarea.pk)

    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        nota_formset = NotaGestionFormSet(request.POST, instance=tarea, prefix='nota')

        if form.is_valid() and nota_formset.is_valid():
            with transaction.atomic():
                tarea = form.save()

                nota_formset.instance = tarea
                notas_to_save = nota_formset.save(commit=False)
                for nota in notas_to_save:
                    if not nota.pk or not nota.usuario_creacion:
                        nota.usuario_creacion = request.user
                    nota.save()
                for obj in nota_formset.deleted_objects:
                    obj.delete()

            messages.success(request, 'Tarea actualizada exitosamente!')
            return redirect('detalle_tarea', pk=tarea.pk)
        else:
            # ¡AQUÍ ES DONDE NECESITAMOS LA SALIDA!
            print("\n--- ERRORES EN TAREA FORM ---") # Agrega esto
            print(form.errors)                      # Agrega esto
            print("\n--- ERRORES EN NOTA FORMSET ---") # Agrega esto
            print(nota_formset.errors)              # Agrega esto
            print("---------------------------------\n") # Agrega esto

            messages.error(request, 'Por favor, corrige los errores en el formulario.')
    else:
        form = TareaForm(instance=tarea)
        nota_formset = NotaGestionFormSet(instance=tarea, prefix='nota')

    context = {
        'form': form,
        'nota_formset': nota_formset,
        'tarea': tarea,
        'is_new_task': is_new_task
    }
    return render(request, 'tareas/tarea_form.html', context)


@login_required
def detalle_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)

    notas = NotaGestion.objects.filter(tarea=tarea).order_by('fecha_registro')

    historial_eventos = []

    for i, nota in enumerate(notas):
        historial_eventos.append({
            'tipo': 'nota',
            'fecha': nota.fecha_registro,
            'objeto': nota,
            'indice_secuencial': i + 1
        })

    historial_eventos.sort(key=lambda x: x['fecha'])

    context = {
        'tarea': tarea,
        'historial_eventos': historial_eventos,
    }
    return render(request, 'tareas/detalle_tarea.html', context)


@login_required
@require_POST
def eliminar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if tarea.estado == 'Completada':
        messages.warning(request, 'No puedes archivar una tarea que ha sido marcada como "Completada". Desmárcala como completada para archivarla o eliminarla lógicamente.')
        return redirect('detalle_tarea', pk=tarea.pk)

    tarea.soft_delete()
    messages.success(request, f'Tarea #{tarea.id} archivada exitosamente.')
    return redirect('lista_tareas')

@login_required
@require_POST
def restaurar_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    tarea.restore()
    messages.success(request, f'Tarea #{tarea.id} restaurada exitosamente.')
    return redirect('lista_tareas')


@login_required
@require_POST
def toggle_completada_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)

    if tarea.estado == 'Completada':
        tarea.estado = 'En Proceso'
        tarea.fecha_envio_cliente = None
        messages.info(request, f'Tarea #{tarea.id} desmarcada como "Completada".')
    else:
        tarea.estado = 'Completada'
        tarea.fecha_envio_cliente = timezone.now().date()
        messages.success(request, f'Tarea #{tarea.id} marcada como "Completada".')

    tarea.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'new_estado': tarea.get_estado_display(),
            'fecha_envio_cliente': tarea.fecha_envio_cliente.strftime('%d/%m/%Y') if tarea.fecha_envio_cliente else 'N/A',
            'is_completada': tarea.estado == 'Completada'
        })
    return redirect('detalle_tarea', pk=tarea.pk)


@login_required
def add_nota_to_tarea(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    # Asegúrate de que solo los responsables o propietarios puedan añadir notas, si es tu lógica
    # if request.user != tarea.responsable and request.user != tarea.propietario:
    #     if not request.user.is_superuser: # O un permiso específico
    #         return HttpResponseForbidden("No tienes permiso para agregar notas a esta tarea.")

    if request.method == 'POST':
        form = NotaGestionForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.tarea = tarea
            nota.autor = request.user
            nota.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Si es una petición AJAX, devuelve JSON
                return JsonResponse({'status': 'success', 'message': 'Nota agregada con éxito.'})
            else:
                # Si no es AJAX, redirige (comportamiento por defecto)
                messages.success(request, 'Nota agregada con éxito!')
                return redirect('detalle_tarea', pk=tarea.pk)
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Si es AJAX y el formulario tiene errores, devuelve el HTML del formulario con errores
                form_html = render_to_string('tareas/add_related_item_form.html', {'form': form, 'tarea': tarea, 'form_title': 'Agregar Nueva Nota'})
                return JsonResponse({'status': 'error', 'form_html': form_html})
            else:
                # Si no es AJAX, renderiza la página con el formulario y errores
                return render(request, 'tareas/add_related_item_form.html', {'form': form, 'tarea': tarea, 'form_title': 'Agregar Nueva Nota'})
    else:
        form = NotaGestionForm()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            # Si es AJAX GET, devuelve solo el HTML del formulario
            return render(request, 'tareas/add_related_item_form.html', {'form': form, 'tarea': tarea, 'form_title': 'Agregar Nueva Nota'})
        else:
            # Si no es AJAX GET, renderiza la página completa
            return render(request, 'tareas/add_related_item_form.html', {'form': form, 'tarea': tarea, 'form_title': 'Agregar Nueva Nota'})
