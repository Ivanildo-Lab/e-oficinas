from django.db import models
from workshops.models import Oficina

class Servico(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome_servico = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

class ItemEstoque(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome_item = models.CharField(max_length=200)
    quantidade = models.IntegerField(default=0)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)