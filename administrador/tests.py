from django.test import TestCase
from django.urls import reverse

from core.models import UsuarioBase, Usuario, Estado, Cidade, Hub, Noticia


class AdministradorTestSetupMixin:
    """Cria um usuário admin e um usuário comum para os testes de acesso.

    O usuário comum precisa de um perfil Usuario completo, porque
    core:login faz Usuario.objects.get(user=usuario) sempre que
    tipo == 'usuario' — sem isso, o próprio login quebra com
    Usuario.DoesNotExist antes de chegar nas views do administrador.
    """

    def setUp(self):
        self.senha_admin = 'SenhaAdmin123'
        self.admin = UsuarioBase.objects.create_superuser(
            email='admin@example.com',
            nome='Admin Teste',
            tipo='admin',
            password=self.senha_admin,
        )

        self.estado = Estado.objects.create(
            nome_estado='Minas Gerais', sigla_estado='MG'
        )
        self.cidade = Cidade.objects.create(
            nome_cidade='Bambuí', estado_cidade=self.estado
        )

        self.senha_usuario = 'SenhaComum123'
        self.usuario_comum_base = UsuarioBase.objects.create_user(
            email='comum@example.com',
            nome='Usuário Comum',
            tipo='usuario',
            password=self.senha_usuario,
        )
        self.usuario_comum = Usuario.objects.create(
            user=self.usuario_comum_base,
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

    def _login(self, email, senha):
        return self.client.post(reverse('core:login'), {
            'txtEmail': email,
            'txtSenha': senha,
        })


class ToggleHubTestCase(AdministradorTestSetupMixin, TestCase):
    """Testes da view administrador:deletaHub (toggle ativo/inativo)."""

    def setUp(self):
        super().setUp()
        self.hub = Hub.objects.create(
            nome_hub='Agro',
            descricao_hub='Hub do agronegócio',
            isActive=True,
        )
        self.url = reverse('administrador:deletaHub', args=[self.hub.id])

    def test_deletahub_nao_autenticado_redireciona_para_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_deletahub_usuario_comum_tambem_estoura_erro_por_bug_de_parametro(self):
        """
        Mesmo bug documentado em test_deletahub_admin_estoura_erro_por_bug_de_parametro.
        O TypeError acontece na hora que o Django chama a view com o kwarg
        errado — ANTES de qualquer linha de código da view rodar (inclusive
        antes do `if request.user.is_admin`). Por isso nem a checagem de
        "Acesso negado" chega a executar: usuário comum ou admin, o
        resultado é o mesmo erro. Isso mostra que a rota está quebrada para
        qualquer pessoa, não só para admins.
        """
        self._login('comum@example.com', self.senha_usuario)

        with self.assertRaises(TypeError):
            self.client.get(self.url)

    def test_deletahub_admin_estoura_erro_por_bug_de_parametro(self):
        """
        BUG DE PARÂMETRO — administrador/urls.py declara:
            path("deletaHub/<int:noticia_id>", views.deletaHub, name="deletaHub")
        capturando o valor da URL como `noticia_id`, mas a view está definida
        como:
            def deletaHub(request, hubs_id):
        O nome do argumento capturado na URL não bate com o nome do
        parâmetro da view. Resultado: QUALQUER chamada a essa rota — mesmo
        de um admin válido — estoura TypeError em vez de alternar o Hub
        entre ativo/inativo. É o toggle de Hub que está quebrado, não o de
        notícia.

        Este teste documenta o comportamento ATUAL (bug). Correção sugerida:
        trocar `<int:noticia_id>` por `<int:hubs_id>` na URL. Depois de
        corrigir, troque este teste pelo fluxo normal de toggle
        ativo -> inativo -> ativo (veja ToggleNoticiaTestCase como modelo).
        """
        self._login('admin@example.com', self.senha_admin)

        with self.assertRaises(TypeError):
            self.client.get(self.url)


class ToggleNoticiaTestCase(AdministradorTestSetupMixin, TestCase):
    """Testes da view administrador:deletaNoticias (toggle ativo/inativo).

    Aqui o nome do parâmetro na URL (`noticia_id`) bate com o parâmetro da
    view, então o toggle funciona normalmente — ao contrário do Hub.
    """

    def setUp(self):
        super().setUp()
        self.noticia = Noticia.objects.create(
            titulo_noticia='Notícia Teste',
            descricao_noticia='Descrição da notícia',
            fonte='Fonte Teste',
            isActive=True,
        )
        self.url = reverse(
            'administrador:deletaNoticias', args=[self.noticia.id]
        )

    def test_deletanoticias_nao_autenticado_redireciona_para_login(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)

    def test_deletanoticias_usuario_comum_acesso_negado(self):
        self._login('comum@example.com', self.senha_usuario)

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('core:home'))
        self.noticia.refresh_from_db()
        self.assertTrue(self.noticia.isActive)

    def test_toggle_noticia_ativo_para_inativo(self):
        self._login('admin@example.com', self.senha_admin)

        response = self.client.get(self.url)

        self.assertRedirects(
            response, reverse('administrador:gerenciarNoticias')
        )
        self.noticia.refresh_from_db()
        self.assertFalse(self.noticia.isActive)

    def test_toggle_noticia_inativo_para_ativo(self):
        self.noticia.isActive = False
        self.noticia.save()
        self._login('admin@example.com', self.senha_admin)

        response = self.client.get(self.url)

        self.assertRedirects(
            response, reverse('administrador:gerenciarNoticias')
        )
        self.noticia.refresh_from_db()
        self.assertTrue(self.noticia.isActive)

    def test_toggle_noticia_duas_vezes_volta_ao_estado_original(self):
        self._login('admin@example.com', self.senha_admin)

        self.client.get(self.url)
        self.client.get(self.url)

        self.noticia.refresh_from_db()
        self.assertTrue(self.noticia.isActive)

    def test_deletanoticias_inexistente_nao_gera_erro(self):
        self._login('admin@example.com', self.senha_admin)
        url_inexistente = reverse(
            'administrador:deletaNoticias', args=[9999]
        )

        response = self.client.get(url_inexistente)

        self.assertRedirects(
            response, reverse('administrador:gerenciarNoticias')
        )