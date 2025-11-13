from django.core.management.base import BaseCommand
from core.models import *
import json
from empresa.models import Empresa
from vagas.models import Vagas

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
            nome_hub='Agro',
            descricao='Agro é melhor com o pessoal da canastra'
        )
        hub2 = Hub.objects.create(
            nome_hub='Apicultura',
            descricao='Apicultura é melhor com o pessoal da canastra'
        )
        hub3 = Hub.objects.create(
            nome_hub='Calçados',
            descricao='Calçados é melhor com o pessoal da canastra'
        )

        hub4 = Hub.objects.create(
            nome_hub='Milho',
            descricao='Milho é melhor com o pessoal da canastra'
        )
        
        hub5 = Hub.objects.create(
            nome_hub='Queijo',
            descricao='Queijo é melhor com o pessoal da canastra'
        )
        
        hub6 = Hub.objects.create(
            nome_hub='Grãos',
            descricao='Grãos é melhor com o pessoal da canastra'
        )
        
        user = UsuarioBase.objects.create_user(
            email='usuario@teste',
            password='123',
            nome='Cleiton Romario Santos',
            tipo='usuario'
        )
        cidade = Cidade.objects.get(nome_cidade="Arcos")
        usuario = Usuario.objects.create(
            user=user,
            nome_social='Cleiton',
            data_nascimento='2002-07-11',
            genero='masculino',
            estado_civil='solteiro',
            nacionalidade='brasileiro',
            telefone='(37) 99838-1976',
            cep='398000000',
            rua='rua teste',
            numero='981',
            bairro='teste',
            cidade_id=cidade.id,
            estado_id=cidade.estado_cidade.id,
            complemento='complemtento blablabla',
            pretensao_salarial=15.00
        )

        user2 = UsuarioBase.objects.create_user(
            email='empresa@teste',
            password='123',
            nome='Roberta Cafes',
            tipo='empresa'
        )

        empresa = Empresa.objects.create(user=user2,
                                         nomefantasia='Roberta Cafés',
                                         tipo_empresa='Cafecultura',
                                         razao_social='naoseioqeisso',
                                         cnpj='11111111111111',
                                         telefone='44324334243',
                                         rua='Rua jose da silva',
                                         cep='3232132132',
                                         numero='443442',
                                         complemento='embaixo da casa 11',
                                         cidade_id=cidade.id,
                                         estado_id=cidade.estado_cidade.id,
                                         segmento="cafe"
                                         )
        user3 = UsuarioBase.objects.create_superuser(
            email='admin@teste',
            password='123',
            nome='admin',
            tipo='admin'
        )

        vaga1 = Vagas.objects.create(
            cargo_vaga='Operador de Máquinas Agrícolas',
            descricao_vaga='Responsável por operar tratores, colheitadeiras e outros equipamentos agrícolas durante o plantio e a colheita.',
            requisito_vaga='Experiência comprovada na operação de máquinas agrícolas e conhecimento básico em manutenção preventiva.',
            local='Fazenda Primavera',
            data_publicacao='2025-11-03 02:50:00 -03',
            data_atualizacao='2025-11-03 02:50:00 -03',
            status='ativa',
            empresa=empresa
        )

        vaga2 = Vagas.objects.create(
            cargo_vaga='Desenvolvedor Júnior',
            descricao_vaga='Estamos em busca de um Desenvolvedor Júnior motivado e comprometido para integrar nossa equipe de tecnologia. ',
            requisito_vaga='Conhecimento básico em linguagens de programação como Python, JavaScript ou Java. ',
            local='Home Office',
            data_publicacao='2025-11-03 02:50:00 -03',
            data_atualizacao='2025-11-03 02:50:00 -03',
            status='ativa',
            empresa=empresa
        )

        vaga3 = Vagas.objects.create(
            cargo_vaga='Apicultor',
            descricao_vaga='Estamos em busca de um profissional dedicado para atuar no manejo de colmeias, extração de mel e cuidado com abelhas em fazenda de produção apícola. ',
            requisito_vaga='Experiência com manejo de abelhas ou interesse em aprender sobre apicultura.',
            local='Fazenda Mel da Canastra',
            data_publicacao='2025-11-03 02:50:00 -03',
            data_atualizacao='2025-11-03 02:50:00 -03',
            status='ativa',
            empresa=empresa
        )
        
        print("User-1", user.email, usuario)
        print("User-2", user2.email, empresa.segmento)
        print("User-3", user3.email, user3.is_admin)
        print("hub1", hub1.nome_hub)
        print("hub2", hub2.nome_hub)
        print("hub3", hub3.nome_hub)
        print("hub4", hub4.nome_hub)
        print("hub5", hub5.nome_hub)
        print("hub6", hub6.nome_hub)
        print("vaga1", vaga1.cargo_vaga)
        print("vaga2", vaga2.cargo_vaga)
        print("vaga3", vaga3.cargo_vaga)