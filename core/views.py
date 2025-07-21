from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from core.models import UsuarioBase

# Create your views here.
def home(request):
    
    return render(request, 'home.html')

def login(request):
    print("CHEGOU LOGIN")
    if request.method == 'POST':
        print("Chegou POST")
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')
        # perfil_id = request.POST.get('slcPerfil')

        print(email, senha)

        usuario = authenticate(request, username=email, password=senha)
        print(usuario)
        # if usuario is not None and perfil_id:
        if usuario is not None:
            # perfis_usuario = usuario.perfis.filter(id=perfil_id)
            # if perfis_usuario.exists():
                #limpa as sessoes do usuario
                request.session.flush()
                #cria a sessao do usuario
                auth_login(request, usuario)
                
                request.session['is_login'] = False
                if usuario.is_admin:
                    request.session['is_admin'] = usuario.is_admin
                # print(request.session['is_admin'])
                request.session['perfil'] = usuario.tipo
                request.session['id_atual'] = usuario.id
                request.session['email_atual'] = usuario.email                    
                # request.session['perfil_atual'] = perfis_usuario.first().nome                
                # request.session['perfis'] = list(usuario.perfis.values_list('nome', flat=True))
                # print(request.session['perfis'])
                
                #configura sessao para expirar em 4 horas
                request.session.set_expiry(14400)
                
                messages.success(request, 'Login realizado com sucesso!')
                
                #no futuro iremos separar em diferentes paginas
                # if request.session.get('perfil_atual') in {'Administrador', 'Funcionario'}:
                return redirect('core:home')
                
            # else:
            #     messages.error(request, 'Perfil inválido para este usuário.')
        else:
            print("Usuario ou senha invalidos")
            messages.error(request, 'Usuário ou senha inválidos.')
            
    return render(request, 'login.html')

def logout(request):
    #limpa a sessao ao deslogar
    request.session.flush()
    auth_logout(request)
    
    messages.success(request, 'Logout realizado com sucesso.')
    return redirect('core:home')