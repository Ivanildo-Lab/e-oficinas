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
    path('estoque/', include('inventory.urls')),
]

# ADICIONE ESTA LINHA NO FINAL:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Producao (Coolify): WhiteNoise cuida dos estaticos; a midia (logos,
    # fotos de produtos/OS) e servida pelo Django a partir do volume media_data.
    from django.urls import re_path
    from django.views.static import serve

    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$',
            serve,
            {'document_root': settings.MEDIA_ROOT},
        ),
    ]