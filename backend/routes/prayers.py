from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime, date

try:
    from ..models import db, Prayer, PrayerHistory, log_activity
except ImportError:
    from models import db, Prayer, PrayerHistory, log_activity

prayers_bp = Blueprint('prayers', __name__)

@prayers_bp.route('', methods=['GET'])
@login_required
def get_prayers():
    """Obter todas as orações do usuário"""
    try:
        prayers = Prayer.query.filter_by(user_id=current_user.id).all()
        return jsonify([p.to_dict() for p in prayers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('/<int:prayer_id>', methods=['GET'])
@login_required
def get_prayer(prayer_id):
    """Obter uma oração específica"""
    try:
        prayer = Prayer.query.filter_by(id=prayer_id, user_id=current_user.id).first()
        if not prayer:
            return jsonify({'error': 'Oração não encontrada'}), 404
        return jsonify(prayer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('', methods=['POST'])
@login_required
def create_prayer():
    """Criar nova oração"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('time'):
            return jsonify({'error': 'Título e horário são obrigatórios'}), 400
        
        prayer = Prayer(
            user_id=current_user.id,
            title=data.get('title'),
            description=data.get('description', ''),
            time=data.get('time'),
            enabled=data.get('enabled', True),
            notification_enabled=data.get('notification_enabled', False),
            days=data.get('days', 'daily')
        )
        
        db.session.add(prayer)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'CREATE_PRAYER', f'Oração criada: {prayer.title}')
        
        return jsonify({
            'message': 'Oração criada com sucesso',
            'prayer': prayer.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('/<int:prayer_id>', methods=['PUT'])
@login_required
def update_prayer(prayer_id):
    """Atualizar oração"""
    try:
        prayer = Prayer.query.filter_by(id=prayer_id, user_id=current_user.id).first()
        if not prayer:
            return jsonify({'error': 'Oração não encontrada'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            prayer.title = data['title']
        if 'description' in data:
            prayer.description = data['description']
        if 'time' in data:
            prayer.time = data['time']
        if 'enabled' in data:
            prayer.enabled = data['enabled']
        if 'notification_enabled' in data:
            prayer.notification_enabled = data['notification_enabled']
        if 'days' in data:
            prayer.days = data['days']
        
        prayer.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'UPDATE_PRAYER', f'Oração atualizada: {prayer.title}')
        
        return jsonify({
            'message': 'Oração atualizada com sucesso',
            'prayer': prayer.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('/<int:prayer_id>', methods=['DELETE'])
@login_required
def delete_prayer(prayer_id):
    """Deletar oração"""
    try:
        prayer = Prayer.query.filter_by(id=prayer_id, user_id=current_user.id).first()
        if not prayer:
            return jsonify({'error': 'Oração não encontrada'}), 404
        
        prayer_title = prayer.title
        db.session.delete(prayer)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'DELETE_PRAYER', f'Oração deletada: {prayer_title}')
        
        return jsonify({'message': 'Oração deletada com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('/<int:prayer_id>/complete', methods=['POST'])
@login_required
def complete_prayer(prayer_id):
    """Marcar oração como concluída"""
    try:
        prayer = Prayer.query.filter_by(id=prayer_id, user_id=current_user.id).first()
        if not prayer:
            return jsonify({'error': 'Oração não encontrada'}), 404
        
        today = date.today()
        
        # Verificar se já foi concluída hoje
        existing = PrayerHistory.query.filter_by(
            user_id=current_user.id,
            prayer_id=prayer_id,
            date=today
        ).first()
        
        if existing:
            return jsonify({'message': 'Oração já foi concluída hoje'}), 200
        
        # Criar registro de conclusão
        history = PrayerHistory(
            user_id=current_user.id,
            prayer_id=prayer_id,
            date=today
        )
        
        db.session.add(history)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'COMPLETE_PRAYER', f'Oração concluída: {prayer.title}')
        
        return jsonify({
            'message': 'Oração marcada como concluída',
            'history': history.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@prayers_bp.route('/history', methods=['GET'])
@login_required
def get_prayer_history():
    """Obter histórico de orações"""
    try:
        history = PrayerHistory.query.filter_by(user_id=current_user.id).all()
        return jsonify([h.to_dict() for h in history]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
