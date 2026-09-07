import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify, session, send_from_directory, redirect, request, send_file
from flask_login import LoginManager, current_user
from flask_cors import CORS
from sqlalchemy import text

# Carregar variáveis antes de importar a configuração, inclusive no serverless.
load_dotenv()

try:
    from .resource_paths import get_resource_path, ensure_user_data_dir, seed_user_data
except ImportError:
    from resource_paths import get_resource_path, ensure_user_data_dir, seed_user_data

try:
    from .config import config
    from .models import db, User, UserSettings, GamificationProgress
except ImportError:
    from config import config
    from models import db, User, UserSettings, GamificationProgress

def ensure_sqlite_schema(app):
    """Repara migrações mínimas para bancos SQLite antigos."""
    with app.app_context():
        uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
        if not uri.startswith('sqlite'):
            return

        inspector = db.inspect(db.engine)
        table_names = set(inspector.get_table_names())

        def add_column_if_missing(table_name, column_name, column_sql):
            if table_name not in table_names:
                return
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            if column_name not in columns:
                db.session.execute(text(f'ALTER TABLE {table_name} ADD COLUMN {column_sql}'))

        add_column_if_missing('user_settings', 'theme', 'theme VARCHAR(20) DEFAULT "light"')
        add_column_if_missing('user_settings', 'notifications_enabled', 'notifications_enabled BOOLEAN DEFAULT 0')
        add_column_if_missing('user_settings', 'daily_study_goal', 'daily_study_goal INTEGER DEFAULT 30')
        add_column_if_missing('user_settings', 'selected_instrument', 'selected_instrument VARCHAR(50) DEFAULT "teclado"')
        
        # Adicionar campo instrumento ao User
        add_column_if_missing('users', 'instrumento', 'instrumento VARCHAR(50) DEFAULT NULL')

        add_column_if_missing('gamification_progress', 'selected_instrument', 'selected_instrument VARCHAR(50) DEFAULT "teclado"')
        add_column_if_missing('gamification_progress', 'last_study_date', 'last_study_date DATE')
        add_column_if_missing('gamification_progress', 'lessons_data', 'lessons_data TEXT DEFAULT "[]"')
        add_column_if_missing('gamification_progress', 'hymns_data', 'hymns_data TEXT DEFAULT "[]"')

        add_column_if_missing('hymn_progress', 'difficulty', 'difficulty VARCHAR(50) DEFAULT NULL')
        add_column_if_missing('chorus_progress', 'difficulty', 'difficulty VARCHAR(50) DEFAULT NULL')

        if 'custom_instrument_methods' not in table_names:
            db.session.execute(text('''
                CREATE TABLE custom_instrument_methods (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    instrument VARCHAR(80) NOT NULL,
                    original_filename VARCHAR(255) NOT NULL,
                    stored_filename VARCHAR(255) NOT NULL,
                    file_path VARCHAR(500) NOT NULL,
                    file_size INTEGER DEFAULT 0,
                    mime_type VARCHAR(120) DEFAULT 'application/pdf',
                    created_at DATETIME,
                    updated_at DATETIME,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            '''))
            db.session.execute(text('''
                CREATE UNIQUE INDEX uq_user_instrument_custom_method
                ON custom_instrument_methods (user_id, instrument)
            '''))
        else:
            columns = [col['name'] for col in inspector.get_columns('custom_instrument_methods')]
            for column_name, column_sql in [
                ('user_id', 'user_id INTEGER NOT NULL DEFAULT 0'),
                ('instrument', 'instrument VARCHAR(80) NOT NULL DEFAULT "teclado"'),
                ('original_filename', 'original_filename VARCHAR(255) DEFAULT ""'),
                ('stored_filename', 'stored_filename VARCHAR(255) DEFAULT ""'),
                ('file_path', 'file_path VARCHAR(500) DEFAULT ""'),
                ('file_size', 'file_size INTEGER DEFAULT 0'),
                ('mime_type', 'mime_type VARCHAR(120) DEFAULT "application/pdf"'),
            ]:
                if column_name not in columns:
                    db.session.execute(text(f'ALTER TABLE custom_instrument_methods ADD COLUMN {column_sql}'))
            db.session.execute(text('''
                CREATE UNIQUE INDEX IF NOT EXISTS uq_user_instrument_custom_method
                ON custom_instrument_methods (user_id, instrument)
            '''))

        db.session.execute(text('''
            DELETE FROM user_settings
            WHERE id NOT IN (
                SELECT MIN(id) FROM user_settings GROUP BY user_id
            )
        '''))
        db.session.execute(text('''
            DELETE FROM gamification_progress
            WHERE id NOT IN (
                SELECT MIN(id) FROM gamification_progress GROUP BY user_id
            )
        '''))
        db.session.commit()

        for user in User.query.all():
            if UserSettings.query.filter_by(user_id=user.id).first() is None:
                db.session.add(UserSettings(user_id=user.id, selected_instrument='teclado'))

            if GamificationProgress.query.filter_by(user_id=user.id).first() is None:
                db.session.add(GamificationProgress(user_id=user.id, selected_instrument='teclado'))

        db.session.commit()


def create_app(config_name=None):
    """Factory para criar a aplicação Flask"""
    seed_user_data()
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    if config_name not in config:
        config_name = 'development'

    if config_name == 'production' and not os.getenv('SECRET_KEY'):
        raise RuntimeError('SECRET_KEY is required in production. Set it in the environment before deploy.')
    database_url = os.getenv('DATABASE_URL', '')
    if os.getenv('VERCEL') and (not database_url or database_url.startswith('sqlite')):
        raise RuntimeError('DATABASE_URL must point to managed PostgreSQL on Vercel.')
    
    # Caminho do frontend (frontend agora está na raiz do repositório)
    # Antes o frontend ficava em '../projto my t'; agora apontamos para a raiz
    frontend_path = get_resource_path()
    instance_path = ensure_user_data_dir()
    
    app = Flask(__name__, instance_path=str(instance_path), instance_relative_config=True)
    
    # Carregar configuração
    app.config.from_object(config[config_name])
    
    # Aumentar o limite de conteúdo para suportar uploads de até 50 MB
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    
    # Inicializar extensões
    db.init_app(app)
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # CORS para aceitar requisições do frontend
    CORS(app, supports_credentials=True)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()
        ensure_sqlite_schema(app)
    
    # Registrar blueprints (rotas) ANTES das rotas estáticas
    try:
        from .routes.auth import auth_bp
        from .routes.prayers import prayers_bp
        from .routes.music import music_bp
        from .routes.goals import goals_bp
        from .routes.notes import notes_bp
        from .routes.settings import settings_bp
        from .routes.user import user_bp
        from .routes.gamification import gamification_bp
        from .routes.instruments import instruments_bp
        from .routes.msa import msa_bp
        from .routes.api_study import study_bp
    except ImportError:
        from routes.auth import auth_bp
        from routes.prayers import prayers_bp
        from routes.music import music_bp
        from routes.goals import goals_bp
        from routes.notes import notes_bp
        from routes.settings import settings_bp
        from routes.user import user_bp
        from routes.gamification import gamification_bp
        from routes.instruments import instruments_bp
        from routes.msa import msa_bp
        from routes.api_study import study_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(prayers_bp, url_prefix='/api/prayers')
    app.register_blueprint(music_bp, url_prefix='/api/music')
    app.register_blueprint(goals_bp, url_prefix='/api/goals')
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(settings_bp, url_prefix='/api/settings')
    app.register_blueprint(user_bp, url_prefix='/api/user')
    app.register_blueprint(gamification_bp, url_prefix='/api/gamification')
    app.register_blueprint(instruments_bp)
    app.register_blueprint(msa_bp, url_prefix='/api/msa')
    app.register_blueprint(study_bp)
    
    # Rota de teste
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})
    
    # Servir frontend (DEPOIS das APIs)
    @app.route('/')
    def root():
        """Redirecionar / para /login"""
        return redirect('/login')
    
    @app.route('/login')
    def login_page():
        """Servir página de login"""
        login_file = frontend_path / 'login.html'
        if os.path.exists(login_file):
            return send_from_directory(frontend_path, 'login.html')
        return 'Login page not found', 404
    
    @app.route('/metodo/pdf/<instrumento>', methods=['GET'])
    def metodo_pdf_route(instrumento):
        """Serviço seguro do PDF do método para o instrumento atual, sem fallback e sem path traversal."""
        try:
            from .instrument_config import get_metodo_pdf
        except ImportError:
            from instrument_config import get_metodo_pdf

        pdf_path, _, error = get_metodo_pdf(instrumento)
        if error or pdf_path is None:
            return jsonify({
                'error': 'PDF do método para este instrumento não encontrado.',
                'instrumento': instrumento,
                'message': error or 'Arquivo não localizado no diretório do projeto.',
                'arquivo_esperado': f'pdfs/{instrumento}.pdf'
            }), 404

        return send_file(str(pdf_path), mimetype='application/pdf', as_attachment=False)

    @app.route('/dashboard')
    def dashboard():
        """Servir página do dashboard (protegida)"""
        if not current_user.is_authenticated:
            return redirect('/login')
        if not current_user.instrumento:
            return redirect('/instrument-selection')
        dashboard_file = frontend_path / 'index.html'
        if os.path.exists(dashboard_file):
            return send_from_directory(frontend_path, 'index.html')
        return 'Dashboard not found', 404
    
    @app.route('/instrument-selection')
    def instrument_selection():
        """Servir página de seleção de instrumento (protegida)"""
        if not current_user.is_authenticated:
            return redirect('/login')
        if current_user.instrumento:
            return redirect('/dashboard')
        instr_file = frontend_path / 'instrument-selection.html'
        if os.path.exists(instr_file):
            return send_from_directory(frontend_path, 'instrument-selection.html')
        return 'Instrument selection page not found', 404
    
    @app.route('/<filename>')
    def serve_static(filename):
        """Servir arquivos estáticos (CSS, JS, etc)"""
        file_path = frontend_path / filename
        if os.path.exists(file_path):
            return send_from_directory(frontend_path, filename)
        return 'File not found', 404
    
    # Tratamento de erros
    @app.errorhandler(404)
    def not_found(error):
        # Se é uma requisição de arquivo estático, trata como 404
        if request.path.startswith('/api/'):
            return jsonify({'error': 'API endpoint not found'}), 404
        # Caso contrário, redireciona para o login
        return redirect('/login')
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    app.run(debug=False, use_reloader=False, host='127.0.0.1', port=5000)
