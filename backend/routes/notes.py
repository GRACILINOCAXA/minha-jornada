from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from datetime import datetime

try:
    from ..models import db, Note, log_activity
except ImportError:
    from models import db, Note, log_activity

notes_bp = Blueprint('notes', __name__)

@notes_bp.route('', methods=['GET'])
@login_required
def get_notes():
    """Obter todas as anotações do usuário"""
    try:
        notes = Note.query.filter_by(user_id=current_user.id).order_by(Note.created_at.desc()).all()
        return jsonify([n.to_dict() for n in notes]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<int:note_id>', methods=['GET'])
@login_required
def get_note(note_id):
    """Obter uma anotação específica"""
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Anotação não encontrada'}), 404
        return jsonify(note.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@notes_bp.route('', methods=['POST'])
@login_required
def create_note():
    """Criar nova anotação"""
    try:
        data = request.get_json()
        
        if not data or not data.get('content'):
            return jsonify({'error': 'Conteúdo é obrigatório'}), 400
        
        note = Note(
            user_id=current_user.id,
            title=data.get('title', ''),
            content=data.get('content')
        )
        
        db.session.add(note)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'CREATE_NOTE', f'Anotação criada: {note.title or "Sem título"}')
        
        return jsonify({
            'message': 'Anotação criada com sucesso',
            'note': note.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    """Atualizar anotação"""
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Anotação não encontrada'}), 404
        
        data = request.get_json()
        
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'UPDATE_NOTE', f'Anotação atualizada: {note.title or "Sem título"}')
        
        return jsonify({
            'message': 'Anotação atualizada com sucesso',
            'note': note.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    """Deletar anotação"""
    try:
        note = Note.query.filter_by(id=note_id, user_id=current_user.id).first()
        if not note:
            return jsonify({'error': 'Anotação não encontrada'}), 404
        
        note_title = note.title or 'Sem título'
        db.session.delete(note)
        db.session.commit()
        
        # Registrar atividade
        log_activity(current_user.id, 'DELETE_NOTE', f'Anotação deletada: {note_title}')
        
        return jsonify({'message': 'Anotação deletada com sucesso'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
