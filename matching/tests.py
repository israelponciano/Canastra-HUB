# matching/tests.py
from django.test import TestCase
from unittest.mock import patch, MagicMock
from django.test import override_settings


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
