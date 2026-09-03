from django.test import TestCase
from django.urls import reverse, NoReverseMatch

from core.models import Sala, SalaImagem


class EstruturaEstrategicaTest(TestCase):
    def setUp(self):
        self.sala_ativa = Sala.objects.create(
            nome_sala='Auditórios',
            descricao_recursos='Capacidade para 100 pessoas'
        )
        self.sala_inativa = Sala.objects.create(
            nome_sala='Sala Desativada',
            descricao_recursos='Recurso qualquer', isActive=False
        )

    def test_pagina_carrega(self):
        response = self.client.get(reverse('core:espacos_hub'))
        self.assertEqual(response.status_code, 200)

    def test_sala_ativa_aparece_com_descricao(self):
        response = self.client.get(reverse('core:espacos_hub'))
        content = response.content.decode()
        self.assertIn(self.sala_ativa.nome_sala, content)
        self.assertIn(self.sala_ativa.descricao_recursos, content)

    def test_sala_inativa_nao_aparece(self):
        response = self.client.get(reverse('core:espacos_hub'))
        content = response.content.decode()
        self.assertNotIn('Sala Desativada', content)

    def test_rota_sobre_removida(self):
        with self.assertRaises(NoReverseMatch):
            reverse('core:sobre')

    def test_imagens_da_sala_renderizadas_no_carousel(self):
        img1 = SalaImagem.objects.create(sala=self.sala_ativa, imagem='fotos_sala/a.jpg', ordem=0)
        img2 = SalaImagem.objects.create(sala=self.sala_ativa, imagem='fotos_sala/b.jpg', ordem=1)
        response = self.client.get(reverse('core:espacos_hub'))
        content = response.content.decode()
        self.assertIn('data-carousel', content)
        self.assertIn(img1.imagem.url, content)
        self.assertIn(img2.imagem.url, content)
