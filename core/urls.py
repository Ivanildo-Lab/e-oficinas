from django.contrib import admin
from django.urls import path, include
from django.conf import settings # IMPORTAR ISSO
from django.conf.urls.static import static # IMPORTAR ISSO
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='workshops/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('', include('workshops.urls')), 
    path('operacoes/', include('operations.urls')),
]

# ADICIONE ESTA LINHA NO FINAL:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)