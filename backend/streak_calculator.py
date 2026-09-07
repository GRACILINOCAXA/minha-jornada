"""
Cálculo confiável da sequência de dias consecutivos de atividades.
Baseado em histórico real de atividades concluídas pelo usuário.
"""

from datetime import datetime, date, timedelta
from sqlalchemy import func, and_

try:
    from .models import (
        db, User, PrayerHistory, MSAProgress, 
        HymnProgress, MethodProgress, ChorusProgress, 
        StudySession
    )
except ImportError:
    from models import (
        db, User, PrayerHistory, MSAProgress, 
        HymnProgress, MethodProgress, ChorusProgress, 
        StudySession
    )


def get_local_date(dt=None):
    """Retorna a data local (sem timezone awareness issues)."""
    if dt is None:
        dt = datetime.now()
    if isinstance(dt, datetime):
        return dt.date()
    return dt


def is_valid_streak_activity(activity_type, activity_status, completed_at):
    """
    Determina se uma atividade conta para a sequência.
    
    Args:
        activity_type: tipo da atividade (oração, hino, coro, método, msa)
        activity_status: status (concluído, em_andamento, não_iniciado)
        completed_at: timestamp de conclusão
    
    Returns:
        bool: True se a atividade conta para a sequência
    """
    # Só atividades marcadas como concluídas contam
    if activity_status not in ['concluido', 'completed']:
        return False
    
    # Atividade precisa ter data de conclusão
    if not completed_at:
        return False
    
    return True


def get_activity_dates_for_user(user_id):
    """
    Busca todas as datas únicas em que o usuário realizou atividades válidas.
    
    Args:
        user_id: ID do usuário
    
    Returns:
        set: conjunto de datas (date objects) em que houve atividades
    """
    activity_dates = set()
    
    # 1. Orações concluídas
    prayers = db.session.query(func.date(PrayerHistory.completed_at).label('completion_date')).filter(
        PrayerHistory.user_id == user_id
    ).distinct().all()
    
    for row in prayers:
        if row.completion_date:
            # Garantir que é um objeto date
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    # 2. MSA concluído (teoria, método, etc)
    msa_activities = db.session.query(func.date(MSAProgress.completed_at).label('completion_date')).filter(
        and_(
            MSAProgress.user_id == user_id,
            MSAProgress.status == 'concluido',
            MSAProgress.completed_at.isnot(None)
        )
    ).distinct().all()
    
    for row in msa_activities:
        if row.completion_date:
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    # 3. Hinos concluídos
    hymns = db.session.query(func.date(HymnProgress.completed_at).label('completion_date')).filter(
        and_(
            HymnProgress.user_id == user_id,
            HymnProgress.status == 'concluido',
            HymnProgress.completed_at.isnot(None)
        )
    ).distinct().all()
    
    for row in hymns:
        if row.completion_date:
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    # 4. Método concluído
    methods = db.session.query(func.date(MethodProgress.completed_at).label('completion_date')).filter(
        and_(
            MethodProgress.user_id == user_id,
            MethodProgress.status == 'concluido',
            MethodProgress.completed_at.isnot(None)
        )
    ).distinct().all()
    
    for row in methods:
        if row.completion_date:
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    # 5. Coros concluídos
    choruses = db.session.query(func.date(ChorusProgress.completed_at).label('completion_date')).filter(
        and_(
            ChorusProgress.user_id == user_id,
            ChorusProgress.status == 'concluido',
            ChorusProgress.completed_at.isnot(None)
        )
    ).distinct().all()
    
    for row in choruses:
        if row.completion_date:
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    # 6. Sessões de estudo concluídas
    study_sessions = db.session.query(func.date(StudySession.end_time).label('completion_date')).filter(
        and_(
            StudySession.user_id == user_id,
            StudySession.status == 'concluido',
            StudySession.end_time.isnot(None)
        )
    ).distinct().all()
    
    for row in study_sessions:
        if row.completion_date:
            completion_date = row.completion_date
            if isinstance(completion_date, str):
                completion_date = datetime.strptime(completion_date, '%Y-%m-%d').date()
            activity_dates.add(completion_date)
    
    return activity_dates


def calculate_current_streak(user_id):
    """
    Calcula a sequência atual baseada no histórico real de atividades.
    
    Algoritmo:
    1. Coleta todas as datas com atividades válidas
    2. Ordena as datas em ordem decrescente
    3. Começa do dia de hoje e verifica dias consecutivos para trás
    4. Para se encontrar um dia sem atividades
    
    Args:
        user_id: ID do usuário
    
    Returns:
        int: quantidade de dias consecutivos (0 se nenhuma atividade)
    """
    activity_dates = get_activity_dates_for_user(user_id)
    
    if not activity_dates:
        return 0
    
    today = get_local_date()
    
    # Ordenar datas em ordem decrescente (do mais recente para o mais antigo)
    sorted_dates = sorted(activity_dates, reverse=True)
    
    streak = 0
    check_date = today
    
    for activity_date in sorted_dates:
        # Garantir que ambos são objetos date
        if isinstance(activity_date, str):
            activity_date = datetime.strptime(activity_date, '%Y-%m-%d').date()
        if isinstance(check_date, str):
            check_date = datetime.strptime(check_date, '%Y-%m-%d').date()
        
        # Se a data de atividade é o dia que estamos verificando, incrementar sequência
        if activity_date == check_date:
            streak += 1
            # Mover para o dia anterior
            check_date = check_date - timedelta(days=1)
        elif activity_date > check_date:
            # Atividade é mais recente que o dia que estamos verificando, pular
            continue
        else:
            # Encontramos um dia sem atividades, parar
            break
    
    return streak


def update_streak_in_gamification(user_id):
    """
    Calcula e atualiza a sequência no GamificationProgress.
    
    Args:
        user_id: ID do usuário
    
    Returns:
        int: a nova sequência
    """
    try:
        from .models import GamificationProgress
    except ImportError:
        from models import GamificationProgress
    
    streak = calculate_current_streak(user_id)
    
    progress = GamificationProgress.query.filter_by(user_id=user_id).first()
    if not progress:
        progress = GamificationProgress(user_id=user_id, streak=streak)
        db.session.add(progress)
    else:
        progress.streak = streak
        progress.updated_at = datetime.utcnow()
    
    db.session.commit()
    
    return streak


def verify_streak_integrity():
    """
    Verifica e corrige integridade de sequências de todos os usuários.
    Útil para validação/auditoria.
    
    Returns:
        dict: relatório de correções
    """
    report = {
        'users_processed': 0,
        'corrections_made': 0,
        'details': []
    }
    
    users = User.query.all()
    
    for user in users:
        old_streak = user.gamification_progress.streak if user.gamification_progress else 0
        new_streak = update_streak_in_gamification(user.id)
        
        report['users_processed'] += 1
        
        if old_streak != new_streak:
            report['corrections_made'] += 1
            report['details'].append({
                'user_id': user.id,
                'username': user.username,
                'old_streak': old_streak,
                'new_streak': new_streak
            })
    
    return report
