"""
Rotas para seleção e gerenciamento de instrumentos
"""

import os
import uuid
from pathlib import Path

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime

try:
    from ..models import db, User, CustomInstrumentMethod, log_activity
    from ..instrument_config import (
        AVAILABLE_INSTRUMENTS,
        get_tonality_for_instrument,
        get_pdf_url_for_instrument,
        validate_instrument,
        get_instrument_info,
        normalize_instrument_key,
        get_metodo_pdf,
        get_method_config,
        resolve_method_pdf_path
    )
    from ..config import MAX_METHOD_PDF_SIZE
except ImportError:
    from models import db, User, CustomInstrumentMethod, log_activity
    from instrument_config import (
        AVAILABLE_INSTRUMENTS,
        get_tonality_for_instrument,
        get_pdf_url_for_instrument,
        validate_instrument,
        get_instrument_info,
        normalize_instrument_key,
        get_metodo_pdf,
        get_method_config,
        resolve_method_pdf_path
    )
    from config import MAX_METHOD_PDF_SIZE

instruments_bp = Blueprint('instruments', __name__, url_prefix='/api/instruments')


def _get_upload_base_dir():
    base_dir = Path(current_app.instance_path) / 'uploads' / 'custom_methods'
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir


def _normalize_method_instrument(raw_instrument):
    value = (raw_instrument or current_user.instrumento or '').strip()
    if not value:
        return None
    normalized = normalize_instrument_key(value)
    if not normalized or not validate_instrument(normalized):
        return None
    return normalized


def _get_custom_method_for_user(instrument):
    normalized = _normalize_method_instrument(instrument)
    if not normalized:
        return None
    return CustomInstrumentMethod.query.filter_by(user_id=current_user.id, instrument=normalized).first()


def _delete_existing_custom_method_file(entry):
    if not entry or not entry.file_path:
        return
    try:
        file_path = Path(entry.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception:
        pass


@instruments_bp.route('/method', methods=['GET'])
@login_required
def get_custom_method():
    """Retorna o método personalizado do usuário para o instrumento informado."""
    instrument = _normalize_method_instrument(request.args.get('instrument'))
    if not instrument:
        return jsonify({'error': 'Instrumento inválido ou não selecionado', 'custom_method': None}), 404

    record = _get_custom_method_for_user(instrument)
    if record is None:
        return jsonify({
            'instrument': instrument,
            'custom_method': None,
            'has_custom_method': False,
            'official_method': get_method_config(instrument),
            'pdf_url': f'/api/study/pdf/metodo?instrument={instrument}'
        }), 404

    return jsonify({
        'instrument': instrument,
        'custom_method': record.to_dict(),
        'has_custom_method': True,
        'official_method': get_method_config(instrument),
        'pdf_url': f'/api/study/pdf/metodo?instrument={instrument}'
    }), 200


@instruments_bp.route('/method', methods=['POST'])
@login_required
def upload_custom_method():
    """Faz upload do PDF do método personalizado vinculado ao usuário e ao instrumento."""
    instrument = _normalize_method_instrument(request.form.get('instrument'))
    if not instrument:
        return jsonify({'error': 'Instrumento inválido ou não selecionado'}), 400

    file = request.files.get('file')
    if file is None or file.filename == '':
        return jsonify({'error': 'Arquivo do método é obrigatório'}), 400

    filename = secure_filename(file.filename or '')
    if not filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Apenas arquivos PDF são permitidos'}), 400

    stream = file.stream
    stream.seek(0, os.SEEK_END)
    file_size = stream.tell()
    stream.seek(0)
    max_size_mb = MAX_METHOD_PDF_SIZE / (1024 * 1024)
    if file_size <= 0 or file_size > MAX_METHOD_PDF_SIZE:
        return jsonify({'error': f'Arquivo inválido ou excede o tamanho máximo permitido ({int(max_size_mb)} MB)'}), 413

    mime_type = (file.mimetype or '').lower()
    if mime_type and mime_type not in {'application/pdf'}:
        return jsonify({'error': 'Tipo MIME inválido para PDF'}), 400

    first_bytes = stream.read(5)
    stream.seek(0)
    if first_bytes and first_bytes != b'%PDF-':
        return jsonify({'error': 'Conteúdo do arquivo não parece ser um PDF válido'}), 400

    base_dir = _get_upload_base_dir()
    safe_name = f'{current_user.id}_{instrument}_{uuid.uuid4().hex}.pdf'
    destination = base_dir / safe_name
    file.save(destination)

    existing = CustomInstrumentMethod.query.filter_by(user_id=current_user.id, instrument=instrument).first()
    if existing:
        _delete_existing_custom_method_file(existing)
        existing.original_filename = filename
        existing.stored_filename = safe_name
        existing.file_path = str(destination)
        existing.file_size = file_size
        existing.mime_type = 'application/pdf'
        existing.updated_at = datetime.utcnow()
        record = existing
    else:
        record = CustomInstrumentMethod(
            user_id=current_user.id,
            instrument=instrument,
            original_filename=filename,
            stored_filename=safe_name,
            file_path=str(destination),
            file_size=file_size,
            mime_type='application/pdf'
        )
        db.session.add(record)

    db.session.commit()
    log_activity(current_user.id, 'UPLOAD_CUSTOM_METHOD', f'Upload de método personalizado para {instrument}')

    return jsonify({
        'success': True,
        'instrument': instrument,
        'custom_method': record.to_dict(),
        'message': 'Método personalizado salvo com sucesso'
    }), 200


@instruments_bp.route('/method', methods=['DELETE'])
@login_required
def remove_custom_method():
    instrument = _normalize_method_instrument(request.args.get('instrument'))
    if not instrument:
        return jsonify({'error': 'Instrumento inválido ou não selecionado'}), 400

    record = _get_custom_method_for_user(instrument)
    if not record:
        return jsonify({'removed': False, 'instrument': instrument, 'message': 'Nenhum método personalizado encontrado'}), 404

    _delete_existing_custom_method_file(record)
    db.session.delete(record)
    db.session.commit()
    log_activity(current_user.id, 'REMOVE_CUSTOM_METHOD', f'Remoção do método personalizado para {instrument}')
    return jsonify({'removed': True, 'instrument': instrument}), 200


@instruments_bp.route('/method/file', methods=['GET'])
@login_required
def serve_custom_method_file():
    instrument = _normalize_method_instrument(request.args.get('instrument'))
    if not instrument:
        return jsonify({'error': 'Instrumento inválido ou não selecionado'}), 400

    record = _get_custom_method_for_user(instrument)
    if not record:
        return jsonify({'error': 'Método personalizado não encontrado'}), 404

    resolved_path = Path(record.file_path)
    if not resolved_path.exists() or resolved_path.suffix.lower() != '.pdf':
        return jsonify({'error': 'Arquivo personalizado não encontrado ou inválido'}), 404

    try:
        resolved_path.relative_to(Path(current_app.instance_path).resolve())
    except ValueError:
        return jsonify({'error': 'Arquivo fora do diretório permitido'}), 403

    return send_file(str(resolved_path), mimetype='application/pdf', as_attachment=False)


@instruments_bp.route('/method/official', methods=['GET'])
@login_required
def get_official_method_pdf_url():
    instrument = _normalize_method_instrument(request.args.get('instrument'))
    if not instrument:
        return jsonify({'error': 'Instrumento inválido ou não selecionado'}), 400

    official_pdf = resolve_method_pdf_path(instrument)
    if not official_pdf:
        return jsonify({'error': 'PDF oficial não encontrado', 'instrument': instrument}), 404

    return jsonify({
        'instrument': instrument,
        'url': f'/api/study/pdf/metodo?instrument={instrument}',
        'official_path': str(official_pdf)
    }), 200

# ==================== LISTAR INSTRUMENTOS DISPONÍVEIS ====================

@instruments_bp.route('', methods=['GET'])
def list_instruments():
    """
    GET /api/instruments
    
    Retorna lista de instrumentos disponíveis com suas tonalidades
    
    Response:
        [
            {
                "id": "saxofone_soprano",
                "name": "Saxofone Soprano",
                "tonalidade": "Sib"
            },
            ...
        ]
    """
    try:
        return jsonify(AVAILABLE_INSTRUMENTS), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== OBTER INSTRUMENTO DO USUÁRIO ====================

@instruments_bp.route('/current', methods=['GET'])
@login_required
def get_current_instrument():
    """
    GET /api/instruments/current
    
    Retorna instrumento selecionado pelo usuário atual
    
    Response:
        {
            "instrumento": "saxofone_soprano" | null,
            "tonalidade": "sib" | null,
            "pdf_url": "https://..." | null,
            "info": {...} | null
        }
    """
    try:
        instrumento = current_user.instrumento
        tonalidade = None
        pdf_url = None
        info = None
        
        if instrumento:
            tonalidade = get_tonality_for_instrument(instrumento)
            pdf_url = get_pdf_url_for_instrument(instrumento)
            info = get_instrument_info(instrumento)
        
        return jsonify({
            'instrumento': instrumento,
            'tonalidade': tonalidade,
            'pdf_url': pdf_url,
            'info': info
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SELECIONAR/SALVAR INSTRUMENTO ====================

@instruments_bp.route('/select', methods=['POST'])
@login_required
def select_instrument():
    """
    POST /api/instruments/select
    
    Salva o instrumento selecionado pelo usuário
    
    Request body:
        {
            "instrumento": "saxofone_soprano"
        }
    
    Response:
        {
            "success": true,
            "message": "Instrumento salvo com sucesso",
            "instrumento": "saxofone_soprano",
            "tonalidade": "sib",
            "pdf_url": "https://...",
            "info": {...}
        }
    """
    try:
        data = request.get_json()
        
        if not data or not data.get('instrumento'):
            return jsonify({'error': 'Instrumento é obrigatório'}), 400
        
        instrumento_id = data.get('instrumento').lower().strip()
        
        # Validar instrumento
        if not validate_instrument(instrumento_id):
            return jsonify({
                'error': f'Instrumento inválido: {instrumento_id}',
                'available_instruments': [i['id'] for i in AVAILABLE_INSTRUMENTS]
            }), 400
        
        # Salvar no banco de dados e validar persistência real
        user = User.query.get(current_user.id)
        if user is None:
            return jsonify({'error': 'Usuário não encontrado'}), 404

        user.instrumento = instrumento_id
        user.updated_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)

        current_user.instrumento = user.instrumento
        current_user.updated_at = user.updated_at

        persisted_user = User.query.get(current_user.id)
        if persisted_user is None or persisted_user.instrumento != instrumento_id:
            db.session.rollback()
            return jsonify({'error': 'Instrumento não foi persistido corretamente no banco'}), 500

        # Registrar atividade
        log_activity(current_user.id, 'SELECT_INSTRUMENT', f'Instrumento selecionado: {instrumento_id}')

        # Retornar informações do instrumento
        tonalidade = get_tonality_for_instrument(instrumento_id)
        pdf_url = get_pdf_url_for_instrument(instrumento_id)
        info = get_instrument_info(instrumento_id)

        return jsonify({
            'success': True,
            'message': 'Instrumento salvo com sucesso',
            'instrumento': instrumento_id,
            'tonalidade': tonalidade,
            'pdf_url': pdf_url,
            'info': info
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== VERIFICAR SE USUÁRIO TEM INSTRUMENTO ====================

@instruments_bp.route('/has-instrument', methods=['GET'])
@login_required
def has_instrument():
    """
    GET /api/instruments/has-instrument
    
    Verifica se o usuário já selecionou um instrumento
    
    Response:
        {
            "has_instrument": true | false,
            "instrumento": "saxofone_soprano" | null
        }
    """
    try:
        instrumento = current_user.instrumento
        return jsonify({
            'has_instrument': instrumento is not None and instrumento != '',
            'instrumento': instrumento
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== OBTER TONALIDADE E PDF DE UM INSTRUMENTO ====================

@instruments_bp.route('/<instrument_id>/tonality', methods=['GET'])
def get_instrument_tonality(instrument_id):
    """
    GET /api/instruments/<instrument_id>/tonality
    
    Retorna tonalidade e PDF URL para um instrumento específico
    
    Response:
        {
            "instrumento": "saxofone_soprano",
            "tonalidade": "sib",
            "pdf_url": "https://...",
            "info": {...}
        }
    """
    try:
        normalized_id = instrument_id.lower().strip()
        
        if not validate_instrument(normalized_id):
            return jsonify({'error': f'Instrumento inválido: {instrument_id}'}), 404
        
        tonalidade = get_tonality_for_instrument(normalized_id)
        pdf_url = get_pdf_url_for_instrument(normalized_id)
        info = get_instrument_info(normalized_id)
        
        return jsonify({
            'instrumento': normalized_id,
            'tonalidade': tonalidade,
            'pdf_url': pdf_url,
            'info': info
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
