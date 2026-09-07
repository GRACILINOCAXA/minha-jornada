import os
import sys
from pathlib import Path

import shutil

APP_NAME = 'MinhaJornada'


def is_frozen():
    return bool(getattr(sys, 'frozen', False))


def get_resource_root():
    """Retorna a raiz dos recursos, tanto no código-fonte quanto no bundle."""
    if is_frozen():
        return Path(getattr(sys, '_MEIPASS'))
    return Path(__file__).resolve().parent.parent


def get_resource_path(*parts):
    return get_resource_root().joinpath(*parts)


def get_user_data_dir():
    """Retorna uma pasta gravável, independente da localização do executável."""
    if os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME'):
        base_dir = Path('/tmp') / 'minha_jornada'
        base_dir.mkdir(parents=True, exist_ok=True)
        return base_dir

    if not is_frozen():
        return get_resource_path('backend', 'instance')

    local_app_data = os.getenv('LOCALAPPDATA')
    if local_app_data:
        return Path(local_app_data) / APP_NAME
    return Path.home() / 'AppData' / 'Local' / APP_NAME


def ensure_user_data_dir():
    data_dir = get_user_data_dir()
    (data_dir / 'uploads' / 'custom_methods').mkdir(parents=True, exist_ok=True)
    return data_dir


def get_database_path():
    return ensure_user_data_dir() / 'minha_jornada.db'


def seed_user_data():
    """Copia os dados iniciais do bundle sem sobrescrever dados do usuário."""
    if not is_frozen():
        return

    data_dir = ensure_user_data_dir()
    database_path = data_dir / 'minha_jornada.db'
    seed_database = get_resource_path('backend', 'instance', 'minha_jornada.db')
    if not database_path.exists() and seed_database.exists():
        shutil.copy2(seed_database, database_path)

    seed_uploads = get_resource_path('backend', 'instance', 'uploads', 'custom_methods')
    target_uploads = data_dir / 'uploads' / 'custom_methods'
    if seed_uploads.exists():
        for source in seed_uploads.iterdir():
            target = target_uploads / source.name
            if not target.exists() and source.is_file():
                shutil.copy2(source, target)