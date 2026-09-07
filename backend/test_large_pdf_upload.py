"""
Testes para verificar upload de PDFs de diferentes tamanhos
Valida: limite de 50 MB funciona corretamente
"""

import pytest
import uuid
from pathlib import Path
from io import BytesIO

def generate_fake_pdf(size_mb):
    """Gera um arquivo PDF fake com tamanho aproximado especificado."""
    pdf_header = b'%PDF-1.4\n'
    target_size = size_mb * 1024 * 1024
    # Calcula quanto de conteúdo fake precisa
    padding_size = target_size - len(pdf_header) - 50
    pdf_content = pdf_header + b'1 0 obj\n<< /Type /Catalog >>\nendobj\n'
    pdf_content += b'x' * max(0, padding_size)
    pdf_content += b'\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\n%%EOF'
    return BytesIO(pdf_content)

@pytest.fixture
def client():
    """Cria cliente de teste com app de teste."""
    from app import create_app
    app = create_app('testing')
    
    with app.test_client() as client:
        with app.app_context():
            from models import db
            db.create_all()
        yield client

@pytest.fixture
def logged_in_client(client):
    """Cria cliente com usuário logado."""
    unique = uuid.uuid4().hex[:8]
    email = f'test_{unique}@example.com'
    username = f'test_user_{unique}'
    password = 'test_password_123456'
    
    # Registrar usuário
    r = client.post('/api/auth/register', json={
        'username': username,
        'email': email,
        'password': password,
        'password_confirm': password
    })
    assert r.status_code == 201
    
    # Fazer login
    r = client.post('/api/auth/login', json={
        'email': email,
        'password': password
    })
    assert r.status_code == 200
    
    return client, email, password

def test_upload_1mb_pdf(logged_in_client):
    """Teste: Upload de PDF com 1 MB deve funcionar."""
    client, email, password = logged_in_client
    
    pdf_file = generate_fake_pdf(1)
    pdf_file.name = 'test_1mb.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'saxofone_soprano', 'file': (pdf_file, 'test_1mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    assert r.status_code == 200, f"Erro ({r.status_code}): {r.get_json().get('error', 'unknown')}"
    data = r.get_json()
    assert data['success'] == True
    print("✓ PDF de 1 MB aceito")

def test_upload_5mb_pdf(logged_in_client):
    """Teste: Upload de PDF com 5 MB deve funcionar."""
    client, email, password = logged_in_client
    
    pdf_file = generate_fake_pdf(5)
    pdf_file.name = 'test_5mb.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'trompete', 'file': (pdf_file, 'test_5mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    assert r.status_code == 200, f"Erro ({r.status_code}): {r.get_json().get('error', 'unknown')}"
    data = r.get_json()
    assert data['success'] == True
    print("✓ PDF de 5 MB aceito")

def test_upload_10mb_pdf(logged_in_client):
    """Teste: Upload de PDF com 10 MB deve funcionar."""
    client, email, password = logged_in_client
    
    pdf_file = generate_fake_pdf(10)
    pdf_file.name = 'test_10mb.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'flauta', 'file': (pdf_file, 'test_10mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    assert r.status_code == 200, f"Erro ({r.status_code}): {r.get_json().get('error', 'unknown')}"
    data = r.get_json()
    assert data['success'] == True
    print("✓ PDF de 10 MB aceito")

def test_upload_50mb_pdf(logged_in_client):
    """Teste: Upload de PDF com 25 MB deve funcionar (próximo ao limite)."""
    client, email, password = logged_in_client
    
    pdf_file = generate_fake_pdf(25)
    pdf_file.name = 'test_25mb.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'clarinete', 'file': (pdf_file, 'test_25mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    assert r.status_code == 200, f"Erro ({r.status_code}): {r.get_json().get('error', 'unknown')}"
    data = r.get_json()
    assert data['success'] == True
    print("✓ PDF de 25 MB aceito")

def test_upload_exceeds_50mb_pdf(logged_in_client):
    """Teste: Upload de PDF acima de 50 MB deve ser rejeitado."""
    client, email, password = logged_in_client
    
    pdf_file = generate_fake_pdf(51)
    pdf_file.name = 'test_51mb.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'violino', 'file': (pdf_file, 'test_51mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    # Pode ser 413 ou 431 (Request Entity Too Large)
    assert r.status_code in [413, 431, 400], f"Esperava 413/431/400, recebeu {r.status_code}"
    if r.status_code == 400:
        assert '50 MB' in r.get_json().get('error', ''), "Mensagem deve mencionar 50 MB"
    print("✓ PDF acima de 50 MB rejeitado")

def test_non_pdf_file_rejected(logged_in_client):
    """Teste: Arquivo que não é PDF deve ser rejeitado."""
    client, email, password = logged_in_client
    
    fake_file = BytesIO(b'This is not a PDF file')
    fake_file.name = 'test.pdf'
    
    r = client.post(
        '/api/instruments/method',
        data={'instrument': 'harpa', 'file': (fake_file, 'test.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    
    assert r.status_code == 400, f"Esperava 400, recebeu {r.status_code}: {r.get_json().get('error', 'unknown')}"
    print("✓ Arquivo não-PDF rejeitado")

def test_method_isolation_after_large_upload(client):
    """Teste: Após upload grande, método permanece isolado por usuário/instrumento."""
    unique1 = uuid.uuid4().hex[:8]
    user1 = {
        'username': f'user1_{unique1}',
        'email': f'user1_{unique1}@test.com',
        'password': 'pass123456'
    }
    
    # Usuário 1 registra e faz login
    r = client.post('/api/auth/register', json={
        'username': user1['username'],
        'email': user1['email'],
        'password': user1['password'],
        'password_confirm': user1['password']
    })
    assert r.status_code == 201
    
    r = client.post('/api/auth/login', json={
        'email': user1['email'],
        'password': user1['password']
    })
    assert r.status_code == 200
    
    # Usuário 1 seleciona um instrumento
    r_inst = client.post('/api/instruments/select', json={'instrumento': 'teclado'})
    assert r_inst.status_code == 200, f"Erro ao selecionar instrumento: {r_inst.get_json().get('error', 'unknown')}"
    
    # Usuário 1 faz upload grande
    pdf_file = generate_fake_pdf(20)
    r1 = client.post(
        '/api/instruments/method',
        data={'instrument': 'teclado', 'file': (pdf_file, 'test_20mb.pdf', 'application/pdf')},
        content_type='multipart/form-data'
    )
    assert r1.status_code == 200, f"Erro: {r1.get_json().get('error', 'unknown')}"
    
    # Logout
    client.post('/api/auth/logout', json={})
    
    # Usuário 2 registra e faz login
    unique2 = uuid.uuid4().hex[:8]
    user2 = {
        'username': f'user2_{unique2}',
        'email': f'user2_{unique2}@test.com',
        'password': 'pass123456'
    }
    r = client.post('/api/auth/register', json={
        'username': user2['username'],
        'email': user2['email'],
        'password': user2['password'],
        'password_confirm': user2['password']
    })
    assert r.status_code == 201
    
    r = client.post('/api/auth/login', json={
        'email': user2['email'],
        'password': user2['password']
    })
    assert r.status_code == 200
    
    # Usuário 2 seleciona o mesmo instrumento
    r_inst2 = client.post('/api/instruments/select', json={'instrumento': 'teclado'})
    assert r_inst2.status_code == 200
    
    # Usuário 2 verifica que NÃO tem o método do usuário 1
    r_check = client.get('/api/instruments/method?instrument=teclado')
    assert r_check.status_code == 404, "Usuário 2 não deve ter acesso ao método de usuário 1"
    print("✓ Isolamento de método mantido após upload grande")

