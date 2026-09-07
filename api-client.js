/**
 * API Client - Comunicação com backend Flask
 * Substitui localStorage por chamadas de API REST
 */

const API = {
  // Construir BASE_URL dinamicamente baseado na URL atual
  BASE_URL: (() => {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    const port = window.location.port ? `:${window.location.port}` : '';
    return `${protocol}//${hostname}${port}/api`;
  })(),
  
  /**
   * Configuração de fetch padrão com CORS
   */
  fetchOptions() {
    return {
      credentials: 'include', // Incluir cookies de sessão
      headers: {
        'Content-Type': 'application/json'
      }
    };
  },

  /**
   * Faz requisição com tratamento de erro
   */
  async request(endpoint, method = 'GET', body = null) {
    const url = `${this.BASE_URL}${endpoint}`;
    const options = this.fetchOptions();
    options.method = method;
    
    if (body) {
      options.body = JSON.stringify(body);
    }

    try {
      const response = await fetch(url, options);
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || `Erro ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API Error [${method} ${endpoint}]:`, error);
      throw error;
    }
  },

  // ============ AUTENTICAÇÃO ============
  auth: {
    async check() {
      return API.request('/auth/check', 'GET');
    },
    
    async getCurrentUser() {
      return API.request('/auth/me', 'GET');
    },
    
    async logout() {
      return API.request('/auth/logout', 'POST');
    }
  },

  // ============ ORAÇÕES ============
  prayers: {
    async getAll() {
      return API.request('/prayers', 'GET');
    },
    
    async getById(id) {
      return API.request(`/prayers/${id}`, 'GET');
    },
    
    async create(prayer) {
      return API.request('/prayers', 'POST', prayer);
    },
    
    async update(id, prayer) {
      return API.request(`/prayers/${id}`, 'PUT', prayer);
    },
    
    async delete(id) {
      return API.request(`/prayers/${id}`, 'DELETE');
    },
    
    async complete(id) {
      return API.request(`/prayers/${id}/complete`, 'POST');
    },
    
    async getHistory() {
      return API.request('/prayers/history', 'GET');
    }
  },

  // ============ ESTUDOS MUSICAIS ============
  music: {
    async getAll(area = null) {
      const query = area ? `?area=${area}` : '';
      return API.request(`/music/studies${query}`, 'GET');
    },
    
    async getById(id) {
      return API.request(`/music/studies/${id}`, 'GET');
    },
    
    async create(study) {
      return API.request('/music/studies', 'POST', study);
    },
    
    async update(id, study) {
      return API.request(`/music/studies/${id}`, 'PUT', study);
    },
    
    async delete(id) {
      return API.request(`/music/studies/${id}`, 'DELETE');
    },
    
    async getSummary() {
      return API.request('/music/summary', 'GET');
    }
  },

  // ============ METAS ============
  goals: {
    async getAll() {
      return API.request('/goals', 'GET');
    },
    
    async getById(id) {
      return API.request(`/goals/${id}`, 'GET');
    },
    
    async create(goal) {
      return API.request('/goals', 'POST', goal);
    },
    
    async update(id, goal) {
      return API.request(`/goals/${id}`, 'PUT', goal);
    },
    
    async delete(id) {
      return API.request(`/goals/${id}`, 'DELETE');
    }
  },

  // ============ ANOTAÇÕES ============
  notes: {
    async getAll() {
      return API.request('/notes', 'GET');
    },
    
    async getById(id) {
      return API.request(`/notes/${id}`, 'GET');
    },
    
    async create(note) {
      return API.request('/notes', 'POST', note);
    },
    
    async update(id, note) {
      return API.request(`/notes/${id}`, 'PUT', note);
    },
    
    async delete(id) {
      return API.request(`/notes/${id}`, 'DELETE');
    }
  },

  // ============ CONFIGURAÇÕES ============
  settings: {
    async get() {
      return API.request('/settings', 'GET');
    },
    
    async update(settings) {
      return API.request('/settings', 'PUT', settings);
    }
  },

  // ============ GAMIFICAÇÃO ============
  gamification: {
    async get() {
      return API.request('/gamification', 'GET');
    },
    
    async getStreak() {
      return API.request('/gamification/streak', 'GET');
    },
    
    async recalculateStreak() {
      return API.request('/gamification/streak/recalculate', 'POST');
    },
    
    async update(data) {
      return API.request('/gamification', 'PUT', data);
    }
  },

  // ============ PERFIL DO USUÁRIO ============
  user: {
    async getProfile() {
      return API.request('/user/profile', 'GET');
    },
    
    async updateProfile(data) {
      return API.request('/user/profile', 'PUT', data);
    },
    
    async changePassword(oldPassword, newPassword, newPasswordConfirm) {
      return API.request('/user/change-password', 'POST', {
        current_password: oldPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm
      });
    },
    
    async getActivityLog(limit = 100) {
      return API.request(`/user/activity-log?limit=${limit}`, 'GET');
    }
  }
};

/**
 * Verificar autenticação ao carregar a página
 * Se não autenticado, redirecionar para login
 */
async function ensureAuthenticated() {
  try {
    const result = await API.auth.check();
    if (!result.authenticated) {
      if (window.location.pathname !== '/login') {
        window.location.href = '/login';
      }
      return null;
    }

    window.currentUser = result.user;
    if (typeof currentUser !== 'undefined') {
      currentUser = result.user;
    }
    return result.user;
  } catch (error) {
    console.error('Erro ao verificar autenticação:', error);
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
    return null;
  }
}

/**
 * Fazer logout
 */
async function doLogout() {
  try {
    await API.auth.logout();
    window.location.href = '/login';
  } catch (error) {
    console.error('Erro ao fazer logout:', error);
    // Mesmo com erro, redirecionar
    window.location.href = '/login';
  }
}

// ============ INICIALIZAÇÃO ============
document.addEventListener('DOMContentLoaded', async () => {
  // Verificar autenticação
  try {
    const user = await ensureAuthenticated();
    console.log('✓ Autenticado como:', user.username);
  } catch (error) {
    console.error('Erro na autenticação:', error);
  }
});
