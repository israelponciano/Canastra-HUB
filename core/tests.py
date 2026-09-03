from django.test import TestCase, Client
from django.urls import reverse

from core.models import UsuarioBase, Usuario, Estado, Cidade, Hub, UsuarioHub


class ToggleHubInteresseTest(TestCase):
    def setUp(self):
        self.estado = Estado.objects.create(nome_estado='Minas Gerais', sigla_estado='MG')
        self.cidade = Cidade.objects.create(nome_cidade='Arcos', estado_cidade=self.estado)

        self.user = UsuarioBase.objects.create_user(
            email='usuario@teste.com', password='123', nome='Teste', tipo='usuario'
        )
        self.usuario = Usuario.objects.create(
            user=self.user,
            data_nascimento='2000-01-01',
            genero='masculino',
            estado_civil='solteiro',
            nacionalidade='brasileiro',
            telefone='123',
            cep='123',
            rua='rua',
            numero='1',
            bairro='bairro',
            cidade=self.cidade,
            estado=self.estado,
        )

        self.hub = Hub.objects.create(nome_hub='Agro', descricao_hub='desc', isActive=True)
        self.hub_inativo = Hub.objects.create(nome_hub='Inativo', descricao_hub='desc', isActive=False)

        self.client = Client()
        self.client.force_login(self.user)
        session = self.client.session
        session['perfil'] = 'usuario'
        session.save()

    def test_marcar_interesse(self):
        self.client.post(reverse('core:toggle_hub_interesse', args=[self.hub.id]))
        self.assertTrue(UsuarioHub.objects.filter(usuario=self.usuario, hub=self.hub).exists())

    def test_desmarcar_interesse(self):
        UsuarioHub.objects.create(usuario=self.usuario, hub=self.hub)
        self.client.post(reverse('core:toggle_hub_interesse', args=[self.hub.id]))
        self.assertFalse(UsuarioHub.objects.filter(usuario=self.usuario, hub=self.hub).exists())

    def test_requer_login(self):
        self.client.logout()
        response = self.client.post(reverse('core:toggle_hub_interesse', args=[self.hub.id]))
        self.assertNotEqual(response.status_code, 200)
        self.assertFalse(UsuarioHub.objects.filter(hub=self.hub).exists())

    def test_hub_inativo_nao_pode_ser_selecionado(self):
        response = self.client.post(reverse('core:toggle_hub_interesse', args=[self.hub_inativo.id]))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(UsuarioHub.objects.filter(hub=self.hub_inativo).exists())

    def test_empresa_nao_pode_selecionar(self):
        session = self.client.session
        session['perfil'] = 'empresa'
        session.save()
        self.client.post(reverse('core:toggle_hub_interesse', args=[self.hub.id]))
        self.assertFalse(UsuarioHub.objects.filter(hub=self.hub).exists())
