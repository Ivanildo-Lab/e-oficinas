from django.urls import path
from . import views

app_name = 'workshops'

urlpatterns = [
    # Isso fará com que http://127.0.0.1:8000/ abra o dashboard
    path('', views.dashboard, name='dashboard'),
    
    path('mecanicos/', views.lista_mecanicos, name='lista_mecanicos'),
    path('mecanicos/novo/', views.novo_mecanico, name='novo_mecanico'),
    path('mecanicos/editar/<int:pk>/', views.editar_mecanico, name='editar_mecanico'),
    path('mecanicos/excluir/<int:pk>/', views.excluir_mecanico, name='excluir_mecanico'),

]