from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from empresa.models import Empresa
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def cadastro_empresa(request):
    if request.method =='POST':
        pass
    return render(request, 'cadastro_empresa.html')

def criar_hospede(request):
   if request.method =='POST':
      nome = request.POST.get('txtNome')
      empresa = request.POST.get('txtEmpresa')
      telefone = request.POST.get('txtTelefone')
      cpf = request.POST.get('txtCpf')

      empresa = Empresa(
         nome=nome,
         
      )
      empresa.save()
      messages.success(request, f'{nome} --- Cadastro feito com sucesso')
      return redirect('core: ')
   return render(request, 'criar_hospede.html')