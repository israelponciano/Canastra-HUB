from django.test import TestCase

# Create your tests here.
from django.test import TestCase
from django.urls import reverse

from core.models import UsuarioBase, Usuario, Estado, Cidade
from empresa.models import Empresa
from vagas.models import Vagas, UsuarioVaga, CursoVaga


class VagasTestSetupMixin:
    """Cria dados base: Estado/Cidade, um usuário comum (candidato) e um
    usuário empresa, além de uma vaga já publicada."""

    def setUp(self):
        self.estado = Estado.objects.create(
            nome_estado='Minas Gerais', sigla_estado='MG'
        )
        self.cidade = Cidade.objects.create(
            nome_cidade='Bambuí', estado_cidade=self.estado
        )

        # usuário comum (candidato)
        self.senha_usuario = 'SenhaForte123'
        self.user_base = UsuarioBase.objects.create_user(
            email='candidato@example.com',
            nome='Candidato Teste',
            tipo='usuario',
            password=self.senha_usuario,
        )
        self.usuario = Usuario.objects.create(
            user=self.user_base,
            data_nascimento='1995-01-01',
            genero='Feminino',
            estado_civil='Solteira',
            nacionalidade='Brasileira',
            telefone='35999999999',
            cep='38900-000',
            rua='Rua A',
            bairro='Centro',
            numero='10',
            cidade=self.cidade,
            estado=self.estado,
        )

        # usuário empresa
        self.senha_empresa = 'SenhaEmpresa123'
        self.empresa_user_base = UsuarioBase.objects.create_user(
            email='empresa@example.com',
            nome='Empresa Teste',
            tipo='empresa',
            password=self.senha_empresa,
        )
        self.empresa = Empresa.objects.create(
            user=self.empresa_user_base,
            nomefantasia='Empresa Teste',
            tipo_empresa='Ltda',
            razao_social='Empresa Teste Ltda',
            cnpj='00.000.000/0001-00',
            telefone='3599999999',
            rua='Rua B',
            cep='38900-000',
            numero=200,
            cidade=self.cidade,
            estado=self.estado,
            segmento='Tecnologia',
        )

        self.vaga = Vagas.objects.create(
            cargo_vaga='Desenvolvedor Backend',
            descricao_vaga='Descrição da vaga',
            requisito_vaga='Python, Django',
            local='Remoto',
            empresa=self.empresa,
        )

    def _login(self, email, senha):
        return self.client.post(reverse('core:login'), {
            'txtEmail': email,
            'txtSenha': senha,
        })


class CriarVagaTestCase(VagasTestSetupMixin, TestCase):
    """Testes da view vagas:criar_vagas."""

    def setUp(self):
        super().setUp()
        self.url = reverse('vagas:criar_vagas')

    def _dados_validos(self, **overrides):
        dados = {
            'txtTitulo': 'Analista de Dados',
            'txtDescricao': 'Descrição da vaga de analista',
            'txtLocal': 'Bambuí - MG',
            'txtRequisito': 'SQL, Python',
            'txtCursos[]': ['Ciência de Dados', 'Estatística'],
        }
        dados.update(overrides)
        return dados

    def test_criar_vaga_nao_autenticado_redireciona_para_login(self):
        response = self.client.post(self.url, self._dados_validos())

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Vagas.objects.filter(cargo_vaga='Analista de Dados').exists()
        )

    def test_criar_vaga_autenticado_como_empresa_cria_vaga(self):
        self._login('empresa@example.com', self.senha_empresa)

        response = self.client.post(self.url, self._dados_validos())

        self.assertRedirects(response, reverse('core:home'))
        vaga_criada = Vagas.objects.filter(
            cargo_vaga='Analista de Dados'
        ).first()
        self.assertIsNotNone(vaga_criada)
        self.assertEqual(vaga_criada.empresa, self.empresa)
        self.assertEqual(
            CursoVaga.objects.filter(vaga=vaga_criada).count(), 2
        )

    def test_criar_vaga_autenticado_como_usuario_comum_falha(self):
        """
        ATENÇÃO: a view acessa `usuario.empresa` assumindo que todo usuário
        autenticado tem uma Empresa vinculada (OneToOneField reverso). Um
        usuário comum (tipo='usuario') não tem Empresa associada, então
        isso estoura Empresa.DoesNotExist em vez de mostrar uma mensagem
        amigável tipo "apenas empresas podem publicar vagas". Este teste
        documenta o comportamento ATUAL (bug) — deve ser atualizado quando
        a view passar a checar o tipo de usuário antes de acessar
        usuario.empresa.
        """
        self._login('candidato@example.com', self.senha_usuario)

        with self.assertRaises(Empresa.DoesNotExist):
            self.client.post(self.url, self._dados_validos())


class CandidaturaVagaTestCase(VagasTestSetupMixin, TestCase):
    """Testes de candidatura: criar, duplicar e cancelar."""

    def setUp(self):
        super().setUp()
        self.candidatar_url = reverse(
            'vagas:candidatar_vaga', args=[self.vaga.id]
        )
        self.cancelar_url = reverse(
            'vagas:cancelar_candidatura', args=[self.vaga.id]
        )
        self.detalhe_url = reverse('vagas:detalhe_vaga', args=[self.vaga.id])

    def test_candidatar_nao_autenticado_redireciona_para_login(self):
        response = self.client.post(self.candidatar_url)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(UsuarioVaga.objects.filter(vaga=self.vaga).exists())

    def test_candidatar_via_get_nao_permitido(self):
        self._login('candidato@example.com', self.senha_usuario)

        response = self.client.get(self.candidatar_url)

        self.assertEqual(response.status_code, 405)

    def test_candidatar_cria_candidatura(self):
        self._login('candidato@example.com', self.senha_usuario)

        response = self.client.post(self.candidatar_url)

        self.assertRedirects(response, self.detalhe_url)
        self.assertTrue(
            UsuarioVaga.objects.filter(
                vaga=self.vaga, usuario=self.usuario
            ).exists()
        )

    def test_candidatura_duplicada_nao_cria_segundo_registro(self):
        self._login('candidato@example.com', self.senha_usuario)
        self.client.post(self.candidatar_url)

        response = self.client.post(self.candidatar_url)

        self.assertRedirects(response, self.detalhe_url)
        self.assertEqual(
            UsuarioVaga.objects.filter(
                vaga=self.vaga, usuario=self.usuario
            ).count(),
            1,
        )

    def test_cancelar_candidatura_remove_registro(self):
        self._login('candidato@example.com', self.senha_usuario)
        self.client.post(self.candidatar_url)

        response = self.client.post(self.cancelar_url)

        self.assertRedirects(response, self.detalhe_url)
        self.assertFalse(
            UsuarioVaga.objects.filter(
                vaga=self.vaga, usuario=self.usuario
            ).exists()
        )

    def test_cancelar_candidatura_inexistente_nao_gera_erro(self):
        self._login('candidato@example.com', self.senha_usuario)

        response = self.client.post(self.cancelar_url)

        self.assertRedirects(response, self.detalhe_url)
        self.assertFalse(
            UsuarioVaga.objects.filter(
                vaga=self.vaga, usuario=self.usuario
            ).exists()
        )