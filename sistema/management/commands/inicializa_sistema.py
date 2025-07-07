from django.core.management.base import BaseCommand
from core.models import Usuario, UsuarioBase
from empresa.models import Empresa
#from usuario.models import Usuario

class Command(BaseCommand):
   help = "Inicializa o sistema com dados padrão"

   def handle(self, *args, **options):
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
      empresa = Empresa.objects.create(user=user2, segmento="Piru")

      user3 = UsuarioBase.objects.create_superuser(
         email='admin@teste',
         password='123',
         nome='admin',
         tipo='admin'
      )

      print("User-1", user.email, usuario.curso)
      print("User-2", user2.email, empresa.segmento)
      print("User-3", user3.email, user3.is_admin)
   