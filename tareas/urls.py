# tareas/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.lista_tareas, name='lista_tareas'),
    path('nueva/', views.nueva_tarea, name='nueva_tarea'),
    path('<int:pk>/', views.detalle_tarea, name='detalle_tarea'),
    path('<int:pk>/editar/', views.editar_tarea, name='editar_tarea'),
    path('<int:pk>/eliminar/', views.eliminar_tarea, name='eliminar_tarea'), # Para eliminación lógica
    path('<int:pk>/restaurar/', views.restaurar_tarea, name='restaurar_tarea'), # Para restaurar

    # --- NUEVAS URLs (Corregidas) ---
    # URL para añadir nota - ¡Sin el prefijo 'tareas/' aquí!
    path('<int:pk>/add_nota/', views.add_nota_to_tarea, name='add_nota_to_tarea'),
    
    # URL para toggle_completada - Una sola definición y sin el prefijo 'tareas/'
    path('<int:pk>/toggle_completada/', views.toggle_completada_tarea, name='toggle_completada'), # Usa 'toggle_completada' como name

    # URLs de autenticación de Django (estas son correctas si las tienes en este archivo)
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
]