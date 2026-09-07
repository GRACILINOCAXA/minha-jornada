import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """Modelo de usuário"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    instrumento = db.Column(db.String(50), default=None)  # Instrumento do usuário
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    prayers = db.relationship('Prayer', backref='user', lazy=True, cascade='all, delete-orphan')
    prayer_history = db.relationship('PrayerHistory', backref='user', lazy=True, cascade='all, delete-orphan')
    music_studies = db.relationship('MusicStudy', backref='user', lazy=True, cascade='all, delete-orphan')
    goals = db.relationship('Goal', backref='user', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    settings = db.relationship('UserSettings', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    activity_logs = db.relationship('ActivityLog', backref='user', lazy=True, cascade='all, delete-orphan')
    gamification_progress = db.relationship('GamificationProgress', backref='user', lazy=True, uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash e armazena a senha"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """Atualiza a data do último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def to_dict(self):
        """Retorna dados do usuário como dicionário"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'instrumento': self.instrumento,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Prayer(db.Model):
    """Modelo de oração"""
    __tablename__ = 'prayers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    time = db.Column(db.String(5), nullable=False)  # HH:MM
    enabled = db.Column(db.Boolean, default=True)
    notification_enabled = db.Column(db.Boolean, default=False)
    days = db.Column(db.String(100), default='daily')  # daily, monday, tuesday, etc
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento
    history = db.relationship('PrayerHistory', backref='prayer', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time': self.time,
            'enabled': self.enabled,
            'notification_enabled': self.notification_enabled,
            'days': self.days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PrayerHistory(db.Model):
    """Histórico de orações concluídas"""
    __tablename__ = 'prayer_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    prayer_id = db.Column(db.Integer, db.ForeignKey('prayers.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'prayer_id': self.prayer_id,
            'date': self.date.isoformat() if self.date else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }

class MusicStudy(db.Model):
    """Modelo de estudo musical (MSA)"""
    __tablename__ = 'music_studies'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    area = db.Column(db.String(50), nullable=False)  # teoria, metodo, instrumento, hinaro
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, default=0)  # em minutos
    progress = db.Column(db.Integer, default=0)  # 0-100
    difficulty = db.Column(db.String(50))  # fácil, médio, difícil
    rating = db.Column(db.Integer)  # 1-5
    learned = db.Column(db.Text)
    next_goal = db.Column(db.Text)
    notes = db.Column(db.Text)
    study_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'title': self.title,
            'description': self.description,
            'duration': self.duration,
            'progress': self.progress,
            'difficulty': self.difficulty,
            'rating': self.rating,
            'learned': self.learned,
            'next_goal': self.next_goal,
            'notes': self.notes,
            'study_date': self.study_date.isoformat() if self.study_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Goal(db.Model):
    """Modelo de metas"""
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    progress = db.Column(db.Integer, default=0)  # 0-100
    deadline = db.Column(db.Date)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'progress': self.progress,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Note(db.Model):
    """Modelo de anotações"""
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CustomInstrumentMethod(db.Model):
    """Método personalizado anexado por usuário e instrumento."""
    __tablename__ = 'custom_instrument_methods'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'instrument', name='uq_user_instrument_custom_method'),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    instrument = db.Column(db.String(80), nullable=False, index=True)
    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    mime_type = db.Column(db.String(120), default='application/pdf')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'instrument': self.instrument,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'file_url': f'/api/instruments/method/file?instrument={self.instrument}',
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

class UserSettings(db.Model):
    """Configurações do usuário"""
    __tablename__ = 'user_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    theme = db.Column(db.String(20), default='light')  # light, dark
    notifications_enabled = db.Column(db.Boolean, default=False)
    daily_study_goal = db.Column(db.Integer, default=30)  # em minutos
    selected_instrument = db.Column(db.String(50), default='teclado')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'theme': self.theme,
            'notifications_enabled': self.notifications_enabled,
            'daily_study_goal': self.daily_study_goal,
            'selected_instrument': self.selected_instrument or 'teclado'
        }

class ActivityLog(db.Model):
    """Log de atividades do usuário"""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    action = db.Column(db.String(50), nullable=False)  # LOGIN, LOGOUT, CREATE_PRAYER, etc
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'action': self.action,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class GamificationProgress(db.Model):
    """Monitoramento de XP, níveis e progresso do MSA"""
    __tablename__ = 'gamification_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True, index=True)
    xp = db.Column(db.Integer, default=0)
    streak = db.Column(db.Integer, default=0)
    total_exercises = db.Column(db.Integer, default=0)
    lessons_completed = db.Column(db.Integer, default=0)
    hymns_dominated = db.Column(db.Integer, default=0)
    selected_instrument = db.Column(db.String(50), default='teclado')
    last_study_date = db.Column(db.Date)
    lessons_data = db.Column(db.Text, default='[]')
    hymns_data = db.Column(db.Text, default='[]')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'xp': self.xp or 0,
            'streak': self.streak or 0,
            'total_exercises': self.total_exercises or 0,
            'lessons_completed': self.lessons_completed or 0,
            'hymns_dominated': self.hymns_dominated or 0,
            'selected_instrument': self.selected_instrument or 'teclado',
            'last_study_date': self.last_study_date.isoformat() if self.last_study_date else None,
            'lessons': json.loads(self.lessons_data or '[]'),
            'hymns': json.loads(self.hymns_data or '[]'),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MSAProgress(db.Model):
    """Rastreamento de progresso do MSA por seção/fase"""
    __tablename__ = 'msa_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    area = db.Column(db.String(50), nullable=False)  # teoria, metodo, hinario
    phase = db.Column(db.Integer)  # número da fase (1, 2, 3...)
    section_id = db.Column(db.String(100))  # identificador único da seção
    section_name = db.Column(db.String(200))  # nome da seção
    status = db.Column(db.String(50), default='nao_iniciado')  # nao_iniciado, em_andamento, concluido
    start_page = db.Column(db.Integer)  # página inicial da seção no PDF
    end_page = db.Column(db.Integer)  # página final da seção no PDF
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'phase': self.phase,
            'section_id': self.section_id,
            'section_name': self.section_name,
            'status': self.status,
            'start_page': self.start_page,
            'end_page': self.end_page,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class HymnProgress(db.Model):
    """Rastreamento de progresso de hinos"""
    __tablename__ = 'hymn_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    hymn_number = db.Column(db.Integer, nullable=False)  # número do hino
    hymn_name = db.Column(db.String(200))  # nome do hino
    status = db.Column(db.String(50), default='nao_iniciado')  # nao_iniciado, em_andamento, concluido
    difficulty = db.Column(db.String(50))  # facilidade, médio, difícil
    stars = db.Column(db.Integer, default=0)  # 0-5 stars
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'hymn_number': self.hymn_number,
            'hymn_name': self.hymn_name,
            'status': self.status,
            'difficulty': self.difficulty,
            'stars': self.stars,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MethodProgress(db.Model):
    """Rastreamento de progresso do método por instrumento"""
    __tablename__ = 'method_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    instrument = db.Column(db.String(50), nullable=False)  # teclado, violao, guitarra, canto
    phase = db.Column(db.Integer)  # número da fase/aula
    section_id = db.Column(db.String(100))  # identificador único
    section_name = db.Column(db.String(200))  # nome da seção/aula
    status = db.Column(db.String(50), default='nao_iniciado')  # nao_iniciado, em_andamento, concluido
    start_page = db.Column(db.Integer)  # página inicial no PDF
    end_page = db.Column(db.Integer)  # página final no PDF
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'instrument': self.instrument,
            'phase': self.phase,
            'section_id': self.section_id,
            'section_name': self.section_name,
            'status': self.status,
            'start_page': self.start_page,
            'end_page': self.end_page,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChorusProgress(db.Model):
    """Rastreamento de progresso dos 6 coros do Hinário"""
    __tablename__ = 'chorus_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    chorus_number = db.Column(db.Integer, nullable=False)  # 1-6
    chorus_name = db.Column(db.String(200))  # nome do coro
    status = db.Column(db.String(50), default='nao_iniciado')  # nao_iniciado, em_andamento, concluido
    difficulty = db.Column(db.String(50), nullable=True)  # baixa, media, alta
    stars = db.Column(db.Integer, default=0)  # 0-5 stars
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'chorus_number': self.chorus_number,
            'chorus_name': self.chorus_name,
            'status': self.status,
            'difficulty': self.difficulty,
            'stars': self.stars,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class StudySession(db.Model):
    """Rastreamento de sessões de estudo para revisão"""
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    area = db.Column(db.String(50), nullable=False)  # teoria, metodo, hinario
    section_id = db.Column(db.String(100), nullable=False)  # identificador da seção
    section_name = db.Column(db.String(200))  # nome da seção
    instrument = db.Column(db.String(50))  # para método (opcional)
    status = db.Column(db.String(50), default='em_andamento')  # em_andamento, concluido, repassado
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer, default=0)  # duração em minutos
    is_first_completion = db.Column(db.Boolean, default=True)  # primeira conclusão ou repassagem?
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'section_id': self.section_id,
            'section_name': self.section_name,
            'instrument': self.instrument,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_minutes': self.duration_minutes,
            'is_first_completion': self.is_first_completion,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PDFViewing(db.Model):
    """Rastreamento de última página visualizada de cada PDF"""
    __tablename__ = 'pdf_viewing'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    area = db.Column(db.String(50), nullable=False)  # teoria, metodo, hinario
    instrument = db.Column(db.String(50))  # para método (opcional)
    last_page_viewed = db.Column(db.Integer, default=1)  # última página visualizada
    total_pages = db.Column(db.Integer, default=0)  # total de páginas do PDF
    last_viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'area': self.area,
            'instrument': self.instrument,
            'last_page_viewed': self.last_page_viewed,
            'total_pages': self.total_pages,
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None
        }

def log_activity(user_id, action, description=''):
    """Helper para registrar atividades"""
    try:
        log = ActivityLog(user_id=user_id, action=action, description=description)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Erro ao registrar atividade: {e}")
        db.session.rollback()
