from django.urls import path, include
from apps.ferreteria import views

app_name = 'ferreteria'

producto_patterns = [
    path('', views.producto_list, name='home'),
    path('<int:pk>/', views.producto_detail, name='producto-detail'),
    path('crear/', views.producto_create, name='producto-create'),
    path('<int:pk>/editar/', views.producto_update, name='producto-edit'),
    path('<int:pk>/eliminar/', views.producto_delete, name='producto-delete'),
]

urlpatterns = [
    path('', views.log_in, name='log-in'),
    path('logout/', views.log_out, name='log-out'),
    path('categorias/', views.categoria_list, name='category-list'),
    path('productos/', include(producto_patterns)),
]
