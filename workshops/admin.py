# F:\HD 1tb\...\workshops\admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Oficina, PerfilUsuario, Mecanico

# Isso faz a Oficina aparecer dentro da tela de Usuário
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Vínculo com Oficina'

class UserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)

# Re-registra o Usuário padrão do Django com o nosso "puxadinho" da Oficina
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

# Registra os outros modelos normalmente
admin.site.register(Oficina)
admin.site.register(Mecanico)