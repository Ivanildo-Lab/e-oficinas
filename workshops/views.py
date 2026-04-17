from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .utils import get_oficina
from .models import Mecanico
from .forms import MecanicoForm
from operations.models import OrdemServico, Veiculo

# --- DASHBOARD PRINCIPAL ---
@login_required(login_url='login')
def dashboard(request):
    oficina = get_oficina(request)
    
    # Dados Reais filtrados pela oficina
    ultimas_os = OrdemServico.objects.filter(oficina=oficina).order_by('-data_abertura')[:10]
    total_os_abertas = OrdemServico.objects.filter(oficina=oficina, status='aberta').count()
    total_veiculos = Veiculo.objects.filter(oficina=oficina).count()
    
    context = {
        'oficina_logada': oficina,
        'ultimas_os': ultimas_os,
        'total_os_abertas': total_os_abertas,
        'total_veiculos': total_veiculos,
    }
    return render(request, 'workshops/dashboard.html', context)

# --- GESTÃO DE MECÂNICOS ---
@login_required
def lista_mecanicos(request):
    oficina = get_oficina(request)
    mecanicos = Mecanico.objects.filter(oficina=oficina)
    return render(request, 'workshops/mecanico_list.html', {
        'mecanicos': mecanicos,
        'oficina_logada': oficina
    })

@login_required
def novo_mecanico(request):
    oficina = get_oficina(request)
    if request.method == 'POST':
        form = MecanicoForm(request.POST)
        if form.is_valid():
            mecanico = form.save(commit=False)
            mecanico.oficina = oficina
            mecanico.save()
            return redirect('workshops:lista_mecanicos')
    else:
        form = MecanicoForm()
    return render(request, 'workshops/mecanico_form.html', {'form': form, 'titulo': 'Novo Mecânico'})

@login_required
def editar_mecanico(request, pk):
    oficina = get_oficina(request)
    mecanico = get_object_or_404(Mecanico, pk=pk, oficina=oficina)
    if request.method == 'POST':
        form = MecanicoForm(request.POST, instance=mecanico)
        if form.is_valid():
            form.save()
            return redirect('workshops:lista_mecanicos')
    else:
        form = MecanicoForm(instance=mecanico)
    return render(request, 'workshops/mecanico_form.html', {'form': form, 'titulo': 'Editar Mecânico'})

@login_required
def excluir_mecanico(request, pk):
    oficina = get_oficina(request)
    mecanico = get_object_or_404(Mecanico, pk=pk, oficina=oficina)
    if request.method == 'POST':
        mecanico.delete()
    return redirect('workshops:lista_mecanicos')