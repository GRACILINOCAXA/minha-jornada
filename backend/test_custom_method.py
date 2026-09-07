import io
import uuid

from app import create_app
from models import db, User


def make_user(username, email):
    user = User(username=username, email=email)
    user.set_password('123456')
    db.session.add(user)
    db.session.commit()
    return user


def test_user_custom_method_upload_is_saved_per_instrument():
    app = create_app('testing')
    with app.app_context():
        user = make_user(f'user_{uuid.uuid4().hex[:8]}', f'user_{uuid.uuid4().hex[:8]}@example.com')
        user.instrumento = 'trompete'
        db.session.add(user)
        db.session.commit()

        with app.test_client() as client:
            login = client.post('/api/auth/login', json={'email': user.email, 'password': '123456'})
            assert login.status_code == 200, login.get_data(as_text=True)

            pdf = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
            upload = client.post(
                '/api/instruments/method',
                data={
                    'instrument': 'trompete',
                    'file': (io.BytesIO(pdf), 'meu_metodo.pdf', 'application/pdf')
                },
                content_type='multipart/form-data'
            )
            assert upload.status_code == 200, upload.get_data(as_text=True)
            payload = upload.get_json()
            assert payload['instrument'] == 'trompete'
            assert payload['custom_method']['stored_filename']
            assert payload['custom_method']['original_filename'] == 'meu_metodo.pdf'


def test_user_method_is_isolated_by_user_and_instrument():
    app = create_app('testing')
    with app.app_context():
        user_a = make_user(f'user_a_{uuid.uuid4().hex[:8]}', f'user_a_{uuid.uuid4().hex[:8]}@example.com')
        user_b = make_user(f'user_b_{uuid.uuid4().hex[:8]}', f'user_b_{uuid.uuid4().hex[:8]}@example.com')
        user_a.instrumento = 'trompete'
        user_b.instrumento = 'saxofone_soprano'
        db.session.add_all([user_a, user_b])
        db.session.commit()

        with app.test_client() as client:
            client.post('/api/auth/login', json={'email': user_a.email, 'password': '123456'})
            custom_pdf = b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'
            upload = client.post(
                '/api/instruments/method',
                data={'instrument': 'trompete', 'file': (io.BytesIO(custom_pdf), 'metodo_a.pdf', 'application/pdf')},
                content_type='multipart/form-data'
            )
            assert upload.status_code == 200, upload.get_data(as_text=True)

            client.post('/api/auth/logout', json={})
            login_b = client.post('/api/auth/login', json={'email': user_b.email, 'password': '123456'})
            assert login_b.status_code == 200, login_b.get_data(as_text=True)

            get_custom = client.get('/api/instruments/method?instrument=trompete')
            assert get_custom.status_code == 404, get_custom.get_data(as_text=True)

            client.post('/api/auth/logout', json={})
            client.post('/api/auth/login', json={'email': user_a.email, 'password': '123456'})
            custom = client.get('/api/instruments/method?instrument=trompete')
            assert custom.status_code == 200, custom.get_data(as_text=True)
            payload = custom.get_json()
            assert payload['custom_method']['original_filename'] == 'metodo_a.pdf'


def test_invalid_or_large_method_is_rejected():
    app = create_app('testing')
    with app.app_context():
        user = make_user(f'user_{uuid.uuid4().hex[:8]}', f'user_{uuid.uuid4().hex[:8]}@example.com')
        user.instrumento = 'trompete'
        db.session.add(user)
        db.session.commit()

        with app.test_client() as client:
            login = client.post('/api/auth/login', json={'email': user.email, 'password': '123456'})
            assert login.status_code == 200, login.get_data(as_text=True)

            invalid = client.post(
                '/api/instruments/method',
                data={'instrument': 'trompete', 'file': (io.BytesIO(b'not-a-pdf'), 'arquivo.txt', 'text/plain')},
                content_type='multipart/form-data'
            )
            assert invalid.status_code == 400

            # Gerar um PDF fake válido maior que 50 MB
            pdf_header = b'%PDF-1.4\n'
            pdf_content = pdf_header + b'1 0 obj\n<< /Type /Catalog >>\nendobj\n'
            padding_size = (51 * 1024 * 1024) - len(pdf_content) - 50
            pdf_content += b'x' * padding_size
            pdf_content += b'\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n%%EOF'
            
            large = client.post(
                '/api/instruments/method',
                data={'instrument': 'trompete', 'file': (io.BytesIO(pdf_content), 'grande.pdf', 'application/pdf')},
                content_type='multipart/form-data'
            )
            assert large.status_code == 413


def test_remove_custom_method_works():
    app = create_app('testing')
    with app.app_context():
        user = make_user(f'user_{uuid.uuid4().hex[:8]}', f'user_{uuid.uuid4().hex[:8]}@example.com')
        user.instrumento = 'trompete'
        db.session.add(user)
        db.session.commit()

        with app.test_client() as client:
            login = client.post('/api/auth/login', json={'email': user.email, 'password': '123456'})
            assert login.status_code == 200, login.get_data(as_text=True)

            upload = client.post(
                '/api/instruments/method',
                data={'instrument': 'trompete', 'file': (io.BytesIO(b'%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF'), 'remover.pdf', 'application/pdf')},
                content_type='multipart/form-data'
            )
            assert upload.status_code == 200

            delete_response = client.delete('/api/instruments/method?instrument=trompete')
            assert delete_response.status_code == 200
            assert delete_response.get_json()['removed'] is True

            get_response = client.get('/api/instruments/method?instrument=trompete')
            assert get_response.status_code == 404
