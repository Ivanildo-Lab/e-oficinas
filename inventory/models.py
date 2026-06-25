from django.db import models
from django.core.exceptions import ValidationError
from workshops.models import Oficina

class Fornecedor(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=200)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    contato = models.CharField(max_length=100, blank=True, verbose_name='Pessoa de Contato')
    observacao = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Fornecedor'
        verbose_name_plural = 'Fornecedores'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Setor(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)
    responsavel = models.CharField(max_length=100, blank=True, verbose_name='Responsável')
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Setor / Destino'
        verbose_name_plural = 'Setores / Destinos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class GrupoProduto(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome = models.CharField(max_length=150)

    class Meta:
        verbose_name = 'Grupo de Produto'
        verbose_name_plural = 'Grupos de Produtos'
        ordering = ['nome']

    def __str__(self):
        return self.nome

class Servico(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    nome_servico = models.CharField(max_length=200)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome_servico

class ItemEstoque(models.Model):
    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    grupo = models.ForeignKey(GrupoProduto, on_delete=models.SET_NULL, null=True, blank=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    referencia = models.CharField(max_length=100, blank=True, null=True)
    nome_item = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    quantidade = models.IntegerField(default=0)
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    minimo_ideal = models.IntegerField(default=1)

    class Meta:
        ordering = ['nome_item']
        constraints = [
            models.UniqueConstraint(fields=['oficina', 'referencia'], name='unique_referencia_por_oficina')
        ]

    def __str__(self):
        return f"{self.nome_item} ({self.referencia or 'sem ref'})"

    @property
    def valor_total(self):
        return self.quantidade * self.preco_unitario

    @property
    def quantidade_sugerida(self):
        if self.quantidade <= self.minimo_ideal:
            return max(1, (self.minimo_ideal * 2) - self.quantidade)
        return 0

    @property
    def precisa_repor(self):
        return self.quantidade <= self.minimo_ideal

    def ajustar_quantidade(self, delta):
        self.quantidade = max(0, self.quantidade + delta)
        self.save()

class MovimentoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    oficina = models.ForeignKey(Oficina, on_delete=models.CASCADE)
    item = models.ForeignKey(ItemEstoque, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    quantidade = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    observacao = models.TextField(blank=True)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Fornecedor')
    setor_destino = models.ForeignKey(Setor, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Setor / Destino')
    data = models.DateTimeField(verbose_name='Data da Movimentação')

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.quantidade}x {self.item.nome_item}"

    @property
    def valor_total(self):
        return self.quantidade * self.valor_unitario

    def clean(self):
        if self.tipo == 'saida':
            available = self.item.quantidade
            if self.pk:
                previous = MovimentoEstoque.objects.get(pk=self.pk)
                if previous.tipo == 'saida':
                    available += previous.quantidade
                else:
                    available -= previous.quantidade
            if self.quantidade > available:
                raise ValidationError('Quantidade insuficiente para saída no estoque.')

    def save(self, *args, **kwargs):
        previous = None
        if self.pk:
            previous = MovimentoEstoque.objects.select_related('item').get(pk=self.pk)
        if previous:
            if previous.tipo == 'entrada':
                previous.item.quantidade -= previous.quantidade
            else:
                previous.item.quantidade += previous.quantidade
            previous.item.save()
        if self.tipo == 'entrada':
            self.item.quantidade += self.quantidade
        else:
            self.item.quantidade -= self.quantidade
        self.item.save()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.tipo == 'entrada':
            self.item.quantidade -= self.quantidade
        else:
            self.item.quantidade += self.quantidade
        self.item.save()
        super().delete(*args, **kwargs)
