"""
Script para testar login e acessar dados do app
"""
import urllib.request
import urllib.error
import json
import http.cookiejar

# Criar um cookie jar para manter a sessão
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

BASE_URL = "http://127.0.0.1:5000"

print("🧪 Testando Login via API\n")

# Step 1: Fazer login
print("1️⃣  Fazendo login...")
login_data = json.dumps({
    "email": "demo2024",  # username ou email
    "password": "demo123456"
}).encode('utf-8')

try:
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",  # Use /api/auth prefix
        data=login_data,
        headers={"Content-Type": "application/json"}
    )
    response = opener.open(req)
    response_text = response.read().decode()
    print(f"Response status: {response.status}")
    result = json.loads(response_text)
    print(f"✅ Login bem-sucedido!")
    print(f"   User: {result['user']['username']}")
    print(f"   Status: {response.status}\n")
except urllib.error.HTTPError as e:
    error_text = e.read().decode()
    print(f"HTTP Error {e.code}: {error_text[:200]}\n")
    try:
        error_data = json.loads(error_text)
        print(f"❌ Login falhou: {error_data.get('error', 'Unknown error')}\n")
    except:
        print(f"❌ Could not parse response: {error_text[:100]}\n")
    exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}\n")
    exit(1)

# Step 2: Acessar dashboard
print("2️⃣  Acessando dashboard...")
try:
    req = urllib.request.Request(f"{BASE_URL}/dashboard")
    response = opener.open(req)
    content = response.read().decode()
    if "Minha Jornada" in content and "Hinário" in content:
        print(f"✅ Dashboard acessível!")
        print(f"   Status: {response.status}\n")
    else:
        print(f"⚠️  Dashboard carregou mas conteúdo esperado não encontrado\n")
except urllib.error.HTTPError as e:
    print(f"❌ Erro ao acessar dashboard: {e.code}\n")

# Step 3: Testar API de estrutura
print("3️⃣  Testando /api/study/structure/hinario...")
try:
    req = urllib.request.Request(f"{BASE_URL}/api/study/structure/hinario")
    response = opener.open(req)
    data = json.loads(response.read().decode())
    print(f"✅ API respondeu com sucesso!")
    print(f"   Total hinos: {data.get('total_hinos', '?')}")
    print(f"   Total coros: {data.get('total_coros', '?')}")
    print(f"   Hinos carregados: {len(data.get('hinos', []))}")
    print(f"   Coros carregados: {len(data.get('coros', []))}\n")
except urllib.error.HTTPError as e:
    error_content = e.read().decode()
    try:
        error_data = json.loads(error_content)
        print(f"❌ API erro: {error_data.get('error', error_content)}\n")
    except:
        print(f"❌ API erro ({e.code}): {error_content[:100]}\n")

print("✅ Teste completo!")
