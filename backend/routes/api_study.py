"""
API de Estudo Musical - MSA, Método, Hinário
Rota principal: /api/study
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from pathlib import Path
import json

try:
    from ..models import db, MSAProgress, HymnProgress, MethodProgress, ChorusProgress, StudySession, PDFViewing, GamificationProgress, CustomInstrumentMethod, log_activity
    from ..instrument_config import (
        get_tonality_for_instrument,
        get_pdf_url_for_instrument,
        get_instrument_info,
        validate_instrument,
        get_method_config,
        get_method_display_name,
        get_method_pdf_for_instrument,
        validate_method_config,
        resolve_method_pdf_path,
        resolve_project_pdf_path,
        get_hinario_config,
        get_hinario_pdf,
        resolve_hinario_pdf_path
    )
except ImportError:
    from models import db, MSAProgress, HymnProgress, MethodProgress, ChorusProgress, StudySession, PDFViewing, GamificationProgress, CustomInstrumentMethod, log_activity
    from instrument_config import (
        get_tonality_for_instrument,
        get_pdf_url_for_instrument,
        get_instrument_info,
        validate_instrument,
        get_method_config,
        get_method_display_name,
        get_method_pdf_for_instrument,
        validate_method_config,
        resolve_method_pdf_path,
        resolve_project_pdf_path,
        get_hinario_config,
        get_hinario_pdf,
        resolve_hinario_pdf_path
    )

study_bp = Blueprint('study', __name__, url_prefix='/api/study')

# ==================== CARREGAMENTO DE ESTRUTURAS ====================

def load_msa_structure():
    """Carrega estrutura do MSA do arquivo JSON"""
    try:
        path = Path(current_app.root_path) / 'data' / 'msa_structure_complete.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar MSA: {e}")
        return None

def load_metodo_structure():
    """Carrega estrutura do Método do arquivo JSON"""
    try:
        path = Path(current_app.root_path) / 'data' / 'metodo_structure_complete.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar Método: {e}")
        return None

def load_hinario_structure():
    """Carrega estrutura do Hinário do arquivo JSON"""
    try:
        path = Path(current_app.root_path) / 'data' / 'hinario_structure_complete.json'
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Erro ao carregar Hinário: {e}")
        return None

def generate_hymn_name(number):
    """Gera nome de hino baseado no número"""
    # Dicionário com nomes reais dos primeiros hinos
    hymn_names = {
        1: "Glória ao Criador", 2: "Louvai ao Rei dos Reis", 3: "Cristo, Rei Divino",
        4: "Firme na Fé", 5: "Doce Comunhão", 6: "Que Paz!", 7: "Graça Divina",
        8: "Sal da Terra", 9: "Guardião Eterno", 10: "Caminho da Vitória",
    }
    return hymn_names.get(number, f"Hino {number}")


def get_user_instrument_for_method():
    """Retorna o instrumento persistido do usuário autenticado."""
    instrumento = (current_user.instrumento or '').strip()
    if not instrumento or not validate_instrument(instrumento):
        raise ValueError('Usuário não possui instrumento válido selecionado')
    return instrumento

# ==================== ROTA: OBTER ESTRUTURA COM PROGRESSO ====================

@study_bp.route('/structure/<area>', methods=['GET'])
@login_required
def get_study_structure(area):
    """
    GET /api/study/structure/<area>
    
    Retorna estrutura de estudo com progresso do usuário
    
    Args:
        area: 'teoria' | 'metodo' | 'hinario'
    
    Query params:
        instrument (opcional): para método (teclado, violao, guitarra, canto)
    """
    
    area = (area or '').lower()
    legacy_aliases = {'msa': 'teoria', 'hinaro': 'hinario'}
    area = legacy_aliases.get(area, area)

    if area not in ['teoria', 'metodo', 'hinario']:
        return jsonify({"error": f"Área inválida: {area}"}), 400

    if area == 'teoria':
        return get_msa_structure()
    elif area == 'metodo':
        return get_metodo_structure()
    elif area == 'hinario':
        return get_hinario_structure()


def get_msa_progress_entries(user_id):
    """Retorna registros do MSA em ambos os nomes de área, para compatibilidade."""
    return MSAProgress.query.filter(
        MSAProgress.user_id == user_id,
        MSAProgress.area.in_(['teoria', 'msa'])
    ).all()


def get_msa_structure():
    """Retorna estrutura do MSA (Teoria) com progresso do usuário"""
    msa = load_msa_structure()
    if not msa:
        return jsonify({"error": "Estrutura MSA não encontrada"}), 500

    user_progress = {}
    progresses = get_msa_progress_entries(current_user.id)
    for p in progresses:
        user_progress[p.section_id] = {
            'status': p.status,
            'started_at': p.started_at.isoformat() if p.started_at else None,
            'completed_at': p.completed_at.isoformat() if p.completed_at else None
        }

    total_secoes = sum(len(fase['secoes']) for fase in msa['fases'])
    concluidas = len([p for p in progresses if p.status == 'concluido'])
    total_progress = int((concluidas / total_secoes * 100) if total_secoes > 0 else 0)

    fases_progress = {}
    for fase in msa['fases']:
        secoes_fase = len(fase['secoes'])
        concluidas_fase = len([p for p in progresses if p.phase == fase['numero'] and p.status == 'concluido'])
        fases_progress[fase['id']] = int((concluidas_fase / secoes_fase * 100) if secoes_fase > 0 else 0)

    response = msa.copy()
    response['user_progress'] = user_progress
    response['fases_progress'] = fases_progress
    response['total_progress_percent'] = total_progress

    return jsonify(response), 200


def get_metodo_structure(instrument=''):
    """Retorna estrutura do Método com progresso do usuário.

    A fonte de verdade é sempre o instrumento persistido no usuário autenticado.
    Qualquer valor vindo da URL/client não deve sobrescrever esse valor.
    """
    metodo = load_metodo_structure()
    if not metodo:
        return jsonify({"error": "Estrutura Método não encontrada"}), 500

    try:
        instrument = get_user_instrument_for_method()
    except ValueError as exc:
        return jsonify({
            "error": "Usuário não possui instrumento selecionado",
            "message": "Por favor, selecione um instrumento antes de acessar o Método"
        }), 400

    requested_instrument = (instrument or '').lower().strip()
    client_instrument = (request.args.get('instrument') or '').strip().lower()
    if client_instrument and client_instrument != requested_instrument:
        return jsonify({
            "error": "Instrumento informado não corresponde ao usuário autenticado",
            "message": "O método foi carregado com o instrumento salvo no banco do usuário."
        }), 400

    method_config = get_method_config(instrument)
    if method_config is None:
        return jsonify({
            "error": "Método indisponível para este instrumento",
            "message": f"Não existe um método cadastrado para o instrumento {instrument}.",
            "instrument": instrument,
            "titulo": "Método ainda não disponível para este instrumento.",
            "method_config": None,
            "user_progress": {},
            "total_progress_percent": 0,
            "fases": []
        }), 404

    # Garante que o conteúdo do método seja logo descrito a partir do instrumento atual,
    # sem reusar qualquer conteúdo pré-definido de outro instrumento.
    response = metodo.copy()
    response['titulo'] = method_config.get('metodo') or f"Método de {method_config.get('nome', instrument)}"
    response['instrument'] = instrument
    response['instrument_name'] = method_config.get('nome', instrument)
    response['method_config'] = method_config
    response['method_name'] = method_config.get('metodo')
    response['pdf_status'] = 'not_found' if not method_config.get('pdf_filename') else 'ok'
    response['pdf_message'] = (
        'PDF do método deste instrumento não encontrado.'
        if not method_config.get('pdf_filename')
        else None
    )

    # Carrega progresso do usuário para este instrumento
    user_progress = {}
    progresses = MethodProgress.query.filter_by(
        user_id=current_user.id,
        instrument=instrument
    ).all()

    custom_record = CustomInstrumentMethod.query.filter_by(
        user_id=current_user.id,
        instrument=instrument
    ).first()

    for p in progresses:
        user_progress[p.section_id] = {
            'status': p.status,
            'started_at': p.started_at.isoformat() if p.started_at else None,
            'completed_at': p.completed_at.isoformat() if p.completed_at else None
        }

    total_fases = len(response.get('fases', [])) or len(metodo.get('fases', []))
    concluidas = len([p for p in progresses if p.status == 'concluido'])
    total_progress = int((concluidas / total_fases * 100) if total_fases > 0 else 0)

    response['user_progress'] = user_progress
    response['total_progress_percent'] = total_progress
    response['method_pdf_path'] = method_config.get('pdf_filename')
    response['custom_method'] = custom_record.to_dict() if custom_record else None
    response['has_custom_method'] = custom_record is not None
    response['custom_pdf_url'] = f'/api/instruments/method/file?instrument={instrument}' if custom_record else None
    response['official_pdf_url'] = f'/api/study/pdf/metodo?instrument={instrument}'

    return jsonify(response), 200

def get_hinario_structure():
    """Retorna estrutura do Hinário (480 hinos + 6 coros) com progresso do usuário"""
    
    # Validar: usuário deve ter instrumento selecionado
    if not current_user.instrumento:
        return jsonify({
            "error": "Usuário não possui instrumento selecionado",
            "message": "Por favor, selecione um instrumento antes de acessar o Hinário"
        }), 400
    
    hinario_data = load_hinario_structure() or {}
    catalog_hinos = hinario_data.get('hinos', []) or []
    catalog_coros = hinario_data.get('coros', []) or []

    user_hymn_progress = {}
    hymn_progresses = HymnProgress.query.filter_by(user_id=current_user.id).all()
    for p in hymn_progresses:
        user_hymn_progress[f"hymn_{p.hymn_number}"] = {
            'status': p.status,
            'stars': p.stars,
            'difficulty': p.difficulty,
            'completed_at': p.completed_at.isoformat() if p.completed_at else None
        }

    user_chorus_progress = {}
    chorus_progresses = ChorusProgress.query.filter_by(user_id=current_user.id).all()
    for p in chorus_progresses:
        user_chorus_progress[f"chorus_{p.chorus_number}"] = {
            'status': p.status,
            'stars': p.stars,
            'difficulty': p.difficulty,
            'completed_at': p.completed_at.isoformat() if p.completed_at else None
        }

    TOTAL_HINOS = 480
    TOTAL_COROS = 6
    HINOS_PER_PAGE = TOTAL_HINOS

    hinos = []
    for i in range(1, TOTAL_HINOS + 1):
        hymn_data = next((item for item in catalog_hinos if int(item.get('numero', i)) == i), {'numero': i, 'titulo': generate_hymn_name(i)})
        hymn_id = f"hymn_{i}"
        hinos.append({
            'id': hymn_id,
            'numero': i,
            'nome': hymn_data.get('titulo') or hymn_data.get('nome') or generate_hymn_name(i),
            'status': user_hymn_progress.get(hymn_id, {}).get('status', 'nao_iniciado'),
            'stars': user_hymn_progress.get(hymn_id, {}).get('stars', 0),
            'difficulty': user_hymn_progress.get(hymn_id, {}).get('difficulty')
        })

    coros = []
    for coro in (catalog_coros[:TOTAL_COROS] or []):
        chorus_number = int(coro.get('numero', 1))
        chorus_id = f"chorus_{chorus_number}"
        coros.append({
            'id': chorus_id,
            'numero': chorus_number,
            'nome': coro.get('titulo') or coro.get('nome') or f"Coro {chorus_number}",
            'status': user_chorus_progress.get(chorus_id, {}).get('status', 'nao_iniciado'),
            'stars': user_chorus_progress.get(chorus_id, {}).get('stars', 0),
            'difficulty': user_chorus_progress.get(chorus_id, {}).get('difficulty')
        })

    if len(coros) < TOTAL_COROS:
        COROS_NAMES = {
            1: 'Coro do Aleluia',
            2: 'Coro de Louvor',
            3: 'Coro de Adoração',
            4: 'Coro de Celebração',
            5: 'Coro de Paz',
            6: 'Coro de Glória'
        }
        for i in range(1, TOTAL_COROS + 1):
            chorus_id = f"chorus_{i}"
            if not any(c.get('id') == chorus_id for c in coros):
                coros.append({
                    'id': chorus_id,
                    'numero': i,
                    'nome': COROS_NAMES.get(i, f'Coro {i}'),
                    'status': user_chorus_progress.get(chorus_id, {}).get('status', 'nao_iniciado'),
                    'stars': user_chorus_progress.get(chorus_id, {}).get('stars', 0),
                    'difficulty': user_chorus_progress.get(chorus_id, {}).get('difficulty')
                })

    hinos_concluidos = len([p for p in hymn_progresses if p.status == 'concluido'])
    hinos_progress = int((hinos_concluidos / TOTAL_HINOS * 100) if TOTAL_HINOS > 0 else 0)
    coros_concluidos = len([p for p in chorus_progresses if p.status == 'concluido'])
    coros_progress = int((coros_concluidos / TOTAL_COROS * 100) if TOTAL_COROS > 0 else 0)
    total_progress = int(((hinos_concluidos + coros_concluidos) / (TOTAL_HINOS + TOTAL_COROS) * 100))

    hinario_config = get_hinario_config(current_user.instrumento)
    if not hinario_config:
        return jsonify({
            'error': 'PDF do Hinário não encontrado para este instrumento/afinação.',
            'instrumento': current_user.instrumento,
            'message': 'Não existe um PDF local do Hinário para a afinação atual do usuário.'
        }), 404

    pdf_url = hinario_config.get('route') or '/api/study/pdf/hinario'
    instrument_name = get_instrument_info(current_user.instrumento) or {}

    return jsonify({
        'titulo': f'Hinário — {instrument_name.get("name") or current_user.instrumento}',
        'total_hinos': TOTAL_HINOS,
        'total_coros': TOTAL_COROS,
        'total_itens': TOTAL_HINOS + TOTAL_COROS,
        'total_paginas': 525,
        'descricao': 'Hinário com 480 hinos e 6 coros - Coletânea completa de música religiosa',
        'hinos': hinos,
        'hinos_carregados': len(hinos),
        'hinos_total_disponivel': len(catalog_hinos) or TOTAL_HINOS,
        'hinos_tem_mais': len(hinos) < (len(catalog_hinos) or TOTAL_HINOS),
        'hinos_concluidos': hinos_concluidos,
        'hinos_progress': hinos_progress,
        'coros': coros,
        'coros_concluidos': coros_concluidos,
        'coros_progress': coros_progress,
        'total_progress_percent': total_progress,
        'user_hymn_progress': user_hymn_progress,
        'user_chorus_progress': user_chorus_progress,
        'instrumento': current_user.instrumento,
        'tonalidade': hinario_config.get('tonalidade'),
        'pdf_url': pdf_url,
        'pdf_path': hinario_config.get('pdf_path'),
        'hinario_pdf_path': hinario_config.get('pdf_path'),
        'instrumento_info': instrument_name
    }), 200

# ==================== ROTA: ATUALIZAR PROGRESSO ====================

@study_bp.route('/progress/<area>/<section_id>', methods=['PUT'])
@login_required
def update_progress(area, section_id):
    """
    PUT /api/study/progress/<area>/<section_id>
    
    Atualiza status de uma seção/fase
    
    Request body:
        {
            "status": "em_andamento" | "concluido" | "repassado",
            "instrument": "violao" (opcional, para método),
            "stars": 5 (opcional, para hinário)
        }
    
    Response:
        {
            "success": true,
            "message": "...",
            "xp_awarded": 50
        }
    """
    
    area = (area or '').lower()
    legacy_aliases = {'msa': 'teoria', 'hinaro': 'hinario'}
    area = legacy_aliases.get(area, area)

    if area not in ['teoria', 'metodo', 'hinario']:
        return jsonify({"error": f"Área inválida: {area}"}), 400
    
    try:
        data = request.get_json() or {}
        status = data.get('status', 'em_andamento')
        
        if status not in ['nao_iniciado', 'em_andamento', 'concluido', 'repassado']:
            return jsonify({"error": "Status inválido"}), 400
        
        xp_awarded = 0
        
        if area == 'teoria':
            return update_msa_progress(section_id, status)
        
        elif area == 'metodo':
            try:
                instrument = get_user_instrument_for_method()
            except ValueError:
                return jsonify({
                    "error": "Usuário não possui instrumento válido selecionado",
                    "message": "Selecione um instrumento antes de atualizar o progresso do Método."
                }), 400
            return update_metodo_progress(section_id, instrument, status)
        
        elif area == 'hinario':
            hymn_number = int(section_id.replace('hymn_', ''))
            stars = data.get('stars', 0)
            return update_hinario_progress(hymn_number, status, stars)
    
    except Exception as e:
        print(f"Erro ao atualizar progresso: {e}")
        return jsonify({"error": str(e)}), 500

def update_msa_progress(section_id, status):
    """Atualiza progresso do MSA"""
    try:
        # Compatibilidade com registros legados armazenados como 'msa' e com o nome atual 'teoria'.
        progress = MSAProgress.query.filter(
            MSAProgress.user_id == current_user.id,
            MSAProgress.section_id == section_id,
            MSAProgress.area.in_(['teoria', 'msa'])
        ).first()

        if not progress:
            parts = section_id.split('_')
            phase = int(parts[1]) if len(parts) > 1 else 1

            progress = MSAProgress(
                user_id=current_user.id,
                area='teoria',
                phase=phase,
                section_id=section_id,
                section_name=f"Seção {section_id}",
                status=status
            )
        else:
            progress.area = 'teoria'
            progress.status = status

        if status == 'em_andamento' and not progress.started_at:
            progress.started_at = datetime.utcnow()

        if status == 'concluido':
            progress.completed_at = datetime.utcnow()
            xp_awarded = 50
        elif status == 'repassado':
            xp_awarded = 0
        else:
            xp_awarded = 0

        db.session.add(progress)

        if status == 'concluido' and xp_awarded > 0:
            gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
            if gamif:
                gamif.xp += xp_awarded
            db.session.commit()
        else:
            db.session.commit()

        log_activity(current_user.id, 'UPDATE_PROGRESS', f'MSA {section_id} → {status}')

        return jsonify({
            "success": True,
            "message": f"Progresso atualizado para {status}",
            "xp_awarded": xp_awarded
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def update_metodo_progress(section_id, instrument, status):
    """Atualiza progresso do Método usando o instrumento do usuário autenticado."""
    try:
        instrument = (instrument or '').strip().lower()
        if not instrument or not validate_instrument(instrument):
            return jsonify({
                "error": "Instrumento inválido para o método",
                "message": "O método só pode ser atualizado com o instrumento do usuário autenticado."
            }), 400

        progress = MethodProgress.query.filter_by(
            user_id=current_user.id,
            section_id=section_id,
            instrument=instrument
        ).first()
        
        if not progress:
            # Extrai fase do ID
            parts = section_id.split('_')
            phase = int(parts[-1]) if parts[-1].isdigit() else 1
            
            progress = MethodProgress(
                user_id=current_user.id,
                instrument=instrument,
                phase=phase,
                section_id=section_id,
                section_name=f"Fase {phase}",
                status=status
            )
        else:
            progress.status = status
        
        # Atualiza timestamps
        if status == 'em_andamento' and not progress.started_at:
            progress.started_at = datetime.utcnow()
        
        if status == 'concluido':
            progress.completed_at = datetime.utcnow()
            xp_awarded = 100  # XP para método é maior
        else:
            xp_awarded = 0
        
        db.session.add(progress)
        
        # Atualiza gamificação
        if status == 'concluido' and xp_awarded > 0:
            gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
            if gamif:
                gamif.xp += xp_awarded
            db.session.commit()
        else:
            db.session.commit()
        
        log_activity(current_user.id, 'UPDATE_PROGRESS', f'Método {instrument} {section_id} → {status}')
        
        return jsonify({
            "success": True,
            "message": f"Progresso atualizado para {status}",
            "xp_awarded": xp_awarded
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def parse_hymn_selection(raw_selection):
    """Converte entradas como '1, 5, 10-15, 001' em um conjunto de números válidos."""
    if raw_selection is None:
        return set()

    selection = str(raw_selection).strip()
    if not selection:
        return set()

    result = set()
    for chunk in selection.split(','):
        item = chunk.strip()
        if not item:
            continue

        if '-' in item:
            start_text, end_text = (part.strip() for part in item.split('-', 1))
            if not start_text or not end_text:
                continue
            try:
                start = int(start_text)
                end = int(end_text)
            except ValueError:
                continue
            if start < 1 or end < 1 or start > 480 or end > 480:
                continue
            if start > end:
                start, end = end, start
            result.update(range(start, end + 1))
            continue

        try:
            number = int(item)
        except ValueError:
            continue

        if number < 1 or number > 480:
            continue
        result.add(number)

    return result


def update_hinario_progress(hymn_number, status, stars, difficulty=None):
    """Atualiza progresso do Hinário"""
    try:
        progress = HymnProgress.query.filter_by(
            user_id=current_user.id,
            hymn_number=hymn_number
        ).first()
        
        if not progress:
            progress = HymnProgress(
                user_id=current_user.id,
                hymn_number=hymn_number,
                hymn_name=f"Hino {hymn_number}",
                status=status,
                stars=stars,
                difficulty=difficulty
            )
        else:
            progress.status = status
            progress.stars = max(progress.stars, stars)
            if difficulty is not None:
                progress.difficulty = difficulty
        
        if status == 'em_andamento' and not progress.started_at:
            progress.started_at = datetime.utcnow()
        
        if status == 'concluido':
            progress.completed_at = datetime.utcnow()
            xp_awarded = 25
        else:
            xp_awarded = 0
        
        db.session.add(progress)
        
        if status == 'concluido' and xp_awarded > 0:
            gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
            if gamif:
                gamif.xp += xp_awarded
            db.session.commit()
        else:
            db.session.commit()
        
        log_activity(current_user.id, 'UPDATE_PROGRESS', f'Hinário {hymn_number} → {status}')
        
        return jsonify({
            "success": True,
            "message": f"Hino {hymn_number} atualizado",
            "xp_awarded": xp_awarded
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== ROTA: SERVIR PDFs ====================

@study_bp.route('/pdf/<area>', methods=['GET'])
@study_bp.route('/pdf/hymn/<int:hymn_number>', methods=['GET'])
def serve_pdf(area=None, hymn_number=None):
    """
    GET /api/study/pdf/<area>
    GET /api/study/pdf/hymn/<hymn_number>
    
    Retorna o arquivo PDF para visualização
    
    Áreas suportadas: msa, metodo, hinario, hymn
    
    Query params:
        instrument (opcional): para método (teclado, violao, guitarra, canto)
    """
    
    # Mapeia nomes de áreas para arquivos PDF
    pdf_mapping = {
        'msa': 'MSA.pdf',
        'teoria': 'MSA.pdf'
    }

    # Define qual PDF procurar
    if hymn_number is not None:
        area = 'hymn'

    area_lower = area.lower() if area else 'msa'

    if area_lower not in pdf_mapping and area_lower != 'metodo' and area_lower not in ['hinario', 'hymn']:
        return jsonify({
            "error": f"Área inválida: {area}",
            "supported": list(pdf_mapping.keys()) + ['metodo', 'hinario', 'hymn']
        }), 400

    if area_lower == 'metodo':
        user_instrument = (current_user.instrumento or '').strip().lower() if current_user.is_authenticated else ''
        if request.args.get('instrument'):
            requested_instrument = request.args.get('instrument', '').strip().lower()
            if current_user.is_authenticated and user_instrument and requested_instrument != user_instrument:
                return jsonify({
                    "error": "Instrumento informado não corresponde ao usuário autenticado",
                    "message": "O PDF do método foi bloqueado para evitar mistura de instrumentos."
                }), 400
            user_instrument = requested_instrument if requested_instrument else user_instrument

        if not user_instrument:
            return jsonify({
                "error": "Usuário não possui instrumento selecionado",
                "message": "Selecione um instrumento antes de abrir o PDF do método."
            }), 400

        custom_record = CustomInstrumentMethod.query.filter_by(user_id=current_user.id, instrument=user_instrument).first() if current_user.is_authenticated else None
        if custom_record and custom_record.file_path:
            pdf_file = Path(custom_record.file_path)
            if pdf_file.exists():
                try:
                    pdf_file.relative_to(Path(current_app.instance_path).resolve())
                    return send_file(str(pdf_file), mimetype='application/pdf', as_attachment=False)
                except ValueError:
                    return jsonify({'error': 'Arquivo do método personalizado fora do diretório permitido'}), 403

        method_config = get_method_config(user_instrument)
        if not method_config:
            return jsonify({
                "error": "Método indisponível para este instrumento",
                "message": f"Não existe um método cadastrado para o instrumento {user_instrument}.",
                "instrumento": user_instrument,
                "metodo": None
            }), 404

        pdf_filename = method_config.get('pdf_filename')
        if not pdf_filename:
            return jsonify({
                "error": "PDF do método para este instrumento não encontrado.",
                "message": f"Arquivo esperado: pdfs/{user_instrument}.pdf",
                "instrumento": user_instrument,
                "metodo": method_config.get('metodo'),
                "caminho_procurado": f"pdfs/{user_instrument}.pdf"
            }), 404

        pdf_file = resolve_method_pdf_path(user_instrument)
        if not pdf_file:
            return jsonify({
                "error": f"PDF do método para {user_instrument} não encontrado.",
                "message": f"Arquivo esperado: pdfs/{pdf_filename}",
                "instrumento": user_instrument,
                "metodo": method_config.get('metodo'),
                "caminho_procurado": f"pdfs/{pdf_filename}"
            }), 404

        if not validate_method_config(user_instrument, pdf_filename):
            return jsonify({
                "error": "PDF não corresponde ao instrumento do usuário",
                "message": "Bloqueado: associação instrumento → PDF inválida."
            }), 400
    elif area_lower in ['hinario', 'hymn']:
        user_instrument = (current_user.instrumento or '').strip().lower() if current_user.is_authenticated else ''
        if not user_instrument:
            return jsonify({
                "error": "Usuário não possui instrumento selecionado",
                "message": "Selecione um instrumento antes de abrir o Hinário."
            }), 400

        hinario_config = get_hinario_config(user_instrument)
        if not hinario_config:
            return jsonify({
                "error": "PDF do Hinário não encontrado para este instrumento/afinação.",
                "message": f"Instrumento: {user_instrument}; afinação do Hinário não foi encontrada ou o arquivo local não existe.",
                "instrumento": user_instrument,
                "caminho_esperado": f"pdfs/{user_instrument}.pdf"
            }), 404

        pdf_file = resolve_hinario_pdf_path(user_instrument)
        if not pdf_file:
            return jsonify({
                "error": "PDF do Hinário não encontrado para este instrumento/afinação.",
                "message": f"Arquivo esperado: {hinario_config.get('pdf_path') or 'pdfs/' + user_instrument + '.pdf'}",
                "instrumento": user_instrument,
                "afinacao": hinario_config.get('tonalidade'),
                "caminho_esperado": hinario_config.get('pdf_path') or f"pdfs/{user_instrument}.pdf"
            }), 404
    else:
        pdf_filename = pdf_mapping[area_lower]
        pdf_file = resolve_project_pdf_path(pdf_filename)
        if not pdf_file:
            return jsonify({
                "error": f"Arquivo PDF não encontrado: {pdf_filename}",
                "area": area,
                "searched_paths": [str(p / pdf_filename) for p in [Path(current_app.root_path), Path(current_app.root_path) / '..', Path(current_app.root_path) / '..' / 'backend']]
            }), 404
    
    try:
        # Registra visualização do PDF
        if hymn_number and current_user.is_authenticated:
            log_activity(
                current_user.id,
                'VIEW_PDF',
                f'Visualizou Hino {hymn_number}'
            )
        
        return send_file(
            str(pdf_file),
            mimetype='application/pdf',
            as_attachment=False  # Inline viewing
        )
    except Exception as e:
        return jsonify({"error": f"Erro ao servir PDF: {e}"}), 500


# ==================== ROTA: HISTÓRICO DE REVISÃO ====================

@study_bp.route('/review', methods=['GET'])
@login_required
def get_review_items():
    """
    GET /api/study/review
    
    Retorna conteúdo completado disponível para revisão
    
    Response:
        {
            "msa": [...],
            "metodo": [...],
            "hinario": [...]
        }
    """
    
    try:
        review_data = {
            "msa": [],
            "metodo": {},  # Por instrumento
            "hinario": []
        }
        
        # MSA
        msa_completed = MSAProgress.query.filter(
            MSAProgress.user_id == current_user.id,
            MSAProgress.area.in_(['teoria', 'msa']),
            MSAProgress.status == 'concluido'
        ).order_by(MSAProgress.completed_at.desc()).all()
        
        for item in msa_completed:
            review_data["msa"].append({
                'id': item.section_id,
                'nome': item.section_name,
                'fase': item.phase,
                'concluido_em': item.completed_at.isoformat() if item.completed_at else None
            })
        
        # Método
        metodo_completed = MethodProgress.query.filter_by(
            user_id=current_user.id,
            status='concluido'
        ).order_by(MethodProgress.completed_at.desc()).all()
        
        for item in metodo_completed:
            instrument = item.instrument or 'teclado'
            if instrument not in review_data["metodo"]:
                review_data["metodo"][instrument] = []
            review_data["metodo"][instrument].append({
                'id': item.section_id,
                'nome': item.section_name,
                'fase': item.phase,
                'concluido_em': item.completed_at.isoformat() if item.completed_at else None
            })
        
        # Hinário
        hymn_completed = HymnProgress.query.filter_by(
            user_id=current_user.id,
            status='concluido'
        ).order_by(HymnProgress.completed_at.desc()).all()
        
        for item in hymn_completed:
            review_data["hinario"].append({
                'id': f'hymn_{item.hymn_number}',
                'numero': item.hymn_number,
                'nome': item.hymn_name,
                'stars': item.stars,
                'concluido_em': item.completed_at.isoformat() if item.completed_at else None
            })
        
        return jsonify(review_data), 200
    
    except Exception as e:
        print(f"Erro ao obter itens de revisão: {e}")
        return jsonify({"error": str(e)}), 500

# ==================== ROTAS: HINÁRIO E COROS ====================

@study_bp.route('/hymns/load-more', methods=['GET'])
@login_required
def load_more_hymns():
    """
    GET /api/study/hymns/load-more?offset=20&limit=20
    
    Carrega mais hinos para lazy loading
    """
    offset = request.args.get('offset', 20, type=int)
    limit = request.args.get('limit', 20, type=int)
    search = request.args.get('search', '', type=str).lower()
    
    # Carrega progresso do usuário
    user_hymn_progress = {}
    progresses = HymnProgress.query.filter_by(user_id=current_user.id).all()
    for p in progresses:
        user_hymn_progress[f"hymn_{p.hymn_number}"] = {
            'status': p.status,
            'stars': p.stars,
        }
    
    # Gera hinos solicitados
    TOTAL_HINOS = 480
    hinos = []
    end = min(offset + limit, TOTAL_HINOS + 1)
    
    for i in range(offset, end):
        hymn_id = f"hymn_{i}"
        hymn_name = generate_hymn_name(i)
        
        # Aplica filtro de busca se fornecido
        if search and search not in str(i).lower() and search not in hymn_name.lower():
            continue
        
        hymn_data = {
            'id': hymn_id,
            'numero': i,
            'nome': hymn_name,
            'status': user_hymn_progress.get(hymn_id, {}).get('status', 'nao_iniciado'),
            'stars': user_hymn_progress.get(hymn_id, {}).get('stars', 0)
        }
        hinos.append(hymn_data)
    
    return jsonify({
        'hinos': hinos,
        'total': len(hinos),
        'offset': offset,
        'limit': limit,
        'tem_mais': end < TOTAL_HINOS + 1
    }), 200

@study_bp.route('/hymns/search', methods=['GET'])
@login_required
def search_hymns():
    """
    GET /api/study/hymns/search?q=palavra
    
    Busca hinos por número ou título
    """
    query = (request.args.get('q', '') or '').strip().lower()
    user_hymn_progress = {}
    progresses = HymnProgress.query.filter_by(user_id=current_user.id).all()
    for p in progresses:
        user_hymn_progress[f"hymn_{p.hymn_number}"] = {
            'status': p.status,
            'stars': p.stars,
            'difficulty': p.difficulty,
        }

    catalog_hinos = load_hinario_structure().get('hinos', []) if load_hinario_structure() else []
    TOTAL_HINOS = 480
    hinos = []

    for i in range(1, TOTAL_HINOS + 1):
        hymn_number = i
        hymn_data = next((item for item in catalog_hinos if int(item.get('numero', i)) == hymn_number), {'numero': hymn_number, 'titulo': generate_hymn_name(hymn_number)})
        hymn_id = f"hymn_{hymn_number}"
        hymn_name = (hymn_data.get('titulo') or hymn_data.get('nome') or generate_hymn_name(hymn_number)).lower()
        normalized_query = query.strip()
        match = False

        if not normalized_query:
            match = True
        elif normalized_query.isdigit():
            numeric_value = str(hymn_number)
            numeric_aliases = {numeric_value, numeric_value.zfill(2), numeric_value.zfill(3)}
            match = normalized_query in numeric_aliases or normalized_query in numeric_value
        else:
            match = normalized_query in hymn_name or normalized_query in str(hymn_number)

        if match:
            hinos.append({
                'id': hymn_id,
                'numero': hymn_number,
                'nome': hymn_data.get('titulo') or hymn_data.get('nome') or generate_hymn_name(hymn_number),
                'status': user_hymn_progress.get(hymn_id, {}).get('status', 'nao_iniciado'),
                'stars': user_hymn_progress.get(hymn_id, {}).get('stars', 0),
                'difficulty': user_hymn_progress.get(hymn_id, {}).get('difficulty')
            })

    return jsonify({
        'hinos': hinos,
        'total': len(hinos),
        'query': query
    }), 200

@study_bp.route('/hymn/<int:hymn_number>', methods=['GET'])
@login_required
def get_hymn_details(hymn_number):
    """
    GET /api/study/hymn/<hymn_number>
    
    Retorna detalhes de um hino específico
    """
    TOTAL_HINOS = 480
    if hymn_number < 1 or hymn_number > TOTAL_HINOS:
        return jsonify({"error": f"Número de hino inválido (1-{TOTAL_HINOS})"}), 400
    
    progress = HymnProgress.query.filter_by(
        user_id=current_user.id,
        hymn_number=hymn_number
    ).first()
    
    return jsonify({
        'numero': hymn_number,
        'nome': generate_hymn_name(hymn_number),
        'status': progress.status if progress else 'nao_iniciado',
        'stars': progress.stars if progress else 0,
        'pdf_path': f'/api/study/pdf/hymn/{hymn_number}'
    }), 200

@study_bp.route('/chorus/<int:chorus_number>', methods=['GET'])
@login_required
def get_chorus_details(chorus_number):
    """
    GET /api/study/chorus/<chorus_number>
    
    Retorna detalhes de um coro específico (1-6)
    """
    if chorus_number < 1 or chorus_number > 6:
        return jsonify({"error": "Número de coro inválido (1-6)"}), 400
    
    COROS_NAMES = {
        1: "Coro do Aleluia",
        2: "Coro de Louvor",
        3: "Coro de Adoração",
        4: "Coro de Celebração",
        5: "Coro de Paz",
        6: "Coro de Glória"
    }
    
    progress = ChorusProgress.query.filter_by(
        user_id=current_user.id,
        chorus_number=chorus_number
    ).first()
    
    return jsonify({
        'numero': chorus_number,
        'nome': COROS_NAMES.get(chorus_number, f"Coro {chorus_number}"),
        'status': progress.status if progress else 'nao_iniciado',
        'stars': progress.stars if progress else 0,
        'pdf_path': f'/api/study/pdf/chorus/{chorus_number}'
    }), 200

@study_bp.route('/progress/hymn/<int:hymn_number>', methods=['PUT'])
@login_required
def update_hymn_progress(hymn_number):
    """
    PUT /api/study/progress/hymn/<hymn_number>
    
    Atualiza progresso de um hino
    """
    TOTAL_HINOS = 480
    if hymn_number < 1 or hymn_number > TOTAL_HINOS:
        return jsonify({"error": f"Número de hino inválido (1-{TOTAL_HINOS})"}), 400
    
    try:
        data = request.get_json() or {}
        status = data.get('status', 'em_andamento')
        stars = data.get('stars', 0)
        difficulty = data.get('difficulty')
        
        if status not in ['nao_iniciado', 'em_andamento', 'concluido']:
            return jsonify({"error": "Status inválido"}), 400
        
        progress = HymnProgress.query.filter_by(
            user_id=current_user.id,
            hymn_number=hymn_number
        ).first()
        
        if not progress:
            progress = HymnProgress(
                user_id=current_user.id,
                hymn_number=hymn_number,
                hymn_name=(load_hinario_structure() or {}).get('hinos', [{}])[hymn_number - 1].get('titulo') if (load_hinario_structure() or {}).get('hinos', []) and hymn_number <= len((load_hinario_structure() or {}).get('hinos', [])) else generate_hymn_name(hymn_number),
                status=status,
                stars=stars,
                difficulty=difficulty
            )
        else:
            progress.status = status
            progress.stars = stars
            if difficulty is not None:
                progress.difficulty = difficulty
        
        if status == 'em_andamento' and not progress.started_at:
            progress.started_at = datetime.utcnow()
        
        xp_awarded = 0
        if status == 'concluido':
            progress.completed_at = datetime.utcnow()
            xp_awarded = 10
        
        db.session.add(progress)
        if xp_awarded > 0:
            gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
            if gamif:
                gamif.xp += xp_awarded
        db.session.commit()
        log_activity(current_user.id, 'UPDATE_HYMN_PROGRESS', f'Hino {hymn_number} → {status}')
        
        return jsonify({
            "success": True,
            "message": f"Hino {hymn_number} atualizado para {status}",
            "xp_awarded": xp_awarded
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar progresso do hino: {e}")
        return jsonify({"error": str(e)}), 500

@study_bp.route('/progress/chorus/<int:chorus_number>', methods=['PUT'])
@login_required
def update_chorus_progress(chorus_number):
    """
    PUT /api/study/progress/chorus/<chorus_number>
    
    Atualiza progresso de um coro
    """
    if chorus_number < 1 or chorus_number > 6:
        return jsonify({"error": "Número de coro inválido (1-6)"}), 400
    
    try:
        data = request.get_json() or {}
        status = data.get('status', 'em_andamento')
        stars = data.get('stars', 0)
        difficulty = data.get('difficulty')
        
        if status not in ['nao_iniciado', 'em_andamento', 'concluido']:
            return jsonify({"error": "Status inválido"}), 400
        
        COROS_NAMES = {
            1: "Coro do Aleluia",
            2: "Coro de Louvor",
            3: "Coro de Adoração",
            4: "Coro de Celebração",
            5: "Coro de Paz",
            6: "Coro de Glória"
        }
        
        progress = ChorusProgress.query.filter_by(
            user_id=current_user.id,
            chorus_number=chorus_number
        ).first()
        
        if not progress:
            progress = ChorusProgress(
                user_id=current_user.id,
                chorus_number=chorus_number,
                chorus_name=COROS_NAMES.get(chorus_number),
                status=status,
                stars=stars,
                difficulty=difficulty
            )
        else:
            progress.status = status
            progress.stars = stars
            if difficulty is not None:
                progress.difficulty = difficulty
        
        if status == 'em_andamento' and not progress.started_at:
            progress.started_at = datetime.utcnow()
        
        xp_awarded = 0
        if status == 'concluido':
            progress.completed_at = datetime.utcnow()
            xp_awarded = 15
        
        db.session.add(progress)
        if xp_awarded > 0:
            gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
            if gamif:
                gamif.xp += xp_awarded
        db.session.commit()
        log_activity(current_user.id, 'UPDATE_CHORUS_PROGRESS', f'Coro {chorus_number} → {status}')
        
        return jsonify({
            "success": True,
            "message": f"Coro {chorus_number} atualizado para {status}",
            "xp_awarded": xp_awarded
        }), 200
    
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao atualizar progresso do coro: {e}")
        return jsonify({"error": str(e)}), 500

@study_bp.route('/hinario/bulk-update', methods=['POST'])
@login_required
def bulk_update_hinario():
    try:
        data = request.get_json() or {}
        kind = data.get('kind', 'hymn')
        status = data.get('status', 'nao_iniciado')
        difficulty = data.get('difficulty')
        ids = data.get('ids') or []
        select_all = bool(data.get('all'))
        selection = data.get('selection')

        if kind not in ['hymn', 'chorus']:
            return jsonify({'error': 'Tipo inválido'}), 400

        if kind == 'hymn':
            if select_all:
                ids = list(range(1, 481))
            elif selection is not None:
                ids = sorted(parse_hymn_selection(selection))
            else:
                ids = [int(item) for item in ids if str(item).strip()]
            for hymn_number in ids:
                if hymn_number < 1 or hymn_number > 480:
                    continue
                update_hinario_progress(hymn_number, status, 0, difficulty)
        else:
            if select_all:
                ids = list(range(1, 7))
            elif selection is not None:
                ids = sorted(parse_hymn_selection(selection))
            else:
                ids = [int(item) for item in ids if str(item).strip()]
            for chorus_number in ids:
                if chorus_number < 1 or chorus_number > 6:
                    continue
                progress = ChorusProgress.query.filter_by(user_id=current_user.id, chorus_number=chorus_number).first()
                if not progress:
                    progress = ChorusProgress(
                        user_id=current_user.id,
                        chorus_number=chorus_number,
                        chorus_name=f'Coro {chorus_number}',
                        status=status,
                        difficulty=difficulty
                    )
                else:
                    progress.status = status
                    if difficulty is not None:
                        progress.difficulty = difficulty
                db.session.add(progress)
                db.session.commit()

        return jsonify({'success': True, 'updated': len(ids)}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@study_bp.route('/progress-report', methods=['GET'])
@login_required
def get_progress_report():
    """
    GET /api/study/progress-report
    
    Retorna relatório completo de progresso do usuário
    
    Response:
        {
            "msa": {...},
            "metodo": {...},
            "hinario": {...},
            "xp_total": 1250,
            "instrumento": "saxofone_soprano",
            "tonalidade": "sib",
            "ultima_atividade": "2024-01-15T10:30:00"
        }
    """
    
    try:
        msa_total = MSAProgress.query.filter(
            MSAProgress.user_id == current_user.id,
            MSAProgress.area.in_(['teoria', 'msa'])
        ).count()
        msa_completed = MSAProgress.query.filter(
            MSAProgress.user_id == current_user.id,
            MSAProgress.area.in_(['teoria', 'msa']),
            MSAProgress.status == 'concluido'
        ).count()
        msa_progress = int((msa_completed / msa_total * 100) if msa_total > 0 else 0)
        
        metodo_total = MethodProgress.query.filter_by(user_id=current_user.id).count()
        metodo_completed = MethodProgress.query.filter_by(user_id=current_user.id, status='concluido').count()
        metodo_progress = int((metodo_completed / metodo_total * 100) if metodo_total > 0 else 0)
        
        hinario_total = 480
        hinario_completed = HymnProgress.query.filter_by(user_id=current_user.id, status='concluido').count()
        hinario_progress = int((hinario_completed / hinario_total * 100) if hinario_total > 0 else 0)
        
        coros_total = 6
        coros_completed = ChorusProgress.query.filter_by(user_id=current_user.id, status='concluido').count()
        coros_progress = int((coros_completed / coros_total * 100) if coros_total > 0 else 0)
        
        gamif = GamificationProgress.query.filter_by(user_id=current_user.id).first()
        xp_total = gamif.xp if gamif else 0
        
        from models import ActivityLog
        ultima_log = ActivityLog.query.filter_by(user_id=current_user.id).order_by(
            ActivityLog.created_at.desc()
        ).first()
        ultima_atividade = ultima_log.created_at.isoformat() if ultima_log else None
        
        # Informações do instrumento do usuário
        tonalidade = get_tonality_for_instrument(current_user.instrumento) if current_user.instrumento else None
        
        return jsonify({
            "msa": {
                "total_secoes": msa_total,
                "secoes_concluidas": msa_completed,
                "progresso_percent": msa_progress
            },
            "metodo": {
                "total_fases": metodo_total,
                "fases_concluidas": metodo_completed,
                "progresso_percent": metodo_progress
            },
            "hinario": {
                "total_hinos": 480,
                "hinos_concluidos": hinario_completed,
                "progresso_percent": hinario_progress
            },
            "coros": {
                "total_coros": 6,
                "coros_concluidos": coros_completed,
                "progresso_percent": coros_progress
            },
            "gamificacao": {
                "xp_total": xp_total
            },
            "instrumento": current_user.instrumento,
            "tonalidade": tonalidade,
            "ultima_atividade": ultima_atividade
        }), 200
    
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({"error": str(e)}), 500
