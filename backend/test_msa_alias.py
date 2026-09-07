#!/usr/bin/env python3
"""Teste para garantir que o MSA usa a área correta de progresso."""

from app import create_app
from models import db, User, UserSettings, GamificationProgress, MSAProgress
from routes.api_study import get_progress_report

app = create_app()

with app.app_context():
    username = 'msa_alias_check'
    user = User.query.filter_by(username=username).first()
    if not user:
        user = User(username=username, email='msa_alias_check@example.com')
        user.set_password('Test123!')
        db.session.add(user)
        db.session.flush()
        db.session.add(UserSettings(user_id=user.id, selected_instrument='teclado'))
        db.session.add(GamificationProgress(user_id=user.id))
        db.session.commit()

    db.session.query(MSAProgress).filter_by(user_id=user.id).delete()
    db.session.add(MSAProgress(
        user_id=user.id,
        area='teoria',
        phase=1,
        section_id='msa_1_1',
        section_name='Teste',
        status='concluido'
    ))
    db.session.commit()

    with app.test_request_context('/api/study/progress-report'):
        from flask_login import login_user
        login_user(user)
        response, status_code = get_progress_report()
        data = response.get_json()
        print(data)
        assert data['msa']['secoes_concluidas'] == 1, 'MSA completeness should count theory-area records'
        assert data['msa']['progresso_percent'] == 100, 'MSA progress should reflect theory-area completion'
        assert status_code == 200, 'The progress report should succeed'
        print('✅ MSA theory progress alias test passed')
