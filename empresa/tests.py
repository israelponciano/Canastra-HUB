from django.test import TestCase
from django.urls import reverse

from core.models import UsuarioBase, Estado, Cidade, Hub
from empresa.models import Empresa


class EmpresaTestSetupMixin:
    """Cria Estado/Cidade base (+ uma cidade de outro estado, para testar
    combinação inválida) e dois Hubs."""

    def setUp(self):
        self.estado = Estado.objects.create(
            nome_estado='Minas Gerais', sigla_estado='MG'
        )
        self.cidade = Cidade.objects.create(
            nome_cidade='Bambuí', estado_cidade=self.estado
        )

        self.outro_estado = Estado.objects.create(
            nome_estado='São Paulo', sigla_estado='SP'
        )
        self.outra_cidade = Cidade.objects.create(
            nome_cidade='Campinas', estado_cidade=self.outro_estado
        )

        self.hub1 = Hub.objects.create(
            nome_hub='Agro', descricao_hub='Hub do agronegócio'
        )
        self.hub2 = Hub.objects.create(
            nome_hub='Tech', descricao_hub='Hub de tecnologia'
        )

    def _login(self, email, senha):
        return self.client.post(reverse('core:login'), {
            'txtEmail': email,
            'txtSenha': senha,
        })


class CriarEmpresaTestCase(EmpresaTestSetupMixin, TestCase):
    """Testes da view empresa:criar_empresa."""

    def setUp(self):
        super().setUp()
        self.url = reverse('empresa:criar_empresa')

    def _dados_validos(self, **overrides):
        dados = {
            'txtSenha': 'SenhaForte123',
            'txtConfirmarSenha': 'SenhaForte123',
            'txtNome': 'Empresa Teste',
            'txtEmail': 'contato@empresateste.com',
            'txtSegmento': 'Tecnologia',
            'txtTipo': 'Ltda',
            'txtTelefone': '35999999999',
            'txtRua': 'Rua A',
            'txtCep': '38900000',
            'txtNumero': '100',
            'txtComplemento': 'Sala 1',
            'cidade': str(self.cidade.id),
            'estado': str(self.estado.id),
            'txtCnpj': '00000000000100',
            'txtRazaoSocial': 'Empresa Teste Ltda',
        }
        dados.update(overrides)
        return dados

    def _assert_nao_criou_empresa(self):
        self.assertFalse(
            UsuarioBase.objects.filter(email='contato@empresateste.com').exists()
        )

    # --- fluxo geral ---

    def test_get_renderiza_formulario_de_cadastro(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro_empresa.html')

    def test_usuario_ja_logado_via_post_nao_permite_cadastro(self):
        UsuarioBase.objects.create_user(
            email='logado@example.com', nome='Logado', tipo='usuario',
            password='Senha123456'
        )
        self._login('logado@example.com', 'Senha123456')

        response = self.client.post(self.url, self._dados_validos())

        self.assertRedirects(response, reverse('core:home'))
        self._assert_nao_criou_empresa()

    def test_usuario_ja_logado_via_get_redireciona_para_home(self):
        UsuarioBase.objects.create_user(
            email='logado2@example.com', nome='Logado2', tipo='usuario',
            password='Senha123456'
        )
        self._login('logado2@example.com', 'Senha123456')

        response = self.client.get(self.url)

        self.assertRedirects(response, reverse('core:home'))

    def test_cadastro_sucesso_cria_usuariobase_e_empresa_com_hubs(self):
        response = self.client.post(self.url, self._dados_validos(**{
            'hubs[]': [str(self.hub1.id), str(self.hub2.id)],
        }))

        self.assertRedirects(response, reverse('core:login'))

        user = UsuarioBase.objects.get(email='contato@empresateste.com')
        self.assertEqual(user.tipo, 'empresa')
        self.assertTrue(user.check_password('SenhaForte123'))

        empresa = Empresa.objects.get(user=user)
        self.assertEqual(empresa.cnpj, '00000000000100')
        self.assertCountEqual(
            empresa.hubs.values_list('id', flat=True),
            [self.hub1.id, self.hub2.id],
        )

    def test_cadastro_sucesso_sem_hubs(self):
        response = self.client.post(self.url, self._dados_validos())

        self.assertRedirects(response, reverse('core:login'))
        empresa = Empresa.objects.get(user__email='contato@empresateste.com')
        self.assertEqual(empresa.hubs.count(), 0)

    # --- validação de senha ---

    def test_senha_confirmacao_diferente(self):
        response = self.client.post(self.url, self._dados_validos(
            txtConfirmarSenha='OutraSenha1234'
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'As senhas devem ser iguais.')
        self._assert_nao_criou_empresa()

    def test_senha_curta(self):
        response = self.client.post(self.url, self._dados_validos(
            txtSenha='1234567', txtConfirmarSenha='1234567'
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'A senha deve ter pelo menos 8 caracteres.'
        )
        self._assert_nao_criou_empresa()

    def test_senha_vazia_e_barrada_pela_checagem_de_confirmacao(self):
        """
        A checagem senha != confirmacaoSenha roda antes da checagem de
        campos obrigatórios. Com os dois campos vazios ('' == ''), essa
        checagem passa e quem barra o cadastro é a validação de campo
        obrigatório logo em seguida — o resultado final (não cria conta)
        é o mesmo, isso só documenta a ordem das validações.
        """
        response = self.client.post(self.url, self._dados_validos(
            txtSenha='', txtConfirmarSenha=''
        ))

        self.assertEqual(response.status_code, 200)
        self._assert_nao_criou_empresa()

    # --- campos obrigatórios ---

    def test_campos_obrigatorios_faltando(self):
        campos_para_testar = [
            'txtNome', 'txtEmail', 'txtSegmento', 'txtTipo', 'txtTelefone',
            'txtRua', 'txtCep', 'txtNumero', 'estado', 'cidade', 'txtCnpj',
            'txtRazaoSocial',
        ]
        for campo in campos_para_testar:
            with self.subTest(campo=campo):
                response = self.client.post(
                    self.url, self._dados_validos(**{campo: ''})
                )
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'obrigatório')
                self._assert_nao_criou_empresa()

    # --- validações de formato ---

    def test_email_invalido(self):
        response = self.client.post(
            self.url, self._dados_validos(txtEmail='nao-e-email')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Endereço de e-mail inválido.')
        self._assert_nao_criou_empresa()

    def test_cnpj_invalido(self):
        response = self.client.post(
            self.url, self._dados_validos(txtCnpj='123')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CNPJ inválido')
        self._assert_nao_criou_empresa()

    def test_telefone_invalido(self):
        response = self.client.post(
            self.url, self._dados_validos(txtTelefone='123')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Telefone inválido')
        self._assert_nao_criou_empresa()

    def test_cep_invalido(self):
        response = self.client.post(
            self.url, self._dados_validos(txtCep='123')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'CEP inválido')
        self._assert_nao_criou_empresa()

    def test_numero_nao_numerico(self):
        response = self.client.post(
            self.url, self._dados_validos(txtNumero='abc')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'O número do endereço deve ser numérico.'
        )
        self._assert_nao_criou_empresa()

    def test_complemento_excede_tamanho_maximo(self):
        max_length = Empresa._meta.get_field('complemento').max_length
        response = self.client.post(self.url, self._dados_validos(
            txtComplemento='A' * (max_length + 1)
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no máximo')
        self._assert_nao_criou_empresa()

    # --- estado / cidade ---

    def test_estado_ou_cidade_nao_numerico(self):
        response = self.client.post(
            self.url, self._dados_validos(estado='abc')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Seleção de estado ou cidade inválida.'
        )
        self._assert_nao_criou_empresa()

    def test_estado_nao_encontrado(self):
        response = self.client.post(
            self.url, self._dados_validos(estado='9999')
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Estado selecionado não encontrado.')
        self._assert_nao_criou_empresa()

    def test_cidade_nao_pertence_ao_estado_selecionado(self):
        response = self.client.post(self.url, self._dados_validos(
            cidade=str(self.outra_cidade.id)
        ))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            'Cidade inválida ou não pertence ao estado selecionado.'
        )
        self._assert_nao_criou_empresa()

    # --- hubs ---

    def test_hub_invalido(self):
        response = self.client.post(self.url, self._dados_validos(**{
            'hubs[]': ['9999'],
        }))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Um ou mais hubs selecionados são inválidos.'
        )
        self._assert_nao_criou_empresa()

    # --- duplicidade ---

    def test_email_duplicado(self):
        UsuarioBase.objects.create_user(
            email='contato@empresateste.com', nome='Já existe',
            tipo='empresa', password='Outra12345'
        )

        response = self.client.post(self.url, self._dados_validos())

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Já existe uma conta cadastrada com este e-mail.'
        )

    def test_cnpj_duplicado(self):
        outro_user = UsuarioBase.objects.create_user(
            email='outra@empresateste.com', nome='Outra Empresa',
            tipo='empresa', password='Outra12345'
        )
        Empresa.objects.create(
            user=outro_user,
            nomefantasia='Outra',
            tipo_empresa='Ltda',
            razao_social='Outra Ltda',
            cnpj='00000000000100',
            telefone='35988888888',
            rua='Rua X',
            cep='38900000',
            numero=1,
            cidade=self.cidade,
            estado=self.estado,
            segmento='Tecnologia',
        )

        response = self.client.post(self.url, self._dados_validos())

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, 'Já existe uma empresa cadastrada com este CNPJ.'
        )
        self._assert_nao_criou_empresa()