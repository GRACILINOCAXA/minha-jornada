"""
Script de teste para APIs do Study App
Testa endpoints sem dependências externas
"""
import urllib.request
import urllib.error
import json
import os

BASE_URL = "http://127.0.0.1:5000"

print("🔍 Testando API do Study App\n")

# Test 1: Check if server is running
print("🌐 Verificando servidor...")
try:
    response = urllib.request.urlopen(f"{BASE_URL}/", timeout=2)
    print(f"✅ Servidor respondendo (status {response.status})")
except urllib.error.HTTPError as e:
    print(f"✅ Servidor respondendo (status {e.code})")
except Exception as e:
    print(f"❌ Servidor não está respondendo: {e}")
    exit(1)

# Test 2: Hinário endpoint (should require auth)
print("\n📚 Testando endpoint /api/study/structure/hinario")
try:
    response = urllib.request.urlopen(f"{BASE_URL}/api/study/structure/hinario", timeout=2)
    print(f"✅ Endpoint respondeu com status {response.status}")
except urllib.error.HTTPError as e:
    if e.code == 401:
        print("✅ Endpoint existe e requer autenticação (esperado)")
    else:
        print(f"Status: {e.code}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Test 3: Teoria endpoint
print("\n📖 Testando endpoint /api/study/structure/teoria")
try:
    response = urllib.request.urlopen(f"{BASE_URL}/api/study/structure/teoria", timeout=2)
    print(f"✅ Endpoint respondeu com status {response.status}")
except urllib.error.HTTPError as e:
    if e.code == 401:
        print("✅ Endpoint existe e requer autenticação (esperado)")
    else:
        print(f"Status: {e.code}")
except Exception as e:
    print(f"❌ Erro: {e}")

# Test 4: Check JSON data files
print("\n📁 Verificando arquivos de dados:")
data_files = [
    'data/hinario_structure_complete.json',
    'data/msa_structure_complete.json',
    'data/metodo_structure_complete.json'
]

for file_path in data_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"   ✅ {file_path} ({size} bytes)")
    else:
        print(f"   ❌ {file_path} não encontrado")

# Test 5: Check PDF files
print("\n📄 Verificando arquivos PDF:")
pdf_files = [
    'pdfs/MSA.pdf',
    'pdfs/Metodo.pdf',
    'pdfs/hnaro.pdf'
]

for file_path in pdf_files:
    if os.path.exists(file_path):
        size = os.path.getsize(file_path)
        print(f"   ✅ {file_path} ({size} bytes)")
    else:
        print(f"   ❌ {file_path} não encontrado")

# Test 6: Database
print("\n💾 Verificando banco de dados:")
try:
    from models import db, ChorusProgress, HymnProgress
    from app import create_app
    
    app = create_app()
    with app.app_context():
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        required_tables = ['chorus_progress', 'hymn_progress', 'msa_progress', 'method_progress']
        for table in required_tables:
            if table in tables:
                print(f"   ✅ Tabela {table} existe")
            else:
                print(f"   ⚠️  Tabela {table} não encontrada")
                
except Exception as e:
    print(f"   ❌ Erro ao verificar BD: {e}")

print("\n✅ Testes básicos completo!")
print("Para testes completos com autenticação, acesse o app no browser.")
