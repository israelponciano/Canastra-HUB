from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from core.models import * 

# Create your views here.



@login_required
def areaAdm(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    return render(request, "areaAdm.html")

@login_required
def gerenciarHubs(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    hubs_lista = Hub.objects.order_by('-isActive')
    return render(request, "gerenciarHubs.html", {'hubs_lista': hubs_lista})

@login_required
def cadastrarHub(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        nome_hub = request.POST.get('txtNomeHub')
        foto_hub = request.FILES.get("fleFotoHub")  
        descricao_hub= request.POST.get("txtDescricaoHub") 
        
        if Hub.objects.filter(nome_hub=nome_hub):
            messages.error(request, "Hub já Cadastrado no sistema")
            return redirect('administrador:gerenciarHubs') 

        hubs = Hub.objects.create(    
        nome_hub=nome_hub,
        foto_hub = foto_hub,
        descricao_hub = descricao_hub
      )

        hubs.save()
        messages.success(request, ("Hub cadastrado com sucesso"))
        return redirect('administrador:cadastrarHub')

    return render(request, "cadastrar_hubs.html")

@login_required
def alterarHub(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        id = request.POST.get('idhub')
        nome_hub = request.POST.get('txtNomeHub')
        foto_hub = request.FILES.get("fleFotoHubs")  
        descricao_hub= request.POST.get("txtDescricaoHub")

        hub = Hub.objects.get(id=id)
        if Hub.objects.filter(nome_hub=nome_hub).exclude(id=hub.id).exists():
            messages.error(request, "Essa Hub já existe")
            return redirect('administrador:gerenciarHubs')

        if nome_hub:
            hub.nome_hub = nome_hub
    
        if foto_hub:
            hub.foto_hub = foto_hub

        if descricao_hub:  
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
def deletaHub(request, hubs_id):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    hub = Hub.objects.get(id=hubs_id)
    if hub.isActive:
        hub.isActive = False
        hub.save()
        messages.success(request, "Hub Desativado com sucesso!")
    else:
        hub.isActive = True
        hub.save()
        messages.success(request, "Hub Ativado com sucesso!")
    return redirect('administrador:gerenciarHubs')


@login_required
def cadastrarNoticias(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        titulo_noticia = request.POST.get('txtTituloNoticia')
        descricao_noticia = request.POST.get('txtDescricaoNoticia')
        fonte = request.POST.get('txtFonte')
        url = request.POST.get('txtUrl')
        imagem_noticia = request.FILES.get('fleImagemNoticia')
        is_home = request.POST.get('chkIsHome') == 'on'
        
        # Verificar se já existe notícia com o mesmo título
        if Noticia.objects.filter(titulo_noticia=titulo_noticia).exists():
            messages.error(request, "Notícia com este título já cadastrada no sistema")
            return redirect('administrador:cadastrarNoticias') 

        # Criar notícia
        noticia = Noticia.objects.create(    
            titulo_noticia=titulo_noticia,
            descricao_noticia=descricao_noticia,
            fonte=fonte,
            url=url if url else None,
            imagem_noticia=imagem_noticia if imagem_noticia else None,
            isHome=is_home,
            isActive=True
        )

        noticia.save()

        messages.success(request, "Notícia cadastrada com sucesso")
        return redirect('administrador:gerenciarNoticias')

    return render(request, "cadastrar_noticias.html")


@login_required
def alterarNoticias(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    if request.method == 'POST':
        id_noticia = request.POST.get('idnoticia')
        titulo_noticia = request.POST.get('txtTituloNoticia')
        descricao_noticia = request.POST.get('txtDescricaoNoticia')
        fonte = request.POST.get('txtFonte')
        url = request.POST.get('txtUrl')
        imagem_noticia = request.FILES.get('fleImagemNoticia')

        try:
            noticia = Noticia.objects.get(id=id_noticia)
            
            # Verificar se já existe outra notícia com o mesmo título
            if Noticia.objects.filter(titulo_noticia=titulo_noticia).exclude(id=noticia.id).exists():
                messages.error(request, "Já existe outra notícia com este título")
                return redirect('administrador:gerenciarNoticias')
            
            # Atualizar campos
            noticia.titulo_noticia = titulo_noticia
            noticia.descricao_noticia = descricao_noticia
            noticia.fonte = fonte
            noticia.url = url if url else None
            
            # Atualizar imagem se fornecida
            if imagem_noticia is not None:
                # Deletar imagem antiga se existir
                if noticia.imagem_noticia:
                    noticia.imagem_noticia.delete(save=False)
                noticia.imagem_noticia = imagem_noticia

            noticia.save()
            messages.success(request, "Notícia alterada com sucesso")
            return redirect('administrador:gerenciarNoticias')
            
        except Noticia.DoesNotExist:
            messages.error(request, "Notícia não encontrada")
            return redirect('administrador:gerenciarNoticias')
    
    messages.error(request, "Método de requisição inválido")
    return redirect('administrador:gerenciarNoticias')


@login_required
def deletaNoticias(request, noticia_id):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    try:
        noticia = Noticia.objects.get(id=noticia_id)
        
        if noticia.isActive:
            noticia.isActive = False
            noticia.save()
            messages.success(request, "Notícia desativada com sucesso!")
        else:
            noticia.isActive = True
            noticia.save()
            messages.success(request, "Notícia ativada com sucesso!")
            
        return redirect('administrador:gerenciarNoticias')
        
    except Noticia.DoesNotExist:
        messages.error(request, "Notícia não encontrada")
        return redirect('administrador:gerenciarNoticias')


@login_required
def gerenciarNoticias(request):
    if (request.user.is_admin != True):
        messages.error(request, "Acesso negado")
        return redirect('core:home')
    
    noticias_lista = Noticia.objects.all().order_by('-id')
    
    context = {
        'noticias_lista': noticias_lista
    }
    
    return render(request, "gerenciarNoticias.html", context)