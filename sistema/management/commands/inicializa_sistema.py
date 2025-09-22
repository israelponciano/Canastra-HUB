from django.core.management.base import BaseCommand
from core.models import *
import json
from empresa.models import Empresa, Segmento, EmpresaSegmento

# from usuario.models import Usuario


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
                print(
                    f"Inserido estado {estado.nome_estado} com {len(cidades_objs)} cidades.")
            except Exception as e:
                print(f"Erro ao inserir {estado_data['nome']}: {e}")

        hub1 = Hub.objects.create(
            nome_hub='Café',
            descricao='Cafeculura é melhor com o pessoal da canastra'
        )
        hub2 = Hub.objects.create(
            nome_hub='Mel',
            descricao='Mel é melhor com o pessoal da canastra'
        )

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
        cidade = Cidade.objects.get(nome_cidade="Arcos")
        print("cidade", cidade.id)
        print("estado", cidade.estado_cidade.id)
        empresa = Empresa.objects.create(user=user2,
                                         nomefantasia='Roberta Cafés',
                                         tipo_empresa='Cafecultura',
                                         razao_social='naoseioqeisso',
                                         cnpj='236343',
                                         telefone='44324334243',
                                         rua='Rua jose da silva',
                                         cep='3232132132',
                                         numero='443442',
                                         complemento='embaixo da casa 11',
                                         cidade_id=cidade.id,
                                         estado_id=cidade.estado_cidade.id
                                         )
        EmpresaSegmento.objects.create(empresa=empresa, segmento=segcafe)
        EmpresaSegmento.objects.create(
            empresa=empresa, segmento=segtecnologia)

        user3 = UsuarioBase.objects.create_superuser(
            email='admin@teste',
            password='123',
            nome='admin',
            tipo='admin'
        )

        print("User-1", user.email, usuario.curso)
        print("User-2", user2.email, empresa.segmentos)
        print("User-3", user3.email, user3.is_admin)
        print("hub1", hub1.nome_hub)
        print("hub2", hub2.nome_hub)
