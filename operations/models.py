from django.db import models
from workshops.models import Oficina
from django.db.models import UniqueConstraint
from workshops.models import Mecanico

class Cliente(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF") 
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    telefone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    endereco = models.TextField()
    def __str__(self):
        return self.nome    

class Veiculo(models.Model):
    # Campos que já tínhamos
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    placa = models.CharField(max_length=10, verbose_name="Placa")
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=100) # Campo "Veículo" no PDF
    ano = models.CharField(max_length=20) # Campo "Ano / Modelo"

    versao = models.CharField(max_length=50, blank=True, null=True)
    motor = models.CharField(max_length=50, blank=True, null=True)
    cor = models.CharField(max_length=30, blank=True, null=True)
    chassi = models.CharField(max_length=50, blank=True, null=True)
    
    TRANSMISSAO_CHOICES = [('Manual', 'Manual'), ('Automatica', 'Automática')]
    transmissao = models.CharField(max_length=20, choices=TRANSMISSAO_CHOICES, default='Manual')
    
    COMBUSTIVEL_CHOICES = [('Etanol', 'Etanol'), ('Gasolina', 'Gasolina'), ('Flex', 'Flex'), ('Diesel', 'Diesel')]
    combustivel = models.CharField(max_length=20, choices=COMBUSTIVEL_CHOICES, default='Flex')
    
    PORTAS_CHOICES = [('2', '2 Portas'), ('4', '4 Portas')]
    portas = models.CharField(max_length=10, choices=PORTAS_CHOICES, default='4')
    
    tem_abs = models.BooleanField(default=False)

    class Meta:
        # Criamos a restrição: A combinação de oficina + placa deve ser única
        constraints = [
            UniqueConstraint(fields=['oficina', 'placa'], name='unique_placa_por_oficina')
        ]

    def save(self, *args, **kwargs):
        # Padronização: ABC1234
        self.placa = self.placa.upper().replace(" ", "").replace("-", "")
        super(Veiculo, self).save(*args, **kwargs)    

    def __str__(self):
        return f"{self.placa} - {self.modelo}"
    
class OrdemServico(models.Model):

    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    veiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)
    mecanico = models.ForeignKey('workshops.Mecanico', on_delete=models.SET_NULL, null=True) 
    whatsapp = models.CharField(max_length=20, blank=True)
    onde_nos_conheceu = models.CharField(max_length=100, blank=True)
    horario_orcamento = models.TimeField(null=True, blank=True)
    data_entrega = models.DateTimeField(null=True, blank=True)
    
    km_atual = models.IntegerField(default=0)
    motor = models.CharField(max_length=50, blank=True)
    cor = models.CharField(max_length=30, blank=True)
    transmissao = models.CharField(max_length=20, choices=[('Manual','Manual'),('Automatica','Automática')], default='Manual')
    portas = models.CharField(max_length=10, choices=[('2','2 Portas'),('4','4 Portas')], default='4')
    combustivel_tipo = models.CharField(max_length=20, choices=[('Flex','Flex'),('Gasolina','Gasolina'),('Etanol','Etanol'),('Diesel','Diesel')], default='Flex')
    
    tem_abs = models.BooleanField(default=False)
    luz_injecao_acesa = models.BooleanField(default=False)
    tem_documento = models.BooleanField(default=False)
    
    capa_protecao_frontal = models.BooleanField(default=False)
    capa_banco = models.BooleanField(default=False)
    filme_volante = models.BooleanField(default=False)
    filme_cambio_freio = models.BooleanField(default=False)
    
    servico_solicitado = models.TextField()
    status = models.CharField(max_length=20, default='aberta')
    data_abertura = models.DateTimeField(auto_now_add=True)

    nivel_combustivel = models.IntegerField(default=0) # 0 a 100
    tem_documento = models.BooleanField(default=False)
    
    # Salvaremos o "mapa de riscos" e a "assinatura" como dados de imagem Base64
    mapa_avarias_base64 = models.TextField(blank=True, null=True)
    assinatura_cliente_base64 = models.TextField(blank=True, null=True)

    ultima_troca_oleo_data = models.DateField(null=True, blank=True)
    ultima_troca_oleo_km = models.IntegerField(null=True, blank=True)
    luz_injecao_acesa = models.BooleanField(default=False)
    conclusao_tecnica = models.TextField(blank=True, null=True)

class ChecklistItem(models.Model):
    os = models.ForeignKey(OrdemServico, related_name='itens_checklist', on_delete=models.CASCADE)
    descricao = models.CharField(max_length=100)
    fase = models.CharField(max_length=10) # 'entrada' ou 'saida'
    status = models.CharField(max_length=5, default='p') 

class OSFoto(models.Model):
    os = models.ForeignKey(OrdemServico, related_name='fotos', on_delete=models.CASCADE)
    foto = models.ImageField(upload_to='os/inspecao/')
    data_upload = models.DateTimeField(auto_now_add=True)