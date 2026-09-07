from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

try:
    from ..models import db, User, ActivityLog, log_activity
except ImportError:
    from models import db, User, ActivityLog, log_activity

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Obter perfil do usuário"""
    try:
        return jsonify(current_user.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Atualizar perfil do usuário"""
    try:
        data = request.get_json()
        
        # Validar novo username se fornecido
        if 'username' in data:
            new_username = data['username'].strip()
            if len(new_username) < 3 or len(new_username) > 80:
                return jsonify({'error': 'Nome de usuário deve ter entre 3 e 80 caracteres'}), 400
            
            # Verificar se já existe
            existing = User.query.filter_by(username=new_username).first()
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'Nome de usuário já existe'}), 400
            
            current_user.username = new_username
        
        # Validar novo email se fornecido
        if 'email' in data:
            new_email = data['email'].strip().lower()
            if '@' not in new_email or '.' not in new_email:
                return jsonify({'error': 'E-mail inválido'}), 400
            
            # Verificar se já existe
            existing = User.query.filter_by(email=new_email).first()
            if existing and existing.id != current_user.id:
                return jsonify({'error': 'E-mail já está registrado'}), 400
            
            current_user.email = new_email
        
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'UPDATE_PROFILE', 'Perfil atualizado')
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': current_user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    """Alterar senha do usuário"""
    try:
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Senha atual e nova senha são obrigatórias'}), 400
        
        # Verificar senha atual
        if not current_user.check_password(data.get('current_password')):
            return jsonify({'error': 'Senha atual incorreta'}), 401
        
        # Validar nova senha
        new_password = data.get('new_password')
        if len(new_password) < 6:
            return jsonify({'error': 'Nova senha deve ter no mínimo 6 caracteres'}), 400
        
        # Validar confirmação
        if data.get('new_password') != data.get('password_confirm'):
            return jsonify({'error': 'As senhas não conferem'}), 400
        
        # Atualizar senha
        current_user.set_password(new_password)
        current_user.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'CHANGE_PASSWORD', 'Senha alterada')
        
        return jsonify({'message': 'Senha alterada com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/activity-log', methods=['GET'])
@login_required
def get_activity_log():
    """Obter histórico de atividades do usuário"""
    try:
        limit = request.args.get('limit', 100, type=int)
        logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.created_at.desc()).limit(limit).all()
        return jsonify([l.to_dict() for l in logs]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
