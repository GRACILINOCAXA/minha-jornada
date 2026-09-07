"""
Testes completos para o sistema de sequência (streak) de atividades.
Valida: cálculo correto, isolamento por usuário, timezone, etc.
"""

import pytest
import uuid
from datetime import datetime, date, timedelta
from io import BytesIO

def test_no_activities_streak_is_zero():
    """TESTE 1: Sem nenhuma atividade, sequência = 0."""
    from app import create_app
    from models import db, User, GamificationProgress
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        # Criar usuário sem atividades
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Calcular sequência
        streak = calculate_current_streak(user.id)
        assert streak == 0, f"Esperava 0, recebeu {streak}"
        print("✓ TESTE 1 PASSOU: Nenhuma atividade = 0d")


def test_activity_today_streak_is_one():
    """TESTE 2: Atividade hoje = 1 dia."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        # Criar usuário
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Criar oração
        prayer = Prayer(
            user_id=user.id,
            title='Oração de teste',
            time='09:00'
        )
        db.session.add(prayer)
        db.session.commit()
        
        # Registrar conclusão hoje
        history = PrayerHistory(
            user_id=user.id,
            prayer_id=prayer.id,
            date=date.today(),
            completed_at=datetime.now()
        )
        db.session.add(history)
        db.session.commit()
        
        # Calcular sequência
        streak = calculate_current_streak(user.id)
        assert streak == 1, f"Esperava 1, recebeu {streak}"
        print("✓ TESTE 2 PASSOU: Atividade hoje = 1d")


def test_activity_today_and_yesterday_streak_is_two():
    """TESTE 3: Atividades hoje + ontem = 2 dias."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        # Criar usuário
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Criar oração
        prayer = Prayer(
            user_id=user.id,
            title='Oração de teste',
            time='09:00'
        )
        db.session.add(prayer)
        db.session.commit()
        
        # Registrar conclusões
        today = date.today()
        yesterday = today - timedelta(days=1)
        
        for activity_date in [today, yesterday]:
            history = PrayerHistory(
                user_id=user.id,
                prayer_id=prayer.id,
                date=activity_date,
                completed_at=datetime.combine(activity_date, datetime.min.time())
            )
            db.session.add(history)
        db.session.commit()
        
        # Calcular sequência
        streak = calculate_current_streak(user.id)
        assert streak == 2, f"Esperava 2, recebeu {streak}"
        print("✓ TESTE 3 PASSOU: Hoje + ontem = 2d")


def test_three_consecutive_days():
    """TESTE 4: Três dias consecutivos."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        prayer = Prayer(
            user_id=user.id,
            title='Oração de teste',
            time='09:00'
        )
        db.session.add(prayer)
        db.session.commit()
        
        # 3 dias consecutivos
        today = date.today()
        for i in range(3):
            activity_date = today - timedelta(days=i)
            history = PrayerHistory(
                user_id=user.id,
                prayer_id=prayer.id,
                date=activity_date,
                completed_at=datetime.combine(activity_date, datetime.min.time())
            )
            db.session.add(history)
        db.session.commit()
        
        streak = calculate_current_streak(user.id)
        assert streak == 3, f"Esperava 3, recebeu {streak}"
        print("✓ TESTE 4 PASSOU: Três dias consecutivos = 3d")


def test_streak_breaks_with_gap():
    """TESTE 5: Sequência quebra com gap de dias."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        prayer = Prayer(
            user_id=user.id,
            title='Oração de teste',
            time='09:00'
        )
        db.session.add(prayer)
        db.session.commit()
        
        # Hoje, ontem, 2 dias atrás (sem atividade), 3 dias atrás
        today = date.today()
        dates_with_activity = [today, today - timedelta(days=1), today - timedelta(days=3)]
        
        for activity_date in dates_with_activity:
            history = PrayerHistory(
                user_id=user.id,
                prayer_id=prayer.id,
                date=activity_date,
                completed_at=datetime.combine(activity_date, datetime.min.time())
            )
            db.session.add(history)
        db.session.commit()
        
        streak = calculate_current_streak(user.id)
        # Sequência atual deve ser 2 (hoje + ontem), porque há um gap no dia anterior a ontem
        assert streak == 2, f"Esperava 2 (quebrado pelo gap), recebeu {streak}"
        print("✓ TESTE 5 PASSOU: Gap quebra a sequência = 2d")


def test_multiple_activities_same_day_counts_as_one():
    """TESTE 6: Múltiplas atividades no mesmo dia = apenas 1 dia na sequência."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Criar 5 orações diferentes
        prayers = []
        for i in range(5):
            prayer = Prayer(
                user_id=user.id,
                title=f'Oração {i}',
                time='09:00'
            )
            db.session.add(prayer)
            prayers.append(prayer)
        db.session.commit()
        
        # Todas concluídas hoje
        today = date.today()
        for prayer in prayers:
            for j in range(2):  # 2 vezes cada oração
                history = PrayerHistory(
                    user_id=user.id,
                    prayer_id=prayer.id,
                    date=today,
                    completed_at=datetime.combine(today, datetime.min.time())
                )
                db.session.add(history)
        db.session.commit()
        
        streak = calculate_current_streak(user.id)
        assert streak == 1, f"Esperava 1d (mesmo com múltiplas atividades), recebeu {streak}"
        print("✓ TESTE 6 PASSOU: Múltiplas atividades hoje = 1d")


def test_user_isolation():
    """TESTE 7: Sequência de cada usuário é independente."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        # Usuário A com sequência
        user_a = User(
            username=f'test_a_{uuid.uuid4().hex[:8]}',
            email=f'test_a_{uuid.uuid4().hex[:8]}@example.com'
        )
        user_a.set_password('123456')
        db.session.add(user_a)
        db.session.commit()
        
        # Usuário B sem sequência
        user_b = User(
            username=f'test_b_{uuid.uuid4().hex[:8]}',
            email=f'test_b_{uuid.uuid4().hex[:8]}@example.com'
        )
        user_b.set_password('123456')
        db.session.add(user_b)
        db.session.commit()
        
        # Criar orações
        prayer_a = Prayer(user_id=user_a.id, title='Oração A', time='09:00')
        prayer_b = Prayer(user_id=user_b.id, title='Oração B', time='09:00')
        db.session.add(prayer_a)
        db.session.add(prayer_b)
        db.session.commit()
        
        # Usuário A tem 3 dias de atividades
        today = date.today()
        for i in range(3):
            activity_date = today - timedelta(days=i)
            history = PrayerHistory(
                user_id=user_a.id,
                prayer_id=prayer_a.id,
                date=activity_date,
                completed_at=datetime.combine(activity_date, datetime.min.time())
            )
            db.session.add(history)
        db.session.commit()
        
        # Calcular sequências
        streak_a = calculate_current_streak(user_a.id)
        streak_b = calculate_current_streak(user_b.id)
        
        assert streak_a == 3, f"Usuário A esperava 3, recebeu {streak_a}"
        assert streak_b == 0, f"Usuário B esperava 0, recebeu {streak_b}"
        print("✓ TESTE 7 PASSOU: Isolamento por usuário mantido")


def test_mixed_activity_types():
    """TESTE 8: Diferentes tipos de atividades no mesmo dia = 1 dia."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer, HymnProgress
    from streak_calculator import calculate_current_streak
    
    app = create_app('testing')
    
    with app.app_context():
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Oração concluída hoje
        prayer = Prayer(user_id=user.id, title='Oração', time='09:00')
        db.session.add(prayer)
        db.session.commit()
        
        today = date.today()
        
        history = PrayerHistory(
            user_id=user.id,
            prayer_id=prayer.id,
            date=today,
            completed_at=datetime.combine(today, datetime.min.time())
        )
        db.session.add(history)
        
        # Hino concluído hoje
        hymn = HymnProgress(
            user_id=user.id,
            hymn_number=1,
            hymn_name='Hino 1',
            status='concluido',
            completed_at=datetime.combine(today, datetime.min.time())
        )
        db.session.add(hymn)
        db.session.commit()
        
        streak = calculate_current_streak(user.id)
        assert streak == 1, f"Esperava 1d (mesmo com tipos diferentes), recebeu {streak}"
        print("✓ TESTE 8 PASSOU: Diferentes tipos de atividade = 1d")


def test_endpoint_returns_correct_streak():
    """TESTE 9: Endpoint /api/gamification/streak retorna valor correto."""
    from app import create_app
    from models import db, User, PrayerHistory, Prayer
    
    app = create_app('testing')
    
    with app.app_context():
        user = User(
            username=f'test_{uuid.uuid4().hex[:8]}',
            email=f'test_{uuid.uuid4().hex[:8]}@example.com'
        )
        user.set_password('123456')
        db.session.add(user)
        db.session.commit()
        
        # Criar atividade
        prayer = Prayer(user_id=user.id, title='Oração', time='09:00')
        db.session.add(prayer)
        db.session.commit()
        
        today = date.today()
        for i in range(2):
            history = PrayerHistory(
                user_id=user.id,
                prayer_id=prayer.id,
                date=today - timedelta(days=i),
                completed_at=datetime.combine(today - timedelta(days=i), datetime.min.time())
            )
            db.session.add(history)
        db.session.commit()
        
        # Testar endpoint
        with app.test_client() as client:
            # Login
            r_login = client.post('/api/auth/login', json={
                'email': user.email,
                'password': '123456'
            })
            assert r_login.status_code == 200
            
            # Obter streak
            r_streak = client.get('/api/gamification/streak')
            assert r_streak.status_code == 200
            
            data = r_streak.get_json()
            assert data['streak'] == 2, f"Esperava 2, recebeu {data['streak']}"
            print("✓ TESTE 9 PASSOU: Endpoint retorna sequência correta")


@pytest.fixture
def client():
    """Client de teste."""
    from app import create_app
    from models import db
    
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app.test_client()


if __name__ == '__main__':
    # Executar testes manualmente
    print("\n" + "="*60)
    print("TESTES DE SEQUÊNCIA (STREAK)")
    print("="*60 + "\n")
    
    test_no_activities_streak_is_zero()
    test_activity_today_streak_is_one()
    test_activity_today_and_yesterday_streak_is_two()
    test_three_consecutive_days()
    test_streak_breaks_with_gap()
    test_multiple_activities_same_day_counts_as_one()
    test_user_isolation()
    test_mixed_activity_types()
    test_endpoint_returns_correct_streak()
    
    print("\n" + "="*60)
    print("✅ TODOS OS TESTES DE SEQUÊNCIA PASSARAM")
    print("="*60 + "\n")
