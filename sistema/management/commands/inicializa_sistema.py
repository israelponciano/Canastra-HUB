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
                print(f"Inserido estado {estado.nome_estado} com {len(cidades_objs)} cidades.")
            except Exception as e:
                print(f"Erro ao inserir {estado_data['nome']}: {e}")

        # --- Hubs ---
        caminho_hub1_imagem = settings.BASE_DIR / 'media' / 'fotos_hub' / 'agro_hub.jpg'
        with open(caminho_hub1_imagem, 'rb') as f:
            hub1 = Hub.objects.create(
                nome_hub='Agro',
                descricao_hub='Agro é melhor com o pessoal da canastra',
                foto_hub=File(f, name=caminho_hub1_imagem.name)
            )

        caminho_hub4_imagem = settings.BASE_DIR / 'media' / 'fotos_hub' / 'milho_hub.jpg'
        with open(caminho_hub4_imagem, 'rb') as f:
            hub4 = Hub.objects.create(
                nome_hub='Milho',
                descricao_hub='Milho é melhor com o pessoal da canastra',
                foto_hub=File(f, name=caminho_hub4_imagem.name)
            )

        caminho_hub6_imagem = settings.BASE_DIR / 'media' / 'fotos_hub' / 'graos_hub.jpg'
        with open(caminho_hub6_imagem, 'rb') as f:
            hub6 = Hub.objects.create(
                nome_hub='Grãos',
                descricao_hub='Grãos é melhor com o pessoal da canastra',
                foto_hub=File(f, name=caminho_hub6_imagem.name)
            )

        # --- Empresa e Admin ---
        cidade = Cidade.objects.get(nome_cidade="Arcos")

        user_empresa = UsuarioBase.objects.create_user(
            email='empresa@teste',
            password='123',
            nome='Roberta Cafes',
            tipo='empresa'
        )
        empresa = Empresa.objects.create(
            user=user_empresa,
            nomefantasia='Roberta Cafés',
            tipo_empresa='Cafecultura',
            razao_social='Roberta Cafés Ltda',
            cnpj='11111111111111',
            telefone='(37) 3322-4433',
            rua='Rua José da Silva',
            cep='39800000',
            numero='443',
            complemento='Sala 11',
            cidade=cidade,
            estado=cidade.estado_cidade,
            segmento='cafe'
        )

        user_admin = UsuarioBase.objects.create_superuser(
            email='admin@teste',
            password='123',
            nome='admin',
            tipo='admin'
        )

        # --- Notícias Agro ---
        caminho_agro_noticia_1 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_agro_1.png'
        with open(caminho_agro_noticia_1, 'rb') as f:
            noticia_agro_1 = Noticia.objects.create(
                titulo_noticia='Minas Gerais lidera ranking dos melhores cafés do Brasil em 2025',
                descricao_noticia='Produtores mineiros conquistaram as três categorias do Cup of Excellence, o mais prestigiado concurso de qualidade do setor.',
                fonte='Paloma Santos',
                url='https://agro.estadao.com.br/agricultura/minas-gerais-lidera-ranking-dos-melhores-cafes-do-brasil-em-2025',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_agro_noticia_1.name)
            )
        NoticiaHub.objects.create(noticia=noticia_agro_1, hub=hub1)

        caminho_agro_noticia_2 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_agro_2.jpeg'
        with open(caminho_agro_noticia_2, 'rb') as f:
            noticia_agro_2 = Noticia.objects.create(
                titulo_noticia='O futuro sustentável do agronegócio passa pela boa gestão',
                descricao_noticia='No Brasil, anualmente, os dados econômicos demonstram que o agro permanece no centro da economia.',
                fonte='André Paranhos',
                url='https://globorural.globo.com/google/amp/opiniao/vozes-do-agro/noticia/2025/11/o-futuro-sustentavel-do-agronegocio-passa-pela-boa-gestao.ghtml',
                isActive=True,
                isHome=True,
                imagem_noticia=File(f, name=caminho_agro_noticia_2.name)
            )
        NoticiaHub.objects.create(noticia=noticia_agro_2, hub=hub1)

        caminho_agro_noticia_3 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_agro_3.png'
        with open(caminho_agro_noticia_3, 'rb') as f:
            noticia_agro_3 = Noticia.objects.create(
                titulo_noticia='MG lança certificação para produtores que adotam agricultura regenerativa',
                descricao_noticia='Reconhecimento integra o programa Certifica Minas e estará disponível a partir de 2026.',
                fonte='Redação Agro Estadão',
                url='https://agro.estadao.com.br/sustentabilidade/mg-lanca-certificacao-para-produtores-que-adotam-agricultura-regenerativa',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_agro_noticia_3.name)
            )
        NoticiaHub.objects.create(noticia=noticia_agro_3, hub=hub1)

        # --- Notícias Grãos ---
        caminho_grao_noticia_1 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'graos' / 'noticia_graos1.png'
        with open(caminho_grao_noticia_1, 'rb') as f:
            noticia_grao_1 = Noticia.objects.create(
                titulo_noticia='A jornada dos grãos pelo Tapajós rumo ao mercado externo',
                descricao_noticia='Reportagem viajou em empurrador e acompanhou transporte de grãos pela hidrovia',
                fonte='Raphael Salomão',
                url='https://globorural.globo.com/google/amp/especiais/caminhos-da-safra/noticia/2025/11/a-jornada-dos-graos-pelo-tapajos-rumo-ao-mercado-externo.ghtml',
                isActive=True,
                isHome=True,
                imagem_noticia=File(f, name=caminho_grao_noticia_1.name)
            )
        NoticiaHub.objects.create(noticia=noticia_grao_1, hub=hub6)

        caminho_grao_noticia_2 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'graos' / 'noticia_graos2.png'
        with open(caminho_grao_noticia_2, 'rb') as f:
            noticia_grao_2 = Noticia.objects.create(
                titulo_noticia='Feijão: Exportações seguem registrando desempenho recorde',
                descricao_noticia='As exportações brasileiras de feijão seguem registrando um desempenho recorde, tanto no volume mensal quanto no acumulado de 12 meses.',
                fonte='Sociedade Nacional de Agricultura',
                url='https://sna.agr.br/feijao-exportacoes-seguem-registrando-desempenho-recorde/',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_grao_noticia_2.name)
            )
        NoticiaHub.objects.create(noticia=noticia_grao_2, hub=hub6)

        caminho_grao_noticia_3 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'graos' / 'noticia_graos3.png'
        with open(caminho_grao_noticia_3, 'rb') as f:
            noticia_grao_3 = Noticia.objects.create(
                titulo_noticia='SIC 2025 destaca inovação e sustentabilidade na cafeicultura mundial',
                descricao_noticia='Aconteceu na última quarta-feira (05/11), no Expominas, em Belo Horizonte, a 13ª SIC (Semana Internacional do Café).',
                fonte='Hannah Andrade',
                url='https://amirt.com.br/sic-2025-destaca-inovacao-e-sustentabilidade-reforcando-protagonismo-de-minas-gerais-na-cafeicultura-mundial/',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_grao_noticia_3.name)
            )
        NoticiaHub.objects.create(noticia=noticia_grao_3, hub=hub6)

        # --- Notícias Milho ---
        caminho_milho_noticia_1 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_milho_1.png'
        with open(caminho_milho_noticia_1, 'rb') as f:
            noticia_milho_1 = Noticia.objects.create(
                titulo_noticia='Plantio do milho segunda safra avança com chegada de chuvas',
                descricao_noticia='Condições climáticas favoráveis impulsionam o avanço do plantio da segunda safra de milho no Centro-Oeste.',
                fonte='G1 Sorocaba',
                url='https://g1.globo.com/sp/sorocaba-jundiai/nosso-campo/noticia/2025/11/09/plantio-do-milho-segunda-safra-avanca-com-chegada-de-chuvas.ghtml',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_milho_noticia_1.name)
            )
        NoticiaHub.objects.create(noticia=noticia_milho_1, hub=hub4)

        caminho_milho_noticia_2 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_milho_2.png'
        with open(caminho_milho_noticia_2, 'rb') as f:
            noticia_milho_2 = Noticia.objects.create(
                titulo_noticia='Levantamento da Emater-MG aponta municípios campeões na produção de milho e soja',
                descricao_noticia='Triângulo e Noroeste de Minas dominam a lista na safra 2024/2025.',
                fonte='Roberto Meokare',
                url='https://www.otempo.com.br/canal-o-tempo/podcasts/agrotempo/2025/9/8/levantamento-da-emater-mg-aponta-municipios-campeoes-na-producao-de-milho-e-soja',
                isActive=True,
                isHome=True,
                imagem_noticia=File(f, name=caminho_milho_noticia_2.name)
            )
        NoticiaHub.objects.create(noticia=noticia_milho_2, hub=hub4)

        caminho_milho_noticia_3 = settings.BASE_DIR / 'resources' / 'static' / 'img' / 'hubs' / 'noticia_milho_3.png'
        with open(caminho_milho_noticia_3, 'rb') as f:
            noticia_milho_3 = Noticia.objects.create(
                titulo_noticia='Santa Catarina registra recuperação na produção de milho em 2025',
                descricao_noticia='Depois de anos consecutivos de queda na produção, a safra de milho em Santa Catarina começa a dar sinais de recuperação.',
                fonte='NDTV',
                url='https://ndmais.com.br/video/santa-catarina-registra-recuperacao-na-producao-de-milho-em-2025/',
                isActive=True,
                isHome=False,
                imagem_noticia=File(f, name=caminho_milho_noticia_3.name)
            )
        NoticiaHub.objects.create(noticia=noticia_milho_3, hub=hub4)

        # --- Vagas com campos de matching ---
        vaga1 = Vagas.objects.create(
            cargo_vaga='Operador de Máquinas Agrícolas',
            descricao_vaga='Responsável por operar tratores, colheitadeiras e outros equipamentos agrícolas durante o plantio e a colheita.',
            requisito_vaga='Experiência comprovada na operação de máquinas agrícolas e conhecimento básico em manutenção preventiva.',
            local='Fazenda Primavera',
            status='ativa',
            anos_experiencia_req=2.0,
            nivel_formacao_req=3,  # Ensino Médio Completo
            empresa=empresa
        )

        vaga2 = Vagas.objects.create(
            cargo_vaga='Desenvolvedor Júnior',
            descricao_vaga='Estamos em busca de um Desenvolvedor Júnior motivado e comprometido para integrar nossa equipe de tecnologia.',
            requisito_vaga='Conhecimento básico em linguagens de programação como Python, JavaScript ou Java.',
            local='Home Office',
            status='ativa',
            anos_experiencia_req=0.0,
            nivel_formacao_req=5,  # Ensino Superior Incompleto
            empresa=empresa
        )
        CursoVaga.objects.create(vaga=vaga2, curso='Ciência da Computação')
        CursoVaga.objects.create(vaga=vaga2, curso='Sistemas de Informação')

        vaga3 = Vagas.objects.create(
            cargo_vaga='Apicultor',
            descricao_vaga='Estamos em busca de um profissional dedicado para atuar no manejo de colmeias, extração de mel e cuidado com abelhas em fazenda de produção apícola.',
            requisito_vaga='Experiência com manejo de abelhas ou interesse em aprender sobre apicultura. Disposição para trabalho ao ar livre.',
            local='Fazenda Mel da Canastra',
            status='ativa',
            anos_experiencia_req=1.0,
            nivel_formacao_req=3,  # Ensino Médio Completo
            empresa=empresa
        )

        # --- Usuário 1: perfil agrícola ---
        user1 = UsuarioBase.objects.create_user(
            email='usuario@teste',
            password='123',
            nome='Cleiton Romario Santos',
            tipo='usuario'
        )
        usuario1 = Usuario.objects.create(
            user=user1,
            nome_social='Cleiton',
            data_nascimento='2002-07-11',
            genero='masculino',
            estado_civil='solteiro',
            nacionalidade='brasileiro',
            telefone='(37) 99838-1976',
            cep='39800000',
            rua='Rua das Palmeiras',
            numero='981',
            bairro='Centro',
            cidade=cidade,
            estado=cidade.estado_cidade,
            complemento='Apto 12',
            cargo_pretendido='Operador de Máquinas Agrícolas',
            area_interesse='Agronegócio',
            disponibilidade='Imediata',
            remoto=False,
            pretensao_salarial=2500.00,
            grau_escolaridade1='Ensino Médio Completo',
            instituicao_nome1='Escola Estadual de Arcos',
            situacao_academica1='Concluído',
            competencias_tecnicas1='Operação de tratores, colheitadeiras e implementos agrícolas. Manutenção preventiva básica de equipamentos.',
            competencias_comportamentais1='Responsabilidade, pontualidade, trabalho em equipe e iniciativa.',
            interesses_hobbies='Agricultura, criação de animais, pesca'
        )
        ExperienciaProfissional.objects.create(
            usuario=usuario1,
            cargo1='Auxiliar de Campo',
            nome_empresa1='Fazenda São João',
            data_inicio1='2021-03-01',
            data_fim1='2023-12-31',
            cargo2='Operador de Trator',
            nome_empresa2='Cooperativa Agrícola do Oeste',
            data_inicio2='2024-01-15',
        )

        # --- Usuário 2: perfil desenvolvedor ---
        user2 = UsuarioBase.objects.create_user(
            email='usuario1@teste',
            password='123',
            nome='Romario Santos',
            tipo='usuario'
        )
        usuario2 = Usuario.objects.create(
            user=user2,
            nome_social='Romario',
            data_nascimento='2003-04-22',
            genero='masculino',
            estado_civil='solteiro',
            nacionalidade='brasileiro',
            telefone='(37) 98765-4321',
            cep='39800000',
            rua='Av. Brasil',
            numero='200',
            bairro='Jardim América',
            cidade=cidade,
            estado=cidade.estado_cidade,
            cargo_pretendido='Desenvolvedor de Software',
            area_interesse='Tecnologia da Informação',
            disponibilidade='Imediata',
            remoto=True,
            pretensao_salarial=3000.00,
            grau_escolaridade1='Ensino Superior Incompleto',
            instituicao_nome1='IFMG - Instituto Federal de Minas Gerais',
            curso_graduacao1='Ciência da Computação',
            situacao_academica1='Cursando',
            competencias_tecnicas1='Python, JavaScript, Django, React, Git, SQL.',
            competencias_comportamentais1='Proatividade, aprendizado rápido, trabalho em equipe, resolução de problemas.',
            interesses_hobbies='Programação, tecnologia, jogos eletrônicos, leitura'
        )
        ExperienciaProfissional.objects.create(
            usuario=usuario2,
            cargo1='Estagiário de Desenvolvimento',
            nome_empresa1='TechSul Soluções',
            data_inicio1='2023-06-01',
            data_fim1='2024-05-31',
        )

        print("user_empresa:", user_empresa.email, empresa.segmento)
        print("user_admin:", user_admin.email, user_admin.is_admin)
        print("hub1:", hub1.nome_hub)
        print("hub4:", hub4.nome_hub)
        print("hub6:", hub6.nome_hub)
        print("vaga1:", vaga1.cargo_vaga, f"(req: {vaga1.anos_experiencia_req}a, formação: {vaga1.nivel_formacao_req})")
        print("vaga2:", vaga2.cargo_vaga, f"(req: {vaga2.anos_experiencia_req}a, formação: {vaga2.nivel_formacao_req})")
        print("vaga3:", vaga3.cargo_vaga, f"(req: {vaga3.anos_experiencia_req}a, formação: {vaga3.nivel_formacao_req})")
        print("usuario1:", user1.email, usuario1.cargo_pretendido)
        print("usuario2:", user2.email, usuario2.cargo_pretendido)
