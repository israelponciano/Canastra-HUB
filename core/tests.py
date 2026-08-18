from django.test import TestCase
from django.urls import reverse
from django.db import IntegrityError

from core.models import UsuarioBase, Usuario, Estado, Cidade


class CoreTestSetupMixin:
    """Cria Estado/Cidade base, usados tanto no cadastro quanto no login."""

    def setUp(self):
        self.estado = Estado.objects.create(
            nome_estado='Minas Gerais', sigla_estado='MG'
        )
        self.cidade = Cidade.objects.create(
            nome_cidade='Bambuí', estado_cidade=self.estado
        )


class CadastroUsuarioTestCase(CoreTestSetupMixin, TestCase):
    """Testes da view core:cadastro_usuario (POST)."""

    def setUp(self):
        super().setUp()
        self.url = reverse('core:cadastro_usuario')

    def _dados_validos(self, **overrides):
        dados = {
            'txtNome': 'Maria Silva',
            'txtSenha': 'SenhaForte123',
            'confirmar_Senha': 'SenhaForte123',
            'txtNomeSocial': 'Maria',
            'txtDataNasc': '1995-05-20',
            'txtGenero': 'Feminino',
            'txtEstadoCivil': 'Solteira',
            'txtNacionalidade': 'Brasileira',
            'txtEmail': 'maria@example.com',
            'txtTelefone': '35999999999',
            'txtCep': '38900-000',
            'txtRua': 'Rua A',
            'txtNumero': '100',
            'txtBairro': 'Centro',
            'txtComplemento': '',
            'cidade': str(self.cidade.id),
            'estado': str(self.estado.id),
        }
        dados.update(overrides)
        return dados

    def test_cadastro_sucesso_cria_usuariobase_e_usuario(self):
        response = self.client.post(self.url, self._dados_validos())

        self.assertRedirects(response, reverse('core:login'))
        self.assertTrue(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )
        user = UsuarioBase.objects.get(email='maria@example.com')
        self.assertTrue(user.check_password('SenhaForte123'))
        self.assertTrue(Usuario.objects.filter(user=user).exists())

    def test_cadastro_sem_nome_nao_cria_usuario(self):
        response = self.client.post(self.url, self._dados_validos(txtNome=''))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'O nome é obrigatório.')
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_nome_curto_nao_cria_usuario(self):
        response = self.client.post(self.url, self._dados_validos(txtNome='Ma'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'O nome deve possuir no mínimo 3 caracteres.'
        )
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_senha_confirmacao_diferente_nao_cria_usuario(self):
        response = self.client.post(
            self.url, self._dados_validos(confirmar_Senha='OutraSenha123')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'As senhas devem ser iguais.')
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_sem_cidade_redireciona(self):
        response = self.client.post(self.url, self._dados_validos(cidade=''))

        self.assertRedirects(response, reverse('core:cadastro_usuario'))
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_estado_invalido_nao_cria_usuario(self):
        response = self.client.post(self.url, self._dados_validos(estado='9999'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estado inválido.')
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_cidade_invalida_nao_cria_usuario(self):
        response = self.client.post(self.url, self._dados_validos(cidade='9999'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Cidade inválida.')
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )

    def test_cadastro_email_duplicado(self):
        """
        ATENÇÃO: a view atual não valida e-mail duplicado antes de chamar
        create_user(). Como UsuarioBase.email é unique=True, um cadastro
        com e-mail já existente estoura IntegrityError em vez de mostrar
        uma mensagem amigável. Este teste documenta o comportamento ATUAL
        (bug) e deve ser atualizado quando a view passar a validar isso
        antes do create_user().
        """
        UsuarioBase.objects.create_user(
            email='maria@example.com',
            nome='Já Cadastrada',
            tipo='usuario',
            password='Outra123',
        )

        with self.assertRaises(IntegrityError):
            self.client.post(self.url, self._dados_validos())

    def test_cadastro_usuario_ja_logado_nao_permite_novo_cadastro(self):
        user = UsuarioBase.objects.create_user(
            email='logado@example.com',
            nome='Logado',
            tipo='usuario',
            password='Senha123',
        )
        self.client.force_login(user)

        response = self.client.post(self.url, self._dados_validos())

        self.assertRedirects(response, reverse('core:home'))
        self.assertFalse(
            UsuarioBase.objects.filter(email='maria@example.com').exists()
        )


class LoginTestCase(CoreTestSetupMixin, TestCase):
    """Testes da view core:login."""

    def setUp(self):
        super().setUp()
        self.url = reverse('core:login')
        self.senha = 'SenhaForte123'
        self.user = UsuarioBase.objects.create_user(
            email='usuario@example.com',
            nome='Usuário Teste',
            tipo='usuario',
            password=self.senha,
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            data_nascimento='1990-01-01',
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

    def test_login_credenciais_validas_redireciona_para_home(self):
        response = self.client.post(self.url, {
            'txtEmail': 'usuario@example.com',
            'txtSenha': self.senha,
        })

        self.assertRedirects(response, reverse('core:home'))
        self.assertEqual(self.client.session['email_atual'], 'usuario@example.com')
        self.assertEqual(self.client.session['nome'], 'Usuário Teste')

    def test_login_credenciais_invalidas_nao_autentica(self):
        response = self.client.post(self.url, {
            'txtEmail': 'usuario@example.com',
            'txtSenha': 'senhaErrada',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha inválidos.')
        self.assertNotIn('email_atual', self.client.session)

    def test_login_email_inexistente_nao_autentica(self):
        response = self.client.post(self.url, {
            'txtEmail': 'naoexiste@example.com',
            'txtSenha': 'qualquer',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Usuário ou senha inválidos.')

    def test_login_usuario_sem_area_interesse_marca_cadastro_incompleto(self):
        response = self.client.post(self.url, {
            'txtEmail': 'usuario@example.com',
            'txtSenha': self.senha,
        })

        self.assertRedirects(response, reverse('core:home'))
        self.assertTrue(self.client.session.get('incompleto'))