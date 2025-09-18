from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from empresa.models import Empresa
from core.models import UsuarioBase, Cidade, Estado
from django.contrib import messages
from django.http import JsonResponse

# Create your views here.
def cadastro_empresa(request):
    estados = Estado.objects.all().order_by('nome_estado')
    if request.method =='POST':
        pass
    return render(request, 'cadastro_empresa.html', {'estados': estados})


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
      cidade = request.POST.get('cidade')
      estado = request.POST.get('estado')
      cnpj = request.POST.get('txtCnpj')
      razao_social = request.POST.get('txtRazaoSocial')
      
      try:
            # Buscar os objetos Estado e Cidade no banco
            estado = Estado.objects.get(id=estado)
            cidade = Cidade.objects.get(id=cidade)
            
            # Criar usuário
            user = UsuarioBase.objects.create_user(
                email=email,
                password=senha,
                nome=nome,
                tipo='empresa'
            )
            
            # Criar empresa
            empresa = Empresa.objects.create(
                user=user,
                nomefantasia=nomefantasia,
                tipo_empresa=tipo_empresa,
                razao_social=razao_social,
                cnpj=cnpj,
                telefone=telefone,
                rua=rua,
                cep=cep,
                numero=numero,
                complemento=complemento,
                cidade=cidade,
                estado=estado
            )
            
            messages.success(request, 'Empresa cadastrada com sucesso!')
            return redirect('core:login')
            
      except Estado.DoesNotExist:
            messages.error(request, 'Estado inválido.')
      except Cidade.DoesNotExist:
            messages.error(request, 'Cidade inválida.')
      except Exception as e:
            messages.error(request, f'Erro ao cadastrar empresa: {str(e)}')
    
    # GET request - carregar página com estados do banco
   estados = Estado.objects.all().order_by('nome_estado')
   return render(request, 'cadastro_empresa.html', {'estados': estados})

@require_http_methods(["GET"])
def get_cidades(request):
    """View para retornar cidades via AJAX baseado no estado selecionado"""
    estado_id = request.GET.get('estado_id')
    
    if not estado_id:
        return JsonResponse({'cidades': []})
    
    try:
        # Verifica se o estado_id é um número válido
        estado_id = int(estado_id)
        
        cidades = Cidade.objects.filter(
            estado_cidade_id=estado_id
        ).order_by('nome_cidade').values('id', 'nome_cidade')
        
        cidades_data = [
            {'id': cidade['id'], 'nome': cidade['nome_cidade']} 
            for cidade in cidades
        ]
        
        return JsonResponse({
            'cidades': cidades_data,
            'total': len(cidades_data)
        })
        
    except (ValueError, TypeError):
        return JsonResponse({
            'cidades': [], 
            'error': 'ID do estado inválido'
        })
    except Exception as e:
        return JsonResponse({
            'cidades': [], 
            'error': 'Erro interno do servidor'
        })  