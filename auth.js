// Configuração da API
// Construir API_BASE_URL dinamicamente baseado na URL atual
const API_BASE_URL = (() => {
  const protocol = window.location.protocol;
  const hostname = window.location.hostname;
  const port = window.location.port ? `:${window.location.port}` : '';
  return `${protocol}//${hostname}${port}/api`;
})();

// Estado da aplicação
let currentUser = null;

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
  checkAuthentication();
});

// Verificar se usuário está autenticado
async function checkAuthentication() {
  try {
    const response = await fetch(`${API_BASE_URL}/auth/check`, {
      method: 'GET',
      credentials: 'include'
    });

    const data = await response.json();

    if (data.authenticated) {
      currentUser = data.user;

      if (!currentUser.instrumento) {
        if (window.location.pathname !== '/instrument-selection') {
          window.location.replace('/instrument-selection');
        }
        return;
      }

      if (window.location.pathname !== '/dashboard') {
        window.location.replace('/dashboard');
      }
    }
  } catch (error) {
    console.log('Não autenticado ou erro na conexão');
  }
}

// Alternar para formulário de login
function switchToLogin() {
  document.getElementById('loginForm').style.display = 'block';
  document.getElementById('registerForm').style.display = 'none';
  document.getElementById('forgotForm').style.display = 'none';
}

// Alternar para formulário de registro
function switchToRegister() {
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('registerForm').style.display = 'block';
  document.getElementById('forgotForm').style.display = 'none';
  clearErrors();
}

// Alternar para formulário de recuperação de senha
function showForgotPassword() {
  document.getElementById('loginForm').style.display = 'none';
  document.getElementById('registerForm').style.display = 'none';
  document.getElementById('forgotForm').style.display = 'block';
  clearErrors();
}

// Limpar erros
function clearErrors() {
  document.getElementById('loginError').style.display = 'none';
  document.getElementById('registerError').style.display = 'none';
  document.getElementById('registerSuccess').style.display = 'none';
  document.getElementById('forgotError').style.display = 'none';
  document.getElementById('forgotSuccess').style.display = 'none';
}

// Exibir erro
function showError(elementId, message) {
  const element = document.getElementById(elementId);
  element.textContent = message;
  element.style.display = 'block';
}

// Exibir sucesso
function showSuccess(elementId, message) {
  const element = document.getElementById(elementId);
  element.textContent = message;
  element.style.display = 'block';
}

// Handle Login
async function handleLogin(event) {
  event.preventDefault();
  clearErrors();
  
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  
  if (!email || !password) {
    showError('loginError', 'Por favor, preencha todos os campos');
    return;
  }
  
  const loginBtn = document.getElementById('loginBtn');
  const loginLoading = document.getElementById('loginLoading');
  loginBtn.disabled = true;
  loginLoading.style.display = 'block';
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ email, password })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      currentUser = data.user;
      
      // Verificar se usuário tem instrumento selecionado
      if (!currentUser.instrumento) {
        console.log('📍 Usuário sem instrumento, redirecionando para seleção');
        showSuccess('loginError', '✓ Login bem-sucedido! Escolha seu instrumento...');
        setTimeout(() => {
          window.location.href = '/instrument-selection';
        }, 1000);
      } else {
        console.log('✓ Usuário com instrumento:', currentUser.instrumento);
        showSuccess('loginError', '✓ Login bem-sucedido! Redirecionando...');
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
      }
    } else {
      showError('loginError', data.error || 'Erro ao fazer login');
    }
  } catch (error) {
    console.error('Erro:', error);
    showError('loginError', 'Erro na conexão com o servidor');
  } finally {
    loginBtn.disabled = false;
    loginLoading.style.display = 'none';
  }
}

// Handle Register
async function handleRegister(event) {
  event.preventDefault();
  clearErrors();
  
  const username = document.getElementById('registerUsername').value.trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value;
  const passwordConfirm = document.getElementById('registerPasswordConfirm').value;
  
  // Validações
  if (!username || !email || !password) {
    showError('registerError', 'Por favor, preencha todos os campos');
    return;
  }
  
  if (username.length < 3) {
    showError('registerError', 'Nome de usuário deve ter no mínimo 3 caracteres');
    return;
  }
  
  if (password.length < 6) {
    showError('registerError', 'Senha deve ter no mínimo 6 caracteres');
    return;
  }
  
  if (password !== passwordConfirm) {
    showError('registerError', 'As senhas não conferem');
    return;
  }
  
  const registerBtn = document.getElementById('registerBtn');
  const registerLoading = document.getElementById('registerLoading');
  registerBtn.disabled = true;
  registerLoading.style.display = 'block';
  
  try {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({
        username,
        email,
        password,
        password_confirm: passwordConfirm
      })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      showSuccess('registerSuccess', '✓ Conta criada com sucesso! Fazendo login...');
      
      // Fazer login automaticamente
      setTimeout(() => {
        document.getElementById('loginEmail').value = email;
        document.getElementById('loginPassword').value = password;
        switchToLogin();
        handleLogin(new Event('submit'));
      }, 1500);
    } else {
      showError('registerError', data.error || 'Erro ao criar conta');
    }
  } catch (error) {
    console.error('Erro:', error);
    showError('registerError', 'Erro na conexão com o servidor');
  } finally {
    registerBtn.disabled = false;
    registerLoading.style.display = 'none';
  }
}

// Handle Forgot Password
async function handleForgotPassword(event) {
  event.preventDefault();
  clearErrors();
  
  const email = document.getElementById('forgotEmail').value.trim();
  
  if (!email) {
    showError('forgotError', 'Por favor, digite seu e-mail');
    return;
  }
  
  const forgotBtn = document.getElementById('forgotBtn');
  const forgotLoading = document.getElementById('forgotLoading');
  forgotBtn.disabled = true;
  forgotLoading.style.display = 'block';
  
  try {
    // TODO: Implementar endpoint de recuperação de senha no backend
    showSuccess('forgotSuccess', 'Funcionalidade de recuperação de senha será implementada em breve.');
  } catch (error) {
    console.error('Erro:', error);
    showError('forgotError', 'Erro ao processar sua solicitação');
  } finally {
    forgotBtn.disabled = false;
    forgotLoading.style.display = 'none';
  }
}
