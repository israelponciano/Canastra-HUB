from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from empresa.models import Empresa
from core.models import UsuarioBase
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def cadastro_empresa(request):
    if request.method =='POST':
        pass
    return render(request, 'cadastro_empresa.html')


def criar_empresa(request):
   if request.user.is_authenticated:
         messages.warning(request, f'Você ja está logado, não é possivel realizar outro cadastro.')
         return redirect('core:home')
   if request.method =='POST':
      nome = request.POST.get('txtNome')
      nomefantasia = request.POST.get('txtNomeFantasia')
      email = request.POST.get('txtEmail')
      senha = request.POST.get('txtSenha')
      tipo_empresa = request.POST.get('txtEmpresa')
      telefone = request.POST.get('txtTelefone')
      rua = request.POST.get('txtRua')
      cep = request.POST.get('txtCep')
      numero = request.POST.get('txtNumero')
      complemento = request.POST.get('txtComplemento')
      cidade = request.POST.get('txtCidade')
      estado = request.POST.get('txtEstado')
      cnpj = request.POST.get('txtCnpj')
      razao_social = request.POST.get('txtRazaoSocial')
      
      user = UsuarioBase.objects.create_user(
         email=email,
         password=senha,
         nome=nome,
         tipo='empresa'
      )
      
      empresa = Empresa(
         user = user,
         nomefantasia = nomefantasia,
         tipo_empresa = tipo_empresa,
         razao_social = razao_social,
         cnpj = cnpj,
         telefone = telefone,
         rua = rua,
         cep = cep,
         numero = numero,
         complemento = complemento,
         cidade = cidade,
         estado = estado,
      )
      empresa.save()
      messages.success(request, f'Empresa {nome} --- Cadastrada com sucesso')
      return redirect('core:home')
   return render(request, 'criar_hospede.html')