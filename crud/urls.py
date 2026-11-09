"""
Rutas globales del sistema para Ferretería "El Constructor".
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.ferreteria.urls')),
]

# En desarrollo Django sirve las imágenes subidas (media/). Los estáticos los sirve runserver por sí solo.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
