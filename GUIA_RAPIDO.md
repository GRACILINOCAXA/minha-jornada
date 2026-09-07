# 🎵 Minha Jornada - Guia Rápido

## ✅ Status Atual
- **Backend**: ✓ Flask + SQLAlchemy (rodando em http://localhost:5000)
- **Frontend**: ✓ HTML/CSS/JS (servido pelo Flask)
- **Banco de Dados**: ✓ SQLite com 8 tabelas
- **Autenticação**: ✓ Login/Registro com hash de senha
- **APIs**: ✓ 7 módulos com 40+ endpoints

---

## 🚀 Como Iniciar

### Opção 1: Script Rápido (Recomendado)
```
Duplo clique em: INICIAR.bat
ou
./INICIAR.ps1
```

### Opção 2: Terminal Manual
```powershell
cd "c:\Users\caxa\Documents\projto my t\backend"
python app.py
```

Depois acesse: **http://localhost:5000**

---

## 📱 Contas de Teste

### Conta 1
- **Usuário**: testuser
- **E-mail**: test@example.com
- **Senha**: password123

### Criar Nova Conta
1. Clique em "Criar conta"
2. Preencha os dados
3. Clique em "CRIAR CONTA"

---

## 📚 Funcionalidades Disponíveis

### ✅ Implementado
- 🔐 Login/Logout
- 🙏 Orações (ler, marcar como concluída)
- 📊 Dashboard com estatísticas
- 👤 Exibição do nome do usuário
- 💾 Sincronização com banco de dados

### 🔄 Em Progresso
- 🎵 Criar/Editar Estudos MSA
- 🎯 Criar/Editar Metas
- 📝 Criar/Editar Anotações
- ➕ Adicionar Orações (criar via API)

### ⏳ Planejado
- 💾 Backup/Export de dados
- 📊 Gráficos de progresso
- 🔐 Recuperação de senha
- 🌙 Modo escuro (já funciona com tema)

---

## 🔍 URLs Importantes

| Função | URL |
|--------|-----|
| Login | http://localhost:5000/login |
| Dashboard | http://localhost:5000/dashboard |
| API Saúde | http://localhost:5000/api/health |
| API Orações | http://localhost:5000/api/prayers |
| API Estudos | http://localhost:5000/api/music/studies |
| API Metas | http://localhost:5000/api/goals |

---

## 🛠️ Estrutura do Projeto

```
Projeto/
├── backend/
│   ├── app.py              # Aplicação Flask
│   ├── models.py           # Modelos do banco (8 tabelas)
│   ├── config.py           # Configurações
│   ├── requirements.txt     # Dependências Python
│   ├── .env                # Variáveis de ambiente
│   └── routes/
│       ├── auth.py         # Autenticação
│       ├── prayers.py      # Orações
│       ├── music.py        # Estudos MSA
│       ├── goals.py        # Metas
│       ├── notes.py        # Anotações
│       ├── settings.py     # Configurações
│       └── user.py         # Perfil do usuário
│
└── projto my t/            # Frontend
    ├── index.html          # Dashboard
    ├── login.html          # Login
    ├── app.js              # Lógica principal
    ├── auth.js             # Autenticação JS
    ├── api-client.js       # Cliente de API
    ├── styles.css          # Estilos
    └── README.md           # Documentação

```

---

## 🔐 Segurança Implementada

✅ Senhas com hash bcrypt (nunca em texto puro)
✅ Validação de autenticação em todas as rotas
✅ Proteção contra acesso a dados de outros usuários
✅ CORS configurado
✅ Sessões seguras com cookies HTTPONLY
✅ Audit log de todas as ações

---

## 📈 Próximos Passos

1. **Criar Orações via API** - Adicionar novo modal com chamada POST
2. **Estudos MSA** - Integrar criação de sessões
3. **Metas** - Implementar formulário de criação
4. **Backup** - Exportar dados em JSON

---

## ⚙️ Troubleshooting

### Backend não inicia
```
pip install -r requirements.txt
```

### Porta 5000 já está em uso
```powershell
# Liberar a porta
Get-Process | Where-Object {$_.Port -eq 5000} | Stop-Process
```

### Banco de dados corrompido
```
# Deletar arquivo e deixar recriar
rm "c:\Users\caxa\Documents\projto my t\backend\minha_jornada.db"
```

---

## 📞 Comandos Úteis

| Comando | Efeito |
|---------|--------|
| Ctrl+C | Parar o servidor |
| F5 | Recarregar página |
| Ctrl+Shift+I | Abrir DevTools (F12) |

---

**Feito com ❤️ — Minha Jornada**
