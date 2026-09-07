# Minha Jornada - Backend

Backend da aplicação "Minha Jornada" construído com Flask e SQLAlchemy.

## 🚀 Começando

### Pré-requisitos

- Python 3.8+
- pip

### Instalação

1. **Criar ambiente virtual** (recomendado):

```bash
python -m venv venv
```

2. **Ativar o ambiente virtual**:

No Windows:
```bash
venv\Scripts\activate
```

No macOS/Linux:
```bash
source venv/bin/activate
```

3. **Instalar dependências**:

```bash
pip install -r requirements.txt
```

4. **Configurar variáveis de ambiente**:

Copiar `.env.example` para `.env`:
```bash
cp .env.example .env
```

Editar `.env` com suas configurações (em desenvolvimento, pode deixar os valores padrão).

5. **Executar a aplicação**:

```bash
python app.py
```

A aplicação rodará em `http://127.0.0.1:5000`

## 📁 Estrutura do Projeto

```
backend/
├── app.py              # Aplicação principal
├── config.py           # Configurações
├── models.py           # Modelos do banco de dados
├── requirements.txt    # Dependências
├── .env               # Variáveis de ambiente (não commitar)
├── .env.example       # Exemplo de variáveis
├── minha_jornada.db   # Banco SQLite (criado automaticamente)
└── routes/
    ├── auth.py       # Autenticação (login, register)
    ├── prayers.py    # API de orações
    ├── music.py      # API de estudos musicais
    ├── goals.py      # API de metas
    ├── notes.py      # API de anotações
    ├── settings.py   # API de configurações
    └── user.py       # API de perfil do usuário
```

## 🔐 Segurança

- Senhas são hashadas com `werkzeug.security`
- Sessões seguras com Flask-Login
- CORS habilitado para desenvolvimento
- Validação de dados em todas as rotas
- Proteção contra acesso a dados de outros usuários

## 📚 Endpoints da API

### Autenticação

- `POST /api/auth/register` - Registrar novo usuário
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Dados do usuário autenticado
- `GET /api/auth/check` - Verificar autenticação

### Orações

- `GET /api/prayers` - Listar orações
- `GET /api/prayers/<id>` - Obter oração
- `POST /api/prayers` - Criar oração
- `PUT /api/prayers/<id>` - Atualizar oração
- `DELETE /api/prayers/<id>` - Deletar oração
- `POST /api/prayers/<id>/complete` - Marcar como concluída
- `GET /api/prayers/history` - Histórico

### Estudos Musicais

- `GET /api/music/studies` - Listar estudos
- `GET /api/music/studies/<id>` - Obter estudo
- `POST /api/music/studies` - Criar estudo
- `PUT /api/music/studies/<id>` - Atualizar estudo
- `DELETE /api/music/studies/<id>` - Deletar estudo
- `GET /api/music/summary` - Resumo dos estudos

### Metas

- `GET /api/goals` - Listar metas
- `GET /api/goals/<id>` - Obter meta
- `POST /api/goals` - Criar meta
- `PUT /api/goals/<id>` - Atualizar meta
- `DELETE /api/goals/<id>` - Deletar meta

### Anotações

- `GET /api/notes` - Listar anotações
- `GET /api/notes/<id>` - Obter anotação
- `POST /api/notes` - Criar anotação
- `PUT /api/notes/<id>` - Atualizar anotação
- `DELETE /api/notes/<id>` - Deletar anotação

### Configurações

- `GET /api/settings` - Obter configurações
- `PUT /api/settings` - Atualizar configurações

### Perfil do Usuário

- `GET /api/user/profile` - Obter perfil
- `PUT /api/user/profile` - Atualizar perfil
- `POST /api/user/change-password` - Alterar senha
- `GET /api/user/activity-log` - Histórico de atividades

## 🗄️ Banco de Dados

### Tabelas

- **users** - Usuários do sistema
- **prayers** - Orações cadastradas
- **prayer_history** - Histórico de orações concluídas
- **music_studies** - Estudos musicais (MSA)
- **goals** - Metas
- **notes** - Anotações
- **user_settings** - Configurações por usuário
- **activity_logs** - Log de atividades

## 📋 Variáveis de Ambiente

```
FLASK_ENV=development          # development, production, testing
FLASK_APP=app.py              # Arquivo principal
SECRET_KEY=your-secret-key    # Chave secreta para sessões
DATABASE_URL=sqlite:///...    # URL do banco de dados
```

## 🧪 Testes

Para executar os testes:

```bash
# TODO: Adicionar testes
```

## 📝 Notas para Produção

Antes de colocar em produção:

1. Gerar uma `SECRET_KEY` forte
2. Configurar `DATABASE_URL` para PostgreSQL
3. Configurar `FLASK_ENV=production`
4. Desabilitar `DEBUG`
5. Configurar HTTPS
6. Configurar CORS apropriadamente
7. Implementar rate limiting
8. Adicionar logging
9. Configurar backup do banco

## 🐛 Troubleshooting

### "ModuleNotFoundError" ao executar

Certifique-se de que o ambiente virtual está ativado e as dependências foram instaladas:

```bash
pip install -r requirements.txt
```

### CORS error

Certifique-se de que `Flask-CORS` está instalado e que o frontend está acessando `http://localhost:5000`.

### Banco de dados não criado

O banco é criado automaticamente na primeira execução. Se houver erros, delete `minha_jornada.db` e reinicie.

## 📖 Documentação Adicional

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-Login](https://flask-login.readthedocs.io/)

## 📄 Licença

Todos os direitos reservados
