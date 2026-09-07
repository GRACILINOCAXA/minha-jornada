import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, send_file
from flask_login import current_user, login_required

try:
    from ..models import db, MSAProgress, HymnProgress, MethodProgress, GamificationProgress, log_activity
except ImportError:
    from models import db, MSAProgress, HymnProgress, MethodProgress, GamificationProgress, log_activity

msa_bp = Blueprint('msa', __name__)

# Estrutura de fases e seções do MSA (a ser preenchida com dados reais do PDF)
MSA_STRUCTURE = {
    'teoria': {
        'pdf': 'MSA.pdf',  # Arquivo PDF real
        'phases': [
            {
                'phase': 1,
                'name': 'Fundamentos Musicais',
                'sections': [
                    {'id': 'teoria_1_1', 'name': 'Notação Musical', 'start_page': 1, 'end_page': 15},
                    {'id': 'teoria_1_2', 'name': 'Leitura de Partituras', 'start_page': 16, 'end_page': 30},
                    {'id': 'teoria_1_3', 'name': 'Ritmo e Tempo', 'start_page': 31, 'end_page': 45}
                ]
            },
            {
                'phase': 2,
                'name': 'Acordes e Harmonia',
                'sections': [
                    {'id': 'teoria_2_1', 'name': 'Acordes Básicos', 'start_page': 46, 'end_page': 60},
                    {'id': 'teoria_2_2', 'name': 'Progressões Harmônicas', 'start_page': 61, 'end_page': 75}
                ]
            },
            {
                'phase': 3,
                'name': 'Técnicas Avançadas',
                'sections': [
                    {'id': 'teoria_3_1', 'name': 'Modulação', 'start_page': 76, 'end_page': 90},
                    {'id': 'teoria_3_2', 'name': 'Análise de Composições', 'start_page': 91, 'end_page': 105}
                ]
            }
        ]
    },
    'metodo': {
        'instruments': {
            'teclado': {'pdf': 'MSA_Teclado.pdf', 'phases': []},
            'violao': {'pdf': 'MSA_Violao.pdf', 'phases': []},
            'guitarra': {'pdf': 'MSA_Guitarra.pdf', 'phases': []},
            'canto': {'pdf': 'MSA_Canto.pdf', 'phases': []}
        }
    },
    'hinario': {
        'pdf': 'Hinario.pdf',
        'total_hymns': 350  # Ajustar para o número real
    }
}

# ========== MSA SECTIONS ==========
@msa_bp.route('/sections/<area>', methods=['GET'])
@login_required
def get_msa_sections(area):
    """Obter estrutura de seções do MSA com progresso do usuário"""
    try:
        if area not in ['teoria', 'metodo', 'hinario']:
            return jsonify({'error': 'Área inválida'}), 400
        
        # Estructura base
        structure = MSA_STRUCTURE.get(area, {})
        
        if area == 'metodo':
            # Método é específico do instrumento
            instrument = request.args.get('instrument', 'teclado')
            if instrument not in structure.get('instruments', {}):
                instrument = 'teclado'
            
            # Retornar estrutura do método para o instrumento selecionado
            method_data = structure['instruments'].get(instrument, {})
            
            # Buscar progresso do usuário
            progress_records = MethodProgress.query.filter_by(
                user_id=current_user.id,
                instrument=instrument
            ).all()
            
            progress_map = {p.section_id: p.to_dict() for p in progress_records}
            
            return jsonify({
                'area': area,
                'instrument': instrument,
                'pdf': method_data.get('pdf'),
                'phases': method_data.get('phases', []),
                'user_progress': progress_map,
                'total_progress': calculate_area_progress(area, current_user.id, instrument)
            }), 200
        
        elif area == 'hinario':
            # Retornar informações sobre hinário
            hymn_progress = HymnProgress.query.filter_by(user_id=current_user.id).all()
            completed = len([h for h in hymn_progress if h.status == 'concluido'])
            total = structure.get('total_hymns', 350)
            
            return jsonify({
                'area': area,
                'pdf': structure.get('pdf'),
                'total_hymns': total,
                'user_hymn_progress': [h.to_dict() for h in hymn_progress],
                'total_progress': round((completed / max(1, total)) * 100)
            }), 200
        
        else:  # teoria
            # Buscar progresso do usuário para a Teoria
            progress_records = MSAProgress.query.filter_by(
                user_id=current_user.id,
                area='teoria'
            ).all()
            
            progress_map = {p.section_id: p.to_dict() for p in progress_records}
            
            return jsonify({
                'area': area,
                'pdf': structure.get('pdf'),
                'phases': structure.get('phases', []),
                'user_progress': progress_map,
                'total_progress': calculate_area_progress(area, current_user.id)
            }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== PROGRESS TRACKING ==========
@msa_bp.route('/progress/<area>/<section_id>', methods=['PUT'])
@login_required
def update_section_progress(area, section_id):
    """Atualizar progresso de uma seção"""
    try:
        data = request.get_json() or {}
        status = data.get('status', 'em_andamento')  # nao_iniciado, em_andamento, concluido
        
        if area == 'metodo':
            instrument = data.get('instrument', 'teclado')
            progress = MethodProgress.query.filter_by(
                user_id=current_user.id,
                instrument=instrument,
                section_id=section_id
            ).first()
            
            if not progress:
                # Buscar informações da seção na estrutura
                section_info = find_section_in_structure(area, section_id, instrument)
                progress = MethodProgress(
                    user_id=current_user.id,
                    instrument=instrument,
                    section_id=section_id,
                    section_name=section_info.get('name', ''),
                    start_page=section_info.get('start_page'),
                    end_page=section_info.get('end_page')
                )
                db.session.add(progress)
            
            if status == 'concluido' and progress.status != 'concluido':
                progress.completed_at = datetime.utcnow()
                award_section_xp(current_user.id, 30, f"Seção {progress.section_name} concluída")
            
            progress.status = status
            if status != 'nao_iniciado' and not progress.started_at:
                progress.started_at = datetime.utcnow()
        
        elif area == 'hinario':
            hymn_number = int(section_id.split('_')[1])
            progress = HymnProgress.query.filter_by(
                user_id=current_user.id,
                hymn_number=hymn_number
            ).first()
            
            if not progress:
                progress = HymnProgress(
                    user_id=current_user.id,
                    hymn_number=hymn_number,
                    hymn_name=data.get('hymn_name', f'Hino {hymn_number}')
                )
                db.session.add(progress)
            
            if status == 'concluido' and progress.status != 'concluido':
                progress.completed_at = datetime.utcnow()
                progress.stars = data.get('stars', 3)
                award_section_xp(current_user.id, 25, f"Hino {hymn_number} concluído")
            
            progress.status = status
            if status != 'nao_iniciado' and not progress.started_at:
                progress.started_at = datetime.utcnow()
        
        else:  # teoria
            progress = MSAProgress.query.filter_by(
                user_id=current_user.id,
                section_id=section_id,
                area='teoria'
            ).first()
            
            if not progress:
                section_info = find_section_in_structure(area, section_id)
                progress = MSAProgress(
                    user_id=current_user.id,
                    area='teoria',
                    section_id=section_id,
                    section_name=section_info.get('name', ''),
                    phase=section_info.get('phase'),
                    start_page=section_info.get('start_page'),
                    end_page=section_info.get('end_page')
                )
                db.session.add(progress)
            
            if status == 'concluido' and progress.status != 'concluido':
                progress.completed_at = datetime.utcnow()
                award_section_xp(current_user.id, 35, f"Seção {progress.section_name} concluída")
            
            progress.status = status
            if status != 'nao_iniciado' and not progress.started_at:
                progress.started_at = datetime.utcnow()
        
        progress.updated_at = datetime.utcnow()
        db.session.commit()
        
        log_activity(current_user.id, f'UPDATE_{area.upper()}_PROGRESS', f'Seção {section_id} marcada como {status}')
        
        return jsonify({
            'message': 'Progresso atualizado',
            'progress': progress.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ========== PDF SERVING ==========
@msa_bp.route('/pdf/<area>', methods=['GET'])
def serve_pdf(area):
    """Servir PDF sem redirecionar para login"""
    try:
        instrument = request.args.get('instrument', 'teclado')
        
        # Determinar o caminho do PDF
        pdf_filename = None
        if area == 'teoria':
            pdf_filename = MSA_STRUCTURE['teoria'].get('pdf')
        elif area == 'metodo':
            pdf_filename = MSA_STRUCTURE['metodo']['instruments'].get(instrument, {}).get('pdf')
        elif area == 'hinario':
            pdf_filename = MSA_STRUCTURE['hinario'].get('pdf')
        
        if not pdf_filename:
            return jsonify({'error': 'PDF não encontrado para esta área'}), 404
        
        # Procurar o arquivo PDF em várias localizações
        possible_paths = [
            os.path.join(os.path.dirname(__file__), '..', '..', 'projto my t', pdf_filename),
            os.path.join(os.path.dirname(__file__), '..', pdf_filename),
            os.path.join(os.getcwd(), pdf_filename),
            os.path.join('/static', pdf_filename),
            os.path.join('/docs', pdf_filename)
        ]
        
        pdf_path = None
        for path in possible_paths:
            if os.path.exists(path):
                pdf_path = path
                break
        
        if not pdf_path:
            return jsonify({'error': f'Arquivo PDF {pdf_filename} não encontrado no servidor'}), 404
        
        # Servir o PDF com headers corretos
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=pdf_filename
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========== HELPERS ==========
def find_section_in_structure(area, section_id, instrument=None):
    """Encontrar informações de uma seção na estrutura"""
    structure = MSA_STRUCTURE.get(area, {})
    
    if area == 'metodo' and instrument:
        phases = structure.get('instruments', {}).get(instrument, {}).get('phases', [])
    else:
        phases = structure.get('phases', [])
    
    for phase in phases:
        for section in phase.get('sections', []):
            if section['id'] == section_id:
                return {**section, 'phase': phase['phase']}
    
    return {}

def calculate_area_progress(area, user_id, instrument=None):
    """Calcular progresso geral de uma área"""
    if area == 'metodo':
        total = MethodProgress.query.filter_by(user_id=user_id, instrument=instrument).count()
        completed = MethodProgress.query.filter_by(user_id=user_id, instrument=instrument, status='concluido').count()
    elif area == 'hinario':
        total = HymnProgress.query.filter_by(user_id=user_id).count()
        completed = HymnProgress.query.filter_by(user_id=user_id, status='concluido').count()
    else:  # teoria
        total = MSAProgress.query.filter_by(user_id=user_id, area='teoria').count()
        completed = MSAProgress.query.filter_by(user_id=user_id, area='teoria', status='concluido').count()
    
    return round((completed / max(1, total)) * 100) if total > 0 else 0

def award_section_xp(user_id, xp_amount, reason):
    """Dar XP ao completar uma seção"""
    progress = GamificationProgress.query.filter_by(user_id=user_id).first()
    if progress:
        progress.xp += xp_amount
        progress.updated_at = datetime.utcnow()
        db.session.commit()
        log_activity(user_id, 'AWARD_XP', f'+{xp_amount} XP: {reason}')
