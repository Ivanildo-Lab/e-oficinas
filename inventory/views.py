from django.contrib.auth.decorators import login_required
from django.db.models import F, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.utils import timezone

from workshops.utils import get_oficina
from .forms import ItemEstoqueForm, MovimentoEstoqueForm, FornecedorForm, SetorForm
from .models import GrupoProduto, ItemEstoque, MovimentoEstoque, Fornecedor, Setor


@login_required
def lista_itens(request):
    oficina = get_oficina(request)
    itens = ItemEstoque.objects.filter(oficina=oficina)
    low_stock = itens.filter(quantidade__lte=F('minimo_ideal')).count()
    return render(request, 'inventory/item_list.html', {
        'itens': itens,
        'low_stock': low_stock,
    })


@login_required
def novo_item(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, oficina=oficina)
        if form.is_valid():
            item = form.save(commit=False)
            item.oficina = oficina
            if not item.data_cadastro:
                item.data_cadastro = timezone.now()
            item.save()
            return redirect('inventory:lista_itens')
    else:
        form = ItemEstoqueForm(oficina=oficina, initial={'data_cadastro': timezone.now().strftime('%Y-%m-%dT%H:%M')})
    return render(request, 'inventory/item_form.html', {'form': form, 'titulo': 'Novo Item'})


@login_required
def editar_item(request, pk):
    oficina = get_oficina(request)
    item = get_object_or_404(ItemEstoque, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = ItemEstoqueForm(request.POST, request.FILES, instance=item, oficina=oficina)
        if form.is_valid():
            form.save()
            return redirect('inventory:lista_itens')
    else:
        form = ItemEstoqueForm(instance=item, oficina=oficina)
    return render(request, 'inventory/item_form.html', {'form': form, 'titulo': 'Editar Item'})


@login_required
def excluir_item(request, pk):
    oficina = get_oficina(request)
    item = get_object_or_404(ItemEstoque, pk=pk, oficina=oficina)
    if request.method == 'POST':
        item.delete()
        return redirect('inventory:lista_itens')
    return render(request, 'inventory/confirm_exclusao.html', {'objeto': item, 'tipo': 'item'})


@login_required
def lista_grupos(request):
    oficina = get_oficina(request)
    grupos = GrupoProduto.objects.filter(oficina=oficina)
    return render(request, 'inventory/grupo_list.html', {'grupos': grupos})


@login_required
def novo_grupo(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            GrupoProduto.objects.create(oficina=oficina, nome=nome.strip())
            return redirect('inventory:lista_grupos')
    return render(request, 'inventory/grupo_form.html', {'titulo': 'Novo Grupo'})


@login_required
def editar_grupo(request, pk):
    oficina = get_oficina(request)
    grupo = get_object_or_404(GrupoProduto, pk=pk, oficina=oficina)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        if nome:
            grupo.nome = nome.strip()
            grupo.save()
            return redirect('inventory:lista_grupos')
    return render(request, 'inventory/grupo_form.html', {'titulo': 'Editar Grupo', 'grupo': grupo})


@login_required
def excluir_grupo(request, pk):
    oficina = get_oficina(request)
    grupo = get_object_or_404(GrupoProduto, pk=pk, oficina=oficina)
    if request.method == 'POST':
        grupo.delete()
        return redirect('inventory:lista_grupos')
    return render(request, 'inventory/confirm_exclusao.html', {'objeto': grupo, 'tipo': 'grupo'})


@login_required
def buscar_itens(request):
    oficina = get_oficina(request)
    termo = request.GET.get('q', '').strip()
    itens = ItemEstoque.objects.filter(oficina=oficina)
    if termo:
        itens = itens.filter(
            Q(nome_item__icontains=termo) |
            Q(referencia__icontains=termo) |
            Q(marca__icontains=termo)
        )
    resultados = [
        {
            'id': item.id,
            'label': f"{item.nome_item} ({item.referencia or 'sem ref'}) - {item.marca or 'sem marca'}",
            'value': item.nome_item,
            'referencia': item.referencia,
            'marca': item.marca,
            'quantidade': item.quantidade,
        }
        for item in itens.order_by('nome_item')[:20]
    ]
    return JsonResponse(resultados, safe=False)


@login_required
def buscar_fornecedores(request):
    oficina = get_oficina(request)
    termo = request.GET.get('q', '').strip()
    fornecedores = Fornecedor.objects.filter(oficina=oficina, ativo=True)
    if termo:
        fornecedores = fornecedores.filter(
            Q(nome__icontains=termo) |
            Q(telefone__icontains=termo) |
            Q(email__icontains=termo)
        )
    resultados = [
        {
            'id': f.id,
            'label': f"{f.nome} - {f.telefone or 's/ tel'}",
            'value': f.nome,
        }
        for f in fornecedores.order_by('nome')[:20]
    ]
    return JsonResponse(resultados, safe=False)


@login_required
def buscar_setores(request):
    oficina = get_oficina(request)
    termo = request.GET.get('q', '').strip()
    setores = Setor.objects.filter(oficina=oficina, ativo=True)
    if termo:
        setores = setores.filter(
            Q(nome__icontains=termo) |
            Q(responsavel__icontains=termo)
        )
    resultados = [
        {
            'id': s.id,
            'label': f"{s.nome} - {s.responsavel or 's/ resp'}",
            'value': s.nome,
        }
        for s in setores.order_by('nome')[:20]
    ]
    return JsonResponse(resultados, safe=False)


@login_required
def lista_movimentos(request):
    oficina = get_oficina(request)
    movimentos = MovimentoEstoque.objects.filter(oficina=oficina)
    return render(request, 'inventory/movimento_list.html', {'movimentos': movimentos})


@login_required
def nova_movimentacao(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = MovimentoEstoqueForm(request.POST, oficina=oficina)
        if form.is_valid():
            movimento = form.save(commit=False)
            movimento.oficina = oficina
            movimento.save()
            return redirect('inventory:lista_movimentos')
    else:
        form = MovimentoEstoqueForm(oficina=oficina, initial={'data': timezone.now().strftime('%Y-%m-%dT%H:%M')})
    return render(request, 'inventory/movimento_form.html', {'form': form, 'titulo': 'Nova Movimentação'})


@login_required
def editar_movimentacao(request, pk):
    oficina = get_oficina(request)
    movimento = get_object_or_404(MovimentoEstoque, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = MovimentoEstoqueForm(request.POST, instance=movimento, oficina=oficina)
        if form.is_valid():
            form.save()
            return redirect('inventory:lista_movimentos')
    else:
        form = MovimentoEstoqueForm(instance=movimento, oficina=oficina)
    return render(request, 'inventory/movimento_form.html', {'form': form, 'titulo': 'Editar Movimentação'})


@login_required
def excluir_movimentacao(request, pk):
    oficina = get_oficina(request)
    movimento = get_object_or_404(MovimentoEstoque, pk=pk, oficina=oficina)
    if request.method == 'POST':
        movimento.delete()
        return redirect('inventory:lista_movimentos')
    return render(request, 'inventory/confirm_exclusao.html', {'objeto': movimento, 'tipo': 'movimentação', 'cancel_url': reverse('inventory:lista_movimentos')})


@login_required
def relatorio_estoque(request):
    oficina = get_oficina(request)
    itens = ItemEstoque.objects.filter(oficina=oficina)
    movimentos = MovimentoEstoque.objects.filter(oficina=oficina)

    item_id = request.GET.get('item')
    tipo = request.GET.get('tipo')
    fornecedor = request.GET.get('fornecedor')
    setor = request.GET.get('setor')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    if item_id:
        movimentos = movimentos.filter(item_id=item_id)
    if tipo:
        movimentos = movimentos.filter(tipo=tipo)
    if fornecedor:
        movimentos = movimentos.filter(fornecedor_id=fornecedor)
    if setor:
        movimentos = movimentos.filter(setor_destino_id=setor)
    if data_inicio:
        movimentos = movimentos.filter(data__date__gte=data_inicio)
    if data_fim:
        movimentos = movimentos.filter(data__date__lte=data_fim)

    total_entradas = movimentos.filter(tipo='entrada').aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_saidas = movimentos.filter(tipo='saida').aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_estoque_valor = itens.aggregate(
        total=Sum(F('quantidade') * F('preco_unitario'))
    )['total'] or 0

    sugestoes = [
        item for item in itens if item.quantidade_sugerida > 0
    ]

    fornecedores = Fornecedor.objects.filter(oficina=oficina, ativo=True).order_by('nome')
    setores = Setor.objects.filter(oficina=oficina, ativo=True).order_by('nome')

    return render(request, 'inventory/relatorio_estoque.html', {
        'itens': itens,
        'movimentos': movimentos,
        'total_entradas': total_entradas,
        'total_saidas': total_saidas,
        'total_estoque_valor': total_estoque_valor,
        'filtro_item': item_id,
        'filtro_tipo': tipo,
        'filtro_fornecedor': fornecedor,
        'filtro_setor': setor,
        'filtro_data_inicio': data_inicio,
        'filtro_data_fim': data_fim,
        'sugestoes': sugestoes,
        'lista_fornecedores': fornecedores,
        'lista_setores': setores,
    })


@login_required
def relatorio_movimentacoes_produto(request):
    oficina = get_oficina(request)
    itens = ItemEstoque.objects.filter(oficina=oficina).order_by('nome_item')
    movimentos = MovimentoEstoque.objects.filter(oficina=oficina).select_related('item', 'fornecedor', 'setor_destino')

    item_id = request.GET.get('item')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')

    item_selecionado = None
    if item_id:
        item_selecionado = itens.filter(id=item_id).first()
        movimentos = movimentos.filter(item_id=item_id)

    if data_inicio:
        movimentos = movimentos.filter(data__date__gte=data_inicio)
    if data_fim:
        movimentos = movimentos.filter(data__date__lte=data_fim)

    total_entradas_qtd = movimentos.filter(tipo='entrada').aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_entradas_valor = movimentos.filter(tipo='entrada').aggregate(total=Sum(F('quantidade') * F('valor_unitario')))['total'] or 0
    total_saidas_qtd = movimentos.filter(tipo='saida').aggregate(Sum('quantidade'))['quantidade__sum'] or 0
    total_saidas_valor = movimentos.filter(tipo='saida').aggregate(total=Sum(F('quantidade') * F('valor_unitario')))['total'] or 0

    return render(request, 'inventory/relatorio_movimentacoes_produto.html', {
        'itens': itens,
        'movimentos': movimentos,
        'item_selecionado': item_selecionado,
        'filtro_item': item_id,
        'filtro_data_inicio': data_inicio,
        'filtro_data_fim': data_fim,
        'total_entradas_qtd': total_entradas_qtd,
        'total_entradas_valor': total_entradas_valor,
        'total_saidas_qtd': total_saidas_qtd,
        'total_saidas_valor': total_saidas_valor,
    })


@login_required
def sugestao_compras(request):
    oficina = get_oficina(request)
    itens = ItemEstoque.objects.filter(oficina=oficina).order_by('nome_item')
    sugestoes = []
    for item in itens:
        if item.quantidade_sugerida > 0:
            sugestoes.append({
                'item': item,
                'qtd_atual': item.quantidade,
                'qtd_minima': item.minimo_ideal,
                'qtd_sugerida': item.quantidade_sugerida,
                'valor_unitario': item.preco_unitario,
                'valor_total': item.quantidade_sugerida * item.preco_unitario,
            })
    valor_total_compras = sum(s['valor_total'] for s in sugestoes)

    return render(request, 'inventory/sugestao_compras.html', {
        'sugestoes': sugestoes,
        'valor_total_compras': valor_total_compras,
    })


# === CRUD FORNECEDORES ===

@login_required
def lista_fornecedores(request):
    oficina = get_oficina(request)
    fornecedores = Fornecedor.objects.filter(oficina=oficina)
    return render(request, 'inventory/fornecedor_list.html', {'fornecedores': fornecedores})


@login_required
def novo_fornecedor(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = FornecedorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.oficina = oficina
            obj.save()
            return redirect('inventory:lista_fornecedores')
    else:
        form = FornecedorForm()
    return render(request, 'inventory/fornecedor_form.html', {'form': form, 'titulo': 'Novo Fornecedor'})


@login_required
def editar_fornecedor(request, pk):
    oficina = get_oficina(request)
    obj = get_object_or_404(Fornecedor, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = FornecedorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('inventory:lista_fornecedores')
    else:
        form = FornecedorForm(instance=obj)
    return render(request, 'inventory/fornecedor_form.html', {'form': form, 'titulo': 'Editar Fornecedor'})


@login_required
def excluir_fornecedor(request, pk):
    oficina = get_oficina(request)
    obj = get_object_or_404(Fornecedor, pk=pk, oficina=oficina)
    if request.method == 'POST':
        obj.delete()
        return redirect('inventory:lista_fornecedores')
    return render(request, 'inventory/confirm_exclusao.html', {'objeto': obj, 'tipo': 'fornecedor'})


# === CRUD SETORES / DESTINOS ===

@login_required
def lista_setores(request):
    oficina = get_oficina(request)
    setores = Setor.objects.filter(oficina=oficina)
    return render(request, 'inventory/setor_list.html', {'setores': setores})


@login_required
def novo_setor(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.oficina = oficina
            obj.save()
            return redirect('inventory:lista_setores')
    else:
        form = SetorForm()
    return render(request, 'inventory/setor_form.html', {'form': form, 'titulo': 'Novo Setor'})


@login_required
def editar_setor(request, pk):
    oficina = get_oficina(request)
    obj = get_object_or_404(Setor, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = SetorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect('inventory:lista_setores')
    else:
        form = SetorForm(instance=obj)
    return render(request, 'inventory/setor_form.html', {'form': form, 'titulo': 'Editar Setor'})


@login_required
def excluir_setor(request, pk):
    oficina = get_oficina(request)
    obj = get_object_or_404(Setor, pk=pk, oficina=oficina)
    if request.method == 'POST':
        obj.delete()
        return redirect('inventory:lista_setores')
    return render(request, 'inventory/confirm_exclusao.html', {'objeto': obj, 'tipo': 'setor'})

