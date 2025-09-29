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

def cadastro(request):
    
    return render(request, 'cadastro.html')

def cadastro_usuario(request):
    
    return render(request, 'cadastro_usuario.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('txtEmail')
        senha = request.POST.get('txtSenha')

        print(email, senha)

        usuario = authenticate(request, username=email, password=senha)
        print(usuario)
        
        if usuario is not None:
            request.session.flush()
            #cria a sessao do usuario
            auth_login(request, usuario)
                
            request.session['is_login'] = False
            if usuario.foto and hasattr(usuario.foto, "url"):
                foto = usuario.foto.url
            else:
                foto = None
            if usuario.is_admin:
                request.session['is_admin'] = usuario.is_admin
            request.session['nome'] = usuario.nome
            request.session['foto'] = foto
            request.session['perfil'] = usuario.tipo
            request.session['id_atual'] = usuario.id
            request.session['email_atual'] = usuario.email
            
            #configura sessao para expirar em 4 horas
            request.session.set_expiry(14400)
            
            messages.success(request, 'Login realizado com sucesso!')
            return redirect('core:home')
        
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