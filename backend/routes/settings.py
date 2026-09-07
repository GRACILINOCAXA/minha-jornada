from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

try:
    from ..models import db, UserSettings, log_activity
except ImportError:
    from models import db, UserSettings, log_activity

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('', methods=['GET'])
@login_required
def get_settings():
    """Obter configurações do usuário"""
    try:
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings:
            # Criar configurações padrão se não existirem
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
            db.session.commit()
        
        return jsonify(settings.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@settings_bp.route('', methods=['PUT'])
@login_required
def update_settings():
    """Atualizar configurações do usuário"""
    try:
        settings = UserSettings.query.filter_by(user_id=current_user.id).first()
        
        if not settings:
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
            db.session.flush()
        
        data = request.get_json()
        
        if 'theme' in data:
            if data['theme'] not in ['light', 'dark']:
                return jsonify({'error': 'Tema deve ser "light" ou "dark"'}), 400
            settings.theme = data['theme']
        
        if 'notifications_enabled' in data:
            settings.notifications_enabled = data['notifications_enabled']
        
        if 'daily_study_goal' in data:
            settings.daily_study_goal = max(1, data['daily_study_goal'])

        if 'selected_instrument' in data:
            settings.selected_instrument = data['selected_instrument']
        
        settings.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'ALTER_SETTINGS', 'Configurações alteradas')
        
        return jsonify({
            'message': 'Configurações atualiza com sucesso',
            'settings': settings.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
