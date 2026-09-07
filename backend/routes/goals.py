from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

try:
    from ..models import db, Goal, log_activity
except ImportError:
    from models import db, Goal, log_activity

goals_bp = Blueprint('goals', __name__)

@goals_bp.route('', methods=['GET'])
@login_required
def get_goals():
    """Obter todas as metas do usuário"""
    try:
        goals = Goal.query.filter_by(user_id=current_user.id).all()
        return jsonify([g.to_dict() for g in goals]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@goals_bp.route('/<int:goal_id>', methods=['GET'])
@login_required
def get_goal(goal_id):
    """Obter uma meta específica"""
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        if not goal:
            return jsonify({'error': 'Meta não encontrada'}), 404
        return jsonify(goal.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@goals_bp.route('', methods=['POST'])
@login_required
def create_goal():
    """Criar nova meta"""
    try:
        data = request.get_json()
        
        if not data or not data.get('title'):
            return jsonify({'error': 'Título é obrigatório'}), 400
        
        goal = Goal(
            user_id=current_user.id,
            title=data.get('title'),
            description=data.get('description', ''),
            category=data.get('category', ''),
            progress=data.get('progress', 0),
            deadline=datetime.fromisoformat(data.get('deadline')) if data.get('deadline') else None,
            completed=data.get('completed', False)
        )
        
        db.session.add(goal)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'CREATE_GOAL', f'Meta criada: {goal.title}')
        
        return jsonify({
            'message': 'Meta criada com sucesso',
            'goal': goal.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@goals_bp.route('/<int:goal_id>', methods=['PUT'])
@login_required
def update_goal(goal_id):
    """Atualizar meta"""
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        if not goal:
            return jsonify({'error': 'Meta não encontrada'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            goal.title = data['title']
        if 'description' in data:
            goal.description = data['description']
        if 'category' in data:
            goal.category = data['category']
        if 'progress' in data:
            goal.progress = min(100, max(0, data['progress']))
        if 'deadline' in data:
            goal.deadline = datetime.fromisoformat(data['deadline']) if data['deadline'] else None
        if 'completed' in data:
            goal.completed = data['completed']
        
        goal.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'UPDATE_GOAL', f'Meta atualizada: {goal.title}')
        
        return jsonify({
            'message': 'Meta atualizada com sucesso',
            'goal': goal.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_goal(goal_id):
    """Deletar meta"""
    try:
        goal = Goal.query.filter_by(id=goal_id, user_id=current_user.id).first()
        if not goal:
            return jsonify({'error': 'Meta não encontrada'}), 404
        
        goal_title = goal.title
        db.session.delete(goal)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'DELETE_GOAL', f'Meta deletada: {goal_title}')
        
        return jsonify({'message': 'Meta deletada com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
