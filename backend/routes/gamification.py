import json
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required

try:
    from ..models import db, GamificationProgress, log_activity
    from ..streak_calculator import calculate_current_streak, update_streak_in_gamification
except ImportError:
    from models import db, GamificationProgress, log_activity
    from streak_calculator import calculate_current_streak, update_streak_in_gamification

gamification_bp = Blueprint('gamification', __name__)


@gamification_bp.route('', methods=['GET'])
@login_required
def get_gamification():
    """Obter progresso de gamificação do usuário atual."""
    try:
        progress = GamificationProgress.query.filter_by(user_id=current_user.id).first()
        if not progress:
            progress = GamificationProgress(
                user_id=current_user.id,
                xp=0,
                streak=0,
                total_exercises=0,
                lessons_completed=0,
                hymns_dominated=0,
                selected_instrument='teclado',
                lessons_data='[]',
                hymns_data='[]'
            )
            db.session.add(progress)
            db.session.commit()
        return jsonify(progress.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('', methods=['PUT'])
@login_required
def update_gamification():
    """Atualizar progresso do MSA, XP e conquistas do usuário."""
    try:
        progress = GamificationProgress.query.filter_by(user_id=current_user.id).first()
        if not progress:
            progress = GamificationProgress(user_id=current_user.id)
            db.session.add(progress)
            db.session.flush()

        data = request.get_json() or {}

        if 'xp' in data:
            progress.xp = int(data['xp'])
        if 'streak' in data:
            progress.streak = int(data['streak'])
        if 'total_exercises' in data:
            progress.total_exercises = int(data['total_exercises'])
        if 'lessons_completed' in data:
            progress.lessons_completed = int(data['lessons_completed'])
        if 'hymns_dominated' in data:
            progress.hymns_dominated = int(data['hymns_dominated'])
        if 'selected_instrument' in data:
            progress.selected_instrument = data['selected_instrument']
        if 'last_study_date' in data and data['last_study_date']:
            progress.last_study_date = datetime.fromisoformat(data['last_study_date']).date()
        if 'lessons' in data:
            progress.lessons_data = json.dumps(data['lessons'])
        if 'hymns' in data:
            progress.hymns_data = json.dumps(data['hymns'])

        progress.updated_at = datetime.utcnow()
        db.session.commit()

        log_activity(current_user.id, 'UPDATE_GAMIFICATION', 'Progresso de gamificação atualizado')

        return jsonify({
            'message': 'Progresso salvo com sucesso',
            'gamification': progress.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/streak', methods=['GET'])
@login_required
def get_current_streak():
    """Retorna a sequência atual calculada corretamente baseada no histórico real."""
    try:
        # Calcular sequência a partir do histórico
        streak = calculate_current_streak(current_user.id)
        
        # Obter ou criar registro de gamificação
        progress = GamificationProgress.query.filter_by(user_id=current_user.id).first()
        if not progress:
            progress = GamificationProgress(
                user_id=current_user.id,
                streak=streak,
                xp=0,
                total_exercises=0,
                lessons_completed=0,
                hymns_dominated=0,
                selected_instrument='teclado',
                lessons_data='[]',
                hymns_data='[]'
            )
            db.session.add(progress)
        else:
            # Atualizar com o valor calculado se diferente
            progress.streak = streak
            progress.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'streak': streak,
            'gamification': progress.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@gamification_bp.route('/streak/recalculate', methods=['POST'])
@login_required
def recalculate_streak():
    """Force a recalculation of the current streak from activity history."""
    try:
        streak = update_streak_in_gamification(current_user.id)
        progress = GamificationProgress.query.filter_by(user_id=current_user.id).first()
        
        log_activity(current_user.id, 'RECALCULATE_STREAK', f'Sequência recalculada: {streak} dias')
        
        return jsonify({
            'message': 'Sequência recalculada com sucesso',
            'streak': streak,
            'gamification': progress.to_dict() if progress else {'streak': streak}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
