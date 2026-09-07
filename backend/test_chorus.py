"""
Script para testar marcar coro como completo
"""
import urllib.request
import urllib.error
import json
import http.cookiejar

# Criar um cookie jar para manter a sessão
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

BASE_URL = "http://127.0.0.1:5000"

print("🧪 Testando Marcar Coro como Completo\n")

# Step 1: Fazer login
print("1️⃣  Fazendo login...")
login_data = json.dumps({
    "email": "demo2024",
    "password": "demo123456"
}).encode('utf-8')

try:
    req = urllib.request.Request(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/json"}
    )
    response = opener.open(req)
    result = json.loads(response.read().decode())
    print(f"✅ Login bem-sucedido!")
    print(f"   User: {result['user']['username']}\n")
except Exception as e:
    print(f"❌ Login falhou: {e}\n")
    exit(1)

# Step 2: Marcar um coro como completo
print("2️⃣  Marcando Coro 1 como completo...")
coro_data = json.dumps({
    "status": "concluido",
    "stars": 5
}).encode('utf-8')

try:
    req = urllib.request.Request(
        f"{BASE_URL}/api/study/progress/chorus/1",
        data=coro_data,
        headers={"Content-Type": "application/json"},
        method="PUT"
    )
    response = opener.open(req)
    result = json.loads(response.read().decode())
    print(f"✅ Coro marcado como completo!")
    print(f"   XP awarded: {result.get('xp_awarded', 0)}")
    print(f"   Message: {result.get('message')}\n")
except urllib.error.HTTPError as e:
    error_text = e.read().decode()
    print(f"❌ Erro ({e.code}): {error_text}\n")
    exit(1)

# Step 3: Verificar se o coro foi salvo
print("3️⃣  Verificando status do Hinário...")
try:
    req = urllib.request.Request(f"{BASE_URL}/api/study/structure/hinario")
    response = opener.open(req)
    data = json.loads(response.read().decode())
    
    coro_1 = next((c for c in data.get('coros', []) if c['numero'] == 1), None)
    if coro_1:
        print(f"✅ Coro 1 status: {coro_1.get('status')}")
        print(f"   Coros completos: {data.get('coros_concluidos', 0)}\n")
    else:
        print(f"❌ Coro 1 não encontrado\n")
except Exception as e:
    print(f"❌ Erro ao verificar: {e}\n")

print("✅ Teste completo!")
