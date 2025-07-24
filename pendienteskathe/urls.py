# pendienteskathe/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    
    
    # URL de Login (asegúrate de que el nombre sea 'login')
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    
    # ¡CORRECCIÓN CRÍTICA! Elimina next_page='/' para que use LOGOUT_REDIRECT_URL de settings.py
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'), 
    
    # Conexión a tu app 'tareas'
    path('tareas/', include('tareas.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)