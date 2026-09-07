/**
 * Study App - Interface de Estudo Musical
 * Gerencia MSA, Método e Hinário
 */

const StudyApp = {
  currentArea: null,
  currentInstrument: 'teclado',
  structureCache: {},
  pdfCurrentPage: 1,
  pdfTotalPages: 0,
  
  // Estado para Hinário
  hymnOffset: 50,
  hymnLimit: 50,
  allHymns: [],
  displayedHymnsCount: 50,

  // ==================== INICIALIZAÇÃO ====================

  getSelectedInstrument() {
    // Fonte de verdade: instrumento persistido no usuário autenticado no backend.
    const userInstrument = (typeof currentUser !== 'undefined' && currentUser && currentUser.instrumento) ||
      (typeof window !== 'undefined' && window.currentUser && window.currentUser.instrumento) ||
      (typeof this.currentInstrument === 'string' && this.currentInstrument.trim() ? this.currentInstrument : null);

    if (!userInstrument) return null;
    return normalizeInstrumentKey ? normalizeInstrumentKey(userInstrument) : userInstrument;
  },

  init() {
    console.log('🎵 StudyApp inicializado');
    this.currentInstrument = this.getSelectedInstrument();
    this.setupEventListeners();
    this.loadLastActivity();
  },

  setupEventListeners() {
    // Navegação de áreas
    document.querySelectorAll('[data-study-area]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const area = btn.dataset.studyArea;

        if (area === 'metodo') {
          this.currentInstrument = this.getSelectedInstrument();
        }

        this.loadArea(area);
      });
    });

    // Dropdown de instrumentos
    const instrumentSelect = document.getElementById('instrumentSelect');
    if (instrumentSelect) {
      instrumentSelect.addEventListener('change', async (e) => {
        const nextInstrument = normalizeInstrumentKey ? normalizeInstrumentKey(e.target.value) : e.target.value;
        this.currentInstrument = nextInstrument;
        if (typeof applySelectedInstrument === 'function') {
          await applySelectedInstrument(nextInstrument, { syncStudyUI: false });
        }
        this.structureCache = {};
        if (this.currentArea) {
          this.loadArea(this.currentArea);
        }
      });
    }
  },

  loadLastActivity() {
    // Carrega última atividade do usuário (para "Continuar estudo")
    fetch('/api/study/progress-report')
      .then(r => r.json())
      .then(data => {
        this.displayContinueButton(data);
      })
      .catch(e => console.error('Erro ao carregar última atividade:', e));
  },

  displayContinueButton(reportData) {
    const btn = document.getElementById('continueStudyBtn');
    if (!btn) return;

    let nextArea = null;
    let nextText = 'Continuar Estudo';

    const msaProgress = reportData?.msa?.progresso_percent ?? 100;
    const metodoProgress = reportData?.metodo?.progresso_percent ?? 100;
    const hinarioProgress = reportData?.hinario?.progresso_percent ?? 100;

    if (msaProgress < 100) {
      nextArea = 'teoria';
      nextText = `📚 MSA (${msaProgress}%)`;
    } else if (metodoProgress < 100) {
      nextArea = 'metodo';
      nextText = `🎼 Método (${metodoProgress}%)`;
    } else if (hinarioProgress < 100) {
      nextArea = 'hinario';
      nextText = `🎵 Hinário (${hinarioProgress}%)`;
    }

    if (nextArea) {
      btn.textContent = nextText;
      btn.onclick = () => {
        if (nextArea === 'metodo') {
          this.currentInstrument = this.getSelectedInstrument();
        }
        this.loadArea(nextArea);
      };
      btn.style.display = 'block';
      const noActivityMsg = document.getElementById('noActivityMsg');
      if (noActivityMsg) noActivityMsg.style.display = 'none';
    } else {
      btn.style.display = 'none';
      const noActivityMsg = document.getElementById('noActivityMsg');
      if (noActivityMsg) noActivityMsg.style.display = 'block';
    }
  },

  // ==================== CARREGAMENTO DE ESTRUTURAS ====================

  async loadArea(area) {
    const normalizedArea = (area || '').toLowerCase();
    const legacyAliases = { msa: 'teoria', hinaro: 'hinario' };
    const areaKey = legacyAliases[normalizedArea] || normalizedArea;

    if (areaKey === 'metodo') {
      this.currentInstrument = this.getSelectedInstrument();
    }

    if (areaKey === 'metodo' && !this.currentInstrument) {
      alert('Selecione um instrumento antes de abrir o Método.');
      return;
    }

    const cacheKey = areaKey === 'metodo' ? `${areaKey}:${this.currentInstrument}` : areaKey;
    console.log(`📂 Carregando área: ${areaKey} | instrumento: ${this.currentInstrument}`);

    if (!['teoria', 'metodo', 'hinario'].includes(areaKey)) {
      alert('Área inválida');
      return;
    }

    this.currentArea = areaKey;

    if (this.structureCache[cacheKey]) {
      this.renderArea(areaKey, this.structureCache[cacheKey]);
      return;
    }

    try {
      const url = areaKey === 'metodo'
        ? `/api/study/structure/${areaKey}`
        : `/api/study/structure/${areaKey}`;

      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      this.structureCache[cacheKey] = data;
      this.renderArea(areaKey, data);
    } catch (error) {
      console.error(`Erro ao carregar ${areaKey}:`, error);
      alert(`Erro ao carregar ${areaKey}`);
    }
  },

  renderArea(area, data) {
    const container = document.getElementById('studyContainer');
    if (!container) {
      console.error('Container #studyContainer não encontrado');
      return;
    }

    // Mostra a área de estudo e esconde a visão principal
    const mainView = document.getElementById('musicMainView');
    const areaView = document.getElementById('musicAreaView');
    const backBtn = document.getElementById('musicBackBtn');
    
    if (mainView) mainView.style.display = 'none';
    if (areaView) areaView.style.display = 'block';
    if (backBtn) backBtn.style.display = 'block';

    switch (area) {
      case 'teoria':
        this.renderMSA(data);
        break;
      case 'metodo':
        this.renderMetodo(data);
        break;
      case 'hinario':
        this.renderHinario(data);
        break;
    }

    // Atualiza título e progresso
    this.updateProgressDisplay(area, data);
  },

  goBack() {
    // Volta para a visão principal do MSA
    const mainView = document.getElementById('musicMainView');
    const areaView = document.getElementById('musicAreaView');
    const backBtn = document.getElementById('musicBackBtn');
    
    if (mainView) mainView.style.display = 'block';
    if (areaView) areaView.style.display = 'none';
    if (backBtn) backBtn.style.display = 'none';
    
    this.currentArea = null;
    this.showNotification('← Voltando ao menu principal');
  },

  // ==================== RENDERIZAÇÃO: MSA ====================

  renderMSA(data) {
    const html = `
      <div class="study-header">
        <h2>📚 ${data.titulo}</h2>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${data.total_progress_percent}%"></div>
        </div>
        <span class="progress-text">${data.total_progress_percent}% Completo</span>
      </div>

      <div class="study-content">
        ${data.fases.map((fase, idx) => this.renderMSAPhase(fase, data.user_progress, data.fases_progress)).join('')}
      </div>
    `;

    document.getElementById('studyContainer').innerHTML = html;
    this.setupAccordions();
  },

  renderMSAPhase(fase, userProgress, fasesProgress) {
    const fazeProgress = fasesProgress[fase.id] || 0;
    const isExpanded = fazeProgress < 100; // Expande fases não completas

    return `
      <div class="accordion-item" data-fase-id="${fase.id}">
        <div class="accordion-header" onclick="StudyApp.toggleAccordion(this)">
          <span class="accordion-icon">▼</span>
          <div class="accordion-title">
            <span class="fase-number">FASE ${fase.numero}</span>
            <span class="fase-name">${fase.titulo}</span>
          </div>
          <div class="accordion-progress">
            <div class="progress-bar-mini">
              <div class="progress-fill" style="width: ${fazeProgress}%"></div>
            </div>
            <span class="progress-label">${fazeProgress}%</span>
          </div>
        </div>

        <div class="accordion-body" style="${isExpanded ? '' : 'display: none;'}">
          ${fase.secoes.map(secao => this.renderMSASection(secao, userProgress)).join('')}
        </div>
      </div>
    `;
  },

  renderMSASection(secao, userProgress) {
    const progress = userProgress[secao.id] || { status: 'nao_iniciado' };
    const statusIcon = {
      'nao_iniciado': '🔒',
      'em_andamento': '▶️',
      'concluido': '✅'
    }[progress.status] || '❓';

    return `
      <div class="section-item" data-section-id="${secao.id}">
        <div class="section-info">
          <span class="status-icon">${statusIcon}</span>
          <div class="section-text">
            <span class="section-number">${secao.numero}</span>
            <span class="section-title">${secao.titulo}</span>
          </div>
        </div>

        <div class="section-actions">
          <select class="status-select" onchange="StudyApp.updateSectionStatus('msa', '${secao.id}', this.value)">
            <option value="nao_iniciado" ${progress.status === 'nao_iniciado' ? 'selected' : ''}>Não iniciado</option>
            <option value="em_andamento" ${progress.status === 'em_andamento' ? 'selected' : ''}>Em andamento</option>
            <option value="concluido" ${progress.status === 'concluido' ? 'selected' : ''}>Concluído</option>
          </select>

          <button class="btn-pdf" onclick="StudyApp.openPDF('msa')">📖 PDF</button>
          <button class="btn-review" onclick="StudyApp.markForReview('msa', '${secao.id}')">⭐</button>
        </div>
      </div>
    `;
  },

  // ==================== RENDERIZAÇÃO: MÉTODO ====================

  renderMetodo(data) {
    const html = `
      <div class="study-header">
        <h2>🎼 ${data.titulo}</h2>
        <div>Instrumento: <strong>${data.instrument}</strong></div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${data.total_progress_percent}%"></div>
        </div>
        <span class="progress-text">${data.total_progress_percent}% Completo</span>
      </div>

      <div class="study-content">
        ${data.fases.map(fase => this.renderMetodoPhase(fase, data.user_progress, data.modulos)).join('')}
      </div>
    `;

    document.getElementById('studyContainer').innerHTML = html;
    this.setupAccordions();
  },

  renderMetodoPhase(fase, userProgress, modulos) {
    return `
      <div class="accordion-item" data-fase-id="${fase.id}">
        <div class="accordion-header" onclick="StudyApp.toggleAccordion(this)">
          <span class="accordion-icon">▼</span>
          <div class="accordion-title">
            <span class="fase-number">FASE ${fase.numero}</span>
            <span class="fase-name">${fase.titulo}</span>
          </div>
        </div>

        <div class="accordion-body" style="display: none;">
          ${fase.modulos_presentes.map(modNum => {
            const modulo = modulos[modNum - 1];
            return `
              <div class="modulo-section">
                <h4>🎵 ${modulo.nome}</h4>
                <p class="modulo-desc">${modulo.descricao}</p>
                <div class="modulo-actions">
                  <select class="status-select" onchange="StudyApp.updateSectionStatus('metodo', '${fase.id}_mod_${modNum}', this.value)">
                    <option value="nao_iniciado">Não iniciado</option>
                    <option value="em_andamento">Em andamento</option>
                    <option value="concluido">Concluído</option>
                  </select>
                  <button class="btn-pdf" onclick="StudyApp.openPDF('metodo')">📖 PDF</button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  },

  // ==================== RENDERIZAÇÃO: HINÁRIO ====================

  renderHinario(data) {
    // Armazena todos os hinos para lazy loading
    this.allHymns = data.hinos;
    this.hymnOffset = data.total_carregados || 50;
    this.displayedHymnsCount = data.total_carregados || 50;

    const html = `
      <div class="study-header">
        <h2>🎵 ${data.titulo}</h2>
        <div>Total: <strong>${data.total_hinos} hinos</strong> | Carregados: <strong>${data.total_carregados || 50}</strong></div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${data.total_progress_percent}%"></div>
        </div>
        <span class="progress-text">${data.hinos_concluidos}/${data.total_hinos} Concluídos (${data.total_progress_percent}%)</span>
      </div>

      <div class="hymn-controls">
        <input type="search" id="hymnSearch" placeholder="🔍 Procurar hino pelo número ou título..." onkeyup="StudyApp.filterHymns()">
      </div>

      <div class="hymn-grid" id="hymnGrid">
        ${data.hinos.map(hymn => this.renderHymnCard(hymn)).join('')}
      </div>

      ${data.tem_mais ? `
        <div class="load-more-container">
          <button class="btn primary" onclick="StudyApp.loadMoreHymns()">
            ⬇️ Carregar mais ${data.total_hinos - this.hymnOffset} hinos
          </button>
        </div>
      ` : `
        <div class="load-more-container">
          <p style="text-align: center; color: #999;">Todos os ${data.total_hinos} hinos carregados ✓</p>
        </div>
      `}
    `;

    document.getElementById('studyContainer').innerHTML = html;
  },

  renderHymnCard(hymn) {
    const statusIcon = {
      'nao_iniciado': '🔒',
      'em_andamento': '▶️',
      'concluido': '✅'
    }[hymn.status] || '❓';

    const statusColor = {
      'nao_iniciado': '#555',
      'em_andamento': '#2196F3',
      'concluido': '#4CAF50'
    }[hymn.status] || '#555';

    const starsHtml = hymn.stars > 0 ? '⭐'.repeat(hymn.stars) : '☆☆☆';

    return `
      <div class="hymn-card" data-hymn-number="${hymn.numero}" data-hymn-name="${hymn.nome || 'Hino ' + hymn.numero}">
        <div class="hymn-header">
          <div class="hymn-number-badge">#${hymn.numero}</div>
          <div class="hymn-title-section">
            <h4 class="hymn-title">${hymn.nome || 'Hino ' + hymn.numero}</h4>
            <span class="hymn-status-icon" style="color: ${statusColor};">${statusIcon}</span>
          </div>
        </div>
        
        <div class="hymn-rating">
          <span class="hymn-stars">${starsHtml}</span>
        </div>

        <div class="hymn-actions">
          <button class="btn-small btn-view-hymn" onclick="StudyApp.openHymnPdf(${hymn.numero}, '${hymn.nome}')">
            📖 Ver Partitura
          </button>
          <select class="hymn-status-select" onchange="StudyApp.updateSectionStatus('hinario', 'hymn_${hymn.numero}', this.value)">
            <option value="nao_iniciado" ${hymn.status === 'nao_iniciado' ? 'selected' : ''}>Não iniciado</option>
            <option value="em_andamento" ${hymn.status === 'em_andamento' ? 'selected' : ''}>Em andamento</option>
            <option value="concluido" ${hymn.status === 'concluido' ? 'selected' : ''}>Concluído</option>
          </select>
        </div>
      </div>
    `;
  },

  loadMoreHymns() {
    console.log(`⬇️ Carregando mais hinos a partir de ${this.hymnOffset}...`);
    
    fetch(`/api/study/hymns/load-more?offset=${this.hymnOffset}&limit=${this.hymnLimit}`)
      .then(r => r.json())
      .then(data => {
        console.log(`✓ Carregados ${data.total} hinos`);
        
        // Adiciona novos hinos à lista
        this.allHymns.push(...data.hinos);
        this.displayedHymnsCount += data.total;
        this.hymnOffset += this.hymnLimit;
        
        // Renderiza novos cartões
        const hymnGrid = document.getElementById('hymnGrid');
        if (hymnGrid) {
          const newHtml = data.hinos.map(hymn => this.renderHymnCard(hymn)).join('');
          hymnGrid.insertAdjacentHTML('beforeend', newHtml);
        }
        
        // Atualiza ou remove botão de carregar mais
        const loadMoreBtn = document.querySelector('.load-more-container');
        if (loadMoreBtn && !data.tem_mais) {
          loadMoreBtn.innerHTML = `<p style="text-align: center; color: #999;">Todos os 350 hinos carregados ✓</p>`;
        } else if (loadMoreBtn && data.tem_mais) {
          loadMoreBtn.innerHTML = `
            <button class="btn primary" onclick="StudyApp.loadMoreHymns()">
              ⬇️ Carregar mais ${350 - this.hymnOffset} hinos
            </button>
          `;
        }
      })
      .catch(e => {
        console.error('❌ Erro ao carregar mais hinos:', e);
        this.showNotification('Erro ao carregar mais hinos');
      });
  },

  filterHymns() {
    const search = document.getElementById('hymnSearch')?.value.toLowerCase() || '';
    document.querySelectorAll('.hymn-card').forEach(card => {
      const number = card.dataset.hymnNumber.toString();
      const name = card.dataset.hymnName.toLowerCase();
      const matches = number.includes(search) || name.includes(search);
      card.style.display = matches ? 'flex' : 'none';
    });
  },

  // ==================== CONTROLES ====================

  toggleAccordion(header) {
    const body = header.nextElementSibling;
    const icon = header.querySelector('.accordion-icon');

    body.style.display = body.style.display === 'none' ? 'block' : 'none';
    icon.textContent = body.style.display === 'none' ? '▶' : '▼';
  },

  setupAccordions() {
    // Fecha todos exceto o primeiro
    const headers = document.querySelectorAll('.accordion-header');
    headers.forEach((h, idx) => {
      if (idx > 0) {
        h.nextElementSibling.style.display = 'none';
        h.querySelector('.accordion-icon').textContent = '▶';
      }
    });
  },

  async updateSectionStatus(area, sectionId, status) {
    console.log(`🔄 Atualizando ${area} ${sectionId} → ${status}`);

    try {
      const response = await fetch(`/api/study/progress/${area}/${sectionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();
      console.log('✅ Progresso atualizado:', result);

      // Mostra notificação
      if (result.xp_awarded > 0) {
        this.showNotification(`+${result.xp_awarded} XP!`);
      }

      // Recarrega a estrutura
      if (this.currentArea) {
        this.loadArea(this.currentArea);
      }
    } catch (error) {
      console.error('Erro ao atualizar:', error);
      alert('Erro ao atualizar progresso');
    }
  },

  openPDF(area) {
    const areaKey = (area || '').toLowerCase();
    const normalizedArea = areaKey === 'msa' ? 'teoria' : areaKey === 'hinaro' ? 'hinario' : areaKey;
    console.log(`📄 Abrindo PDF de ${normalizedArea}`);

    const url = normalizedArea === 'metodo'
      ? `/api/study/pdf/${normalizedArea}?instrument=${this.currentInstrument}`
      : `/api/study/pdf/${normalizedArea}`;

    this.openPdfViewer(url, normalizedArea);
  },

  openHymnPdf(hymnNumber, hymnName) {
    console.log(`📖 Abrindo hino ${hymnNumber} (${hymnName})`);
    const url = `/api/study/pdf/hymn/${hymnNumber}`;
    this.openPdfViewer(url, `Hino ${hymnNumber} - ${hymnName}`);
  },

  openPdfViewer(pdfUrl, title) {
    // Cria um modal com visualizador de PDF
    const modal = document.createElement('div');
    modal.className = 'pdf-modal';
    modal.id = 'pdfModal';
    
    const html = `
      <div class="pdf-modal-content">
        <div class="pdf-header">
          <h3>${title || 'Visualizador de PDF'}</h3>
          <div class="pdf-controls">
            <button class="pdf-btn" onclick="document.getElementById('pdfModal').remove()" title="Fechar (ESC)">✕</button>
            <button class="pdf-btn" onclick="document.getElementById('pdfEmbed').requestFullscreen()" title="Tela cheia">⛶</button>
            <button class="pdf-btn" onclick="window.open('${pdfUrl}', '_blank')" title="Abrir em nova aba">🔗</button>
          </div>
        </div>
        <div class="pdf-container">
          <iframe 
            id="pdfEmbed"
            src="${pdfUrl}#toolbar=1&navpanes=0&scrollbar=1" 
            type="application/pdf"
            style="width: 100%; height: 100%; border: none;">
          </iframe>
        </div>
      </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Fecha ao clicar fora ou pressionar ESC
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
    
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.getElementById('pdfModal')) {
        document.getElementById('pdfModal').remove();
      }
    });
  },

  markForReview(area, sectionId) {
    this.showNotification('⭐ Marcado para revisão!');
  },

  updateProgressDisplay(area, data) {
    const progressCard = document.querySelector(`[data-progress-${area}]`);
    if (progressCard) {
      progressCard.querySelector('.progress-fill').style.width = `${data.total_progress_percent}%`;
      progressCard.querySelector('.progress-text').textContent = `${data.total_progress_percent}% Completo`;
    }
  },

  showNotification(message) {
    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.textContent = message;
    document.body.appendChild(notif);

    setTimeout(() => {
      notif.style.opacity = '0';
      setTimeout(() => notif.remove(), 300);
    }, 2000);
  },

  // ==================== REVISÃO ====================

  async loadReviewItems() {
    console.log('📋 Carregando itens para revisão...');

    try {
      const response = await fetch('/api/study/review');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      this.renderReviewItems(data);
    } catch (error) {
      console.error('Erro ao carregar revisão:', error);
    }
  },

  renderReviewItems(data) {
    const html = `
      <div class="review-container">
        <h2>🔄 Revisar Conteúdo</h2>

        ${data.msa.length > 0 ? `
          <div class="review-section">
            <h3>📚 MSA (${data.msa.length})</h3>
            <div class="review-list">
              ${data.msa.map(item => `
                <div class="review-item">
                  <span>${item.nome}</span>
                  <button class="btn-review" onclick="StudyApp.updateSectionStatus('msa', '${item.id}', 'repassado')">Repassar</button>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        ${Object.keys(data.metodo).length > 0 ? `
          <div class="review-section">
            <h3>🎼 Método</h3>
            ${Object.entries(data.metodo).map(([inst, items]) => `
              <div>
                <h4>${inst}</h4>
                <div class="review-list">
                  ${items.map(item => `
                    <div class="review-item">
                      <span>${item.nome}</span>
                      <button class="btn-review" onclick="StudyApp.updateSectionStatus('metodo', '${item.id}', 'repassado')">Repassar</button>
                    </div>
                  `).join('')}
                </div>
              </div>
            `).join('')}
          </div>
        ` : ''}

        ${data.hinario.length > 0 ? `
          <div class="review-section">
            <h3>🎵 Hinário (${data.hinario.length})</h3>
            <div class="review-list">
              ${data.hinario.map(item => `
                <div class="review-item">
                  <span>Hino ${item.numero} (${'⭐'.repeat(item.stars)})</span>
                  <button class="btn-review" onclick="StudyApp.updateSectionStatus('hinario', 'hymn_${item.numero}', 'repassado')">Repassar</button>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}

        ${data.msa.length === 0 && Object.keys(data.metodo).length === 0 && data.hinario.length === 0 ? `
          <p style="text-align: center; color: #999;">Nenhum conteúdo para revisar ainda</p>
        ` : ''}
      </div>
    `;

    document.getElementById('studyContainer').innerHTML = html;
  }
};

// Inicializar quando o documento carregar
document.addEventListener('DOMContentLoaded', () => {
  StudyApp.init();
});
