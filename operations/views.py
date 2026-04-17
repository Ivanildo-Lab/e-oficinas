from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from workshops.utils import get_oficina
from .models import Cliente, Veiculo, OrdemServico, ChecklistItem
from .forms import ClienteForm, VeiculoForm, ChecklistOSForm
from django.http import JsonResponse

# --- 1. GESTÃO DE CLIENTES ---
@login_required
def lista_clientes(request):
    oficina = get_oficina(request)
    clientes = Cliente.objects.filter(oficina=oficina)
    # Contador de veículos para o KPI da tela
    total_veiculos = Veiculo.objects.filter(oficina=oficina).count()
    return render(request, 'operations/clientes.html', {
        'clientes': clientes,
        'total_veiculos': total_veiculos
    })

@login_required
def novo_cliente(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save(commit=False)
            cliente.oficina = oficina
            cliente.save()
            return redirect('operations:lista_clientes')
    else:
        form = ClienteForm()
    return render(request, 'operations/form_cliente.html', {'form': form, 'titulo': 'Novo Cliente'})
# --- CRUD CLIENTE ---
@login_required
def editar_cliente(request, pk):
    oficina = get_oficina(request)
    cliente = get_object_or_404(Cliente, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            return redirect('operations:lista_clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'operations/form_cliente.html', {'form': form, 'titulo': 'Editar Cliente'})

@login_required
def excluir_cliente(request, pk):
    oficina = get_oficina(request)
    cliente = get_object_or_404(Cliente, pk=pk, oficina=oficina)
    if request.method == 'POST':
        cliente.delete()
    return redirect('operations:lista_clientes')

# --- 2. GESTÃO DE VEÍCULOS ---

@login_required
def novo_veiculo(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        # Passamos a oficina para validar o cliente no POST
        form = VeiculoForm(request.POST, oficina=oficina)
        if form.is_valid():
            veiculo = form.save(commit=False)
            veiculo.oficina = oficina
            veiculo.save()
            return redirect('operations:lista_clientes')
    else:
        # Passamos a oficina para filtrar a lista no GET
        form = VeiculoForm(oficina=oficina) 
    
    return render(request, 'operations/form_veiculo.html', {'form': form, 'titulo': 'Novo Veículo'})
 
@login_required
def editar_veiculo(request, pk):
    oficina = get_oficina(request)
    veiculo = get_object_or_404(Veiculo, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = VeiculoForm(request.POST, instance=veiculo, oficina=oficina)
        if form.is_valid():
            form.save()
            return redirect('operations:lista_clientes')
    else:
        form = VeiculoForm(instance=veiculo, oficina=oficina)
    return render(request, 'operations/form_veiculo.html', {'form': form, 'titulo': 'Editar Veículo'})

@login_required
def excluir_veiculo(request, pk):
    oficina = get_oficina(request)
    veiculo = get_object_or_404(Veiculo, pk=pk, oficina=oficina)
    if request.method == 'POST':
        veiculo.delete()
    return redirect('operations:lista_clientes')

# --- 3. GESTÃO DE ORDENS DE SERVIÇO (OS) ---
@login_required
def lista_os(request):
    oficina = get_oficina(request)
    ordens = OrdemServico.objects.filter(oficina=oficina).order_by('-data_abertura')
    return render(request, 'operations/lista_os.html', {'ordens': ordens})

# F:\HD 1tb\Dados\Projetos\Desnvolvimento com IA\e-oficinas\operations\views.py

# F:\HD 1tb\Dados\Projetos\Desnvolvimento com IA\e-oficinas\operations\views.py

@login_required
def abrir_os(request):
    oficina = get_oficina(request)
    # Lista de itens para o checklist de entrada (parte central do PDF)
    itens_entrada = [
        "Necessidade de Troca de Óleo", "Colocar água no limpador",
        "Limpar reservatório partida a frio", "Lavar o motor",
        "Trocar palhetas", "Lubrificar portas", 
        "Regular freio de mão", "Trocar alguma lâmpada"
    ]

    itens_saida = [
        "Executou as solicitações do cliente", "Executou o checklist de revisão",
        "Limpou marcas de graxa do veículo", "Preencheu etiqueta de óleo",
        "Separou peças usadas", "Testou o veículo",
        "Calibrou os pneus", "Apertou as rodas"
    ]


    if request.method == 'POST':
        form = ChecklistOSForm(request.POST, oficina=oficina)
        if form.is_valid():
            os_nova = form.save(commit=False)
            os_nova.oficina = oficina
            os_nova.save()
            os_nova.mapa_avarias_base64 = request.POST.get('mapa_avarias_base64')
            os_nova.assinatura_cliente_base64 = request.POST.get('assinatura_cliente_base64')
           
            # Grava o checklist marcado na tela
            for i, desc in enumerate(itens_entrada, start=1):
                valor = request.POST.get(f'chk_entrada_{i}', 'p')
                ChecklistItem.objects.create(os=os_nova, descricao=desc, fase='entrada', status=valor)
            
            # Grava SAÍDA (Pega os valores marcados na abertura, se houver)
            for i, desc in enumerate(itens_saida, start=1):
                valor = request.POST.get(f'chk_saida_{i}', 'p')
                ChecklistItem.objects.create(os=os_nova, descricao=desc, fase='saida', status=valor)
            
            return redirect('operations:lista_os')
    else:
        form = ChecklistOSForm(oficina=oficina)   
        
    return render(request, 'operations/abrir_os.html', {
        'form': form, 
        'oficina_logada': oficina,
        'itens_entrada': itens_entrada,
         'itens_saida': itens_saida
    })

@login_required
def buscar_dados_veiculo(request, veiculo_id):
    oficina = get_oficina(request)
    veiculo = get_object_or_404(Veiculo, id=veiculo_id, oficina=oficina)
    
    # Retornamos todos os campos para preencher o topo da OS
    data = {
        'cliente_nome': veiculo.cliente.nome,
        'cliente_tel': veiculo.cliente.telefone,
        'marca': veiculo.marca,
        'modelo': veiculo.modelo,
        'versao': veiculo.versao or '',
        'motor': veiculo.motor or '',
        'ano': veiculo.ano,
        'cor': veiculo.cor or '',
        'transmissao': veiculo.transmissao,
        'combustivel': veiculo.combustivel,
        'chassi': veiculo.chassi or '',
        'tem_abs': veiculo.tem_abs,
        'portas': veiculo.portas,
    }
    return JsonResponse(data)

@login_required
def detalhes_os(request, os_id):
    oficina = get_oficina(request)
    ordem = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    
    if request.method == 'POST':
        # Lógica para salvar a coluna de SAÍDA e Conclusão
        for item in ordem.itens_checklist.all():
            novo_status = request.POST.get(f'item_{item.id}')
            if novo_status:
                item.status = novo_status
                item.save()
        
        ordem.conclusao_tecnica = request.POST.get('conclusao_entrega')
        ordem.status = 'concluida'
        ordem.save()
        return redirect('operations:lista_os')

    return render(request, 'operations/detalhes_os.html', {'os': ordem})

@login_required
def editar_os(request, os_id):
    oficina = get_oficina(request)
    os_obj = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    
    # Listas estáticas para caso algum item novo seja necessário (opcional)
    itens_entrada_nomes = ["Necessidade de Troca de Óleo", "Colocar água no limpador", "Limpar reservatório partida a frio", "Lavar o motor", "Trocar palhetas", "Lubrificar portas", "Regular freio de mão", "Trocar alguma lâmpada"]
    itens_saida_nomes = ["Executou as solicitações", "Checklist de revisão", "Limpeza de graxa", "Etiqueta de óleo", "Peças usadas", "Testou o veículo", "Calibrou pneus", "Apertou as rodas"]

    if request.method == 'POST':
        form = ChecklistOSForm(request.POST, instance=os_obj, oficina=oficina)
        if form.is_valid():
            os_editada = form.save(commit=False)
            os_editada.mapa_avarias_base64 = request.POST.get('mapa_avarias_base64')
            os_editada.assinatura_cliente_base64 = request.POST.get('assinatura_cliente_base64')
            os_editada.save()

            # ATUALIZA OS ITENS DO CHECKLIST NA EDIÇÃO
            for item in os_obj.itens_checklist.all():
                # Tenta pegar o valor enviado (item_123), se não houver, mantém o que está
                novo_status = request.POST.get(f'item_{item.id}')
                if novo_status:
                    item.status = novo_status
                    item.save()

            return redirect('operations:lista_os')
    else:
        form = ChecklistOSForm(instance=os_obj, oficina=oficina)

    return render(request, 'operations/abrir_os.html', {
        'form': form,
        'os': os_obj,
        'oficina_logada': oficina,
        'itens_entrada': itens_entrada_nomes,
        'itens_saida': itens_saida_nomes,
        'editando': True
    })

@login_required
def excluir_os(request, os_id):
    oficina = get_oficina(request)
    os_obj = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    if request.method == 'POST':
        os_obj.delete()
    return redirect('operations:lista_os')

@login_required
def excluir_os(request, os_id):
    oficina = get_oficina(request)
    os_instancia = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    if request.method == 'POST':
        os_instancia.delete()
        return redirect('operations:lista_os')
    return render(request, 'operations/confirmar_exclusao.html', {'objeto': os_instancia})



@login_required
def buscar_dados_veiculo(request, veiculo_id):
    oficina = get_oficina(request)
    veiculo = get_object_or_404(Veiculo, id=veiculo_id, oficina=oficina)
    
    data = {
        'cliente_nome': veiculo.cliente.nome,
        'cliente_tel': veiculo.cliente.telefone,
        'marca': veiculo.marca,
        'modelo': veiculo.modelo,
        'versao': veiculo.versao or '', 
        'motor': veiculo.motor or '',
        'ano': veiculo.ano or '',       
        'cor': veiculo.cor or '',
        'transmissao': veiculo.transmissao,
        'combustivel': veiculo.combustivel,
        'chassi': veiculo.chassi or '',
        'tem_abs': veiculo.tem_abs,
        'portas': veiculo.portas,
    }
    return JsonResponse(data)

@login_required
def imprimir_os(request, os_id):
    oficina = get_oficina(request)
    os_obj = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    return render(request, 'operations/imprimir_os.html', {'os': os_obj})

@login_required
def imprimir_os(request, os_id):
    oficina = get_oficina(request)
    os_obj = get_object_or_404(OrdemServico, id=os_id, oficina=oficina)
    
    # Buscamos os itens do checklist para exibir na impressão
    itens_entrada = os_obj.itens_checklist.filter(fase='entrada')
    itens_saida = os_obj.itens_checklist.filter(fase='saida')

    return render(request, 'operations/imprimir_os.html', {
        'os': os_obj,
        'itens_entrada': itens_entrada,
        'itens_saida': itens_saida,
        'oficina': oficina
    })