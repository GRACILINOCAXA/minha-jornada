// ===== MSA API CLIENT =====
const MSA_API = {
  getSections: async (area, instrument = 'teklado') => {
    const url = `/api/msa/sections/${area}${instrument && area === 'metodo' ? `?instrument=${instrument}` : ''}`;
    const r = await fetch(url, { credentials: 'include' });
    if (r.ok) return r.json();
    throw new Error(`Erro ao carregar seções: ${r.statusText}`);
  },

  updateProgress: async (area, sectionId, status, data = {}) => {
    const payload = { status, ...data };
    const url = `/api/msa/progress/${area}/${sectionId}`;
    const r = await fetch(url, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(payload)
    });
    if (r.ok) return r.json();
    throw new Error(`Erro ao atualizar progresso: ${r.statusText}`);
  },

  openPdf: (area, instrument = null) => {
    const url = `/api/msa/pdf/${area}${instrument ? `?instrument=${instrument}` : ''}`;
    window.open(url, '_blank', 'noopener,noreferrer');
  }
};

// ===== MSA RENDERING =====

// Estado global para MSA
let msaCurrentArea = null;
let msaStructure = null;

async function loadMSAArea(area) {
  try {
    msaCurrentArea = area;
    const instrument = area === 'metodo' ? (settings.selectedInstrument || 'teclado') : null;
    msaStructure = await MSA_API.getSections(area, instrument);
    renderMSAContent(area);
  } catch (error) {
    console.error('Erro ao carregar MSA:', error);
    const container = document.getElementById('msaAreaContainer');
    if (container) container.innerHTML = `<div class="error">Erro ao carregar conteúdo: ${error.message}</div>`;
  }
}

function renderMSAContent(area) {
  const container = document.getElementById('msaAreaContainer');
  if (!container) return;

  if (area === 'hinario') {
    renderHinarioContent();
  } else if (area === 'metodo') {
    renderMetodoContent();
  } else {
    renderTeoriaContent();
  }
}

function renderTeoriaContent() {
  const container = document.getElementById('msaAreaContainer');
  const structure = msaStructure;
  
  const progressPercent = structure.total_progress || 0;
  const phases = structure.phases || [];

  let html = `
    <div class="msa-header">
      <h3>📖 Teoria</h3>
      <div class="progress"><div class="fill" style="width:${progressPercent}%"></div></div>
      <div style="font-size:12px;color:#666;margin-top:4px;">${progressPercent}% concluído</div>
    </div>
    <div class="msa-actions">
      <button class="btn primary" onclick="MSA_API.openPdf('teoria')">📄 Abrir PDF da Teoria</button>
    </div>
    <div class="msa-phases-container">
  `;

  phases.forEach((phase) => {
    const phaseId = `fase-teoria-${phase.phase}`;
    const sections = phase.sections || [];
    const completedSections = sections.filter((s) => {
      const userProgress = structure.user_progress[s.id];
      return userProgress && userProgress.status === 'concluido';
    }).length;
    
    const phaseProgress = Math.round((completedSections / Math.max(1, sections.length)) * 100);
    
    html += `
      <div class="accordion-phase">
        <div class="accordion-header" onclick="toggleMSAPhase('${phaseId}')">
          <span class="accordion-icon">▶</span>
          <strong>Fase ${phase.phase}:</strong> ${phase.name}
          <span style="margin-left:auto;font-size:12px;color:#666;">${completedSections}/${sections.length}</span>
        </div>
        <div class="accordion-body" id="${phaseId}" style="display:none;">
          ${sections.map((section) => {
            const userProgress = structure.user_progress[section.id] || {};
            const status = userProgress.status || 'nao_iniciado';
            const statusIcon = status === 'concluido' ? '✅' : (status === 'em_andamento' ? '▶️' : '🔒');
            
            return `
              <div class="section-item">
                <div style="flex:1;">
                  <div><strong>${statusIcon} ${section.name}</strong></div>
                  <div style="font-size:11px;color:#666;">Páginas ${section.start_page}-${section.end_page}</div>
                </div>
                <div class="section-actions">
                  <select onchange="updateMSAProgress('teoria', '${section.id}', this.value)" style="padding:4px;font-size:12px;">
                    <option value="nao_iniciado" ${status === 'nao_iniciado' ? 'selected' : ''}>🔒 Não iniciado</option>
                    <option value="em_andamento" ${status === 'em_andamento' ? 'selected' : ''}>▶️ Em andamento</option>
                    <option value="concluido" ${status === 'concluido' ? 'selected' : ''}>✅ Concluído</option>
                  </select>
                  <button class="btn mini" onclick="MSA_API.openPdf('teoria')">📄</button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  });

  html += `
    </div>
  `;

  container.innerHTML = html;
}

function renderMetodoContent() {
  const container = document.getElementById('msaAreaContainer');
  const structure = msaStructure;
  const instrument = structure.instrument || 'teclado';
  
  const progressPercent = structure.total_progress || 0;
  const phases = structure.phases || [];

  let html = `
    <div class="msa-header">
      <h3>🎼 Método — ${INSTRUMENT_NAMES[instrument] || instrument}</h3>
      <div class="progress"><div class="fill" style="width:${progressPercent}%"></div></div>
      <div style="font-size:12px;color:#666;margin-top:4px;">${progressPercent}% concluído</div>
    </div>
    <div class="msa-actions">
      <button class="btn primary" onclick="MSA_API.openPdf('metodo', '${instrument}')">📄 Abrir PDF do Método</button>
    </div>
    <div class="msa-phases-container">
  `;

  phases.forEach((phase) => {
    const phaseId = `fase-metodo-${phase.phase}`;
    const sections = phase.sections || [];
    const completedSections = sections.filter((s) => {
      const userProgress = structure.user_progress[s.id];
      return userProgress && userProgress.status === 'concluido';
    }).length;
    
    const phaseProgress = Math.round((completedSections / Math.max(1, sections.length)) * 100);
    
    html += `
      <div class="accordion-phase">
        <div class="accordion-header" onclick="toggleMSAPhase('${phaseId}')">
          <span class="accordion-icon">▶</span>
          <strong>Aula ${phase.phase}:</strong> ${phase.name}
          <span style="margin-left:auto;font-size:12px;color:#666;">${completedSections}/${sections.length}</span>
        </div>
        <div class="accordion-body" id="${phaseId}" style="display:none;">
          ${sections.map((section) => {
            const userProgress = structure.user_progress[section.id] || {};
            const status = userProgress.status || 'nao_iniciado';
            const statusIcon = status === 'concluido' ? '✅' : (status === 'em_andamento' ? '▶️' : '🔒');
            
            return `
              <div class="section-item">
                <div style="flex:1;">
                  <div><strong>${statusIcon} ${section.name}</strong></div>
                  <div style="font-size:11px;color:#666;">Páginas ${section.start_page}-${section.end_page}</div>
                </div>
                <div class="section-actions">
                  <select onchange="updateMSAProgress('metodo', '${section.id}', this.value, '${instrument}')" style="padding:4px;font-size:12px;">
                    <option value="nao_iniciado" ${status === 'nao_iniciado' ? 'selected' : ''}>🔒 Não iniciado</option>
                    <option value="em_andamento" ${status === 'em_andamento' ? 'selected' : ''}>▶️ Em andamento</option>
                    <option value="concluido" ${status === 'concluido' ? 'selected' : ''}>✅ Concluído</option>
                  </select>
                  <button class="btn mini" onclick="MSA_API.openPdf('metodo', '${instrument}')">📄</button>
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  });

  html += `
    </div>
  `;

  container.innerHTML = html;
}

function renderHinarioContent() {
  const container = document.getElementById('msaAreaContainer');
  const structure = msaStructure;
  const totalHymns = structure.total_hymns || 350;
  const userProgress = structure.user_hymn_progress || [];
  const completedHymns = userProgress.filter((h) => h.status === 'concluido').length;
  const progressPercent = Math.round((completedHymns / Math.max(1, totalHymns)) * 100);

  let html = `
    <div class="msa-header">
      <h3>🎵 Hinário</h3>
      <div class="progress"><div class="fill" style="width:${progressPercent}%"></div></div>
      <div style="font-size:12px;color:#666;margin-top:4px;">${completedHymns}/${totalHymns} hinos concluídos (${progressPercent}%)</div>
    </div>
    <div class="msa-actions">
      <button class="btn primary" onclick="MSA_API.openPdf('hinario')">📄 Abrir Hinário</button>
      <input type="text" id="hymnSearch" placeholder="Buscar hino..." style="padding:6px;border:1px solid #ddd;border-radius:4px;flex:1;max-width:200px;">
    </div>
    <div class="hymn-grid">
  `;

  // Mostrar hinos em grid (com lazy loading virtual para grandes listas)
  for (let i = 1; i <= totalHymns; i++) {
    const hymnProgress = userProgress.find((h) => h.hymn_number === i) || {};
    const status = hymnProgress.status || 'nao_iniciado';
    const statusIcon = status === 'concluido' ? '✅' : (status === 'em_andamento' ? '▶️' : '🔒');
    const stars = hymnProgress.stars || 0;
    const starDisplay = '⭐'.repeat(Math.min(stars, 5));

    html += `
      <div class="hymn-card" data-hymn="${i}" style="display:${i <= 20 ? 'flex' : 'none'};">
        <div>
          <div><strong>${statusIcon} Hino ${i}</strong></div>
          <div style="font-size:11px;color:#999;">${starDisplay}</div>
        </div>
        <select onchange="updateMSAProgress('hinario', 'hino_${i}', this.value, '', { hymn_name: 'Hino ${i}', stars: 0 })" style="padding:4px;font-size:10px;">
          <option value="nao_iniciado" ${status === 'nao_iniciado' ? 'selected' : ''}>🔒</option>
          <option value="em_andamento" ${status === 'em_andamento' ? 'selected' : ''}>▶️</option>
          <option value="concluido" ${status === 'concluido' ? 'selected' : ''}>✅</option>
        </select>
      </div>
    `;
  }

  html += `
    </div>
  `;

  container.innerHTML = html;
  
  // Adicionar busca de hinos
  const searchInput = document.getElementById('hymnSearch');
  if (searchInput) {
    searchInput.addEventListener('input', (e) => filterHymns(e.target.value));
  }
}

// Helpers
const INSTRUMENT_NAMES = {
  teclado: '🎹 Teclado',
  orgao_eletronico: '🪄 Órgão Eletrônico',
  violao: '🎸 Violão',
  guitarra: '🎻 Guitarra',
  baixo: '🎸 Baixo',
  violino: '🎻 Violino',
  viola: '🎻 Viola',
  violoncelo: '🎻 Violoncelo',
  flauta: '🪈 Flauta',
  oboe: '🪈 Oboé',
  oboe_damore: '🪈 Oboé d’Amore',
  corne_ingles: '🪈 Corne Inglês',
  fagote: '🪈 Fagote',
  clarinete: '🪈 Clarinete',
  saxofone_soprano: '🎷 Saxofone Soprano',
  saxofone_alto: '🎷 Saxofone Alto',
  saxofone_tenor: '🎷 Saxofone Tenor',
  saxofone_baritono: '🎷 Saxofone Barítono',
  trompete: '🎺 Trompete',
  trompa: '🎺 Trompa',
  trombone: '🎺 Trombone',
  baritono: '🎺 Barítono',
  eufonio: '🎺 Eufônio',
  tuba: '🎺 Tuba',
  canto: '🎤 Canto',
  bateria: '🥁 Bateria'
};

function toggleMSAPhase(phaseId) {
  const element = document.getElementById(phaseId);
  if (element) {
    const isHidden = element.style.display === 'none';
    element.style.display = isHidden ? 'block' : 'none';
    
    // Rotacionar ícone
    const header = element.previousElementSibling;
    if (header) {
      const icon = header.querySelector('.accordion-icon');
      if (icon) icon.textContent = isHidden ? '▼' : '▶';
    }
  }
}

async function updateMSAProgress(area, sectionId, status, instrument = '', extraData = {}) {
  try {
    const data = { status, instrument, ...extraData };
    await MSA_API.updateProgress(area, sectionId, status, data);
    
    // Re-render para atualizar visual
    await loadMSAArea(area);
  } catch (error) {
    alert(`Erro: ${error.message}`);
  }
}

function filterHymns(query) {
  const cards = document.querySelectorAll('.hymn-card');
  cards.forEach((card) => {
    const hymnNum = card.dataset.hymn;
    const matches = hymnNum.includes(query);
    card.style.display = matches ? 'flex' : 'none';
  });
}
