#!/usr/bin/env python3
"""Teste de sistema de estudo"""

from app import create_app
from models import db, User, UserSettings, GamificationProgress

app = create_app()

with app.app_context():
    user = User.query.filter_by(email='test_study@example.com').first()
    if not user:
        user = User(
            username='test_study',
            email='test_study@example.com'
        )
        user.set_password('Test123!')
        db.session.add(user)
        db.session.flush()

        settings = UserSettings(user_id=user.id, selected_instrument='teclado')
        gamif = GamificationProgress(user_id=user.id)
        db.session.add(settings)
        db.session.add(gamif)
        db.session.commit()
        print("✓ Usuário de teste criado")

with app.test_client() as client:
    login_response = client.post('/api/auth/login', json={
        'email': 'test_study@example.com',
        'password': 'Test123!'
    })
    assert login_response.status_code == 200, f"Login falhou: {login_response.status_code}"

    with app.app_context():
        user = User.query.filter_by(email='test_study@example.com').first()
        if user:
            user.instrumento = 'saxofone_soprano'
            db.session.add(user)
            db.session.commit()

    from routes.api_study import load_msa_structure, load_metodo_structure

    msa = load_msa_structure()
    print(f"\n✓ MSA carregado: {msa['total_fases']} fases")
    print(f"  Exemplo: {msa['fases'][0]['titulo']} com {len(msa['fases'][0]['secoes'])} seções")

    metodo = load_metodo_structure()
    print(f"\n✓ Método carregado: {metodo['total_fases']} fases")
    print(f"  Módulos: {len(metodo['modulos'])} ({', '.join([m['nome'] for m in metodo['modulos'][:2]])}...)")

    teoria_response = client.get('/api/study/structure/teoria')
    assert teoria_response.status_code == 200, f"Teoria deve abrir MSA, recebeu {teoria_response.status_code}"
    print("\n✓ Teoria aceita área válida e carrega estrutura MSA")

    metodo_response = client.get('/api/study/structure/metodo')
    assert metodo_response.status_code == 200, f"Método deve responder 200, recebeu {metodo_response.status_code}"
    assert metodo_response.get_json().get('instrument') == 'saxofone_soprano', 'Método deve seguir o instrumento salvo do usuário'
    print("✓ Método aceita área válida e usa o instrumento salvo")

    hinario_response = client.get('/api/study/structure/hinario')
    assert hinario_response.status_code == 200, f"Hinário deve responder 200, recebeu {hinario_response.status_code}"
    assert hinario_response.get_json().get('instrumento') == 'saxofone_soprano', 'Hinário deve seguir o instrumento salvo do usuário'
    print("✓ Hinário aceita área válida e usa o instrumento salvo")

print("\n✅ Sistema de Estudo pronto para uso!")
