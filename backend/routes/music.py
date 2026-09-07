from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime, date

try:
    from ..models import db, MusicStudy, log_activity
except ImportError:
    from models import db, MusicStudy, log_activity

music_bp = Blueprint('music', __name__)

@music_bp.route('/studies', methods=['GET'])
@login_required
def get_music_studies():
    """Obter todos os estudos musicais do usuário"""
    try:
        area = request.args.get('area')
        
        query = MusicStudy.query.filter_by(user_id=current_user.id)
        
        if area:
            query = query.filter_by(area=area)
        
        studies = query.all()
        return jsonify([s.to_dict() for s in studies]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/studies/<int:study_id>', methods=['GET'])
@login_required
def get_music_study(study_id):
    """Obter um estudo musical específico"""
    try:
        study = MusicStudy.query.filter_by(id=study_id, user_id=current_user.id).first()
        if not study:
            return jsonify({'error': 'Estudo não encontrado'}), 404
        return jsonify(study.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@music_bp.route('/studies', methods=['POST'])
@login_required
def create_music_study():
    """Criar novo estudo musical"""
    try:
        data = request.get_json()
        
        if not data or not data.get('area') or not data.get('title'):
            return jsonify({'error': 'Área e título são obrigatórios'}), 400
        
        # Validar área
        raw_area = (data.get('area') or '').lower()
        area_aliases = {'msa': 'teoria', 'hinaro': 'hinario'}
        area = area_aliases.get(raw_area, raw_area)
        valid_areas = ['teoria', 'metodo', 'hinario']
        if area not in valid_areas:
            return jsonify({'error': f'Área deve ser uma de: {", ".join(valid_areas)}'}), 400
        
        study = MusicStudy(
            user_id=current_user.id,
            area=area,
            title=data.get('title'),
            description=data.get('description', ''),
            duration=data.get('duration', 0),
            progress=data.get('progress', 0),
            difficulty=data.get('difficulty'),
            rating=data.get('rating'),
            learned=data.get('learned', ''),
            next_goal=data.get('next_goal', ''),
            notes=data.get('notes', ''),
            study_date=datetime.fromisoformat(data.get('study_date')) if data.get('study_date') else date.today()
        )
        
        db.session.add(study)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'CREATE_STUDY', f'Estudo criado: {study.area} - {study.title}')
        
        return jsonify({
            'message': 'Estudo criado com sucesso',
            'study': study.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/studies/<int:study_id>', methods=['PUT'])
@login_required
def update_music_study(study_id):
    """Atualizar estudo musical"""
    try:
        study = MusicStudy.query.filter_by(id=study_id, user_id=current_user.id).first()
        if not study:
            return jsonify({'error': 'Estudo não encontrado'}), 404
        
        data = request.get_json()
        
        if 'area' in data:
            raw_area = str(data['area']).lower()
            area_aliases = {'msa': 'teoria', 'hinaro': 'hinario'}
            normalized_area = area_aliases.get(raw_area, raw_area)
            if normalized_area not in ['teoria', 'metodo', 'hinario']:
                return jsonify({'error': 'Área inválida'}), 400
            study.area = normalized_area
        
        if 'title' in data:
            study.title = data['title']
        if 'description' in data:
            study.description = data['description']
        if 'duration' in data:
            study.duration = data['duration']
        if 'progress' in data:
            study.progress = min(100, max(0, data['progress']))
        if 'difficulty' in data:
            study.difficulty = data['difficulty']
        if 'rating' in data:
            study.rating = data['rating']
        if 'learned' in data:
            study.learned = data['learned']
        if 'next_goal' in data:
            study.next_goal = data['next_goal']
        if 'notes' in data:
            study.notes = data['notes']
        if 'study_date' in data:
            study.study_date = datetime.fromisoformat(data['study_date'])
        
        study.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'UPDATE_STUDY', f'Estudo atualizado: {study.area} - {study.title}')
        
        return jsonify({
            'message': 'Estudo atualizado com sucesso',
            'study': study.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/studies/<int:study_id>', methods=['DELETE'])
@login_required
def delete_music_study(study_id):
    """Deletar estudo musical"""
    try:
        study = MusicStudy.query.filter_by(id=study_id, user_id=current_user.id).first()
        if not study:
            return jsonify({'error': 'Estudo não encontrado'}), 404
        
        study_info = f'{study.area} - {study.title}'
        db.session.delete(study)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'DELETE_STUDY', f'Estudo deletado: {study_info}')
        
        return jsonify({'message': 'Estudo deletado com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@music_bp.route('/summary', methods=['GET'])
@login_required
def get_music_summary():
    """Obter resumo dos estudos musicais"""
    try:
        studies = MusicStudy.query.filter_by(user_id=current_user.id).all()
        
        summary = {
            'total_studies': len(studies),
            'total_duration': sum(s.duration for s in studies),
            'average_progress': int(sum(s.progress for s in studies) / len(studies)) if studies else 0,
            'by_area': {}
        }
        
        for area in ['teoria', 'metodo', 'hinario']:
            area_studies = [s for s in studies if s.area == area]
            summary['by_area'][area] = {
                'count': len(area_studies),
                'average_progress': int(sum(s.progress for s in area_studies) / len(area_studies)) if area_studies else 0,
                'total_duration': sum(s.duration for s in area_studies)
            }
        
        return jsonify(summary), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
