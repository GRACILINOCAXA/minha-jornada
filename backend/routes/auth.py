from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from datetime import datetime

try:
    from ..models import db, User, ActivityLog, log_activity
except ImportError:
    from models import db, User, ActivityLog, log_activity

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Registrar novo usuário"""
    try:
        data = request.get_json()
        
        # Validar dados
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Usuário, e-mail e senha são obrigatórios'}), 400
        
        username = data.get('username').strip()
        email = data.get('email').strip().lower()
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        # Validar comprimento do usuário
        if len(username) < 3 or len(username) > 80:
            return jsonify({'error': 'Nome de usuário deve ter entre 3 e 80 caracteres'}), 400
        
        # Validar formato de email
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'E-mail inválido'}), 400
        
        # Validar comprimento de senha
        if len(password) < 6:
            return jsonify({'error': 'Senha deve ter no mínimo 6 caracteres'}), 400
        
        # Validar confirmação de senha
        if password != password_confirm:
            return jsonify({'error': 'As senhas não conferem'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Nome de usuário já existe'}), 400
        
        # Verificar se email já está registrado
        if User.query.filter_by(email=email).first():
            return jsonify({'error': 'E-mail já está registrado'}), 400
        
        # Criar novo usuário
        user = User(username=username, email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Registrar atividade
        log_activity(user.id, 'REGISTER', f'Usuário registrado: {username}')
        
        return jsonify({
            'message': 'Usuário registrado com sucesso',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Fazer login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'E-mail e senha são obrigatórios'}), 400
        
        login_field = data.get('email').strip().lower()
        password = data.get('password')
        
        # Buscar usuário por email OU username
        user = User.query.filter(
            (User.email == login_field) | (User.username == login_field)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'E-mail ou senha inválidos'}), 401
        
        if not user.active:
            return jsonify({'error': 'Conta inativa'}), 403
        
        # Login bem-sucedido
        login_user(user, remember=True)
        user.update_last_login()
        
        # Registrar atividade
        log_activity(user.id, 'LOGIN', f'Login: {user.username}')
        
        return jsonify({
            'message': 'Login bem-sucedido',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """Fazer logout"""
    try:
        user_id = current_user.id
        username = current_user.username
        
        logout_user()
        
        # Registrar atividade
        log_activity(user_id, 'LOGOUT', f'Logout: {username}')
        
        return jsonify({'message': 'Logout bem-sucedido'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    """Obter dados do usuário autenticado"""
    return jsonify(current_user.to_dict()), 200

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Verificar se usuário está autenticado"""
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': current_user.to_dict()}), 200
    return jsonify({'authenticated': False}), 200
