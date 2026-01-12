from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
import json
from pathlib import Path
from empresa.models import *
from vagas.models import *
from core.models import * 


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

        caminho_hub1_imagem = settings.BASE_DIR/'media'/'fotos_hub'/'agro_hub.jpg'
        with open(caminho_hub1_imagem, 'rb') as f:
            hub1 = Hub.objects.create(
                nome_hub='Agro',
                descricao_hub='Agro é melhor com o pessoal da canastra',
                foto_hub = File(f, name=caminho_hub1_imagem.name) # Use o wrapper File
            )        
        # hub2 = Hub.objects.create(
        #     nome_hub='Apicultura',
        #     descricao_hub='Apicultura é melhor com o pessoal da canastra'
        # )
        # hub3 = Hub.objects.create(
        #     nome_hub='Calçados',
        #     descricao_hub='Calçados é melhor com o pessoal da canastra'
        # )

        caminho_hub4_imagem = settings.BASE_DIR/'media'/'fotos_hub'/'milho_hub.jpg'
        with open(caminho_hub4_imagem, 'rb') as f:
            hub4 = Hub.objects.create(
                nome_hub='Milho',
                descricao_hub='Milho é melhor com o pessoal da canastra',
                foto_hub = File(f, name=caminho_hub4_imagem.name)
            )
        
        # hub5 = Hub.objects.create(
        #     nome_hub='Queijo',
        #     descricao_hub='Queijo é melhor com o pessoal da canastra'
        # )
        caminho_hub6_imagem = settings.BASE_DIR/'media'/'fotos_hub'/'graos_hub.jpg'
        with open(caminho_hub6_imagem, 'rb') as f:
            hub6 = Hub.objects.create(
                nome_hub='Grãos',
                descricao_hub='Grãos é melhor com o pessoal da canastra',
                foto_hub = File(f, name=caminho_hub6_imagem.name) 
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

        caminho_agro_noticia_1 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_agro_1.png'
        with open(caminho_agro_noticia_1, 'rb') as f:
            noticia_agro_1 = Noticia.objects.create(
                titulo_noticia = 'Minas Gerais lidera ranking dos melhores cafés do Brasil em 2025',
                descricao_noticia = 'Produtores mineiros conquistaram as três categorias do Cup of Excellence, o mais prestigiado concurso de qualidade do setor.',
                fonte = 'Paloma Santos',
                url = 'https://agro.estadao.com.br/agricultura/minas-gerais-lidera-ranking-dos-melhores-cafes-do-brasil-em-2025',
                isActive = True,
                isHome = True,
                imagem_noticia = File(f, name=caminho_agro_noticia_1.name) # Use o wrapper File
            )
        noticia_agro_1_hub = NoticiaHub.objects.create(
            noticia = noticia_agro_1,
            hub = hub1
        )

        caminho_agro_noticia_2 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_agro_2.png'
        with open(caminho_agro_noticia_2, 'rb') as f:
            noticia_agro_2 = Noticia.objects.create(
                titulo_noticia = 'O futuro sustentável do agronegócio passa pela boa gestão',
                descricao_noticia = 'No Brasil, anualmente, os dados econômicos demonstram que o agro permanece no centro da economia.',
                fonte = 'André Paranhos*',
                url = 'https://globorural.globo.com/google/amp/opiniao/vozes-do-agro/noticia/2025/11/o-futuro-sustentavel-do-agronegocio-passa-pela-boa-gestao.ghtml',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_agro_noticia_2.name) # Use o wrapper File
            )
        noticia_agro_2_hub = NoticiaHub.objects.create(
            noticia = noticia_agro_2,
            hub = hub1
        )

        caminho_agro_noticia_3 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_agro_3.png'
        with open(caminho_agro_noticia_3, 'rb') as f:
            noticia_agro_3 = Noticia.objects.create(
                titulo_noticia = 'MG lança certificação para produtores que adotam agricultura regenerativa',
                descricao_noticia = 'Reconhecimento integra o programa Certifica Minas e estará disponível a partir de 2026.',
                fonte = 'Redação Agro Estadão',
                url = 'https://agro.estadao.com.br/sustentabilidade/mg-lanca-certificacao-para-produtores-que-adotam-agricultura-regenerativa' \
                '',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_agro_noticia_3.name) # Use o wrapper File
            )
        noticia_agro_3_hub = NoticiaHub.objects.create(
            noticia = noticia_agro_3,
            hub = hub1
        )
            

        caminho_grao_noticia_1 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'graos'/'noticia_graos1.png'
        with open(caminho_grao_noticia_1, 'rb') as f:
            noticia1 = Noticia.objects.create(
                titulo_noticia = 'A jornada dos grãos pelo Tapajós rumo ao mercado externo',
                descricao_noticia = 'Reportagem viajou em empurrador e acompanhou transporte de grãos pela hidrovia',
                fonte = 'Raphael Salomão',
                url = 'https://globorural.globo.com/google/amp/especiais/caminhos-da-safra/noticia/2025/11/a-jornada-dos-graos-pelo-tapajos-rumo-ao-mercado-externo.ghtml',
                isActive = True,
                isHome = True,
                imagem_noticia = File(f, name=caminho_grao_noticia_1.name) # Use o wrapper File
            )
        noticia_grao_1_hub = NoticiaHub.objects.create(
            noticia = noticia1,
            hub = hub6
        )

        caminho_grao_noticia2 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'graos'/'noticia_graos2.png'
        with open(caminho_grao_noticia2, 'rb') as f:
            noticia2 = Noticia.objects.create(
                titulo_noticia = 'Feijão: Exportações seguem registrando desempenho recorde',
                descricao_noticia = 'As exportações brasileiras de feijão seguem registrando um desempenho recorde, tanto no volume mensal quanto no acumulado de 12 meses.',
                fonte = 'Sociedade Nacional de Agricultura',
                url = 'https://sna.agr.br/feijao-exportacoes-seguem-registrando-desempenho-recorde/',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_grao_noticia2.name) # Use o wrapper File
            )
        noticia_grao_2_hub = NoticiaHub.objects.create(
            noticia = noticia2,
            hub = hub6
        )

        caminho_grao_noticia3 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'graos'/'noticia_graos3.png'
        with open(caminho_grao_noticia3, 'rb') as f:
            noticia_grao_3 = Noticia.objects.create(
                titulo_noticia = 'SIC 2025 destaca inovação e sustentabilidade, reforçando protagonismo de Minas Gerais na cafeicultura mundial',
                descricao_noticia = 'Aconteceu na última quarta-feira (05/11), no Expominas, em Belo Horizonte, a 13ª SIC (Semana Internacional do Café).',
                fonte = 'Hannah Andrade',
                url = 'https://amirt.com.br/sic-2025-destaca-inovacao-e-sustentabilidade-reforcando-protagonismo-de-minas-gerais-na-cafeicultura-mundial/',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_grao_noticia3.name) # Use o wrapper File
            )
        noticia_grao_3_hub = NoticiaHub.objects.create(
            noticia = noticia_grao_3,
            hub = hub6
        )

        caminho_milho_noticia_1 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_milho_1.png'
        with open(caminho_milho_noticia_1, 'rb') as f:
            noticia_milho_1 = Noticia.objects.create(
                titulo_noticia = 'SIC 2025 destaca inovação e sustentabilidade, reforçando protagonismo de Minas Gerais na cafeicultura mundial',
                descricao_noticia = 'Aconteceu na última quarta-feira (05/11), no Expominas, em Belo Horizonte, a 13ª SIC (Semana Internacional do Café).',
                fonte = 'Hannah Andrade',
                url = 'https://g1.globo.com/sp/sorocaba-jundiai/nosso-campo/noticia/2025/11/09/plantio-do-milho-segunda-safra-avanca-com-chegada-de-chuvas.ghtml',
                isActive = True,
                isHome = True,
                imagem_noticia = File(f, name=caminho_milho_noticia_1.name) # Use o wrapper File
            )
        noticia_milho_1_hub = NoticiaHub.objects.create(
            noticia = noticia_milho_1,
            hub = hub4
        )

        caminho_milho_noticia_2 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_milho_2.png'
        with open(caminho_milho_noticia_2, 'rb') as f:
            noticia_milho_2 = Noticia.objects.create(
                titulo_noticia = 'Levantamento da Emater-MG aponta municípios campeões na produção de milho e soja',
                descricao_noticia = 'Triângulo e Noroeste de Minas dominam a lista na safra 2024/2025.',
                fonte = 'Roberto Meokare',
                url = 'https://www.otempo.com.br/canal-o-tempo/podcasts/agrotempo/2025/9/8/levantamento-da-emater-mg-aponta-municipios-campeoes-na-producao-de-milho-e-soja',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_milho_noticia_2.name) # Use o wrapper File
            )
        noticia_milho_2_hub = NoticiaHub.objects.create(
            noticia = noticia_milho_2,
            hub = hub4
        )

        caminho_milho_noticia_3 = settings.BASE_DIR/'resources'/'static'/'img'/'hubs'/'noticia_milho_3.png'
        with open(caminho_milho_noticia_3, 'rb') as f:
            noticia_milho_3 = Noticia.objects.create(
                titulo_noticia = 'Santa Catarina registra recuperação na produção de milho em 2025',
                descricao_noticia = 'Depois de anos consecutivos de queda na produção, a safra de milho em Santa Catarina começa a dar sinais de recuperação.',
                fonte = 'NDTV',
                url = 'https://ndmais.com.br/video/santa-catarina-registra-recuperacao-na-producao-de-milho-em-2025/',
                isActive = True,
                isHome = False,
                imagem_noticia = File(f, name=caminho_milho_noticia_3.name) # Use o wrapper File
            )
        noticia_milho_1_hub = NoticiaHub.objects.create(
            noticia = noticia_milho_3,
            hub = hub4
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
        # print("hub2", hub2.nome_hub)
        # print("hub3", hub3.nome_hub)
        print("hub4", hub4.nome_hub)
        # print("hub5", hub5.nome_hub)
        print("hub6", hub6.nome_hub)
        print("vaga1", vaga1.cargo_vaga)
        print("vaga2", vaga2.cargo_vaga)
        print("vaga3", vaga3.cargo_vaga)