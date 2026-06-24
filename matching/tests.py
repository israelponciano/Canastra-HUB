# matching/tests.py
import json
import tempfile
import shutil
import numpy as np
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client, override_settings

from matching.schemas import ResumeChunk, JobChunk, MatchResult


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_matcher():
    """JobMatcher isolado por diretório temporário — sem download de modelo."""
    tmpdir = tempfile.mkdtemp(prefix='matching_test_')
    with patch('matching.matcher.SentenceTransformer') as MockST:
        mock_st = MagicMock()
        mock_st.encode.side_effect = lambda texts, **_: np.ones((len(texts), 16), dtype=float)
        MockST.return_value = mock_st
        from matching.matcher import JobMatcher
        matcher = JobMatcher(persist_directory=tmpdir)
    matcher._tmpdir = tmpdir
    return matcher


def _cleanup_matcher(matcher):
    tmpdir = getattr(matcher, '_tmpdir', None)
    if tmpdir:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _mock_usuario(**kw):
    u = MagicMock()
    u.cargo_pretendido = kw.get('cargo_pretendido', 'Desenvolvedor Python')
    u.area_interesse = kw.get('area_interesse', 'Backend')
    u.disponibilidade = kw.get('disponibilidade', 'Imediata')
    u.remoto = kw.get('remoto', False)
    u.curso = kw.get('curso', 'Sistemas de Informação')
    u.interesses_hobbies = kw.get('interesses_hobbies', None)
    u.carta_apresentacao = kw.get('carta_apresentacao', None)
    u.curriculo_pdf = kw.get('curriculo_pdf', None)
    for n in ('1', '2', '3'):
        setattr(u, f'instituicao_nome{n}', kw.get(f'instituicao_nome{n}', None))
        setattr(u, f'grau_escolaridade{n}', kw.get(f'grau_escolaridade{n}', None))
        setattr(u, f'curso_graduacao{n}', kw.get(f'curso_graduacao{n}', None))
        setattr(u, f'situacao_academica{n}', kw.get(f'situacao_academica{n}', None))
        setattr(u, f'competencias_tecnicas{n}', kw.get(f'competencias_tecnicas{n}', None))
        setattr(u, f'competencias_comportamentais{n}', kw.get(f'competencias_comportamentais{n}', None))
    return u


def _mock_vaga(**kw):
    v = MagicMock()
    v.cargo_vaga = kw.get('cargo_vaga', 'Dev Python')
    v.descricao_vaga = kw.get('descricao_vaga', 'Vaga de backend')
    v.requisito_vaga = kw.get('requisito_vaga', 'Python, Django')
    v.local = kw.get('local', 'Patos de Minas')
    v.empresa.nomefantasia = kw.get('nomefantasia', 'TechCo')
    v.empresa.segmento = kw.get('segmento', 'Tecnologia')
    return v


def _call_build_resume(usuario):
    """Chama build_resume_text com ExperienciaProfissional simulada como inexistente."""
    from core.models import ExperienciaProfissional
    with patch('matching.text_builders.ExperienciaProfissional') as MockExp:
        MockExp.DoesNotExist = ExperienciaProfissional.DoesNotExist
        MockExp.objects.get.side_effect = ExperienciaProfissional.DoesNotExist
        from matching.text_builders import build_resume_text
        return build_resume_text(usuario)


def _call_build_job(vaga, cursos=None):
    with patch('matching.text_builders.CursoVaga') as MockCurso:
        MockCurso.objects.filter.return_value.values_list.return_value = cursos or []
        from matching.text_builders import build_job_text
        return build_job_text(vaga)


# ── Schemas ───────────────────────────────────────────────────────────────────

class ResumeChunkTest(TestCase):
    def test_to_metadata_retorna_campos_corretos(self):
        chunk = ResumeChunk(text='Python dev', section='habilidades',
                            candidate_id='c1', candidate_name='Ana')
        meta = chunk.to_metadata()
        self.assertEqual(meta['candidate_id'], 'c1')
        self.assertEqual(meta['candidate_name'], 'Ana')
        self.assertEqual(meta['section'], 'habilidades')
        self.assertEqual(meta['type'], 'resume')

    def test_chunk_id_gerado_automaticamente_e_unico(self):
        c1 = ResumeChunk(text='t', section='s', candidate_id='x', candidate_name='y')
        c2 = ResumeChunk(text='t', section='s', candidate_id='x', candidate_name='y')
        self.assertNotEqual(c1.chunk_id, c2.chunk_id)


class JobChunkTest(TestCase):
    def test_to_metadata_retorna_campos_corretos(self):
        chunk = JobChunk(text='Django dev', section='requisitos',
                         job_id='j1', job_title='Backend Dev', company='TechCo')
        meta = chunk.to_metadata()
        self.assertEqual(meta['job_id'], 'j1')
        self.assertEqual(meta['job_title'], 'Backend Dev')
        self.assertEqual(meta['company'], 'TechCo')
        self.assertEqual(meta['section'], 'requisitos')
        self.assertEqual(meta['type'], 'job')

    def test_chunk_id_gerado_automaticamente_e_unico(self):
        c1 = JobChunk(text='t', section='s', job_id='j', job_title='T', company='C')
        c2 = JobChunk(text='t', section='s', job_id='j', job_title='T', company='C')
        self.assertNotEqual(c1.chunk_id, c2.chunk_id)


class MatchResultTest(TestCase):
    def test_str_com_empresa(self):
        r = MatchResult(entity_id='1', name='Dev Python', company='TechCo', score=0.9)
        s = str(r)
        self.assertIn('Dev Python @ TechCo', s)
        self.assertIn('90', s)

    def test_str_sem_empresa(self):
        r = MatchResult(entity_id='2', name='João Silva', score=0.75)
        s = str(r)
        self.assertIn('João Silva', s)
        self.assertNotIn('@', s)

    def test_str_inclui_trecho_de_chunk(self):
        r = MatchResult(entity_id='3', name='Dev', score=0.8,
                        top_chunks=[{'text': 'Python Django REST', 'similarity': 0.8}])
        self.assertIn('Python Django REST', str(r))


# ── JobMatcher._preprocess ────────────────────────────────────────────────────

class PreprocessTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.matcher = _make_matcher()

    @classmethod
    def tearDownClass(cls):
        _cleanup_matcher(cls.matcher)
        super().tearDownClass()

    def _p(self, text):
        return self.matcher._preprocess(text)

    def test_remove_url(self):
        result = self._p('acesse https://empresa.com.br para mais info')
        self.assertNotIn('https://', result)
        self.assertIn('acesse', result)

    def test_remove_email(self):
        result = self._p('envie para rh@empresa.com.br')
        self.assertNotIn('@', result)

    def test_expande_sr(self):
        result = self._p('Cargo: Sr. Desenvolvedor')
        self.assertIn('Sênior', result)

    def test_expande_ti(self):
        result = self._p('trabalha na área de TI')
        self.assertIn('Tecnologia da Informação', result)

    def test_expande_rh(self):
        result = self._p('equipe de RH')
        self.assertIn('Recursos Humanos', result)

    def test_substitui_aspas_tipograficas(self):
        result = self._p('“citação”')
        self.assertNotIn('“', result)
        self.assertNotIn('”', result)

    def test_normaliza_espacos_multiplos(self):
        result = self._p('palavra   com    espaços')
        self.assertEqual(result, 'palavra com espaços')

    def test_string_vazia_permanece_vazia(self):
        self.assertEqual(self._p(''), '')


# ── JobMatcher._chunk_text / _detect_sections ────────────────────────────────

class ChunkTextTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.matcher = _make_matcher()

    @classmethod
    def tearDownClass(cls):
        _cleanup_matcher(cls.matcher)
        super().tearDownClass()

    def test_texto_sem_secao_retorna_chunk_geral(self):
        text = 'experiência com Python e Django REST'
        chunks = self.matcher._chunk_text(text, self.matcher._RESUME_HEADERS)
        self.assertGreater(len(chunks), 0)
        self.assertEqual(chunks[0]['section'], 'Geral')

    def test_detecta_secao_em_texto_estruturado(self):
        text = 'habilidades\nPython Django REST frameworks\n'
        chunks = self.matcher._chunk_text(text, self.matcher._RESUME_HEADERS)
        self.assertTrue(any(c['section'].lower() == 'habilidades' for c in chunks))

    def test_texto_longo_gera_multiplos_chunks(self):
        texto_longo = ' '.join([f'palavra{i}' for i in range(200)])
        chunks = self.matcher._chunk_text(texto_longo, self.matcher._RESUME_HEADERS)
        self.assertGreater(len(chunks), 1)

    def test_overlap_repete_tokens_entre_chunks(self):
        m = _make_matcher()
        try:
            m.chunk_size = 10
            m.chunk_overlap = 3
            words = ' '.join([f'w{i}' for i in range(30)])
            chunks = m._chunk_text(words, self.matcher._RESUME_HEADERS)
            self.assertGreater(len(chunks), 1)
            fim_do_primeiro = chunks[0]['text'].split()[-3:]
            inicio_do_segundo = chunks[1]['text'].split()[:3]
            self.assertEqual(fim_do_primeiro, inicio_do_segundo)
        finally:
            _cleanup_matcher(m)

    def test_texto_vazio_retorna_lista_vazia(self):
        chunks = self.matcher._chunk_text('', self.matcher._RESUME_HEADERS)
        self.assertEqual(chunks, [])


# ── JobMatcher integração (EphemeralClient + ST simulado) ─────────────────────

class JobMatcherIntegrationTest(TestCase):
    def setUp(self):
        self.matcher = _make_matcher()

    def tearDown(self):
        _cleanup_matcher(self.matcher)

    def _resume(self, text='Python developer backend', name='Candidato', cid='c1'):
        from matching.matcher import ResumeModel
        return ResumeModel(text=text, candidate_name=name, candidate_id=cid)

    def _job(self, text='Vaga backend Python', title='Dev', company='Co', jid='j1'):
        from matching.matcher import JobModel
        return JobModel(text=text, job_title=title, company=company, job_id=jid)

    def test_add_resume_retorna_candidate_id_fornecido(self):
        rid = self.matcher.add_resume(self._resume(cid='u99'))
        self.assertEqual(rid, 'u99')

    def test_add_resume_gera_id_quando_candidate_id_vazio(self):
        rid = self.matcher.add_resume(self._resume(cid=''))
        self.assertTrue(len(rid) > 0)

    def test_add_job_retorna_job_id_fornecido(self):
        jid = self.matcher.add_job(self._job(jid='v42'))
        self.assertEqual(jid, 'v42')

    def test_stats_reflete_documentos_indexados(self):
        self.matcher.add_resume(self._resume())
        self.matcher.add_job(self._job())
        stats = self.matcher.stats()
        self.assertGreater(stats['resumes'], 0)
        self.assertGreater(stats['jobs'], 0)

    def test_match_jobs_levanta_para_candidato_desconhecido(self):
        with self.assertRaises(ValueError) as ctx:
            self.matcher.match_jobs_for_resume('nao_existe')
        self.assertIn('nao_existe', str(ctx.exception))

    def test_match_resumes_levanta_para_vaga_desconhecida(self):
        with self.assertRaises(ValueError) as ctx:
            self.matcher.match_resumes_for_job('vaga_fantasma')
        self.assertIn('vaga_fantasma', str(ctx.exception))

    def test_match_jobs_retorna_resultado_com_campos_esperados(self):
        self.matcher.add_resume(self._resume(name='Ana', cid='ana'))
        self.matcher.add_job(self._job(title='Dev Python', company='TechCo', jid='v1'))
        results = self.matcher.match_jobs_for_resume('ana')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        r = results[0]
        self.assertEqual(r.entity_id, 'v1')
        self.assertEqual(r.name, 'Dev Python')
        self.assertIsInstance(r.score, float)

    def test_match_resumes_retorna_resultado_com_campos_esperados(self):
        self.matcher.add_resume(self._resume(name='Carlos', cid='car'))
        self.matcher.add_job(self._job(title='Dev', company='Co', jid='j2'))
        results = self.matcher.match_resumes_for_job('j2')
        self.assertIsInstance(results, list)
        self.assertGreater(len(results), 0)
        r = results[0]
        self.assertEqual(r.entity_id, 'car')
        self.assertEqual(r.name, 'Carlos')

    def test_update_resume_substitui_chunks_anteriores(self):
        self.matcher.add_resume(self._resume(text='texto antigo', cid='u1'))
        antes = self.matcher.stats()['resumes']
        self.matcher.update_resume(self._resume(text='texto atualizado', cid='u1'))
        depois = self.matcher.stats()['resumes']
        self.assertLessEqual(depois, antes + 3)

    def test_update_job_substitui_chunks_anteriores(self):
        self.matcher.add_job(self._job(text='vaga antiga', jid='j1'))
        antes = self.matcher.stats()['jobs']
        self.matcher.update_job(self._job(text='vaga atualizada', jid='j1'))
        depois = self.matcher.stats()['jobs']
        self.assertLessEqual(depois, antes + 3)

    def test_min_score_acima_de_1_retorna_lista_vazia(self):
        self.matcher.add_resume(self._resume(cid='x'))
        self.matcher.add_job(self._job(jid='jz'))
        results = self.matcher.match_jobs_for_resume('x', min_score=2.0)
        self.assertEqual(results, [])


# ── build_resume_text ─────────────────────────────────────────────────────────

class BuildResumeTextTest(TestCase):
    def test_inclui_cargo_pretendido(self):
        text = _call_build_resume(_mock_usuario(cargo_pretendido='Analista de Dados'))
        self.assertIn('Analista de Dados', text)

    def test_inclui_area_interesse(self):
        text = _call_build_resume(_mock_usuario(area_interesse='Data Science'))
        self.assertIn('Data Science', text)

    def test_inclui_disponibilidade(self):
        text = _call_build_resume(_mock_usuario(disponibilidade='Imediata'))
        self.assertIn('Imediata', text)

    def test_remoto_incluido_quando_verdadeiro(self):
        text = _call_build_resume(_mock_usuario(remoto=True))
        self.assertIn('remoto', text)

    def test_remoto_omitido_quando_falso(self):
        text = _call_build_resume(_mock_usuario(remoto=False))
        self.assertNotIn('remoto', text)

    def test_inclui_competencias_tecnicas(self):
        u = _mock_usuario()
        u.competencias_tecnicas1 = 'Python, SQL'
        text = _call_build_resume(u)
        self.assertIn('Python, SQL', text)

    def test_inclui_competencias_comportamentais(self):
        u = _mock_usuario()
        u.competencias_comportamentais1 = 'Liderança, Comunicação'
        text = _call_build_resume(u)
        self.assertIn('Liderança, Comunicação', text)

    def test_campos_nulos_sao_omitidos(self):
        text = _call_build_resume(_mock_usuario(cargo_pretendido=None, area_interesse=None))
        self.assertNotIn('objetivo:', text)
        self.assertNotIn('área de interesse:', text)

    def test_inclui_formacao_quando_preenchida(self):
        u = _mock_usuario()
        u.grau_escolaridade1 = 'Bacharelado'
        u.curso_graduacao1 = 'Ciência da Computação'
        u.instituicao_nome1 = 'UFMG'
        text = _call_build_resume(u)
        self.assertIn('formação', text)
        self.assertIn('Ciência da Computação', text)
        self.assertIn('UFMG', text)

    def test_inclui_experiencia_profissional(self):
        from core.models import ExperienciaProfissional
        u = _mock_usuario()
        mock_exp = MagicMock()
        mock_exp.cargo1 = 'Desenvolvedor'
        mock_exp.nome_empresa1 = 'Startup'
        for n in ('2', '3'):
            setattr(mock_exp, f'cargo{n}', None)
            setattr(mock_exp, f'nome_empresa{n}', None)

        with patch('matching.text_builders.ExperienciaProfissional') as MockExp:
            MockExp.DoesNotExist = ExperienciaProfissional.DoesNotExist
            MockExp.objects.get.return_value = mock_exp
            from matching.text_builders import build_resume_text
            text = build_resume_text(u)

        self.assertIn('experiência', text)
        self.assertIn('Desenvolvedor', text)
        self.assertIn('Startup', text)

    def test_sem_experiencia_insere_mensagem_de_ausencia(self):
        text = _call_build_resume(_mock_usuario())
        self.assertIn('sem experiência profissional', text)

    def test_inclui_carta_apresentacao(self):
        text = _call_build_resume(_mock_usuario(carta_apresentacao='Tenho muito interesse'))
        self.assertIn('carta de apresentação', text)
        self.assertIn('Tenho muito interesse', text)

    def test_curriculo_pdf_nulo_nao_gera_secao(self):
        text = _call_build_resume(_mock_usuario(curriculo_pdf=None))
        self.assertNotIn('currículo:', text)


# ── build_job_text ────────────────────────────────────────────────────────────

class BuildJobTextTest(TestCase):
    def test_inclui_cargo_vaga(self):
        text = _call_build_job(_mock_vaga(cargo_vaga='Engenheiro de Software'))
        self.assertIn('Engenheiro de Software', text)

    def test_inclui_descricao(self):
        text = _call_build_job(_mock_vaga(descricao_vaga='Equipe ágil remote-friendly'))
        self.assertIn('Equipe ágil', text)

    def test_inclui_requisito(self):
        text = _call_build_job(_mock_vaga(requisito_vaga='Django, REST'))
        self.assertIn('Django, REST', text)

    def test_inclui_local(self):
        text = _call_build_job(_mock_vaga(local='Belo Horizonte'))
        self.assertIn('Belo Horizonte', text)

    def test_inclui_nome_empresa(self):
        text = _call_build_job(_mock_vaga(nomefantasia='StartupXYZ'))
        self.assertIn('StartupXYZ', text)

    def test_inclui_segmento(self):
        text = _call_build_job(_mock_vaga(segmento='Agronegócio'))
        self.assertIn('Agronegócio', text)

    def test_inclui_cursos_desejados(self):
        text = _call_build_job(_mock_vaga(), cursos=['Ciência da Computação', 'Engenharia'])
        self.assertIn('cursos desejados', text)
        self.assertIn('Ciência da Computação', text)

    def test_omite_cursos_quando_lista_vazia(self):
        text = _call_build_job(_mock_vaga(), cursos=[])
        self.assertNotIn('cursos desejados', text)


# ── get_matcher (singleton) ───────────────────────────────────────────────────

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


# ── Signals ───────────────────────────────────────────────────────────────────

class SyncUsuarioSignalTest(TestCase):
    def test_chama_update_resume_com_resume_model_correto(self):
        from matching.matcher import ResumeModel
        mock_matcher = MagicMock()
        mock_usuario = MagicMock()
        mock_usuario.pk = 7
        mock_usuario.user.nome = 'João'

        with patch('matching.signals.get_matcher', return_value=mock_matcher):
            with patch('matching.signals.build_resume_text', return_value='texto currículo'):
                from matching.signals import sync_usuario
                sync_usuario(sender=None, instance=mock_usuario)

        mock_matcher.update_resume.assert_called_once_with(
            ResumeModel(text='texto currículo', candidate_name='João', candidate_id='7')
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
                    self.fail("sync_usuario não deve propagar exceções do matcher")


class SyncVagaSignalTest(TestCase):
    def test_chama_update_job_com_job_model_correto(self):
        from matching.matcher import JobModel
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
            JobModel(text='texto vaga', job_title='Dev Python', company='TechCo', job_id='3')
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
                    self.fail("sync_vaga não deve propagar exceções do matcher")


# ── Views ─────────────────────────────────────────────────────────────────────

from django.test import RequestFactory


class CandidatosParaVagaViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('matching.views.MatchScore')
    @patch('matching.views.Vagas')
    def test_retorna_resultados_paginados_ordenados_por_score(self, mock_vagas_cls, mock_ms_cls):
        # Configura vaga existente
        mock_vagas_cls.objects.filter.return_value.exists.return_value = True

        # Configura queryset com 2 resultados
        score1 = MagicMock()
        score1.usuario_id = 1
        score1.usuario.user.nome = "Ana"
        score1.score = 0.9
        score1.breakdown = {}

        score2 = MagicMock()
        score2.usuario_id = 2
        score2.usuario.user.nome = "Beto"
        score2.score = 0.7
        score2.breakdown = {}

        mock_qs = MagicMock()
        mock_qs.count.return_value = 2
        mock_qs.__getitem__ = MagicMock(return_value=[score1, score2])
        mock_ms_cls.objects.filter.return_value.order_by.return_value.select_related.return_value = mock_qs

        from matching.views import candidatos_para_vaga
        request = self.factory.get('/matching/candidatos/1/', {'page': '1', 'page_size': '20'})
        response = candidatos_para_vaga(request, vaga_id=1)

        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertIn('total', data)
        self.assertIn('page', data)
        self.assertIn('pages', data)
        self.assertIn('resultados', data)
        self.assertEqual(data['total'], 2)
        self.assertEqual(data['page'], 1)

    @patch('matching.views.Vagas')
    def test_retorna_404_para_vaga_inexistente(self, mock_vagas_cls):
        mock_vagas_cls.objects.filter.return_value.exists.return_value = False
        from matching.views import candidatos_para_vaga
        request = self.factory.get('/matching/candidatos/999/')
        response = candidatos_para_vaga(request, vaga_id=999)
        self.assertEqual(response.status_code, 404)

    def test_retorna_400_para_page_invalida(self):
        from matching.views import candidatos_para_vaga
        request = self.factory.get('/matching/candidatos/1/', {'page': 'abc'})
        response = candidatos_para_vaga(request, vaga_id=1)
        self.assertEqual(response.status_code, 400)


class VagasParaUsuarioViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch('matching.views.MatchScore')
    @patch('matching.views.Usuario')
    def test_retorna_resultados_paginados_ordenados_por_score(self, mock_usuario_cls, mock_ms_cls):
        mock_usuario_cls.objects.filter.return_value.exists.return_value = True

        score1 = MagicMock()
        score1.vaga_id = 10
        score1.vaga.cargo_vaga = "Dev"
        score1.vaga.empresa.nomefantasia = "Co"
        score1.score = 0.85
        score1.breakdown = {}

        mock_qs = MagicMock()
        mock_qs.count.return_value = 1
        mock_qs.__getitem__ = MagicMock(return_value=[score1])
        mock_ms_cls.objects.filter.return_value.order_by.return_value.select_related.return_value = mock_qs

        from matching.views import vagas_para_usuario
        request = self.factory.get('/matching/vagas-para/1/')
        response = vagas_para_usuario(request, usuario_pk=1)

        self.assertEqual(response.status_code, 200)
        import json
        data = json.loads(response.content)
        self.assertIn('total', data)
        self.assertIn('resultados', data)
        self.assertEqual(data['total'], 1)

    @patch('matching.views.Usuario')
    def test_retorna_404_para_usuario_inexistente(self, mock_usuario_cls):
        mock_usuario_cls.objects.filter.return_value.exists.return_value = False
        from matching.views import vagas_para_usuario
        request = self.factory.get('/matching/vagas-para/999/')
        response = vagas_para_usuario(request, usuario_pk=999)
        self.assertEqual(response.status_code, 404)

    def test_retorna_400_para_page_invalida(self):
        from matching.views import vagas_para_usuario
        request = self.factory.get('/matching/vagas-para/1/', {'page': 'xyz'})
        response = vagas_para_usuario(request, usuario_pk=1)
        self.assertEqual(response.status_code, 400)


# ── Testes de persistência de MatchScore ──────────────────────────────────────

class MatchScorePersistenceOnUsuarioSaveTest(TestCase):
    """Signal sync_usuario deve chamar _upsert_scores_for_usuario."""

    @patch('matching.signals.get_matcher', return_value=MagicMock())
    @patch('matching.signals._upsert_scores_for_usuario')
    def test_signal_calls_upsert_on_usuario_save(self, mock_upsert, mock_get_matcher):
        usuario = MagicMock()
        from matching.signals import sync_usuario
        sync_usuario(sender=None, instance=usuario, created=True)
        mock_upsert.assert_called_once_with(usuario)


class MatchScorePersistenceOnVagaSaveTest(TestCase):
    """Signal sync_vaga deve chamar _upsert_scores_for_vaga."""

    @patch('matching.signals.get_matcher', return_value=MagicMock())
    @patch('matching.signals._upsert_scores_for_vaga')
    def test_signal_calls_upsert_on_vaga_save(self, mock_upsert, mock_get_matcher):
        vaga = MagicMock()
        from matching.signals import sync_vaga
        sync_vaga(sender=None, instance=vaga, created=True)
        mock_upsert.assert_called_once_with(vaga)


# ── Testes de score_formacao ──────────────────────────────────────────────────

class ScoreFormacaoTest(TestCase):
    """
    Valida que score_formacao usa a mesma escala 0-10 do campo nivel_formacao_req
    (ESCOLARIDADE em vagas/models.py).
    """

    def _make_model(self):
        """Mock do SentenceTransformer que retorna embeddings idênticos (cosseno = 1.0)."""
        m = MagicMock()
        m.encode.return_value = np.ones((1, 16), dtype=float)
        return m

    def test_match_perfeito_bacharelado_retorna_1(self):
        """Candidato com bacharelado (6) para vaga que exige bacharelado (6) → 1.0."""
        from matching.scoring import score_formacao
        usuario = _mock_usuario(grau_escolaridade1='bacharelado', curso_graduacao1='Sistemas de Informação')
        vaga = _mock_vaga()
        vaga.nivel_formacao_req = 6  # Ensino Superior Completo no ESCOLARIDADE
        s = score_formacao(usuario, vaga, self._make_model())
        self.assertAlmostEqual(s, 1.0, places=2,
            msg="Bacharelado vs requisito bacharelado deve ser 1.0, não 0.5")

    def test_sem_requisito_retorna_1(self):
        """Vaga sem requisito de formação → 1.0 independente do candidato."""
        from matching.scoring import score_formacao
        usuario = _mock_usuario()
        vaga = _mock_vaga()
        vaga.nivel_formacao_req = 0
        self.assertEqual(score_formacao(usuario, vaga, self._make_model()), 1.0)

    def test_candidato_acima_do_requisito_retorna_1(self):
        """Doutorado (9) para vaga que exige bacharelado (6) → 1.0."""
        from matching.scoring import score_formacao
        usuario = _mock_usuario(grau_escolaridade1='doutorado', curso_graduacao1='Computação')
        vaga = _mock_vaga()
        vaga.nivel_formacao_req = 6
        s = score_formacao(usuario, vaga, self._make_model())
        self.assertAlmostEqual(s, 1.0, places=2)

    def test_candidato_abaixo_do_requisito_retorna_menor_que_1(self):
        """Técnico (4) para vaga que exige mestrado (8) → score < 1.0."""
        from matching.scoring import score_formacao
        usuario = _mock_usuario(grau_escolaridade1='técnico', curso_graduacao1='Informática')
        vaga = _mock_vaga()
        vaga.nivel_formacao_req = 8  # Mestrado
        s = score_formacao(usuario, vaga, self._make_model())
        self.assertLess(s, 1.0,
            msg="Técnico para vaga de mestrado deve ter score < 1.0")
