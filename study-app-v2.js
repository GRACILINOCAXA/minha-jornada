/**
 * Study App v2 - Interface de Estudo Musical Completa
 * Suporta: Teoria, Método, Hinário (480 hinos + 6 coros)
 * Visualizador PDF integrado | Lazy loading | Busca
 */

const StudyAppV2 = {
  currentArea: null,
  currentInstrument: 'teclado',
  structureCache: {},
  
  // Estado do Hinário
  hinarioState: {
    allHinos: [],
    displayedHinos: [],
    allCoros: [],
    currentTab: 'hinos', // 'hinos' or 'coros'
    hymnOffset: 0,
    hymnLimit: 20,
    currentPage: 1,
    pageSize: 20,
    totalHymns: 480,
    searchQuery: ''
  },

  // ==================== INICIALIZAÇÃO ====================

  getSelectedInstrument() {
    const selectedInstrument = (typeof currentUser !== 'undefined' && currentUser && currentUser.instrumento) ||
      (typeof window !== 'undefined' && window.currentUser && window.currentUser.instrumento) ||
      (typeof this.currentInstrument === 'string' && this.currentInstrument.trim() ? this.currentInstrument : null);

    if (!selectedInstrument) return null;
    return normalizeInstrumentKey ? normalizeInstrumentKey(selectedInstrument) : selectedInstrument;
  },

  init() {
    console.log('🎵 StudyApp v2 inicializado');
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
    // Carrega última atividade do usuário
    fetch('/api/study/progress-report', { credentials: 'include' })
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
      nextText = `📚 Teoria (${msaProgress}%)`;
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

  // ==================== CARREGAMENTO DE ÁREAS ====================

  async loadArea(area) {
    const normalizedArea = (area || '').toLowerCase();
    const legacyAliases = { msa: 'teoria', hinaro: 'hinario', teoria: 'teoria', metodo: 'metodo', hinario: 'hinario' };
    const areaKey = legacyAliases[normalizedArea] || normalizedArea;

    if (!['teoria', 'metodo', 'hinario'].includes(areaKey)) {
      console.error(`❌ Área inválida: ${areaKey}`);
      return;
    }

    if (areaKey === 'metodo') {
      this.currentInstrument = this.getSelectedInstrument();
    }

    if (areaKey === 'metodo' && !this.currentInstrument) {
      console.warn('Método bloqueado: usuário sem instrumento autenticado.');
      return;
    }

    const cacheKey = areaKey === 'metodo' ? `${areaKey}:${this.currentInstrument}` : areaKey;
    console.log(`📂 Carregando área: ${areaKey} | instrumento: ${this.currentInstrument}`);

    this.currentArea = areaKey;

    const mainView = document.getElementById('musicMainView');
    const areaView = document.getElementById('musicAreaView');
    const backBtn = document.getElementById('musicBackBtn');

    if (mainView) mainView.style.display = 'none';
    if (areaView) areaView.style.display = 'block';
    if (backBtn) backBtn.style.display = 'block';

    if (this.structureCache[cacheKey]) {
      this.renderArea(areaKey, this.structureCache[cacheKey]);
      return;
    }

    try {
      const url = `/api/study/structure/${areaKey}`;

      const response = await fetch(url, {
        credentials: 'include'  // Incluir cookies de sessão
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      this.structureCache[cacheKey] = data;
      this.renderArea(areaKey, data);
    } catch (error) {
      console.error(`❌ Erro ao carregar ${areaKey}:`, error);
      this.showError(`Erro ao carregar ${areaKey}. Verifique a conexão.`);
    }
  },

  renderArea(area, data) {
    const container = document.getElementById('studyContainer');
    if (!container) {
      console.error('❌ Container #studyContainer não encontrado');
      return;
    }

    switch (area) {
      case 'teoria':
        this.renderTeoria(data);
        break;
      case 'metodo':
        this.renderMetodo(data);
        break;
      case 'hinario':
        this.renderHinario(data);
        break;
    }
  },

  goBack() {
    const mainView = document.getElementById('musicMainView');
    const areaView = document.getElementById('musicAreaView');
    const backBtn = document.getElementById('musicBackBtn');
    
    if (mainView) mainView.style.display = 'block';
    if (areaView) areaView.style.display = 'none';
    if (backBtn) backBtn.style.display = 'none';
    
    this.currentArea = null;
  },

  // ==================== RENDERIZAÇÃO: TEORIA ====================

  renderTeoria(data) {
    const container = document.getElementById('studyContainer');
    const progressPercent = data.total_progress_percent || 0;
    const phases = data.fases || [];

    let html = `
      <div class="study-header">
        <h2>📖 Teoria do MSA</h2>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${progressPercent}%"></div>
        </div>
        <span class="progress-text">${progressPercent}% Completo</span>
      </div>

      <div class="msa-actions">
        <button class="btn primary" onclick="StudyAppV2.openPDF('teoria')">📄 Visualizar PDF da Teoria</button>
      </div>

      <div class="pdf-viewer-container" id="pdfViewerContainer" style="display:none;">
        <iframe id="pdfViewer" class="pdf-viewer" src="/api/study/pdf/teoria#toolbar=1&navpanes=1&scrollbar=1"></iframe>
      </div>

      <div class="msa-phases-container">
    `;

    phases.forEach((phase) => {
      const phaseId = `fase-teoria-${phase.numero}`;
      const sections = phase.secoes || [];
      const completedSections = sections.filter((s) => {
        const userProgress = data.user_progress[s.id];
        return userProgress && userProgress.status === 'concluido';
      }).length;
      
      const phaseProgress = Math.round((completedSections / Math.max(1, sections.length)) * 100);
      
      html += `
        <div class="accordion-item">
          <div class="accordion-header" onclick="StudyAppV2.toggleAccordion(this)">
            <span class="accordion-icon">▶</span>
            <strong>Fase ${phase.numero}:</strong> ${phase.titulo}
            <span style="margin-left:auto;font-size:12px;color:#666;">${completedSections}/${sections.length} (${phaseProgress}%)</span>
          </div>
          <div class="accordion-body" style="display:none;">
            ${sections.map((section) => {
              const userProgress = data.user_progress[section.id] || {};
              const status = userProgress.status || 'nao_iniciado';
              const statusIcon = status === 'concluido' ? '✅' : (status === 'em_andamento' ? '▶️' : '🔒');
              
              return `
                <div class="section-item">
                  <div style="flex:1;">
                    <div><strong>${statusIcon} ${section.titulo}</strong></div>
                    <div style="font-size:11px;color:#999;">Páginas ${section.start_page || '?'}-${section.end_page || '?'}</div>
                  </div>
                  <div class="section-actions">
                    <select onchange="StudyAppV2.updateProgress('teoria', '${section.id}', this.value)" style="padding:4px;font-size:12px;">
                      <option value="nao_iniciado" ${status === 'nao_iniciado' ? 'selected' : ''}>🔒 Não</option>
                      <option value="em_andamento" ${status === 'em_andamento' ? 'selected' : ''}>▶️ Em andamento</option>
                      <option value="concluido" ${status === 'concluido' ? 'selected' : ''}>✅ Concluído</option>
                    </select>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  },

  // ==================== RENDERIZAÇÃO: MÉTODO ====================

  renderMetodo(data) {
    const container = document.getElementById('studyContainer');
    const instrument = data.instrument || 'teclado';
    const progressPercent = data.total_progress_percent || 0;
    const phases = data.fases || [];
    const customMethod = data.custom_method || null;
    const hasCustomMethod = Boolean(data.has_custom_method && customMethod);
    const customName = customMethod ? (customMethod.original_filename || 'meu_metodo.pdf') : '';
    const customUrl = customMethod ? `/api/instruments/method/file?instrument=${encodeURIComponent(instrument)}` : '';

    let html = `
      <div class="study-header">
        <h2>🎼 Método — ${this.getInstrumentLabel(instrument)}</h2>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${progressPercent}%"></div>
        </div>
        <span class="progress-text">${progressPercent}% Completo</span>
      </div>

      <div class="msa-actions" style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
        <button class="btn primary" onclick="StudyAppV2.openOfficialMethodPDF('${instrument}')">📖 Abrir Método Oficial</button>
      </div>

      <div class="pdf-viewer-container" id="pdfViewerContainer" style="display:none;">
        <iframe id="pdfViewer" class="pdf-viewer" src="/api/study/pdf/metodo?instrument=${encodeURIComponent(instrument)}#toolbar=1&navpanes=1&scrollbar=1"></iframe>
      </div>

      <div class="custom-method-panel" style="margin-top:18px;padding:16px;border:1px solid #dfeafc;border-radius:12px;background:#f8fbff;display:flex;flex-direction:column;gap:12px;">
        <h3 style="margin:0;">📎 MEU MÉTODO</h3>
        <div style="color:#475569;font-size:14px;">Envie seu método em PDF — tamanho máximo: 50 MB.</div>
        <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
          <input id="customMethodFileInput" type="file" accept="application/pdf" style="max-width:100%;" />
          <button class="btn primary" onclick="StudyAppV2.uploadCustomMethod('${instrument}')">📎 Anexar meu método</button>
        </div>
        ${hasCustomMethod ? `
          <div style="display:flex;flex-direction:column;gap:10px;padding:12px;border:1px solid #d9e1f2;border-radius:10px;background:#fff;">
            <div style="font-weight:700;">📄 ${customName}</div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;">
              <a class="btn mini primary" href="${customUrl}" target="_blank" rel="noopener noreferrer">📖 Abrir</a>
              <button class="btn mini" onclick="StudyAppV2.uploadCustomMethod('${instrument}', true)">🔄 Substituir</button>
              <button class="btn mini danger" onclick="StudyAppV2.removeCustomMethod('${instrument}')">🗑️ Remover</button>
            </div>
          </div>
        ` : `
          <div style="color:#475569;">Nenhum método personalizado foi anexado para este instrumento.</div>
        `}
      </div>

      <div class="msa-phases-container">
    `;

    phases.forEach((phase) => {
      const phaseId = `fase-metodo-${phase.numero}`;
      const sections = phase.secoes || [];
      const completedSections = sections.filter((s) => {
        const userProgress = data.user_progress[s.id];
        return userProgress && userProgress.status === 'concluido';
      }).length;
      
      const phaseProgress = Math.round((completedSections / Math.max(1, sections.length)) * 100);
      
      html += `
        <div class="accordion-item">
          <div class="accordion-header" onclick="StudyAppV2.toggleAccordion(this)">
            <span class="accordion-icon">▶</span>
            <strong>Fase ${phase.numero}:</strong> ${phase.titulo}
            <span style="margin-left:auto;font-size:12px;color:#666;">${completedSections}/${sections.length} (${phaseProgress}%)</span>
          </div>
          <div class="accordion-body" style="display:none;">
            ${sections.map((section) => {
              const userProgress = data.user_progress[section.id] || {};
              const status = userProgress.status || 'nao_iniciado';
              const statusIcon = status === 'concluido' ? '✅' : (status === 'em_andamento' ? '▶️' : '🔒');
              
              return `
                <div class="section-item">
                  <div style="flex:1;">
                    <div><strong>${statusIcon} ${section.titulo}</strong></div>
                  </div>
                  <div class="section-actions">
                    <select onchange="StudyAppV2.updateProgress('metodo', '${section.id}', this.value)" style="padding:4px;font-size:12px;">
                      <option value="nao_iniciado" ${status === 'nao_iniciado' ? 'selected' : ''}>🔒 Não</option>
                      <option value="em_andamento" ${status === 'em_andamento' ? 'selected' : ''}>▶️ Em andamento</option>
                      <option value="concluido" ${status === 'concluido' ? 'selected' : ''}>✅ Concluído</option>
                    </select>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  },

  // ==================== RENDERIZAÇÃO: HINÁRIO ====================

  renderHinario(data) {
    const container = document.getElementById('studyContainer');

    this.hinarioState.allHinos = data.hinos || [];
    this.hinarioState.allCoros = data.coros || [];
    this.hinarioState.displayedHinos = data.hinos || [];
    this.hinarioState.hymnOffset = data.hinos_carregados || this.hinarioState.totalHymns;
    this.hinarioState.totalHymns = Number(data.total_hinos || 480);
    this.hinarioState.totalCoros = Number(data.total_coros || 6);
    this.hinarioState.currentTab = 'hinos';
    this.hinarioState.currentPage = 1;
    this.hinarioState.selectedHymns = new Set();
    this.hinarioState.selectedCoros = new Set();
    this.hinarioState.searchQuery = '';
    this.hinarioState.statusFilter = 'todos';
    this.hinarioState.difficultyFilter = 'todos';

    const completedHymns = Number(data.hinos_concluidos || 0);
    const hymnPercent = this.hinarioState.totalHymns > 0 ? Math.round((completedHymns / this.hinarioState.totalHymns) * 100) : 0;
    const totalProgress = Number(data.total_progress_percent || 0);

    let html = `
      <div class="study-header">
        <h2>🎵 Hinário</h2>
        <div style="font-size:14px;margin:8px 0;">
          <strong>🎵 Hinos</strong><br>
          <span>${completedHymns}/${this.hinarioState.totalHymns} concluídos (${hymnPercent}%)</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" style="width: ${hymnPercent}%"></div>
        </div>
      </div>

      <div class="hinario-tabs">
        <button class="tab-btn active" onclick="StudyAppV2.switchHinarioTab('hinos', this)">
          🎵 Hinos (${completedHymns}/${this.hinarioState.totalHymns})
        </button>
        <button class="tab-btn" onclick="StudyAppV2.switchHinarioTab('coros', this)">
          🎶 Coros (${data.coros_concluidos || 0}/${this.hinarioState.totalCoros})
        </button>
      </div>

      <div class="hinario-controls" style="display:flex;flex-direction:column;gap:12px;margin:16px 0;">
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
          <input type="text" id="hymnSearch" placeholder="🔎 Pesquisar..." style="flex:1;min-width:220px;padding:10px 12px;border:1px solid #d9e1f2;border-radius:8px;" value="">
        </div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
          <button id="markHymnsDoneBtn" class="btn primary" style="padding:10px 14px;">✅ Marcar como concluído</button>
          <select id="hymnStatusFilter" style="padding:8px 10px;border:1px solid #d9e1f2;border-radius:8px;">
            <option value="todos">Status: Todos</option>
            <option value="nao_iniciado">Status: Não iniciado</option>
            <option value="em_andamento">Status: Em andamento</option>
            <option value="concluido">Status: Concluído</option>
          </select>
          <select id="hymnDifficultyFilter" style="padding:8px 10px;border:1px solid #d9e1f2;border-radius:8px;">
            <option value="todos">Dificuldade: Todas</option>
            <option value="baixa">Dificuldade: Baixa</option>
            <option value="media">Dificuldade: Média</option>
            <option value="alta">Dificuldade: Alta</option>
          </select>
        </div>
        <div id="hinarioBulkBar" class="bulk-bar" style="display:none;align-items:center;gap:10px;flex-wrap:wrap;padding:10px 12px;border:1px solid #dfeafc;border-radius:10px;background:#f5f8ff;">
          <label style="display:flex;align-items:center;gap:6px;cursor:pointer;"><input type="checkbox" id="selectVisibleItems"> Selecionar exibidos</label>
          <button class="btn mini" data-bulk-action="concluido">Concluir</button>
          <button class="btn mini" data-bulk-action="em_andamento">Em andamento</button>
          <button class="btn mini" data-bulk-action="nao_iniciado">Não iniciado</button>
          <button class="btn mini" data-bulk-action="clear">Limpar seleção</button>
          <button class="btn mini" data-bulk-action="clear-all">Desmarcar todos os 480</button>
          <button class="btn mini primary" data-bulk-action="all">Selecionar todos os 480</button>
        </div>
      </div>

      <div id="hinosTab" class="hinario-tab active">
        <div id="hymnPaginationInfo" style="font-size:12px;color:#475569;margin:0 0 12px;display:block;"></div>
        <div id="hymnPagination" style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;justify-content:center;margin-bottom:12px;"></div>
        <div id="hinosContainer" class="hinos-grid"></div>
        <div id="hymnEmptyState" style="display:none; padding:18px; text-align:center; color:#64748b;">Nenhum resultado encontrado.</div>
      </div>

      <div id="corosTab" class="hinario-tab" style="display:none;">
        <div id="corosContainer" class="coros-grid"></div>
        <div id="corosEmptyState" style="display:none; padding:18px; text-align:center; color:#64748b;">Nenhum resultado encontrado.</div>
      </div>
    `;

    container.innerHTML = html;
    this.hinarioState.searchInput = document.getElementById('hymnSearch');
    this.hinarioState.statusFilterInput = document.getElementById('hymnStatusFilter');
    this.hinarioState.difficultyFilterInput = document.getElementById('hymnDifficultyFilter');

    if (this.hinarioState.searchInput) {
      this.hinarioState.searchInput.addEventListener('input', (event) => {
        this.hinarioState.searchQuery = (event.target.value || '').trim().toLowerCase();
        this.hinarioState.currentPage = 1;
        this.renderHinarioLists();
      });
    }

    if (this.hinarioState.statusFilterInput) {
      this.hinarioState.statusFilterInput.addEventListener('change', (event) => {
        this.hinarioState.statusFilter = event.target.value;
        this.hinarioState.currentPage = 1;
        this.renderHinarioLists();
      });
    }

    if (this.hinarioState.difficultyFilterInput) {
      this.hinarioState.difficultyFilterInput.addEventListener('change', (event) => {
        this.hinarioState.difficultyFilter = event.target.value;
        this.hinarioState.currentPage = 1;
        this.renderHinarioLists();
      });
    }

    document.querySelectorAll('[data-bulk-action]').forEach((button) => {
      button.addEventListener('click', async () => {
        const action = button.dataset.bulkAction;
        if (action === 'clear') {
          this.hinarioState.selectedHymns = new Set();
          this.hinarioState.selectedCoros = new Set();
          this.renderHinarioLists();
          return;
        }
        if (action === 'clear-all') {
          const confirmClear = window.confirm('Tem certeza que deseja desmarcar todos os 480 hinos?');
          if (!confirmClear) return;
          await this.applyBulkHymnSelection(Array.from({ length: 480 }, (_, index) => index + 1), 'nao_iniciado');
          return;
        }
        if (action === 'all') {
          await this.selectAllHymns();
          return;
        }
        await this.applyBulkAction(action);
      });
    });

    const visibleSelect = document.getElementById('selectVisibleItems');
    if (visibleSelect) {
      visibleSelect.addEventListener('change', () => {
        if (visibleSelect.checked) {
          this.selectVisibleItems();
        } else {
          this.hinarioState.selectedHymns = new Set();
          this.hinarioState.selectedCoros = new Set();
          this.renderHinarioLists();
        }
      });
    }

    const markHymnsBtn = document.getElementById('markHymnsDoneBtn');
    if (markHymnsBtn) {
      markHymnsBtn.addEventListener('click', () => this.openBulkHymnModal('concluido'));
    }

    this.renderHinarioLists();
  },

  getFilteredHymns() {
    const query = (this.hinarioState.searchQuery || '').trim().toLowerCase();
    const statusFilter = this.hinarioState.statusFilter || 'todos';
    const difficultyFilter = this.hinarioState.difficultyFilter || 'todos';
    const items = this.hinarioState.allHinos || [];

    return items.filter((hymn) => {
      const number = String(hymn.numero || '').trim();
      const title = (hymn.nome || hymn.titulo || '').toLowerCase();
      const status = hymn.status || 'nao_iniciado';
      const difficulty = (hymn.difficulty || '').toLowerCase();

      const queryMatches = !query || query === '1' || query === '01' || query === '001'
        ? String(number).includes(query) || String(number).padStart(3, '0').includes(query)
        : title.includes(query) || String(number).includes(query) || String(number).padStart(3, '0').includes(query);

      const statusMatches = statusFilter === 'todos' || status === statusFilter;
      const difficultyMatches = difficultyFilter === 'todos' || difficulty === difficultyFilter;
      return queryMatches && statusMatches && difficultyMatches;
    });
  },

  getFilteredCoros() {
    const query = (this.hinarioState.searchQuery || '').trim().toLowerCase();
    const statusFilter = this.hinarioState.statusFilter || 'todos';
    const difficultyFilter = this.hinarioState.difficultyFilter || 'todos';
    const items = this.hinarioState.allCoros || [];

    return items.filter((coro) => {
      const number = String(coro.numero || '').trim();
      const title = (coro.nome || coro.titulo || '').toLowerCase();
      const status = coro.status || 'nao_iniciado';
      const difficulty = (coro.difficulty || '').toLowerCase();

      const queryMatches = !query || title.includes(query) || number.includes(query) || String(number).padStart(2, '0').includes(query);
      const statusMatches = statusFilter === 'todos' || status === statusFilter;
      const difficultyMatches = difficultyFilter === 'todos' || difficulty === difficultyFilter;
      return queryMatches && statusMatches && difficultyMatches;
    });
  },

  renderHinarioLists() {
    const hymnItems = this.getFilteredHymns();
    const coroItems = this.getFilteredCoros();
    const pageSize = this.hinarioState.pageSize || 20;
    const totalPages = Math.max(1, Math.ceil(hymnItems.length / pageSize));
    this.hinarioState.currentPage = Math.min(this.hinarioState.currentPage || 1, totalPages);
    const safeStart = (this.hinarioState.currentPage - 1) * pageSize;
    const pageHymns = hymnItems.slice(safeStart, safeStart + pageSize);

    const hymnsContainer = document.getElementById('hinosContainer');
    const hymnEmpty = document.getElementById('hymnEmptyState');
    const hymnPagination = document.getElementById('hymnPagination');
    const hymnPaginationInfo = document.getElementById('hymnPaginationInfo');

    if (hymnPaginationInfo) {
      const pageStart = hymnItems.length ? safeStart + 1 : 0;
      const pageEnd = Math.min(safeStart + pageSize, hymnItems.length);
      hymnPaginationInfo.textContent = hymnItems.length ? `Mostrando ${pageStart}–${pageEnd} de ${hymnItems.length}` : 'Mostrando 0–0 de 0';
    }

    if (hymnPagination) {
      const prevDisabled = this.hinarioState.currentPage <= 1 ? 'disabled' : '';
      const nextDisabled = this.hinarioState.currentPage >= totalPages ? 'disabled' : '';
      const pages = Array.from({ length: totalPages }, (_, index) => index + 1);
      const pageButtons = pages.map((pageNumber) => `
        <button class="btn mini ${this.hinarioState.currentPage === pageNumber ? 'primary' : ''}" data-page-number="${pageNumber}" ${this.hinarioState.currentPage === pageNumber ? 'disabled' : ''}>
          ${pageNumber}
        </button>
      `).join('');
      hymnPagination.innerHTML = `
        <button class="btn mini" data-page-action="prev" ${prevDisabled}>Anterior</button>
        ${pageButtons}
        <button class="btn mini" data-page-action="next" ${nextDisabled}>Próximo</button>
      `;
      hymnPagination.querySelectorAll('[data-page-action]').forEach((button) => {
        const action = button.dataset.pageAction;
        button.addEventListener('click', () => {
          if (action === 'prev' && this.hinarioState.currentPage > 1) this.hinarioState.currentPage -= 1;
          if (action === 'next' && this.hinarioState.currentPage < totalPages) this.hinarioState.currentPage += 1;
          this.renderHinarioLists();
        });
      });
      hymnPagination.querySelectorAll('[data-page-number]').forEach((button) => {
        button.addEventListener('click', () => {
          this.hinarioState.currentPage = Number(button.dataset.pageNumber) || 1;
          this.renderHinarioLists();
        });
      });
    }

    if (hymnsContainer) {
      if (!hymnItems.length) {
        hymnsContainer.innerHTML = '';
        if (hymnEmpty) hymnEmpty.style.display = 'block';
      } else {
        if (hymnEmpty) hymnEmpty.style.display = 'none';
        hymnsContainer.innerHTML = pageHymns.map((hymn) => this.renderHymnCard(hymn)).join('');
      }
    }

    const corosContainer = document.getElementById('corosContainer');
    const corosEmpty = document.getElementById('corosEmptyState');
    if (corosContainer) {
      if (!coroItems.length) {
        corosContainer.innerHTML = '';
        if (corosEmpty) corosEmpty.style.display = 'block';
      } else {
        if (corosEmpty) corosEmpty.style.display = 'none';
        corosContainer.innerHTML = coroItems.map((coro) => this.renderChorusCard(coro)).join('');
      }
    }

    document.querySelectorAll('input[data-kind="hymn"]').forEach((checkbox) => {
      checkbox.addEventListener('change', () => {
        const key = checkbox.dataset.id;
        if (checkbox.checked) {
          this.hinarioState.selectedHymns.add(key);
        } else {
          this.hinarioState.selectedHymns.delete(key);
        }
        this.renderHinarioLists();
      });
    });

    const hasSelection = (this.hinarioState.selectedHymns && this.hinarioState.selectedHymns.size > 0) || (this.hinarioState.selectedCoros && this.hinarioState.selectedCoros.size > 0);
    const bulkBar = document.getElementById('hinarioBulkBar');
    if (bulkBar) bulkBar.style.display = hasSelection ? 'flex' : 'none';

    const selectVisible = document.getElementById('selectVisibleItems');
    if (selectVisible) {
      const visibleKeys = pageHymns.map((item) => item.id || `hymn_${item.numero}`);
      const selectedVisible = visibleKeys.length > 0 && visibleKeys.every((key) => this.hinarioState.selectedHymns.has(key));
      selectVisible.checked = selectedVisible && visibleKeys.length > 0;
    }
  },

  renderHymnCard(hymn) {
    const key = hymn.id || `hymn_${hymn.numero}`;
    const status = hymn.status || 'nao_iniciado';
    const isSelected = this.hinarioState.selectedHymns && this.hinarioState.selectedHymns.has(key);
    const difficulty = hymn.difficulty || '';
    const difficultyLabel = {
      baixa: 'Baixa',
      media: 'Média',
      alta: 'Alta'
    }[difficulty] || 'Sem dificuldade';

    return `
      <div class="hymn-card" style="display:flex;flex-direction:column;gap:10px;padding:12px 14px;border:1px solid #e2e8f0;border-radius:12px;background:#fff;box-shadow:0 2px 8px rgba(15,23,42,0.04);">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
          <label style="display:flex;align-items:center;gap:8px;font-size:12px;color:#475569;">
            <input type="checkbox" data-kind="hymn" data-id="${key}" ${isSelected ? 'checked' : ''}> <span>#${String(hymn.numero).padStart(3, '0')}</span>
          </label>
        </div>
        <div style="font-weight:700; font-size:15px; color:#0f172a; line-height:1.4;">🎵 ${hymn.nome || hymn.titulo || `Hino ${hymn.numero}`}</div>
        <div style="font-size:12px; color:#475569;">${status === 'concluido' ? '✅ Concluído' : status === 'em_andamento' ? '⏳ Em andamento' : '⏳ Não iniciado'}</div>
        <div style="font-size:12px; color:#475569; display:flex;align-items:center;gap:8px; flex-wrap:wrap;">
          <span>Dificuldade:</span>
          <select data-kind="hymn" data-id="${key}" style="padding:4px 6px;border:1px solid #dbe3ee;border-radius:6px;">
            <option value="" ${!difficulty ? 'selected' : ''}>Sem dificuldade</option>
            <option value="baixa" ${difficulty === 'baixa' ? 'selected' : ''}>Baixa</option>
            <option value="media" ${difficulty === 'media' ? 'selected' : ''}>Média</option>
            <option value="alta" ${difficulty === 'alta' ? 'selected' : ''}>Alta</option>
          </select>
        </div>
        <div style="font-size:12px; color:#475569;">⭐ ${this.renderStars(hymn.stars || 0)}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="btn mini" onclick="StudyAppV2.markHymnStatus('${key}', 'concluido')">Concluir</button>
          <button class="btn mini" onclick="StudyAppV2.openHymnPDF(${hymn.numero})">Partitura</button>
        </div>
      </div>
    `;
  },

  renderChorusCard(coro) {
    const key = coro.id || `chorus_${coro.numero}`;
    const status = coro.status || 'nao_iniciado';
    const isSelected = this.hinarioState.selectedCoros && this.hinarioState.selectedCoros.has(key);
    const difficulty = coro.difficulty || '';

    return `
      <div class="coro-card" style="display:flex;flex-direction:column;gap:10px;padding:12px 14px;border:1px solid #e2e8f0;border-radius:12px;background:#fff;box-shadow:0 2px 8px rgba(15,23,42,0.04);">
        <div style="display:flex;align-items:center;justify-content:space-between;gap:8px;">
          <label style="display:flex;align-items:center;gap:8px;font-size:12px;color:#475569;">
            <input type="checkbox" data-kind="chorus" data-id="${key}" ${isSelected ? 'checked' : ''}> <span>#${String(coro.numero).padStart(2, '0')}</span>
          </label>
        </div>
        <div style="font-weight:700;font-size:15px;color:#0f172a;line-height:1.4;">🎶 ${coro.nome || coro.titulo || `Coro ${coro.numero}`}</div>
        <div style="font-size:12px;color:#475569;">${status === 'concluido' ? '✅ Concluído' : status === 'em_andamento' ? '⏳ Em andamento' : '⏳ Não iniciado'}</div>
        <div style="font-size:12px; color:#475569; display:flex;align-items:center;gap:8px; flex-wrap:wrap;">
          <span>Dificuldade:</span>
          <select data-kind="chorus" data-id="${key}" style="padding:4px 6px;border:1px solid #dbe3ee;border-radius:6px;">
            <option value="" ${!difficulty ? 'selected' : ''}>Sem dificuldade</option>
            <option value="baixa" ${difficulty === 'baixa' ? 'selected' : ''}>Baixa</option>
            <option value="media" ${difficulty === 'media' ? 'selected' : ''}>Média</option>
            <option value="alta" ${difficulty === 'alta' ? 'selected' : ''}>Alta</option>
          </select>
        </div>
        <div style="font-size:12px;color:#475569;">⭐ ${this.renderStars(coro.stars || 0)}</div>
        <div style="display:flex;gap:8px;flex-wrap:wrap;">
          <button class="btn mini" onclick="StudyAppV2.markChorusStatus('${key}', 'concluido')">Concluir</button>
          <button class="btn mini" onclick="StudyAppV2.openChorusPDF(${coro.numero})">Partitura</button>
        </div>
      </div>
    `;
  },

  renderStars(count) {
    return Array.from({ length: 5 }, (_, index) => index < count ? '★' : '☆').join(' ');
  },

  switchHinarioTab(tab, btn) {
    this.hinarioState.currentTab = tab;
    const hinosTab = document.getElementById('hinosTab');
    const corosTab = document.getElementById('corosTab');
    document.querySelectorAll('.tab-btn').forEach((item) => item.classList.toggle('active', item === btn));
    if (hinosTab) hinosTab.style.display = tab === 'hinos' ? 'block' : 'none';
    if (corosTab) corosTab.style.display = tab === 'coros' ? 'block' : 'none';
  },

  selectVisibleItems() {
    const tab = this.hinarioState.currentTab || 'hinos';
    if (tab === 'hinos') {
      const pageHymns = this.getFilteredHymns().slice(
        (this.hinarioState.currentPage - 1) * (this.hinarioState.pageSize || 20),
        this.hinarioState.currentPage * (this.hinarioState.pageSize || 20)
      );
      this.hinarioState.selectedHymns = new Set(pageHymns.map((hymn) => hymn.id || `hymn_${hymn.numero}`));
    } else {
      const coros = this.getFilteredCoros();
      this.hinarioState.selectedCoros = new Set(coros.map((coro) => coro.id || `chorus_${coro.numero}`));
    }
    this.renderHinarioLists();
  },

  async selectAllHymns() {
    try {
      const ids = (this.hinarioState.allHinos || []).map((item) => item.id || `hymn_${item.numero}`);
      this.hinarioState.selectedHymns = new Set(ids);
      this.renderHinarioLists();
    } catch (error) {
      console.error('Erro ao selecionar todos os hinos:', error);
    }
  },

  async applyBulkAction(action) {
    const hymnIds = [...(this.hinarioState.selectedHymns || new Set())];
    const chorusIds = [...(this.hinarioState.selectedCoros || new Set())];
    if (!hymnIds.length && !chorusIds.length) return;

    try {
      const payload = {
        kind: 'hymn',
        status: action,
        ids: hymnIds.map((id) => Number(String(id).replace('hymn_', ''))),
        all: false
      };

      if (hymnIds.length) {
        await fetch('/api/study/hinario/bulk-update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify(payload)
        });
      }

      if (chorusIds.length) {
        await fetch('/api/study/hinario/bulk-update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({
            kind: 'chorus',
            status: action,
            ids: chorusIds.map((id) => Number(String(id).replace('chorus_', ''))),
            all: false
          })
        });
      }

      this.hinarioState.selectedHymns = new Set();
      this.hinarioState.selectedCoros = new Set();
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao aplicar ação em massa:', error);
    }
  },

  parseHymnSelection(input) {
    if (!input || !String(input).trim()) return [];

    const values = [];
    for (const token of String(input).split(',')) {
      const item = token.trim();
      if (!item) continue;

      if (item.includes('-')) {
        const [startRaw, endRaw] = item.split('-');
        if (!startRaw || !endRaw) continue;
        const start = Number(startRaw.trim());
        const end = Number(endRaw.trim());
        if (!Number.isInteger(start) || !Number.isInteger(end) || start < 1 || end < 1 || start > 480 || end > 480) continue;
        const [rangeStart, rangeEnd] = start <= end ? [start, end] : [end, start];
        for (let number = rangeStart; number <= rangeEnd; number += 1) values.push(number);
        continue;
      }

      const number = Number(item);
      if (!Number.isInteger(number) || number < 1 || number > 480) continue;
      values.push(number);
    }

    return [...new Set(values)].sort((a, b) => a - b);
  },

  openBulkHymnModal(defaultStatus = 'concluido') {
    const modal = document.createElement('div');
    modal.style.position = 'fixed';
    modal.style.top = '0';
    modal.style.left = '0';
    modal.style.width = '100vw';
    modal.style.height = '100vh';
    modal.style.background = 'rgba(15, 23, 42, 0.5)';
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    modal.style.zIndex = '2000';

    const panel = document.createElement('div');
    panel.style.width = 'min(500px, 92vw)';
    panel.style.background = '#fff';
    panel.style.borderRadius = '14px';
    panel.style.padding = '20px';
    panel.style.boxShadow = '0 20px 40px rgba(15, 23, 42, 0.2)';

    panel.innerHTML = `
      <h3 style="margin:0 0 12px;">MARCAR HINOS COMO CONCLUÍDOS</h3>
      <p style="margin:0 0 8px; color:#475569;">Digite os números dos hinos:</p>
      <textarea id="hymnBulkInput" rows="4" style="width:100%;padding:10px;border:1px solid #d9e1f2;border-radius:10px;resize:vertical;">1, 5, 10-20</textarea>
      <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="5">✅ +5</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="10">✅ +10</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="30">✅ +30</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="50">✅ +50</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="200">✅ +200</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="mark" data-range="480">✅ Todos</button>
      </div>
      <div style="margin-top:8px; display:flex; gap:8px; flex-wrap:wrap;">
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="5">❌ +5</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="10">❌ +10</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="30">❌ +30</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="50">❌ +50</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="200">❌ +200</button>
        <button class="btn mini quick-bulk-btn" data-quick-bulk="unmark" data-range="480">❌ Todos</button>
      </div>
      <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
        <button id="bulkMarkAllBtn" class="btn mini primary">✓ Marcar TODOS os 480 como concluídos</button>
        <button id="bulkUnmarkAllBtn" class="btn mini">✕ Desmarcar todos os 480</button>
      </div>
      <div style="margin-top:18px; display:flex; justify-content:flex-end; gap:10px;">
        <button id="bulkCancelBtn" class="btn mini">Cancelar</button>
        <button id="bulkApplyBtn" class="btn primary">Marcar como concluídos</button>
      </div>
    `;

    modal.appendChild(panel);
    document.body.appendChild(modal);

    const close = () => modal.remove();

    panel.querySelector('#bulkCancelBtn').addEventListener('click', close);
    panel.querySelector('#bulkApplyBtn').dataset.pendingStatus = defaultStatus || 'concluido';

    panel.querySelectorAll('.quick-bulk-btn').forEach((button) => {
      button.addEventListener('click', () => {
        const range = Number(button.dataset.range || 0);
        const type = button.dataset.quickBulk;
        const input = panel.querySelector('#hymnBulkInput');
        const targetStatus = type === 'unmark' ? 'nao_iniciado' : (defaultStatus || 'concluido');
        if (range > 0 && range <= 480) {
          input.value = `1-${range}`;
        }
        panel.querySelector('#bulkApplyBtn').dataset.pendingStatus = targetStatus;
        panel.querySelector('#bulkApplyBtn').textContent = type === 'unmark' ? 'Desmarcar hinos' : 'Marcar como concluídos';
      });
    });

    panel.querySelector('#bulkMarkAllBtn').addEventListener('click', async () => {
      const confirmAll = window.confirm('Tem certeza que deseja marcar os 480 hinos como concluídos?');
      if (!confirmAll) return;
      await this.applyBulkHymnSelection(Array.from({ length: 480 }, (_, index) => index + 1), defaultStatus);
      close();
    });

    panel.querySelector('#bulkUnmarkAllBtn').addEventListener('click', async () => {
      const confirmClear = window.confirm('Tem certeza que deseja desmarcar todos os 480 hinos?');
      if (!confirmClear) return;
      await this.applyBulkHymnSelection(Array.from({ length: 480 }, (_, index) => index + 1), 'nao_iniciado');
      close();
    });

    panel.querySelector('#bulkApplyBtn').addEventListener('click', async () => {
      const rawSelection = panel.querySelector('#hymnBulkInput').value;
      const numbers = this.parseHymnSelection(rawSelection);
      if (!numbers.length) {
        alert('Informe pelo menos um número ou intervalo válido. Exemplo: 1, 5, 10-20');
        return;
      }
      const pendingStatus = panel.querySelector('#bulkApplyBtn').dataset.pendingStatus || (defaultStatus || 'concluido');
      await this.applyBulkHymnSelection(numbers, pendingStatus);
      close();
    });
  },

  async applyBulkHymnSelection(numbers, status) {
    const uniqueNumbers = [...new Set((numbers || []).map(Number).filter((n) => Number.isInteger(n) && n >= 1 && n <= 480))];
    if (!uniqueNumbers.length) return;

    try {
      const response = await fetch('/api/study/hinario/bulk-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          kind: 'hymn',
          status,
          ids: uniqueNumbers,
          all: false,
          selection: uniqueNumbers.join(',')
        })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao marcar hinos por número:', error);
      this.showError('Não foi possível atualizar os hinos selecionados.');
    }
  },

  async searchHymns(query) {
    this.hinarioState.searchQuery = (query || '').trim().toLowerCase();
    this.renderHinarioLists();
  },

  async loadMoreHymns() {
    return;
  },

  async markHymnStatus(hymnId, status) {
    const hymnNumber = Number(String(hymnId).replace('hymn_', ''));
    try {
      const response = await fetch(`/api/study/progress/hymn/${hymnNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status, stars: 0 })
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao atualizar hino:', error);
    }
  },

  async markChorusStatus(chorusId, status) {
    const chorusNumber = Number(String(chorusId).replace('chorus_', ''));
    try {
      const response = await fetch(`/api/study/progress/chorus/${chorusNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status, stars: 0 })
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao atualizar coro:', error);
    }
  },

  async updateHymnDifficulty(hymnId, difficulty) {
    const hymnNumber = Number(String(hymnId).replace('hymn_', ''));
    try {
      await fetch(`/api/study/progress/hymn/${hymnNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status: 'em_andamento', difficulty })
      });
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao atualizar dificuldade do hino:', error);
    }
  },

  async updateChorusDifficulty(chorusId, difficulty) {
    const chorusNumber = Number(String(chorusId).replace('chorus_', ''));
    try {
      await fetch(`/api/study/progress/chorus/${chorusNumber}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status: 'em_andamento', difficulty })
      });
      delete this.structureCache['hinario'];
      this.loadArea('hinario');
    } catch (error) {
      console.error('Erro ao atualizar dificuldade do coro:', error);
    }
  },

  setStars(element, count) {
    console.log(`⭐ ${count} estrelas`);
  },

  // ==================== PDF ====================

  openPDF(area) {
    const areaLabel = area === 'teoria' ? 'Teoria' : area === 'metodo' ? 'Método' : 'Hinário';
    console.log(`📄 Abrindo PDF: ${areaLabel}`);

    const container = document.getElementById('studyContainer');
    const pdfContainer = container?.querySelector('.pdf-viewer-container');
    
    if (pdfContainer) {
      pdfContainer.style.display = pdfContainer.style.display === 'none' ? 'block' : 'none';
    }
  },

  openOfficialMethodPDF(instrument) {
    const url = `/api/study/pdf/metodo?instrument=${encodeURIComponent(instrument || this.currentInstrument || 'teclado')}`;
    this.openPDFModal(`Método Oficial`, url);
  },

  async uploadCustomMethod(instrument, forceReplace = false) {
    const fileInput = document.getElementById('customMethodFileInput');
    const file = fileInput && fileInput.files && fileInput.files[0];
    const maxSizeMB = 50;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;

    if (!file) {
      alert('Selecione um arquivo PDF antes de anexar.');
      return;
    }
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      alert('Apenas arquivos PDF sao permitidos.');
      return;
    }
    if (file.size > maxSizeBytes) {
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
      alert(`Este arquivo possui ${fileSizeMB} MB e ultrapassa o limite de ${maxSizeMB} MB.`);
      return;
    }

    const payload = new FormData();
    payload.append('instrument', instrument || this.currentInstrument || 'teclado');
    payload.append('file', file);

    try {
      const response = await fetch('/api/instruments/method', {
        method: 'POST',
        credentials: 'include',
        body: payload
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || 'Nao foi possivel salvar o PDF do metodo.');
      }
      alert('Metodo personalizado salvo com sucesso.');
      delete this.structureCache['metodo'];
      this.loadArea('metodo');
    } catch (error) {
      console.error('Erro ao enviar metodo personalizado:', error);
      alert(error.message || 'Erro ao anexar o metodo.');
    }
  },

  async removeCustomMethod(instrument) {
    const confirmed = window.confirm('Deseja remover o método personalizado deste instrumento?');
    if (!confirmed) return;

    try {
      const response = await fetch(`/api/instruments/method?instrument=${encodeURIComponent(instrument || this.currentInstrument || 'teclado')}`, {
        method: 'DELETE',
        credentials: 'include'
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(data.error || 'Não foi possível remover o método personalizado.');
      }
      delete this.structureCache['metodo'];
      this.loadArea('metodo');
    } catch (error) {
      console.error('Erro ao remover método personalizado:', error);
      alert(error.message || 'Erro ao remover o método.');
    }
  },

  openHymnPDF(hymnNumber) {
    const url = `/api/study/pdf/hymn/${hymnNumber}`;
    fetch(url, { credentials: 'include' })
      .then((response) => {
        if (!response.ok) {
          return response.json().then((data) => {
            throw new Error(data.message || data.error || 'Partitura não disponível para este instrumento.');
          });
        }
        this.openPDFModal(`Hino ${String(hymnNumber).padStart(3, '0')}`, url);
      })
      .catch((error) => {
        console.error('Erro ao abrir partitura do hino:', error);
        alert(error.message || 'Partitura não disponível para este instrumento.');
      });
  },

  openChorusPDF(chorusNumber) {
    const url = `/api/study/pdf/chorus/${chorusNumber}`;
    this.openPDFModal(`Coro ${chorusNumber}`, url);
  },

  openPDFModal(title, pdfUrl) {
    const modal = document.createElement('div');
    modal.className = 'pdf-modal';
    modal.id = 'pdfModal';
    
    const html = `
      <div class="pdf-modal-content">
        <div class="pdf-header">
          <h3>${title}</h3>
          <div class="pdf-controls">
            <button class="pdf-btn" onclick="document.getElementById('pdfModal').remove()" title="Fechar (ESC)">✕</button>
            <button class="pdf-btn" onclick="window.open('${pdfUrl}', '_blank')" title="Abrir em nova aba">🔗</button>
          </div>
        </div>
        <div class="pdf-container">
          <iframe 
            id="pdfEmbed"
            src="${pdfUrl}#toolbar=1&navpanes=1&scrollbar=1" 
            style="width: 100%; height: 100%; border: none;">
          </iframe>
        </div>
      </div>
    `;
    
    modal.innerHTML = html;
    document.body.appendChild(modal);
    
    // Fecha ao clicar fora
    modal.addEventListener('click', (e) => {
      if (e.target === modal) modal.remove();
    });
    
    // Fecha com ESC
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && document.getElementById('pdfModal')) {
        document.getElementById('pdfModal').remove();
      }
    });
  },

  // ==================== PROGRESSO ====================

  async updateProgress(area, sectionId, status) {
    try {
      const response = await fetch(`/api/study/progress/${area}/${sectionId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ status })
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const result = await response.json();
      console.log(`✅ ${area}: ${sectionId} → ${status}`);

      if (result.xp_awarded > 0) {
        this.showNotification(`✅ ${status === 'concluido' ? 'Seção concluída!' : 'Progresso atualizado!'} +${result.xp_awarded} XP`);
      }

      // Recarrega para atualizar visual
      if (this.structureCache[area]) {
        delete this.structureCache[area];
      }
      this.loadArea(area);
    } catch (error) {
      console.error(`❌ Erro ao atualizar ${area}:`, error);
      this.showError(`Erro ao atualizar ${area}`);
    }
  },

  // ==================== UTIL ====================

  toggleAccordion(header) {
    const body = header.nextElementSibling;
    const icon = header.querySelector('.accordion-icon');

    if (!body || !icon) return;

    body.style.display = body.style.display === 'none' ? 'block' : 'none';
    icon.textContent = body.style.display === 'none' ? '▶' : '▼';
  },

  getInstrumentLabel(instrument) {
    const labels = {
      'teclado': '🎹 Teclado',
      'violao': '🎸 Violão',
      'guitarra': '🎻 Guitarra',
      'canto': '🎤 Canto'
    };
    return labels[instrument] || instrument;
  },

  showNotification(message) {
    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.textContent = message;
    notif.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #4caf50;
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(notif);

    setTimeout(() => {
      notif.style.opacity = '0';
      setTimeout(() => notif.remove(), 300);
    }, 2000);
  },

  showError(message) {
    const error = document.createElement('div');
    error.className = 'error-notification';
    error.textContent = message;
    error.style.cssText = `
      position: fixed;
      bottom: 20px;
      right: 20px;
      background: #f44336;
      color: white;
      padding: 12px 20px;
      border-radius: 4px;
      z-index: 9999;
      animation: slideIn 0.3s ease-out;
    `;
    document.body.appendChild(error);

    setTimeout(() => {
      error.style.opacity = '0';
      setTimeout(() => error.remove(), 300);
    }, 3000);
  }
};

// Exporta como global para compatibilidade
window.StudyAppV2 = StudyAppV2;
