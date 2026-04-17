from django.contrib import admin
from .models import Cliente, Veiculo, OrdemServico

admin.site.register(Cliente)
admin.site.register(Veiculo)
admin.site.register(OrdemServico)