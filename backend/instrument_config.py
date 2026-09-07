"""
Configuração centralizada de instrumentos, tonalidades e PDFs
Garante que o mapeamento é único e não está espalhado no código.
"""

from pathlib import Path
import unicodedata

try:
    from .resource_paths import get_resource_path
except ImportError:
    from resource_paths import get_resource_path

# ==================== DIRETÓRIOS DE PDF ====================
# O sistema procura somente nos diretórios reais do projeto e nunca usa um PDF genérico de outro instrumento.
PROJECT_ROOT = get_resource_path()
PDF_SEARCH_DIRS = [
    PROJECT_ROOT / 'pdfs',
    PROJECT_ROOT / 'backend' / 'pdfs',
    Path(__file__).resolve().parent / 'pdfs',
]


def get_project_pdf_root():
    """Retorna a pasta raiz do projeto onde os PDFs locais devem ficar."""
    return PROJECT_ROOT / 'pdfs'


def normalize_instrument_key(instrument_id):
    """Normaliza o nome do instrumento para comparação segura."""
    if not instrument_id:
        return ''
    value = str(instrument_id).strip().lower()
    value = unicodedata.normalize('NFKD', value)
    value = value.encode('ascii', 'ignore').decode('ascii')
    value = value.replace(' ', '_').replace('-', '_')
    return ''.join(ch for ch in value if ch.isalnum() or ch == '_').strip('_')

# ==================== MAPEAMENTO INSTRUMENTO → TONALIDADE ====================
# Define qual tonalidade cada instrumento deve usar

INSTRUMENT_TO_TONALITY = {
    # Geral / teclado
    'teclado': 'do',
    'orgao_eletronico': 'do',
    'orgao': 'do',

    # Sopros em Sib
    'saxofone_soprano': 'sib',
    'saxofone_alto': 'sib',
    'saxofone_tenor': 'sib',
    'saxofone_baritono': 'sib',
    'clarinete': 'sib',
    'clarinete_soprano': 'sib',
    'trompete': 'sib',
    'trompa': 'sib',
    'trompa_sib': 'sib',
    'cornet': 'sib',
    'flugelhorn': 'sib',
    'baritono': 'sib',
    'eufonio': 'sib',

    # Instrumentos em Dó
    'do': 'do',
    'flauta': 'do',
    'violino': 'do',
    'oboe': 'do',
    'oboe_damore': 'do',
    'corne_ingles': 'do',
    'fagote': 'do',

    # Instrumentos em Ré
    're': 're',
    'clarinete_re': 're',

    # Mib 2ª Clave de Sol
    'mib_2s': 'mib_2s',
    'clarinete_mib': 'mib_2s',

    # Instrumentos em Fá
    'fa': 'fa',
    'trompa_fa': 'fa',
    'viola': 'fa',
    'violoncelo': 'fa',

    # Instrumentos em Sol
    'sol': 'sol',
    'alaude': 'sol',

    # Instrumentos em Lá
    'la': 'la',
    'clarinete_la': 'la',

    # Cordas / acompanhamento
    'violao': 'do',
    'guitarra': 'do',
    'baixo': 'do',

    # Voz / percussão
    'canto': 'do',
    'bateria': 'do',
}

# ==================== MAPEAMENTO TONALIDADE → PDF URL ====================
# URLs dos repositórios oficiais de hinários

TONALITY_TO_PDF_URL = {
    'sib': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-sib/master/sib/pdf/final.pdf',
    'do': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-do/master/do/pdf/final.pdf',
    're': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-re/master/re/pdf/final.pdf',
    'mib_2s': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-mib-2s/master/mib-2s/pdf/final.pdf',
    'fa': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-fa/master/fa/pdf/final.pdf',
    'sol': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-sol/master/sol/pdf/final.pdf',
    'la': 'https://raw.githubusercontent.com/eneiasramos/ccb-hinario-5-la/master/la/pdf/final.pdf',
}

# ==================== CONFIGURAÇÃO CENTRALIZADA DO HINÁRIO ====================
# O Hinário sempre usa o PDF local do projeto, por afinação do instrumento atual.
# Não há fallback para outro instrumento nem uso de PDF genérico.
HINARIO_PDFS = {
    'sib': ['hinario_sib.pdf', 'hinario-sib.pdf', 'sib.pdf', 'hnaro.pdf', 'hinario.pdf'],
    'do': ['hinario_do.pdf', 'hinario-do.pdf', 'do.pdf', 'hinario_dó.pdf', 'dó.pdf', 'hino_do.pdf'],
    're': ['hinario_re.pdf', 'hinario-re.pdf', 're.pdf', 'hinario_ré.pdf', 'ré.pdf'],
    'mib_2s': ['hinario_mib2sol.pdf', 'hinario_mib_2s.pdf', 'mib2sol.pdf', 'mib_2s.pdf'],
    'fa': ['hinario_fa.pdf', 'hinario-fa.pdf', 'fa.pdf', 'hinario_fá.pdf', 'fá.pdf'],
    'sol': ['hinario_sol.pdf', 'hinario-sol.pdf', 'sol.pdf'],
    'la': ['hinario_la.pdf', 'hinario-la.pdf', 'la.pdf', 'hinario_lá.pdf', 'lá.pdf'],
}


def get_hinario_config(instrument_id):
    """Retorna a configuração do Hinário para o instrumento atual sem fallback entre instrumentos."""
    if not instrument_id:
        return None

    normalized_id = normalize_instrument_key(instrument_id)
    if not normalized_id:
        return None

    tonality = get_tonality_for_instrument(normalized_id)
    if not tonality:
        return None

    pdf_path = get_hinario_pdf(normalized_id)[0]
    return {
        'instrumento': normalized_id,
        'tonalidade': tonality,
        'pdf_candidates': list(HINARIO_PDFS.get(tonality, [])),
        'pdf_path': str(pdf_path) if pdf_path else None,
        'pdf_filename': pdf_path.name if pdf_path else None,
        'route': '/api/study/pdf/hinario'
    }


def get_hinario_pdf(instrumento):
    """Retorna somente o PDF de Hinário correspondente à afinação do instrumento atual."""
    normalized = normalize_instrument_key(instrumento)
    if not normalized:
        return None, None, 'Instrumento inválido para Hinário.'

    tonality = get_tonality_for_instrument(normalized)
    if not tonality:
        return None, None, f'Instrumento sem afinação definida: {instrumento}'

    pdf_root = get_project_pdf_root()
    if not pdf_root.exists():
        return None, pdf_root, f'PDF do Hinário não encontrado para este instrumento/afinação: {instrumento} ({tonality}). Caminho esperado: {pdf_root}'

    candidates = set()
    for name in HINARIO_PDFS.get(tonality, []):
        candidates.add(normalize_pdf_name(name))
    candidates.add(normalize_pdf_name(tonality))
    candidates.add(f'{normalize_pdf_name(tonality)}.pdf')
    candidates.add(f'hinario_{normalize_pdf_name(tonality)}.pdf')

    for item in sorted(pdf_root.iterdir(), key=lambda p: p.name.lower()):
        if not item.is_file() or item.suffix.lower() != '.pdf':
            continue

        normalized_name = normalize_pdf_name(item.name)
        if normalized_name in candidates:
            absolute_path = item.resolve()
            try:
                absolute_path.relative_to(PROJECT_ROOT.resolve())
            except ValueError:
                continue
            return absolute_path, absolute_path, None

        if normalized_name.startswith('hinario_') and normalized_name.endswith(f'_{normalize_pdf_name(tonality)}.pdf'):
            absolute_path = item.resolve()
            return absolute_path, absolute_path, None

        if normalized_name == normalize_pdf_name(tonality) or normalized_name.startswith(normalize_pdf_name(tonality)):
            absolute_path = item.resolve()
            return absolute_path, absolute_path, None

    expected = HINARIO_PDFS.get(tonality, [f'hinario_{tonality}.pdf'])[0]
    return None, pdf_root / expected, f'PDF do Hinário não encontrado para este instrumento/afinação. Instrumento: {instrumento}; Afinação: {tonality}; Caminho esperado: {pdf_root / expected}'


def resolve_hinario_pdf_path(instrument_id):
    """Resolve o PDF local do Hinário para o instrumento atual, sem fallback para outro instrumento."""
    if not instrument_id:
        return None

    normalized_id = normalize_instrument_key(instrument_id)
    if not normalized_id:
        return None

    pdf_file, _, error = get_hinario_pdf(normalized_id)
    if error:
        return None
    return pdf_file

# ==================== LISTA DE INSTRUMENTOS DISPONÍVEIS ====================
# Para exibir no dropdown de seleção de instrumento

AVAILABLE_INSTRUMENTS = [
    {'id': 'teclado', 'name': 'Teclado', 'tonalidade': 'Dó'},
    {'id': 'orgao_eletronico', 'name': 'Órgão Eletrônico', 'tonalidade': 'Dó'},
    {'id': 'violao', 'name': 'Violão', 'tonalidade': 'Dó'},
    {'id': 'guitarra', 'name': 'Guitarra', 'tonalidade': 'Dó'},
    {'id': 'baixo', 'name': 'Baixo', 'tonalidade': 'Dó'},
    {'id': 'violino', 'name': 'Violino', 'tonalidade': 'Dó'},
    {'id': 'viola', 'name': 'Viola', 'tonalidade': 'Fá'},
    {'id': 'violoncelo', 'name': 'Violoncelo', 'tonalidade': 'Fá'},
    {'id': 'flauta', 'name': 'Flauta', 'tonalidade': 'Dó'},
    {'id': 'oboe', 'name': 'Oboé', 'tonalidade': 'Dó'},
    {'id': 'oboe_damore', 'name': 'Oboé d’Amore', 'tonalidade': 'Dó'},
    {'id': 'corne_ingles', 'name': 'Corne Inglês', 'tonalidade': 'Dó'},
    {'id': 'fagote', 'name': 'Fagote', 'tonalidade': 'Dó'},
    {'id': 'clarinete', 'name': 'Clarinete', 'tonalidade': 'Sib'},
    {'id': 'clarinete_soprano', 'name': 'Clarinete Soprano', 'tonalidade': 'Sib'},
    {'id': 'clarinete_re', 'name': 'Clarinete em Ré', 'tonalidade': 'Ré'},
    {'id': 'clarinete_mib', 'name': 'Clarinete em Mib', 'tonalidade': 'Mib - 2ª Clave'},
    {'id': 'clarinete_la', 'name': 'Clarinete em Lá', 'tonalidade': 'Lá'},
    {'id': 'saxofone_soprano', 'name': 'Saxofone Soprano', 'tonalidade': 'Sib'},
    {'id': 'saxofone_alto', 'name': 'Saxofone Alto', 'tonalidade': 'Sib'},
    {'id': 'saxofone_tenor', 'name': 'Saxofone Tenor', 'tonalidade': 'Sib'},
    {'id': 'saxofone_baritono', 'name': 'Saxofone Barítono', 'tonalidade': 'Sib'},
    {'id': 'trompete', 'name': 'Trompete', 'tonalidade': 'Sib'},
    {'id': 'trompa', 'name': 'Trompa', 'tonalidade': 'Sib'},
    {'id': 'trompa_sib', 'name': 'Trompa em Sib', 'tonalidade': 'Sib'},
    {'id': 'trompa_fa', 'name': 'Trompa em Fá', 'tonalidade': 'Fá'},
    {'id': 'trombone', 'name': 'Trombone', 'tonalidade': 'Sib'},
    {'id': 'baritono', 'name': 'Barítono', 'tonalidade': 'Sib'},
    {'id': 'eufonio', 'name': 'Eufônio', 'tonalidade': 'Sib'},
    {'id': 'tuba', 'name': 'Tuba', 'tonalidade': 'Sib'},
    {'id': 'cornet', 'name': 'Cornet', 'tonalidade': 'Sib'},
    {'id': 'flugelhorn', 'name': 'Flugelhorn', 'tonalidade': 'Sib'},
    {'id': 'do', 'name': 'Instrumentos em Dó', 'tonalidade': 'Dó'},
    {'id': 're', 'name': 'Instrumentos em Ré', 'tonalidade': 'Ré'},
    {'id': 'mib_2s', 'name': 'Mib - 2ª Clave de Sol', 'tonalidade': 'Mib - 2ª Clave'},
    {'id': 'fa', 'name': 'Instrumentos em Fá', 'tonalidade': 'Fá'},
    {'id': 'sol', 'name': 'Instrumentos em Sol', 'tonalidade': 'Sol'},
    {'id': 'alaude', 'name': 'Alaúde', 'tonalidade': 'Sol'},
    {'id': 'la', 'name': 'Instrumentos em Lá', 'tonalidade': 'Lá'},
    {'id': 'canto', 'name': 'Canto', 'tonalidade': 'Dó'},
    {'id': 'bateria', 'name': 'Bateria / Percussão', 'tonalidade': 'Dó'},
]

# ==================== CONFIGURAÇÃO CENTRALIZADA DO MÉTODO ====================
# Cada instrumento deve possuir uma configuração explícita e não pode usar PDF de outro instrumento como fallback.
# Se um PDF real não existir, o sistema informa exatamente qual instrumento está sem arquivo em vez de abrir outro.

METHOD_PDF_FILE_MAP = {
    'teclado': 'teclado.pdf',
    'orgao_eletronico': 'orgao_eletronico.pdf',
    'organo': 'orgao_eletronico.pdf',
    'violao': 'violao.pdf',
    'guitarra': 'guitarra.pdf',
    'baixo': 'baixo.pdf',
    'violino': 'violino.pdf',
    'viola': 'viola.pdf',
    'violoncelo': 'violoncelo.pdf',
    'flauta': 'flauta.pdf',
    'oboe': 'oboe.pdf',
    'oboe_damore': 'oboe_damore.pdf',
    'corne_ingles': 'corne_ingles.pdf',
    'fagote': 'fagote.pdf',
    'clarinete': 'clarinete.pdf',
    'clarinete_soprano': 'clarinete.pdf',
    'clarinete_re': 'clarinete_re.pdf',
    'clarinete_mib': 'clarinete_mib.pdf',
    'clarinete_la': 'clarinete_la.pdf',
    'saxofone_soprano': 'saxofone.pdf',
    'saxofone_alto': 'saxofone.pdf',
    'saxofone_tenor': 'saxofone.pdf',
    'saxofone_baritono': 'saxofone.pdf',
    'trompete': 'trompete.pdf',
    'trompa': 'trompa.pdf',
    'trompa_sib': 'trompa.pdf',
    'trompa_fa': 'trompa_fa.pdf',
    'trombone': 'trombone.pdf',
    'baritono': 'baritono.pdf',
    'eufonio': 'eufonio.pdf',
    'tuba': 'tuba.pdf',
    'cornet': 'cornet.pdf',
    'flugelhorn': 'flugelhorn.pdf',
    'do': 'do.pdf',
    're': 're.pdf',
    'mib_2s': 'mib_2s.pdf',
    'fa': 'fa.pdf',
    'sol': 'sol.pdf',
    'alaude': 'alaude.pdf',
    'la': 'la.pdf',
    'canto': 'canto.pdf',
    'bateria': 'bateria.pdf',
}

METHOD_CONFIG = {
    'teclado': {'instrument': 'teclado', 'nome': 'Teclado', 'metodo': 'Método de Teclado', 'pdf_filename': METHOD_PDF_FILE_MAP.get('teclado'), 'pdf_url': None, 'fases': []},
    'orgao_eletronico': {'instrument': 'orgao_eletronico', 'nome': 'Órgão Eletrônico', 'metodo': 'Método de Órgão Eletrônico', 'pdf_filename': METHOD_PDF_FILE_MAP.get('orgao_eletronico'), 'pdf_url': None, 'fases': []},
    'orgao': {'instrument': 'orgao', 'nome': 'Órgão', 'metodo': 'Método de Órgão', 'pdf_filename': METHOD_PDF_FILE_MAP.get('orgao'), 'pdf_url': None, 'fases': []},
    'violao': {'instrument': 'violao', 'nome': 'Violão', 'metodo': 'Método de Violão', 'pdf_filename': METHOD_PDF_FILE_MAP.get('violao'), 'pdf_url': None, 'fases': []},
    'guitarra': {'instrument': 'guitarra', 'nome': 'Guitarra', 'metodo': 'Método de Guitarra', 'pdf_filename': METHOD_PDF_FILE_MAP.get('guitarra'), 'pdf_url': None, 'fases': []},
    'baixo': {'instrument': 'baixo', 'nome': 'Baixo', 'metodo': 'Método de Baixo', 'pdf_filename': METHOD_PDF_FILE_MAP.get('baixo'), 'pdf_url': None, 'fases': []},
    'violino': {'instrument': 'violino', 'nome': 'Violino', 'metodo': 'Método de Violino', 'pdf_filename': METHOD_PDF_FILE_MAP.get('violino'), 'pdf_url': None, 'fases': []},
    'viola': {'instrument': 'viola', 'nome': 'Viola', 'metodo': 'Método de Viola', 'pdf_filename': METHOD_PDF_FILE_MAP.get('viola'), 'pdf_url': None, 'fases': []},
    'violoncelo': {'instrument': 'violoncelo', 'nome': 'Violoncelo', 'metodo': 'Método de Violoncelo', 'pdf_filename': METHOD_PDF_FILE_MAP.get('violoncelo'), 'pdf_url': None, 'fases': []},
    'flauta': {'instrument': 'flauta', 'nome': 'Flauta', 'metodo': 'Método de Flauta', 'pdf_filename': METHOD_PDF_FILE_MAP.get('flauta'), 'pdf_url': None, 'fases': []},
    'oboe': {'instrument': 'oboe', 'nome': 'Oboé', 'metodo': 'Método de Oboé', 'pdf_filename': METHOD_PDF_FILE_MAP.get('oboe'), 'pdf_url': None, 'fases': []},
    'oboe_damore': {'instrument': 'oboe_damore', 'nome': 'Oboé d’Amore', 'metodo': 'Método de Oboé d’Amore', 'pdf_filename': METHOD_PDF_FILE_MAP.get('oboe_damore'), 'pdf_url': None, 'fases': []},
    'corne_ingles': {'instrument': 'corne_ingles', 'nome': 'Corne Inglês', 'metodo': 'Método de Corne Inglês', 'pdf_filename': METHOD_PDF_FILE_MAP.get('corne_ingles'), 'pdf_url': None, 'fases': []},
    'fagote': {'instrument': 'fagote', 'nome': 'Fagote', 'metodo': 'Método de Fagote', 'pdf_filename': METHOD_PDF_FILE_MAP.get('fagote'), 'pdf_url': None, 'fases': []},
    'clarinete': {'instrument': 'clarinete', 'nome': 'Clarinete', 'metodo': 'Método de Clarinete', 'pdf_filename': METHOD_PDF_FILE_MAP.get('clarinete'), 'pdf_url': None, 'fases': []},
    'clarinete_soprano': {'instrument': 'clarinete_soprano', 'nome': 'Clarinete Soprano', 'metodo': 'Método de Clarinete Soprano', 'pdf_filename': METHOD_PDF_FILE_MAP.get('clarinete_soprano'), 'pdf_url': None, 'fases': []},
    'clarinete_re': {'instrument': 'clarinete_re', 'nome': 'Clarinete em Ré', 'metodo': 'Método de Clarinete em Ré', 'pdf_filename': METHOD_PDF_FILE_MAP.get('clarinete_re'), 'pdf_url': None, 'fases': []},
    'clarinete_mib': {'instrument': 'clarinete_mib', 'nome': 'Clarinete em Mib', 'metodo': 'Método de Clarinete em Mib', 'pdf_filename': METHOD_PDF_FILE_MAP.get('clarinete_mib'), 'pdf_url': None, 'fases': []},
    'clarinete_la': {'instrument': 'clarinete_la', 'nome': 'Clarinete em Lá', 'metodo': 'Método de Clarinete em Lá', 'pdf_filename': METHOD_PDF_FILE_MAP.get('clarinete_la'), 'pdf_url': None, 'fases': []},
    'saxofone_soprano': {'instrument': 'saxofone_soprano', 'nome': 'Saxofone Soprano', 'metodo': 'Método de Saxofone Soprano', 'pdf_filename': METHOD_PDF_FILE_MAP.get('saxofone_soprano'), 'pdf_url': None, 'fases': []},
    'saxofone_alto': {'instrument': 'saxofone_alto', 'nome': 'Saxofone Alto', 'metodo': 'Método de Saxofone Alto', 'pdf_filename': METHOD_PDF_FILE_MAP.get('saxofone_alto'), 'pdf_url': None, 'fases': []},
    'saxofone_tenor': {'instrument': 'saxofone_tenor', 'nome': 'Saxofone Tenor', 'metodo': 'Método de Saxofone Tenor', 'pdf_filename': METHOD_PDF_FILE_MAP.get('saxofone_tenor'), 'pdf_url': None, 'fases': []},
    'saxofone_baritono': {'instrument': 'saxofone_baritono', 'nome': 'Saxofone Barítono', 'metodo': 'Método de Saxofone Barítono', 'pdf_filename': METHOD_PDF_FILE_MAP.get('saxofone_baritono'), 'pdf_url': None, 'fases': []},
    'trompete': {'instrument': 'trompete', 'nome': 'Trompete', 'metodo': 'Método de Trompete', 'pdf_filename': METHOD_PDF_FILE_MAP.get('trompete'), 'pdf_url': None, 'fases': []},
    'trompa': {'instrument': 'trompa', 'nome': 'Trompa', 'metodo': 'Método de Trompa', 'pdf_filename': METHOD_PDF_FILE_MAP.get('trompa'), 'pdf_url': None, 'fases': []},
    'trompa_sib': {'instrument': 'trompa_sib', 'nome': 'Trompa em Sib', 'metodo': 'Método de Trompa em Sib', 'pdf_filename': METHOD_PDF_FILE_MAP.get('trompa_sib'), 'pdf_url': None, 'fases': []},
    'trompa_fa': {'instrument': 'trompa_fa', 'nome': 'Trompa em Fá', 'metodo': 'Método de Trompa em Fá', 'pdf_filename': METHOD_PDF_FILE_MAP.get('trompa_fa'), 'pdf_url': None, 'fases': []},
    'trombone': {'instrument': 'trombone', 'nome': 'Trombone', 'metodo': 'Método de Trombone', 'pdf_filename': METHOD_PDF_FILE_MAP.get('trombone'), 'pdf_url': None, 'fases': []},
    'baritono': {'instrument': 'baritono', 'nome': 'Barítono', 'metodo': 'Método de Barítono', 'pdf_filename': METHOD_PDF_FILE_MAP.get('baritono'), 'pdf_url': None, 'fases': []},
    'eufonio': {'instrument': 'eufonio', 'nome': 'Eufônio', 'metodo': 'Método de Eufônio', 'pdf_filename': METHOD_PDF_FILE_MAP.get('eufonio'), 'pdf_url': None, 'fases': []},
    'tuba': {'instrument': 'tuba', 'nome': 'Tuba', 'metodo': 'Método de Tuba', 'pdf_filename': METHOD_PDF_FILE_MAP.get('tuba'), 'pdf_url': None, 'fases': []},
    'cornet': {'instrument': 'cornet', 'nome': 'Cornet', 'metodo': 'Método de Cornet', 'pdf_filename': METHOD_PDF_FILE_MAP.get('cornet'), 'pdf_url': None, 'fases': []},
    'flugelhorn': {'instrument': 'flugelhorn', 'nome': 'Flugelhorn', 'metodo': 'Método de Flugelhorn', 'pdf_filename': METHOD_PDF_FILE_MAP.get('flugelhorn'), 'pdf_url': None, 'fases': []},
    'do': {'instrument': 'do', 'nome': 'Instrumentos em Dó', 'metodo': 'Método de Dó', 'pdf_filename': METHOD_PDF_FILE_MAP.get('do'), 'pdf_url': None, 'fases': []},
    're': {'instrument': 're', 'nome': 'Instrumentos em Ré', 'metodo': 'Método de Ré', 'pdf_filename': METHOD_PDF_FILE_MAP.get('re'), 'pdf_url': None, 'fases': []},
    'mib_2s': {'instrument': 'mib_2s', 'nome': 'Mib - 2ª Clave de Sol', 'metodo': 'Método de Mib - 2ª Clave de Sol', 'pdf_filename': METHOD_PDF_FILE_MAP.get('mib_2s'), 'pdf_url': None, 'fases': []},
    'fa': {'instrument': 'fa', 'nome': 'Instrumentos em Fá', 'metodo': 'Método de Fá', 'pdf_filename': METHOD_PDF_FILE_MAP.get('fa'), 'pdf_url': None, 'fases': []},
    'sol': {'instrument': 'sol', 'nome': 'Instrumentos em Sol', 'metodo': 'Método de Sol', 'pdf_filename': METHOD_PDF_FILE_MAP.get('sol'), 'pdf_url': None, 'fases': []},
    'alaude': {'instrument': 'alaude', 'nome': 'Alaúde', 'metodo': 'Método de Alaúde', 'pdf_filename': METHOD_PDF_FILE_MAP.get('alaude'), 'pdf_url': None, 'fases': []},
    'la': {'instrument': 'la', 'nome': 'Instrumentos em Lá', 'metodo': 'Método de Lá', 'pdf_filename': METHOD_PDF_FILE_MAP.get('la'), 'pdf_url': None, 'fases': []},
    'canto': {'instrument': 'canto', 'nome': 'Canto', 'metodo': 'Método de Canto', 'pdf_filename': METHOD_PDF_FILE_MAP.get('canto'), 'pdf_url': None, 'fases': []},
    'bateria': {'instrument': 'bateria', 'nome': 'Bateria / Percussão', 'metodo': 'Método de Bateria', 'pdf_filename': METHOD_PDF_FILE_MAP.get('bateria'), 'pdf_url': None, 'fases': []},
}

# ==================== FUNÇÕES AUXILIARES ====================

def get_tonality_for_instrument(instrument_id):
    """
    Retorna a tonalidade para um instrumento específico
    
    Args:
        instrument_id: ID do instrumento
    
    Returns:
        str: tonalidade (sib, do, re, mib_2s, fa, sol, la) ou None
    """
    if not instrument_id:
        return None
    
    normalized_id = instrument_id.lower().strip()
    return INSTRUMENT_TO_TONALITY.get(normalized_id)


def get_pdf_url_for_instrument(instrument_id):
    """
    Retorna a URL local do Hinário para o instrumento.
    Não usa URL externa do GitHub nem fallback entre instrumentos.
    """
    if not instrument_id:
        return None

    normalized_id = normalize_instrument_key(instrument_id)
    if not normalized_id or get_hinario_config(normalized_id) is None:
        return None

    return '/api/study/pdf/hinario'


def get_pdf_url_for_tonality(tonality):
    """
    Retorna URL do PDF para uma tonalidade específica
    
    Args:
        tonality: ID da tonalidade (sib, do, re, mib_2s, fa, sol, la)
    
    Returns:
        str: URL do PDF ou None
    """
    if not tonality:
        return None
    
    normalized_tonality = tonality.lower().strip()
    return TONALITY_TO_PDF_URL.get(normalized_tonality)


def get_instrument_info(instrument_id):
    """
    Retorna informações completas de um instrumento
    
    Args:
        instrument_id: ID do instrumento
    
    Returns:
        dict: {id, name, tonalidade} ou None
    """
    for inst in AVAILABLE_INSTRUMENTS:
        if inst['id'] == instrument_id:
            return inst
    return None


def normalize_pdf_name(value):
    """Normaliza o nome de arquivo para comparar PDF real com o mapeamento do instrumento."""
    if not value:
        return ''
    text = unicodedata.normalize('NFKD', str(value))
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower().replace(' ', '_').replace('-', '_')
    text = ''.join(ch for ch in text if ch.isalnum() or ch in ['_', '.'])
    return text.strip('.').strip()


def get_available_project_pdfs():
    """Lista PDFs reais presentes na pasta do projeto, sem inferir automaticamente o instrumento."""
    pdf_files = {}
    for base_dir in PDF_SEARCH_DIRS:
        if not base_dir.exists():
            continue
        for item in base_dir.iterdir():
            if item.is_file() and item.suffix.lower() == '.pdf':
                normalized = normalize_pdf_name(item.name)
                pdf_files[normalized] = item.name
    return pdf_files


def get_method_pdf_filename(instrument_id):
    """Retorna o nome do arquivo PDF esperado para este instrumento, sem fallback."""
    if not instrument_id:
        return None

    normalized_id = normalize_instrument_key(instrument_id)
    if not normalized_id:
        return None

    filename = METHOD_PDF_FILE_MAP.get(normalized_id)
    if not filename:
        return None

    if not filename.lower().endswith('.pdf'):
        filename = f'{filename}.pdf'

    normalized_filename = normalize_pdf_name(filename)
    project_pdfs = get_available_project_pdfs()
    if normalized_filename in project_pdfs:
        return project_pdfs[normalized_filename]

    for candidate in project_pdfs:
        if candidate.startswith(normalize_pdf_name(normalized_id)):
            return project_pdfs[candidate]

    return filename


def get_metodo_pdf(instrumento):
    """Retorna o caminho absoluto do PDF do método para o instrumento enviado, sem fallback e sem path traversal."""
    normalized = normalize_instrument_key(instrumento)
    if not normalized:
        return None, None, 'Instrumento inválido'

    filename = get_method_pdf_filename(normalized)
    if not filename:
        return None, None, f'Instrumento: {instrumento}; Arquivo esperado: pdfs/{normalized}.pdf'

    pdf_root = get_project_pdf_root()
    absolute_path = (pdf_root / filename).resolve()
    if not absolute_path.exists() or absolute_path.suffix.lower() != '.pdf':
        return None, absolute_path, f'Instrumento: {instrumento}; Arquivo esperado: pdfs/{filename}; Caminho absoluto procurado: {absolute_path}'

    try:
        absolute_path.relative_to(PROJECT_ROOT.resolve())
    except ValueError:
        return None, absolute_path, f'Instrumento: {instrumento}; Arquivo fora da raiz do projeto: {absolute_path}'

    print(f'[METODO] Instrumento: {instrumento}')
    print(f'[METODO] Arquivo: {filename}')
    print(f'[METODO] PDFS_DIR: {pdf_root}')
    print(f'[METODO] Caminho completo: {absolute_path}')
    print(f'[METODO] Existe: {absolute_path.exists()}')
    return absolute_path, absolute_path, None


def get_method_config(instrument_id):
    """Retorna a configuração do método do instrumento sem qualquer fallback entre instrumentos."""
    if not instrument_id:
        return None

    normalized_id = instrument_id.lower().strip()
    config = METHOD_CONFIG.get(normalized_id)
    if not config:
        return None

    pdf_filename = get_method_pdf_filename(normalized_id)
    return {
        'instrument': config['instrument'],
        'nome': config['nome'],
        'metodo': config['metodo'],
        'pdf_filename': pdf_filename,
        'pdf_url': config['pdf_url'],
        'fases': list(config.get('fases') or [])
    }


def get_method_display_name(instrument_id):
    """Retorna o nome do método para o instrumento atual."""
    config = get_method_config(instrument_id)
    if not config:
        return None
    return config.get('metodo')


def resolve_project_pdf_path(filename):
    """Resolve um nome de PDF de forma segura, sem fallback e sem aceitar path traversal."""
    if not filename:
        return None

    if not isinstance(filename, str):
        return None

    cleaned = str(filename).strip()
    if not cleaned or cleaned.startswith('..') or '/' in cleaned or '\\' in cleaned:
        return None

    candidate_name = cleaned if cleaned.lower().endswith('.pdf') else f'{cleaned}.pdf'
    if candidate_name.startswith('..'):
        return None

    for base_dir in PDF_SEARCH_DIRS:
        candidate = (base_dir / candidate_name).resolve()
        if candidate.is_file() and candidate.suffix.lower() == '.pdf':
            try:
                candidate.relative_to(PROJECT_ROOT.resolve())
                return candidate
            except ValueError:
                pass

    return None


def resolve_method_pdf_path(instrument_id):
    """Resolve o PDF do método para um instrumento específico somente no diretório do projeto."""
    if not instrument_id:
        return None

    normalized_id = normalize_instrument_key(instrument_id)
    if not normalized_id:
        return None

    pdf_file, _, error = get_metodo_pdf(normalized_id)
    if error:
        return None
    return pdf_file


def get_method_pdf_for_instrument(instrument_id):
    """Retorna o PDF associado ao instrumento atual. Não usa fallback de outro instrumento."""
    config = get_method_config(instrument_id)
    if not config:
        return None
    return config.get('pdf_filename')


def validate_method_config(instrument_id, pdf_filename=None):
    """Valida que o PDF pertence ao instrumento solicitado e nunca a outro instrumento."""
    config = get_method_config(instrument_id)
    if not config:
        return False

    if pdf_filename is None:
        return config.get('pdf_filename') is None

    return config.get('pdf_filename') == pdf_filename


def validate_instrument(instrument_id):
    """
    Valida se um instrumento é válido
    
    Args:
        instrument_id: ID do instrumento
    
    Returns:
        bool: True se válido, False caso contrário
    """
    if not instrument_id:
        return False
    
    normalized_id = instrument_id.lower().strip()
    return normalized_id in INSTRUMENT_TO_TONALITY


def get_all_tonalities():
    """
    Retorna lista de todas as tonalidades disponíveis
    
    Returns:
        list: [sib, do, re, mib_2s, fa, sol, la]
    """
    return list(TONALITY_TO_PDF_URL.keys())


# ==================== CONSTANTES ====================

TOTAL_HINOS = 480  # Hinos oficiais 1-430 + Hinos para Jovens 431-480
TOTAL_COROS = 6
TOTAL_ITEMS = TOTAL_HINOS + TOTAL_COROS

HINARIO_DESCRIPTION = f'Hinário com {TOTAL_HINOS} hinos e {TOTAL_COROS} coros - Coletânea completa de música religiosa'
