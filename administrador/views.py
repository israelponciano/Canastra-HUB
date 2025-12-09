from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from core.models import * 

# Create your views here.

@login_required
def cadastrarHub(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        nome_hub = request.POST.get('txtNomeHub')
        foto_hub = request.FILES.get("fleFotoHubs")  
        descricao_hub= request.POST.get("txtDescricaoHub")  

        hubs = Hub.objects.create(    
        nome_hub=nome_hub,
        foto_hub = foto_hub,
        descricao_hub = descricao_hub
      )

        hubs.save()
        print(hubs.nome)
        messages.success(request, ("Hub cadastrado com sucesso"))
        return redirect('administrador:cadastrarHub')

    return render(request, "cadastrar_hubs.html")

@login_required
def alterarHub(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        nome_hub = request.POST.get('txtNomeHub')
        foto_hub = request.FILES.get("fleFotoHubs")  
        descricao_hub= request.POST.get("txtDescricaoHub")

        hub = Hub.objects.get(id=id)
        hub.nome_hub = nome_hub
        if Hub.objects.filter(nome_hub=nome_hub).exclude(id=hub.id).exists():
            messages.error(request, "Essa Hub já existe")
            return redirect('administrador:gerenciarHubs')
        
        hub.foto_hub = foto_hub
        hub.descricao_hub = descricao_hub
    
                        
        if foto_hub is not None:
            hub.delete_foto_hub()
            hub.foto_hub = foto_hub

        hub.save()
        messages.success(request, "Hub Alterado com sucesso")
        return redirect('administrador:gerenciarHubs')
    
    messages.error(request, "Não foi possivel acessar")
    return redirect('administrador:gerenciarHubs')

@login_required
def gerenciarHubs(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    hubs_lista = Hub.objects.order_by('-is_active')
    return render(request, "gerenciarHubs.html", {'hubs_lista': hubs_lista})


@login_required
def deletaHubs(request, hubs_id):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    hub = Hub.objects.get(id=hubs_id)
    if hub.is_active:
        hub.is_active = False
        hub.save()
        messages.success(request, "Hub Desativado com sucesso!")
    else:
        hub.is_active = True
        hub.save()
        messages.success(request, "Hub Ativado com sucesso!")
    return redirect('administrador:gerenciarHubs')

