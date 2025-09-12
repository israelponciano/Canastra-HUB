from django.core.management.base import BaseCommand
from core.models import Usuario, UsuarioBase, Cidade, Estado, Hub
from empresa.models import Empresa, Segmento, EmpresaSegmento
#from usuario.models import Usuario

class Command(BaseCommand):
   help = "Inicializa o sistema com dados padrão"

   def handle(self, *args, **options):
      
      segcafe = Segmento.objects.create(nome_segmento="Cafe")
      segtecnologia = Segmento.objects.create(nome_segmento="Tecnologia")
      
      user = UsuarioBase.objects.create_user(
         email='usuario@teste',
         password='123',
         nome='Cleiton',
         tipo='usuario'
      )
      usuario = Usuario.objects.create(user=user, curso='Engenharia',)
      
      user2 = UsuarioBase.objects.create_user(
         email='empresa@teste',
         password='123',
         nome='Roberta Cafes',
         tipo='empresa'
      )
      empresa = Empresa.objects.create(user=user2,
      nomefantasia = 'Roberta Cafés',
      tipo_empresa = 'Cafeculura',
      razao_social = 'naoseioqeisso',
      cnpj = '236343',
      telefone = '44324334243',
      rua = 'Rua jose da silva',
      cep = '3232132132',
      numero = '443442',
      complemento = 'embaixo da casa 11',
      cidade_id = 1426,
      estado_id = 11
      )
      EmpresaSegmento.objects.create(empresa_id=empresa, segmento_id=segcafe)
      EmpresaSegmento.objects.create(empresa_id=empresa, segmento_id=segtecnologia)
      
      user3 = UsuarioBase.objects.create_superuser(
         email='admin@teste',
         password='123',
         nome='admin',
         tipo='admin'
      )

      hub1 = Hub.objects.create(
      nome_hub = 'Café',
      descricao = 'Cafeculura é melhor com o pessoal da canastra'
      )
      hub2 = Hub.objects.create(
      nome_hub = 'Mel',
      descricao = 'Mel é melhor com o pessoal da canastra'
      )
      
      print("User-1", user.email, usuario.curso)
      print("User-2", user2.email, empresa.segmentos)
      print("User-3", user3.email, user3.is_admin)
      print("hub1", hub1.nome_hub)
      print("hub2", hub2.nome_hub)
   