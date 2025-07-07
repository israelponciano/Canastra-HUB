from django.core.management.base import BaseCommand
from core.models import Cidade, Estado
import json

class Command(BaseCommand):
   help = "Inicializa o sistema com dados padrão"

   def handle(self, *args, **options):
      with open('resources/static/json/estados-cidades.json', 'r', encoding='utf-8') as f:
         dados = json.load(f)
      
      for estado_data in dados['estados']:
         try:
            estado = Estado.objects.create(
               nome_estado=estado_data['nome'],
               sigla_estado=estado_data['sigla']
            )
            cidades_objs = []
            for nome_cidade in estado_data['cidades']:
               cidade = Cidade(
                  nome_cidade=nome_cidade,
                  estado_cidade=estado
               )
               cidades_objs.append(cidade)
            Cidade.objects.bulk_create(cidades_objs)
            print(f"Inserido estado {estado.nome_estado} com {len(cidades_objs)} cidades.")
         except Exception as e:
            print(f"Erro ao inserir {estado_data['nome']}: {e}")
      