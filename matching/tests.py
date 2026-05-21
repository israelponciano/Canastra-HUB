# matching/tests.py
import json
from django.test import TestCase, Client
from unittest.mock import patch, MagicMock
from django.test import override_settings
from matching.schemas import MatchResult


class MatchingAppSmoke(TestCase):
    def test_app_installed(self):
        from django.apps import apps
        self.assertTrue(apps.is_installed("matching"))


class GetMatcherTest(TestCase):
    def setUp(self):
        import matching.service as svc
        svc._matcher = None

    def tearDown(self):
        import matching.service as svc
        svc._matcher = None

    def test_retorna_instancia_job_matcher(self):
        mock = MagicMock()
        with patch('matching.service.JobMatcher', return_value=mock) as MockCls:
            with override_settings(CHROMADB_PATH='/tmp/test_chroma'):
                from matching.service import get_matcher
                result = get_matcher()
        self.assertEqual(result, mock)
        MockCls.assert_called_once_with(persist_directory='/tmp/test_chroma')

    def test_retorna_mesma_instancia_em_chamadas_repetidas(self):
        mock = MagicMock()
        with patch('matching.service.JobMatcher', return_value=mock) as MockCls:
            with override_settings(CHROMADB_PATH='/tmp/test_chroma'):
                from matching.service import get_matcher
                r1 = get_matcher()
                r2 = get_matcher()
        self.assertIs(r1, r2)
        MockCls.assert_called_once()


def _mock_usuario(**kwargs):
    """Retorna um MagicMock com interface mínima de Usuario."""
    u = MagicMock()
    u.cargo_pretendido = kwargs.get('cargo_pretendido', 'Desenvolvedor Python')
    u.area_interesse = kwargs.get('area_interesse', 'Backend')
    u.disponibilidade = kwargs.get('disponibilidade', 'Imediata')
    u.remoto = kwargs.get('remoto', False)
    u.curso = kwargs.get('curso', 'Sistemas de Informação')
    u.interesses_hobbies = kwargs.get('interesses_hobbies', None)
    for n in ('1', '2', '3'):
        setattr(u, f'instituicao_nome{n}', None)
        setattr(u, f'grau_escolaridade{n}', None)
        setattr(u, f'curso_graduacao{n}', None)
        setattr(u, f'situacao_academica{n}', None)
        setattr(u, f'competencias_tecnicas{n}', None)
        setattr(u, f'competencias_comportamentais{n}', None)
    return u


def _mock_vaga(**kwargs):
    """Retorna um MagicMock com interface mínima de Vagas."""
    v = MagicMock()
    v.cargo_vaga = kwargs.get('cargo_vaga', 'Dev Python')
    v.descricao_vaga = kwargs.get('descricao_vaga', 'Vaga de backend')
    v.requisito_vaga = kwargs.get('requisito_vaga', 'Python, Django')
    v.local = kwargs.get('local', 'Patos de Minas')
    v.empresa.nomefantasia = kwargs.get('nomefantasia', 'TechCo')
    v.empresa.segmento = kwargs.get('segmento', 'Tecnologia')
    return v


class BuildResumeTextTest(TestCase):
    def _call(self, usuario):
        from core.models import ExperienciaProfissional
        with patch('matching.text_builders.ExperienciaProfissional') as MockExp:
            MockExp.DoesNotExist = ExperienciaProfissional.DoesNotExist
            MockExp.objects.get.side_effect = ExperienciaProfissional.DoesNotExist
            from matching.text_builders import build_resume_text
            return build_resume_text(usuario)

    def test_inclui_cargo_pretendido(self):
        text = self._call(_mock_usuario(cargo_pretendido='Analista de Dados'))
        self.assertIn('Analista de Dados', text)

    def test_inclui_area_interesse(self):
        text = self._call(_mock_usuario(area_interesse='Data Science'))
        self.assertIn('Data Science', text)

    def test_inclui_competencias_tecnicas(self):
        u = _mock_usuario()
        u.competencias_tecnicas1 = 'Python, SQL'
        text = self._call(u)
        self.assertIn('Python, SQL', text)

    def test_campos_nulos_sao_omitidos(self):
        u = _mock_usuario(cargo_pretendido=None, area_interesse=None)
        text = self._call(u)
        self.assertNotIn('objetivo:', text)
        self.assertNotIn('área de interesse:', text)

    def test_remoto_incluido_quando_verdadeiro(self):
        text = self._call(_mock_usuario(remoto=True))
        self.assertIn('remoto', text)


class BuildJobTextTest(TestCase):
    def _call(self, vaga):
        with patch('matching.text_builders.CursoVaga') as MockCurso:
            MockCurso.objects.filter.return_value.values_list.return_value = []
            from matching.text_builders import build_job_text
            return build_job_text(vaga)

    def test_inclui_cargo_vaga(self):
        text = self._call(_mock_vaga(cargo_vaga='Engenheiro de Software'))
        self.assertIn('Engenheiro de Software', text)

    def test_inclui_requisito_vaga(self):
        text = self._call(_mock_vaga(requisito_vaga='Django, REST'))
        self.assertIn('Django, REST', text)

    def test_inclui_nome_empresa(self):
        text = self._call(_mock_vaga(nomefantasia='StartupXYZ'))
        self.assertIn('StartupXYZ', text)

    def test_inclui_segmento(self):
        text = self._call(_mock_vaga(segmento='Agronegócio'))
        self.assertIn('Agronegócio', text)


class SyncUsuarioSignalTest(TestCase):
    def test_chama_update_resume_ao_salvar_usuario(self):
        mock_matcher = MagicMock()
        mock_usuario = MagicMock()
        mock_usuario.pk = 7
        mock_usuario.user.nome = 'João'

        with patch('matching.signals.get_matcher', return_value=mock_matcher):
            with patch('matching.signals.build_resume_text', return_value='texto currículo'):
                from matching.signals import sync_usuario
                sync_usuario(sender=None, instance=mock_usuario)

        mock_matcher.update_resume.assert_called_once_with(
            text='texto currículo',
            candidate_name='João',
            candidate_id='7',
        )

    def test_nao_propaga_excecao_do_matcher(self):
        mock_matcher = MagicMock()
        mock_matcher.update_resume.side_effect = Exception("ChromaDB error")
        mock_usuario = MagicMock()
        mock_usuario.pk = 99
        mock_usuario.user.nome = 'Ana'

        with patch('matching.signals.get_matcher', return_value=mock_matcher):
            with patch('matching.signals.build_resume_text', return_value='texto'):
                from matching.signals import sync_usuario
                try:
                    sync_usuario(sender=None, instance=mock_usuario)
                except Exception:
                    self.fail("sync_usuario propagou Exception — deve silenciar erros do matcher")


class SyncVagaSignalTest(TestCase):
    def test_chama_update_job_ao_salvar_vaga(self):
        mock_matcher = MagicMock()
        mock_vaga = MagicMock()
        mock_vaga.id = 3
        mock_vaga.cargo_vaga = 'Dev Python'
        mock_vaga.empresa.nomefantasia = 'TechCo'

        with patch('matching.signals.get_matcher', return_value=mock_matcher):
            with patch('matching.signals.build_job_text', return_value='texto vaga'):
                from matching.signals import sync_vaga
                sync_vaga(sender=None, instance=mock_vaga)

        mock_matcher.update_job.assert_called_once_with(
            text='texto vaga',
            job_title='Dev Python',
            company='TechCo',
            job_id='3',
        )

    def test_nao_propaga_excecao_do_matcher(self):
        mock_matcher = MagicMock()
        mock_matcher.update_job.side_effect = Exception("erro")
        mock_vaga = MagicMock()
        mock_vaga.id = 5
        mock_vaga.cargo_vaga = 'Analista'
        mock_vaga.empresa.nomefantasia = 'Corp'

        with patch('matching.signals.get_matcher', return_value=mock_matcher):
            with patch('matching.signals.build_job_text', return_value='texto'):
                from matching.signals import sync_vaga
                try:
                    sync_vaga(sender=None, instance=mock_vaga)
                except Exception:
                    self.fail("sync_vaga propagou Exception — deve silenciar erros do matcher")


class CandidatosParaVagaViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_retorna_200_com_lista_de_candidatos(self):
        resultados = [
            MatchResult(entity_id='1', name='João', score=0.9),
            MatchResult(entity_id='2', name='Maria', score=0.75),
        ]
        mock_matcher = MagicMock()
        mock_matcher.match_resumes_for_job.return_value = resultados

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/candidatos/42/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['resultados']), 2)
        self.assertEqual(data['resultados'][0]['nome'], 'João')
        self.assertAlmostEqual(data['resultados'][0]['score'], 0.9)

    def test_retorna_404_quando_vaga_nao_indexada(self):
        mock_matcher = MagicMock()
        mock_matcher.match_resumes_for_job.side_effect = ValueError("Vaga '42' não encontrada.")

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/candidatos/42/')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('erro', data)

    def test_retorna_400_com_parametro_top_invalido(self):
        mock_matcher = MagicMock()
        mock_matcher.match_resumes_for_job.return_value = []

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/candidatos/1/?top=abc')

        self.assertEqual(response.status_code, 400)

    def test_repassa_parametro_top_ao_matcher(self):
        mock_matcher = MagicMock()
        mock_matcher.match_resumes_for_job.return_value = []

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            self.client.get('/matching/candidatos/1/?top=3')

        mock_matcher.match_resumes_for_job.assert_called_once_with(
            job_id='1', top_k=3, min_score=0.0
        )


class VagasParaUsuarioViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_retorna_200_com_lista_de_vagas(self):
        resultados = [
            MatchResult(entity_id='10', name='Dev Python', company='TechCo', score=0.88),
        ]
        mock_matcher = MagicMock()
        mock_matcher.match_jobs_for_resume.return_value = resultados

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/vagas-para/7/')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data['resultados']), 1)
        self.assertEqual(data['resultados'][0]['cargo'], 'Dev Python')
        self.assertEqual(data['resultados'][0]['empresa'], 'TechCo')

    def test_retorna_404_quando_candidato_nao_indexado(self):
        mock_matcher = MagicMock()
        mock_matcher.match_jobs_for_resume.side_effect = ValueError("Candidato '7' não encontrado.")

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/vagas-para/7/')

        self.assertEqual(response.status_code, 404)
        data = json.loads(response.content)
        self.assertIn('erro', data)

    def test_repassa_parametro_min_score_ao_matcher(self):
        mock_matcher = MagicMock()
        mock_matcher.match_jobs_for_resume.return_value = []

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            self.client.get('/matching/vagas-para/7/?min_score=0.5')

        mock_matcher.match_jobs_for_resume.assert_called_once_with(
            candidate_id='7', top_k=5, min_score=0.5
        )

    def test_retorna_400_com_min_score_invalido(self):
        mock_matcher = MagicMock()
        mock_matcher.match_jobs_for_resume.return_value = []

        with patch('matching.views.get_matcher', return_value=mock_matcher):
            response = self.client.get('/matching/vagas-para/7/?min_score=nao_numero')

        self.assertEqual(response.status_code, 400)
