from django.db import models
from django.contrib.auth.models import User

class Oficina(models.Model):
    nome = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    logo = models.ImageField(upload_to='oficinas/logos/', null=True, blank=True)
    endereco = models.TextField()
    telefone = models.CharField(max_length=20)
    email = models.EmailField()

    def __str__(self):
        return self.nome

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    perfil = models.CharField(max_length=20, default='admin')

    def __str__(self):
        return f"{self.user.username} - {self.oficina.nome}"
    
class Mecanico(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return self.nome