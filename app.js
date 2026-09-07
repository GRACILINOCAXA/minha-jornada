const STORAGE_KEYS = {
  PRAYERS: 'mj_prayers',
  PRAYER_HISTORY: 'mj_prayerHistory',
  STUDIES: 'mj_studies',
  SESSIONS: 'mj_sessions',
  GOALS: 'mj_goals',
  MUSIC: 'mj_music',
  SETTINGS: 'mj_settings',
  NOTES: 'mj_notes',
  GAMIFICATION: 'mj_gamification'
}

const LEVEL_NAMES = ['Iniciante', 'Básico', 'Intermediário', 'Avançado', 'Mestre']
const LEVEL_THRESHOLDS = [0, 120, 260, 470, 760, 1100]

const INSTRUMENT_CATALOG = {
  teclado: { label: '🎹 Teclado', tuning: 'C–B', clef: 'Clave de Sol / Do', hymnbook: 'Acompanhamento geral' },
  orgao_eletronico: { label: '🪄 Órgão Eletrônico', tuning: 'C–B', clef: 'Clave de Sol / Do', hymnbook: 'Acompanhamento geral' },
  violao: { label: '🎸 Violão', tuning: 'Mi–Si–Sol–Ré–La–Mi', clef: 'Clave de Sol', hymnbook: 'Acompanhamento' },
  guitarra: { label: '🎻 Guitarra', tuning: 'Mi–Si–Sol–Ré–La–Mi', clef: 'Clave de Sol', hymnbook: 'Acompanhamento' },
  baixo: { label: '🎸 Baixo', tuning: 'E–A–D–G', clef: 'Clave de Fá', hymnbook: 'Acompanhamento' },
  violino: { label: '🎻 Violino', tuning: 'G–D–A–E', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  viola: { label: '🎻 Viola', tuning: 'C–G–D–A', clef: 'Clave de Alto', hymnbook: 'Melodia' },
  violoncelo: { label: '🎻 Violoncelo', tuning: 'C–G–D–A', clef: 'Clave de Fá', hymnbook: 'Melodia / Harmonia' },
  flauta: { label: '🪈 Flauta', tuning: 'C–D–E–F–G–A–B', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  oboe: { label: '🪈 Oboé', tuning: 'A–E–B–F♯–C♯', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  oboe_damore: { label: '🪈 Oboé d’Amore', tuning: 'A–E–B–F♯–C♯', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  corne_ingles: { label: '🪈 Corne Inglês', tuning: 'F–C–G–D–A–E', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  fagote: { label: '🪈 Fagote', tuning: 'B♭–F–C–G–D–A', clef: 'Clave de Fá', hymnbook: 'Melodia / Harmonia' },
  clarinete: { label: '🪈 Clarinete', tuning: 'B♭–A–G–F–E–D–C', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  saxofone_soprano: { label: '🎷 Saxofone Soprano', tuning: 'B♭', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  saxofone_alto: { label: '🎷 Saxofone Alto', tuning: 'E♭', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  saxofone_tenor: { label: '🎷 Saxofone Tenor', tuning: 'B♭', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  saxofone_baritono: { label: '🎷 Saxofone Barítono', tuning: 'E♭', clef: 'Clave de Sol', hymnbook: 'Melodia / Harmonia' },
  trompete: { label: '🎺 Trompete', tuning: 'B♭', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  trompa: { label: '🎺 Trompa', tuning: 'F', clef: 'Clave de Sol', hymnbook: 'Melodia / Harmonia' },
  trombone: { label: '🎺 Trombone', tuning: 'B♭', clef: 'Clave de Fá', hymnbook: 'Harmonia' },
  baritono: { label: '🎺 Barítono', tuning: 'B♭', clef: 'Clave de Sol / Fá', hymnbook: 'Harmonia' },
  eufonio: { label: '🎺 Eufônio', tuning: 'B♭', clef: 'Clave de Sol / Fá', hymnbook: 'Harmonia' },
  tuba: { label: '🎺 Tuba', tuning: 'B♭ / E♭', clef: 'Clave de Fá', hymnbook: 'Harmonia' },
  canto: { label: '🎤 Canto', tuning: 'Ajuste vocal', clef: 'Clave de Sol', hymnbook: 'Melodia' },
  bateria: { label: '🥁 Bateria', tuning: 'Percussão', clef: 'Pauta rítmica', hymnbook: 'Ritmo / Acompanhamento' }
}

const INSTRUMENT_ORDER = Object.keys(INSTRUMENT_CATALOG)

const METHOD_LIBRARY = {
  teclado: [
    { number: 1, title: 'Posição e relaxamento', objective: 'Preparar a mão e desenvolver conforto.', exercise: 'Repita 10 exercícios de postura e alongamento.', xp: 25 },
    { number: 2, title: 'Escala inicial', objective: 'Executar a primeira sequência com precisão.', exercise: 'Pratique a escala em 4 tempos com metronomo.', xp: 25 },
    { number: 3, title: 'Acordes básicos', objective: 'Conectar pequenas sequências com fluidez.', exercise: 'Execute 5 acordes em sequência sem quebrar o ritmo.', xp: 25 },
    { number: 4, title: 'Frases musicais', objective: 'Criar frases com fraseado simples.', exercise: 'Repita a frase musical 3 vezes com variação.', xp: 25 },
    { number: 5, title: 'Interpretação', objective: 'Aplicar dinâmica e musicalidade.', exercise: 'Grave uma execução final e avalie precisão.', xp: 25 }
  ],
  violao: [
    { number: 1, title: 'Acorde inicial', objective: 'Sentir a postura e a mão direita.', exercise: 'Toque 5 acordes em sequência com boa sonoridade.', xp: 25 },
    { number: 2, title: 'Dedilhado simples', objective: 'Melhorar articulação e precisão.', exercise: 'Repetir o padrão 8 vezes sem erro.', xp: 25 },
    { number: 3, title: 'Matriz rítmica', objective: 'Integrar compasso e pulso.', exercise: 'Executar a matriz rítmica com metrônomo.', xp: 25 },
    { number: 4, title: 'Melodia acompanhada', objective: 'Ligar nota e acorde.', exercise: 'Tocar uma linha melódica com acompanhamento.', xp: 25 },
    { number: 5, title: 'Apresentação', objective: 'Entregar uma execução musical coesa.', exercise: 'Executar a peça final em 2 tomadas.', xp: 25 }
  ],
  guitarra: [
    { number: 1, title: 'Postura e dedos', objective: 'Equilibrar tensão e agilidade.', exercise: 'Repita os padrões de dedos 10 vezes sem tensão.', xp: 25 },
    { number: 2, title: 'Intervalos básicos', objective: 'Localizar notas com segurança.', exercise: 'Cante e toque as notas ao mesmo tempo.', xp: 25 },
    { number: 3, title: 'Progressões simples', objective: 'Organizar mudança de acordes.', exercise: 'Troque acordes sem perder o pulso.', xp: 25 },
    { number: 4, title: 'Tempo e fraseado', objective: 'Aprimorar legato e musicalidade.', exercise: 'Repetir duas frases em variações de dinâmica.', xp: 25 },
    { number: 5, title: 'Musicalidade completa', objective: 'Encerrar a lição com execução final.', exercise: 'Gravar uma execução final com foco em expressão.', xp: 25 }
  ],
  canto: [
    { number: 1, title: 'Respiração', objective: 'Controlar o ar e a estabilidade do peito.', exercise: 'Faça 10 ciclos de respiração com voz solta.', xp: 25 },
    { number: 2, title: 'Tom e altura', objective: 'Ajustar pitch com controle.', exercise: 'Repetir 5 notas e ajustá-las com atenção.', xp: 25 },
    { number: 3, title: 'Fraseado vocal', objective: 'Conectar ideias melódicas.', exercise: 'Entoar 2 frases mantendo clareza na emissão.', xp: 25 },
    { number: 4, title: 'Expressão', objective: 'Aplicar dinâmica e emocionalidade.', exercise: 'Repetir a música com diferentes nuances.', xp: 25 },
    { number: 5, title: 'Apresentação', objective: 'Realizar uma execução musical completa.', exercise: 'Cantar a peça inteira com foco na interpretação.', xp: 25 }
  ]
}

function normalizeInstrumentKey(value = 'teclado') {
  const raw = String(value || 'teclado').trim().toLowerCase()
  const normalized = raw.normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '')
  const aliases = {
    orgao: 'orgao_eletronico',
    orgao_eletronico: 'orgao_eletronico',
    orgao_electronico: 'orgao_eletronico',
    eufonio: 'eufonio',
    eufonio: 'eufonio',
    sax: 'saxofone_alto',
    saxofone: 'saxofone_alto',
    baixo_eletrico: 'baixo',
    baixo: 'baixo',
    piano: 'teclado',
    teclado: 'teclado',
    violao: 'violao',
    guitarra: 'guitarra',
    canto: 'canto',
    bateria: 'bateria'
  }
  return aliases[normalized] || (INSTRUMENT_CATALOG[normalized] ? normalized : 'teclado')
}

function getInstrumentLabel(value = 'teclado') {
  const key = normalizeInstrumentKey(value)
  return INSTRUMENT_CATALOG[key]?.label || INSTRUMENT_CATALOG.teclado.label
}

function buildInstrumentOptions(selectedValue = 'teclado') {
  const chosen = normalizeInstrumentKey(selectedValue)
  return INSTRUMENT_ORDER.map((key) => `
    <option value="${key}" ${key === chosen ? 'selected' : ''}>${INSTRUMENT_CATALOG[key].label}</option>
  `).join('')
}

const HYMN_LIBRARY = [
  { number: 1, title: 'Hino 1', difficulty: 'Iniciante', partitura: 'Partitura original', xp: 30 },
  { number: 2, title: 'Hino 2', difficulty: 'Básico', partitura: 'Partitura original', xp: 30 },
  { number: 3, title: 'Hino 3', difficulty: 'Médio', partitura: 'Partitura original', xp: 35 },
  { number: 4, title: 'Hino 4', difficulty: 'Médio', partitura: 'Partitura original', xp: 40 },
  { number: 5, title: 'Hino 5', difficulty: 'Avançado', partitura: 'Partitura original', xp: 45 }
]

function buildLessonsForInstrument(instrument = 'teclado') {
  return (METHOD_LIBRARY[instrument] || METHOD_LIBRARY.teclado).map((lesson, index) => ({
    id: `lesson-${instrument}-${lesson.number}`,
    number: lesson.number,
    title: lesson.title,
    objective: lesson.objective,
    exercise: lesson.exercise,
    status: index === 0 ? 'em_andamento' : 'bloqueado',
    xp: lesson.xp,
    bestResult: 0,
    attempts: 0,
    completedAt: null
  }))
}

function buildHymns() {
  return HYMN_LIBRARY.map((hymn) => ({
    id: `hymn-${hymn.number}`,
    number: hymn.number,
    title: hymn.title,
    partitura: hymn.partitura,
    difficulty: hymn.difficulty,
    xp: hymn.xp,
    status: 'conhecendo',
    stars: 1,
    lastUpdated: null
  }))
}

function defaultGamificationState() {
  return {
    xp: 0,
    streak: 0,
    totalExercises: 0,
    lessonsCompleted: 0,
    hymnsDominated: 0,
    selectedInstrument: 'teclado',
    lastStudyDate: null,
    lessons: buildLessonsForInstrument('teclado'),
    hymns: buildHymns()
  }
}

function getLevelInfo(xpValue = 0) {
  let level = 1
  let nextGoal = LEVEL_THRESHOLDS[1]
  let previousGoal = 0

  for (let i = 1; i < LEVEL_THRESHOLDS.length; i++) {
    if (xpValue >= LEVEL_THRESHOLDS[i]) {
      level = i
      previousGoal = LEVEL_THRESHOLDS[i - 1]
      nextGoal = LEVEL_THRESHOLDS[i + 1] || LEVEL_THRESHOLDS[LEVEL_THRESHOLDS.length - 1]
    }
  }

  const progressBase = nextGoal - previousGoal
  const progressValue = progressBase > 0 ? (xpValue - previousGoal) / progressBase * 100 : 100
  const capped = Math.min(100, Math.max(0, progressValue))

  return {
    level,
    name: LEVEL_NAMES[Math.min(level - 1, LEVEL_NAMES.length - 1)],
    xp: xpValue,
    current: previousGoal,
    next: nextGoal,
    progress: capped,
    xpNeeded: Math.max(0, nextGoal - xpValue)
  }
}

function getAchievements(state = gamification) {
  const lessonsDone = (state.lessons || []).filter((lesson) => lesson.status === 'concluido').length
  const hymnsDone = (state.hymns || []).filter((hymn) => hymn.status === 'dominado').length
  const achievements = [
    { id: 'first-exercise', label: '🎼 Primeiro exercício', unlocked: state.totalExercises >= 1 },
    { id: 'first-hymn', label: '🎵 Primeiro hino', unlocked: state.hymns.some((h) => h.status !== 'conhecendo') },
    { id: 'streak-7', label: '🔥 7 dias estudando', unlocked: state.streak >= 7 },
    { id: 'lessons-10', label: '📚 10 lições concluídas', unlocked: lessonsDone >= 10 },
    { id: 'hymns-25', label: '🎺 25 hinos estudados', unlocked: hymnsDone >= 25 },
    { id: 'first-level', label: '🏆 Primeiro nível completo', unlocked: getLevelInfo(state.xp).level >= 1 },
    { id: 'master', label: '👑 Mestre do Método', unlocked: getLevelInfo(state.xp).level >= 5 }
  ]
  return achievements
}

async function persistGamification() {
  save(STORAGE_KEYS.GAMIFICATION, gamification)
  try {
    if (API && API.gamification) {
      await API.gamification.update(gamification)
    }
  } catch (error) {
    console.warn('Não foi possível salvar gamificação no backend:', error)
  }
}

function saveGamification() {
  persistGamification()
}

function ensureGamificationState() {
  const stored = load(STORAGE_KEYS.GAMIFICATION, null)
  if (!stored) return defaultGamificationState()

  const normalized = { ...defaultGamificationState(), ...stored }
  normalized.selectedInstrument = normalizeInstrumentKey(stored.selectedInstrument || 'teclado')
  normalized.lessons = stored.lessons && stored.lessons.length ? stored.lessons : buildLessonsForInstrument(normalized.selectedInstrument)
  normalized.hymns = stored.hymns && stored.hymns.length ? stored.hymns : buildHymns()
  return normalized
}

async function applySelectedInstrument(nextInstrument, options = {}) {
  const { syncStudyUI = true, shouldPersist = true } = options
  const key = normalizeInstrumentKey(nextInstrument)

  settings.selectedInstrument = key
  gamification.selectedInstrument = key
  gamification.lessons = buildLessonsForInstrument(key)

  const selects = [
    document.getElementById('instrumentSelect'),
    document.getElementById('selectedInstrument')
  ].filter(Boolean)

  selects.forEach((select) => {
    if (Array.from(select.options).some((option) => option.value === key)) {
      select.value = key
    }
  })

  if (shouldPersist) {
    save(STORAGE_KEYS.SETTINGS, settings)
    saveGamification()

    try {
      if (typeof API !== 'undefined' && API && typeof API.request === 'function') {
        await API.request('/instruments/select', 'POST', { instrumento: key })

        const freshUser = await API.auth.getCurrentUser().catch(() => null)
        if (freshUser) {
          currentUser = freshUser
          if (typeof window !== 'undefined') window.currentUser = freshUser
        }
      }
    } catch (error) {
      console.error('Erro ao sincronizar instrumento no backend:', error)
    }
  }

  if (syncStudyUI) {
    const refreshStudyArea = (studyApp) => {
      if (!studyApp || typeof studyApp.loadArea !== 'function') return

      studyApp.currentInstrument = key
      studyApp.structureCache = {}

      if (studyApp.currentArea) {
        studyApp.loadArea(studyApp.currentArea)
      }
    }

    refreshStudyArea(StudyAppV2)
    refreshStudyArea(StudyApp)
  }

  renderMusic()
  renderProgress()
}

function updateDailyStreak() {
  // NOTA: Esta função é mantida para compatibilidade, mas o cálculo real é feito no backend
  // via calculate_current_streak() que analisa o histórico completo de atividades.
  // Não use esta função para cálculos críticos.
  const today = todayISO()
  if (!gamification.lastStudyDate) {
    gamification.lastStudyDate = today
  } else {
    gamification.lastStudyDate = today
  }
}

async function recalculateStreakFromBackend() {
  /**
   * Força o recalculo da sequência no backend baseado no histórico real de atividades.
   * Chamada sempre que há conclusão de atividades.
   */
  try {
    const result = await API.gamification.recalculateStreak()
    if (result && typeof result.streak === 'number') {
      gamification.streak = result.streak
      console.log(`✓ Sequência recalculada: ${result.streak}d`)
      save(STORAGE_KEYS.GAMIFICATION, gamification)
      renderProgress()
      renderDashboard()
    }
  } catch (error) {
    console.warn('Não foi possível recalcular sequência:', error)
  }
}

function awardXp(amount, reason = 'estudo') {
  gamification.xp += amount
  updateDailyStreak()  // Mantém lastStudyDate atualizado
  recalculateStreakFromBackend()  // Recalcula o streak real baseado no histórico
  saveGamification()
  renderMusic();
  renderProgress();
  renderDashboard();
  console.log(`+${amount} XP por ${reason}`)
}

function unlockNextLesson() {
  const currentLessons = gamification.lessons || []
  for (let i = 0; i < currentLessons.length; i++) {
    if (currentLessons[i].status === 'em_andamento') {
      currentLessons[i].status = 'concluido'
      currentLessons[i].completedAt = todayISO()
      break
    }
  }

  for (let i = 0; i < currentLessons.length; i++) {
    if (currentLessons[i].status === 'bloqueado') {
      const previous = currentLessons[i - 1]
      if (!previous || previous.status === 'concluido') {
        currentLessons[i].status = 'em_andamento'
        break
      }
    }
  }

  gamification.lessonsCompleted = currentLessons.filter((lesson) => lesson.status === 'concluido').length
  saveGamification()
}

function completeExercise(lessonId) {
  const lesson = (gamification.lessons || []).find((item) => item.id === lessonId)
  if (!lesson || lesson.status === 'concluido') return

  lesson.attempts += 1
  lesson.bestResult = Math.max(lesson.bestResult, 90)
  gamification.totalExercises += 1
  awardXp(10, 'exercício concluído')
  if (lesson.status === 'bloqueado') lesson.status = 'em_andamento'
  saveGamification()
}

function completeLesson(lessonId) {
  const lesson = (gamification.lessons || []).find((item) => item.id === lessonId)
  if (!lesson) return

  lesson.attempts += 1
  lesson.bestResult = Math.max(lesson.bestResult, 100)
  lesson.status = 'concluido'
  lesson.completedAt = todayISO()
  lesson.xp = 25
  gamification.lessonsCompleted += 1
  awardXp(25, 'lição concluída')
  unlockNextLesson()
  saveGamification()
}

function advanceHymnStatus(hymnId, nextStatus) {
  const hymn = (gamification.hymns || []).find((item) => item.id === hymnId)
  if (!hymn) return

  const statusMap = {
    conhecendo: { stars: 1, xp: 30 },
    praticando: { stars: 2, xp: 30 },
    dominado: { stars: 3, xp: 50 },
    excelente: { stars: 4, xp: 60 },
    perfeito: { stars: 5, xp: 80 }
  }

  const status = statusMap[nextStatus] || statusMap.conhecendo
  hymn.status = nextStatus
  hymn.stars = status.stars
  hymn.lastUpdated = todayISO()

  if (nextStatus === 'dominado' || nextStatus === 'excelente' || nextStatus === 'perfeito') {
    awardXp(status.xp, 'hino concluído')
  }

  if (nextStatus === 'dominado') {
    gamification.hymnsDominated = (gamification.hymns || []).filter((item) => item.status === 'dominado' || item.status === 'excelente' || item.status === 'perfeito').length
  }

  saveGamification()
  renderMusic();
  renderProgress();
}

function getLevelToRender() {
  return getLevelInfo(gamification.xp)
}

function getAreaProgress(areaId) {
  const lessons = gamification.lessons || []
  const hymns = gamification.hymns || []

  if (areaId === 'hinaro') {
    if (!hymns.length) return 0
    const completed = hymns.filter((item) => ['dominado', 'excelente', 'perfeito'].includes(item.status)).length
    return Math.round((completed / hymns.length) * 100)
  }

  if (!lessons.length) return 0
  const completed = lessons.filter((item) => item.status === 'concluido').length
  return Math.round((completed / lessons.length) * 100)
}

function getStudyAreaItems(areaId) {
  const instrument = gamification.selectedInstrument || settings.selectedInstrument || 'teclado'

  if (areaId === 'hinaro') {
    return (gamification.hymns || buildHymns()).map((hymn) => ({
      id: hymn.id,
      number: hymn.number,
      title: hymn.title,
      subtitle: hymn.difficulty,
      status: hymn.status,
      type: 'hymn'
    }))
  }

  return (gamification.lessons || buildLessonsForInstrument(instrument)).map((lesson) => ({
    id: lesson.id,
    number: lesson.number,
    title: lesson.title,
    subtitle: lesson.objective || 'Estudo do método',
    status: lesson.status,
    type: 'lesson'
  }))
}

function getStatusLabel(status) {
  if (status === 'concluido') return '✅ Concluído'
  if (status === 'em_andamento') return '▶️ Em andamento'
  if (status === 'dominado' || status === 'excelente' || status === 'perfeito') return '✅ Concluído'
  if (status === 'praticando') return '▶️ Em andamento'
  return '🔒 Não iniciado'
}

function getStatusClass(status) {
  if (status === 'concluido' || status === 'dominado' || status === 'excelente' || status === 'perfeito') return 'completed'
  if (status === 'em_andamento' || status === 'praticando') return 'in_progress'
  return 'locked'
}

function resolveStudyPdfUrl(sectionKey) {
  const normalizedKey = sectionKey === 'hinaro' ? 'hinario' : sectionKey === 'msa' ? 'teoria' : sectionKey
  const userInstrument = (currentUser && currentUser.instrumento) || null
  const candidates = {
    teoria: ['/api/study/pdf/teoria', '/MSA.pdf', '/docs/teoria.pdf', '/docs/msa-teoria.pdf'],
    metodo: userInstrument ? [`/api/study/pdf/metodo?instrument=${encodeURIComponent(userInstrument)}`] : [],
    hinario: ['/api/study/pdf/hinario', '/hnaro.pdf', '/docs/hinario.pdf', '/docs/msa-hinario.pdf']
  }[normalizedKey] || []

  for (const candidate of candidates) {
    const url = candidate.startsWith('/') ? candidate : `/${candidate}`
    try {
      const xhr = new XMLHttpRequest()
      xhr.open('HEAD', url, false)
      xhr.send()
      if (xhr.status >= 200 && xhr.status < 400) return url
    } catch (error) {
      // ignora candidato sem arquivo real
    }
  }
  return null
}

function openStudyDocument(sectionKey) {
  const url = resolveStudyPdfUrl(sectionKey)
  if (url) {
    window.open(url, '_blank', 'noopener,noreferrer')
    return
  }
  alert('Nenhum PDF real foi encontrado no projeto para esta seção. O material continua disponível no MSA e o progresso será salvo por usuário.')
}

function markStudyItemComplete(sectionKey, itemId, itemType) {
  if (itemType === 'lesson') {
    const lesson = (gamification.lessons || []).find((item) => item.id === itemId)
    if (!lesson) return
    lesson.status = 'concluido'
    lesson.completedAt = todayISO()
    lesson.attempts += 1
    lesson.bestResult = Math.max(lesson.bestResult || 0, 100)
    gamification.lessonsCompleted = (gamification.lessons || []).filter((item) => item.status === 'concluido').length
    awardXp(25, 'lição concluída')
    unlockNextLesson()
  }

  if (itemType === 'hymn') {
    const hymn = (gamification.hymns || []).find((item) => item.id === itemId)
    if (!hymn) return
    hymn.status = 'dominado'
    hymn.stars = 3
    hymn.lastUpdated = todayISO()
    awardXp(hymn.xp || 30, 'hino concluído')
  }

  saveGamification()
  renderMusic()
  renderProgress()
  if (currentAreaId) renderMusicArea(currentAreaId)
}

function continueStudy() {
  const lessons = gamification.lessons || []
  const nextLesson = lessons.find((item) => item.status !== 'concluido')
  if (nextLesson) {
    showMusicArea('metodo')
    const target = document.querySelector(`[data-study-item-id="${nextLesson.id}"]`)
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  const nextHymn = (gamification.hymns || []).find((item) => !['dominado', 'excelente', 'perfeito'].includes(item.status))
  if (nextHymn) {
    showMusicArea('hinaro')
    const target = document.querySelector(`[data-study-item-id="${nextHymn.id}"]`)
    if (target) target.scrollIntoView({ behavior: 'smooth', block: 'center' })
    return
  }

  showMusicMain()
  alert('Você já concluiu o conteúdo disponível no MSA. Continue com revisão e prática.')
}

function renderGamificationPanel() {
  const panel = document.getElementById('gamificationPanel')
  if (!panel) return

  const level = getLevelInfo(gamification.xp)
  const totalProgress = Math.min(100, Math.round(((gamification.lessons || []).filter((lesson) => lesson.status === 'concluido').length + (gamification.hymns || []).filter((hymn) => ['dominado', 'excelente', 'perfeito'].includes(hymn.status)).length) / Math.max(1, (gamification.lessons || []).length + (gamification.hymns || []).length) * 100))

  const areaRows = [
    { key: 'teoria', label: '📖 Teoria', value: getAreaProgress('teoria') },
    { key: 'metodo', label: '🎼 Método', value: getAreaProgress('metodo') },
    { key: 'hinaro', label: '🎵 Hinário', value: getAreaProgress('hinaro') }
  ]

  panel.innerHTML = `
    <div class="gamification-card compact-panel">
      <div class="gamification-row">
        <div>
          <div class="mini-meta">🎵 MSA</div>
          <h4>Progresso geral: ${totalProgress}%</h4>
        </div>
        <span class="level-pill">Nível ${level.level}</span>
      </div>
      <div class="progress"><div class="fill" style="width:${totalProgress}%"></div></div>
      <div class="compact-area-grid">
        ${areaRows.map((row) => `
          <div class="compact-area-item">
            <span>${row.label}</span>
            <strong>${row.value}%</strong>
          </div>
        `).join('')}
      </div>
      <div class="gamification-summary compact-summary-row">
        <div class="summary-box"><strong>${gamification.xp}</strong><span>XP</span></div>
        <div class="summary-box"><strong>${level.level}</strong><span>Nível</span></div>
        <div class="summary-box"><strong>${gamification.streak}</strong><span>Sequência</span></div>
      </div>
      <div class="compact-actions">
        <button class="btn primary" data-action="continue-study">Continuar estudo</button>
      </div>
    </div>
  `

  const continueBtn = panel.querySelector('[data-action="continue-study"]')
  if (continueBtn) continueBtn.onclick = continueStudy
}

function renderProgress() {
  const progressEl = document.getElementById('progressDetails')
  if (!progressEl) return

  const stats = getLevelInfo(gamification.xp)
  const achievements = getAchievements(gamification)
  const completedLessons = (gamification.lessons || []).filter((lesson) => lesson.status === 'concluido').length
  const masteredHymns = (gamification.hymns || []).filter((hymn) => ['dominado', 'excelente', 'perfeito'].includes(hymn.status)).length

  progressEl.innerHTML = `
    <div class="gamification-card">
      <div class="gamification-row">
        <div>
          <div class="mini-meta">Painel geral MSA</div>
          <h3>Nível ${stats.level} · ${stats.name}</h3>
        </div>
        <span class="level-pill">${gamification.xp} XP</span>
      </div>
      <div class="progress"><div class="fill" style="width:${stats.progress}%"></div></div>
      <div class="mini-meta">XP atual: <strong>${gamification.xp}</strong> / necessário: <strong>${stats.next}</strong> · Próximo nível em <strong>${stats.xpNeeded}</strong> XP</div>
    </div>

    <div class="gamification-summary">
      <div class="summary-box"><strong>${gamification.streak}</strong><span>Sequência</span></div>
      <div class="summary-box"><strong>${completedLessons}</strong><span>Lições concluídas</span></div>
      <div class="summary-box"><strong>${masteredHymns}</strong><span>Hinos dominados</span></div>
    </div>

    <div class="achievement-list">
      ${achievements.map((item) => `
        <div class="achievement-item">
          <div>${item.unlocked ? '✅' : '⏳'} ${item.label}</div>
        </div>
      `).join('')}
    </div>
  `
}

/* ---------- User & Sync State ---------- */
let currentUser = null
let useBackend = false // Flag para usar backend quando autenticado

// Sincronizar dados do backend
async function syncDataFromBackend() {
  try {
    console.log('Sincronizando dados do backend...')
    
    const [prayersData, historyData, goalsData, musicData, settingsData, notesData, gamificationData, streakData] = await Promise.all([
      API.prayers.getAll().catch(() => null),
      API.prayers.getHistory().catch(() => null),
      API.goals.getAll().catch(() => null),
      API.music.getAll().catch(() => null),
      API.settings.get().catch(() => null),
      API.notes.getAll().catch(() => null),
      API.gamification.get().catch(() => null),
      API.gamification.getStreak().catch(() => null)  // Nova chamada para streak calculado
    ])
    
    // Atualizar variáveis globais com dados do backend
    if (prayersData && prayersData.prayers) {
      prayers = prayersData.prayers
      save(STORAGE_KEYS.PRAYERS, prayers)
    }
    
    if (historyData && historyData.history) {
      prayerHistory = historyData.history
      save(STORAGE_KEYS.PRAYER_HISTORY, prayerHistory)
    }
    
    if (goalsData && goalsData.goals) {
      goals = goalsData.goals
      save(STORAGE_KEYS.GOALS, goals)
    }
    
    if (musicData && musicData.studies) {
      // Transformar array de estudos em estrutura MSA
      music = {
        msa: {
          id: 'msa-1',
          name: 'MSA',
          subareas: [
            {id:'teoria', name:'Teoria', progress:0, sessions:[]},
            {id:'metodo', name:'Método', progress:0, sessions:[]},
            {id:'instrumento', name:'Instrumento', progress:0, sessions:[]},
            {id:'hinaro', name:'Hinaro', progress:0, sessions:[]}
          ]
        }
      }
      
      // Agrupar estudos por área
      musicData.studies.forEach(study => {
        const area = music.msa.subareas.find(a => a.id === study.area)
        if (area) {
          area.sessions.push({
            id: study.id,
            date: study.study_date,
            minutes: study.duration,
            what: study.description,
            learned: study.learned,
            difficulties: study.notes,
            next: study.next_goal,
            notes: study.notes,
            progress: study.progress
          })
          area.progress = study.progress
        }
      })
      
      save(STORAGE_KEYS.MUSIC, music)
    }
    
    if (settingsData && settingsData.settings) {
      const backendInstrument = (currentUser && currentUser.instrumento) || settingsData.settings.selected_instrument || settings.selectedInstrument || 'teclado';
      settings = {
        enableNotifications: settingsData.settings.notifications_enabled,
        dailyGoalStudy: settingsData.settings.daily_study_goal,
        theme: settingsData.settings.theme,
        selectedInstrument: backendInstrument
      }
      save(STORAGE_KEYS.SETTINGS, settings)
    }

    if (gamificationData) {
      const backendInstrument = (currentUser && currentUser.instrumento) || settings.selectedInstrument || gamificationData.selected_instrument || 'teclado';
      const nextState = {
        ...defaultGamificationState(),
        ...gamificationData,
        lessons: Array.isArray(gamificationData.lessons) && gamificationData.lessons.length ? gamificationData.lessons : buildLessonsForInstrument(backendInstrument),
        hymns: Array.isArray(gamificationData.hymns) && gamificationData.hymns.length ? gamificationData.hymns : buildHymns(),
        selectedInstrument: backendInstrument
      }
      gamification = nextState
      save(STORAGE_KEYS.GAMIFICATION, gamification)
    }
    
    // Atualizar streak com valor calculado corretamente do backend
    if (streakData && typeof streakData.streak === 'number') {
      gamification.streak = streakData.streak
      console.log(`✓ Sequência atualizada: ${streakData.streak}d`)
      save(STORAGE_KEYS.GAMIFICATION, gamification)
    }
    
    if (notesData && notesData.notes && notesData.notes.length > 0) {
      // Concatenar todas as notas em um texto
      notes = notesData.notes.map(n => `[${n.created_at}] ${n.title}\n${n.content}`).join('\n\n---\n\n')
      save(STORAGE_KEYS.NOTES, notes)
    }
    
    useBackend = true
    console.log('✓ Dados sincronizados do backend')
  } catch (error) {
    console.warn('Erro ao sincronizar backend, usando localStorage:', error)
    useBackend = false
  }
}

// Atualizar exibição do usuário no topbar
async function updateUserDisplay() {
  try {
    const user = await API.auth.getCurrentUser()
    currentUser = user
    const userDisplay = $('#userDisplay')
    if (userDisplay) {
      userDisplay.textContent = `👤 ${user.username}`
    }
  } catch (error) {
    console.error('Erro ao carregar usuário:', error)
  }
}


/* ---------- Utilities ---------- */
const $ = sel => document.querySelector(sel)
const $$ = sel => Array.from(document.querySelectorAll(sel))
const uid = () => Math.random().toString(36).slice(2,9)
const todayISO = d => (d||new Date()).toISOString().slice(0,10)

const load = (key, def)=>{
  try{const s=localStorage.getItem(key);return s?JSON.parse(s):def}catch(e){return def}
}
const save = (key,val)=>localStorage.setItem(key,JSON.stringify(val))

// helper: return existing element by selector or create using factory
function ensureElement(selector, factory){
  const el = document.querySelector(selector)
  if(el) return el
  return factory()
}

/* ---------- Data init ---------- */
let prayers = load(STORAGE_KEYS.PRAYERS, null)
if(!prayers){
  prayers = [
    {id:uid(),time:'07:00',title:'Oração da manhã',desc:'',enabled:true,lastNotified:''},
    {id:uid(),time:'12:00',title:'Oração da tarde',desc:'',enabled:true,lastNotified:''},
    {id:uid(),time:'20:00',title:'Oração da noite',desc:'',enabled:true,lastNotified:''}
  ]
  save(STORAGE_KEYS.PRAYERS,prayers)
}
let prayerHistory = load(STORAGE_KEYS.PRAYER_HISTORY,[])
let studies = load(STORAGE_KEYS.STUDIES,[])
let sessions = load(STORAGE_KEYS.SESSIONS,[])
let goals = load(STORAGE_KEYS.GOALS,[])
let settings = load(STORAGE_KEYS.SETTINGS,{enableNotifications:false,dailyGoalStudy:30,theme:'light',selectedInstrument:'teclado'})
let notes = load(STORAGE_KEYS.NOTES,'')
let gamification = ensureGamificationState()
if (settings.selectedInstrument) {
  gamification.selectedInstrument = settings.selectedInstrument
  gamification.lessons = buildLessonsForInstrument(gamification.selectedInstrument)
}

// music studies init
let music = load(STORAGE_KEYS.MUSIC, null)
if(!music){
  music = {
    msa: {
      id: uid(),
      name: 'MSA',
      subareas: [
        {id:'teoria', name:'Teoria', progress:0, sessions:[]},
        {id:'metodo', name:'Método', progress:0, sessions:[]},
        {id:'instrumento', name:'Instrumento', progress:0, sessions:[]},
        {id:'hinaro', name:'Hinaro', progress:0, sessions:[]}
      ]
    }
  }
  save(STORAGE_KEYS.MUSIC, music)
}

/* ---------- UI Navigation ---------- */
let currentAreaId = null  // Track current music area being viewed

function showView(id){
  $$('.view').forEach(v=>v.classList.remove('active'))
  const node = $('#'+id)
  if(node) node.classList.add('active')
  $$('.sidebar a').forEach(a=>a.classList.toggle('active', a.getAttribute('href')===('#'+id)))
  
  // Reset music view when changing sections
  if(id !== 'music') {
    currentAreaId = null
    showMusicMain()
  }
}
window.addEventListener('hashchange', ()=>{showView(location.hash.replace('#','')||'dashboard')})
showView(location.hash.replace('#','')||'dashboard')

/* ---------- Prayers UI ---------- */
function renderPrayers(){
  const list = $('#prayersList'); list.innerHTML=''
  prayers.forEach(p=>{
    const el = document.createElement('div');
    const completedToday = isPrayerCompletedToday(p.id)
    el.className='prayer-item '+(completedToday? 'completed':'')
    el.innerHTML = `<div class="left"><div class="time">${p.time}</div><div class="meta"><div class="title">${p.title}</div><div class="desc">${p.desc||''}</div></div></div><div class="right"></div>`
    const right = el.querySelector('.right')
    const complete = document.createElement('button'); complete.className='btn'; complete.textContent=completedToday? 'Desmarcar': 'Concluído ✓'
    complete.onclick = ()=>{ togglePrayerComplete(p.id) }
    const toggle = document.createElement('button'); toggle.className='btn'; toggle.textContent=p.enabled? 'Ativo':'Desativado'
    toggle.onclick = ()=>{p.enabled=!p.enabled; save(STORAGE_KEYS.PRAYERS,prayers); renderPrayers(); renderDashboard()}
    const last = document.createElement('div'); last.className='last-notified'; last.textContent = p.lastNotified? ('Notificado: '+p.lastNotified) : ''
    const edit = document.createElement('button'); edit.className='btn'; edit.textContent='Editar'; edit.onclick=()=>openPrayerModal(p.id)
    const del = document.createElement('button'); del.className='btn'; del.textContent='Excluir'; del.onclick=()=>openConfirmModal(p.id)
    right.appendChild(complete); right.appendChild(toggle); right.appendChild(edit); right.appendChild(del); right.appendChild(last)
    list.appendChild(el)
  })
}

// Modal-based add/edit prayer
function openPrayerModal(prayerId){
  const backdrop = ensureElement('.modal-backdrop#prayerModalBackdrop', createPrayerModal())
  const form = backdrop.querySelector('form')
  form.reset()
  form.dataset.editId = ''
  if(prayerId){
    const p = prayers.find(x=>x.id===prayerId)
    if(p){
      form.dataset.editId = p.id
      form.querySelector('[name="title"]').value = p.title
      form.querySelector('[name="time"]').value = p.time
      form.querySelector('[name="desc"]').value = p.desc||''
      form.querySelector('[name="notify"]').checked = !!p.enabled
    }
  }
  backdrop.classList.add('active')
}

function closePrayerModal(){
  const b = document.querySelector('.modal-backdrop#prayerModalBackdrop')
  if(b) b.classList.remove('active')
}

function createPrayerModal(){
  let backdrop = document.createElement('div'); backdrop.className='modal-backdrop'; backdrop.id='prayerModalBackdrop'
  const modal = document.createElement('div'); modal.className='modal'
  modal.innerHTML = `
    <h3>Nova oração</h3>
    <form>
      <label>Nome da oração <input name="title" required></label>
      <div class="form-row"><div class="col"><label>Horário <input name="time" type="time" required></label></div><div class="col"><label>Notificar <input name="notify" type="checkbox"></label></div></div>
      <label>Descrição (opcional) <textarea name="desc" rows="3"></textarea></label>
      <div class="actions"><button type="button" class="btn" id="cancelPrayerBtn">Cancelar</button><button type="submit" class="btn primary" id="savePrayerBtn">Salvar oração</button></div>
    </form>`
  backdrop.appendChild(modal)
  document.body.appendChild(backdrop)
  // events
  backdrop.querySelector('#cancelPrayerBtn').addEventListener('click', closePrayerModal)
  backdrop.querySelector('form').addEventListener('submit', e=>{
    e.preventDefault(); savePrayerFromModal(e.target);
  })
  return backdrop
}

function savePrayerFromModal(form){
  const id = form.dataset.editId
  const title = form.querySelector('[name="title"]').value.trim()
  const time = form.querySelector('[name="time"]').value
  const desc = form.querySelector('[name="desc"]').value.trim()
  const notify = form.querySelector('[name="notify"]').checked
  if(!title || !time){
    // simple validation UI
    alert('Por favor preencha nome e horário.')
    return
  }
  if(id){
    const p = prayers.find(x=>x.id===id)
    if(p){ p.title=title; p.time=time; p.desc=desc; p.enabled = !!notify }
  } else {
    prayers.push({id:uid(), time, title, desc, enabled: !!notify, lastNotified: ''})
  }
  save(STORAGE_KEYS.PRAYERS,prayers); closePrayerModal(); refreshAllFull()
}

// Confirm delete modal
function openConfirmModal(prayerId){
  let backdrop = document.querySelector('.modal-backdrop#confirmModalBackdrop') || createConfirmModal()
  backdrop.dataset.deleteId = prayerId
  backdrop.classList.add('active')
}

function closeConfirmModal(){
  const b = document.querySelector('.modal-backdrop#confirmModalBackdrop')
  if(b) b.classList.remove('active')
}

function createConfirmModal(){
  const backdrop = document.createElement('div'); backdrop.className='modal-backdrop'; backdrop.id='confirmModalBackdrop'
  const modal = document.createElement('div'); modal.className='modal'
  modal.innerHTML = `<h3>Excluir oração</h3><div>Deseja realmente excluir esta oração?</div><div class="actions"><button id="cancelDeleteBtn" class="btn">Cancelar</button><button id="confirmDeleteBtn" class="btn primary">Excluir</button></div>`
  backdrop.appendChild(modal); document.body.appendChild(backdrop)
  backdrop.querySelector('#cancelDeleteBtn').addEventListener('click', closeConfirmModal)
  backdrop.querySelector('#confirmDeleteBtn').addEventListener('click', ()=>{
    const id = backdrop.dataset.deleteId
    if(id){
      // remove prayer and related history entries
      prayers = prayers.filter(x=>x.id!==id)
      prayerHistory = prayerHistory.filter(h=>h.prayerId!==id)
      save(STORAGE_KEYS.PRAYERS,prayers); save(STORAGE_KEYS.PRAYER_HISTORY,prayerHistory)
      refreshAllFull();
    }
    closeConfirmModal()
  })
  return backdrop
}

function isPrayerCompletedToday(prayerId){
  const today = todayISO()
  return prayerHistory.some(h=>h.prayerId===prayerId && h.date===today)
}

function togglePrayerComplete(id){
  const today = todayISO()
  const exists = prayerHistory.findIndex(h=>h.prayerId===id && h.date===today)
  if(exists>=0){
    // remove completion entries for today for that prayer
    prayerHistory = prayerHistory.filter(h=>!(h.prayerId===id && h.date===today))
  } else {
    const now = new Date()
    prayerHistory.push({id:uid(),prayerId:id,date: today, time: now.toTimeString().slice(0,5)})
  }
  save(STORAGE_KEYS.PRAYER_HISTORY, prayerHistory)
  renderPrayerHistory(); renderPrayers(); renderDashboard()
}

function renderPrayerHistory(){
  const el = $('#prayerHistory'); el.innerHTML=''
  // group by date
  const grouped = {}
  prayerHistory.forEach(h=>{ grouped[h.date]=grouped[h.date]||[]; grouped[h.date].push(h) })
  const dates = Object.keys(grouped).sort((a,b)=>b.localeCompare(a))
  dates.forEach(date=>{
    const section = document.createElement('div'); const hd = document.createElement('h4'); hd.textContent = date; section.appendChild(hd)
    grouped[date].forEach(h=>{
      const p = prayers.find(x=>x.id===h.prayerId) || {title:'(removido)'}
      const row = document.createElement('div'); row.textContent = `🙏 ${p.title} — ${h.time}`
      section.appendChild(row)
    })
    el.appendChild(section)
  })
}

/* ---------- Music / MSA UI ---------- */
function calcMSAOverall(){
  const msa = music.msa
  const subs = msa.subareas
  if(!subs.length) return 0
  const sum = subs.reduce((s,a)=>s + Number(a.progress||0),0)
  return Math.round(sum/subs.length)
}

function calcMSAStats(){
  const msa = music.msa
  let totalTime = 0
  let totalSessions = 0
  let nextGoal = '—'
  
  msa.subareas.forEach(area => {
    totalSessions += area.sessions.length
    area.sessions.forEach(s => {
      totalTime += Number(s.minutes || 0)
    })
    if(!nextGoal || nextGoal === '—') {
      const lastSession = area.sessions[area.sessions.length - 1]
      if(lastSession && lastSession.next) {
        nextGoal = `[${area.name}] ${lastSession.next}`
      }
    }
  })
  
  const hours = Math.floor(totalTime / 60)
  const mins = totalTime % 60
  
  return { totalTime: `${hours}h ${mins}m`, totalSessions, nextGoal }
}

function showMusicMain(){
  currentAreaId = null
  $('#musicMainView').style.display = 'block'
  $('#musicAreaView').style.display = 'none'
  $('#musicBackBtn').style.display = 'none'
  $('#musicTitle').textContent = '🎵 Estudo Musical'
  renderMusic()
}

function showMusicArea(areaId){
  currentAreaId = areaId
  $('#musicMainView').style.display = 'none'
  $('#musicAreaView').style.display = 'block'
  $('#musicBackBtn').style.display = 'block'
  
  const normalizedArea = (areaId === 'hinaro' ? 'hinario' : areaId === 'msa' ? 'teoria' : areaId)
  const areaNames = { teoria: '📖 Teoria', metodo: '🎼 Método', hinario: '🎵 Hinário' }
  $('#musicTitle').textContent = areaNames[normalizedArea] || areaId

  StudyApp.loadArea(normalizedArea)
}

function renderMusic(){
  renderGamificationPanel()

  const areas = [
    { id: 'teoria', label: '📖 Teoria' },
    { id: 'metodo', label: '🎼 Método' },
    { id: 'hinario', label: '🎵 Hinário' }
  ]

  areas.forEach(({ id }) => {
    const card = document.getElementById('area-' + id) || document.querySelector(`[data-study-area="${id}"]`)
    const fill = document.getElementById('progress-' + id)
    const label = document.getElementById('progress-text-' + id)
    const areaProgress = getAreaProgress(id)

    if (fill) fill.style.width = areaProgress + '%'
    if (label) label.textContent = `${areaProgress}% concluído`
    if (card) {
      card.style.cursor = 'pointer'
      card.setAttribute('data-study-area', id)
    }
  })

  const level = getLevelInfo(gamification.xp)
  const msaPct = calcMSAOverall()
  const today = todayISO()
  const prayerSummary = prayers.filter(p => p.enabled)
  const completedToday = prayerHistory.filter(h => h.date === today).length

  const instrumentName = getInstrumentLabel(settings.selectedInstrument || gamification.selectedInstrument || 'teclado')

  if ($('#summaryInstrument')) $('#summaryInstrument').textContent = instrumentName
  if ($('#musicInstrumentLabel')) $('#musicInstrumentLabel').textContent = instrumentName
  if ($('#summaryLevel')) $('#summaryLevel').textContent = String(level.level)
  if ($('#summaryXp')) $('#summaryXp').textContent = String(gamification.xp)
  if ($('#summaryMsaProgress')) $('#summaryMsaProgress').textContent = `${msaPct}%`
  if ($('#summaryStreak')) $('#summaryStreak').textContent = `${gamification.streak}d`
  if ($('#summaryPrayerCount')) $('#summaryPrayerCount').textContent = `${completedToday}/${prayerSummary.length}`

  const stats = calcMSAStats()
  if ($('#musicTotalTime')) $('#musicTotalTime').textContent = stats.totalTime
  if ($('#musicTotalSessions')) $('#musicTotalSessions').textContent = stats.totalSessions
  if ($('#musicNextGoal')) $('#musicNextGoal').textContent = stats.nextGoal
}

function renderMusicArea(areaId){
  const area = music.msa.subareas.find(a => a.id === areaId)
  if(!area) return

  const items = getStudyAreaItems(areaId)
  const listHtml = items.map((item) => `
    <div class="compact-study-row ${item.type}" data-study-item-id="${item.id}">
      <div class="compact-study-meta">
        <strong>${item.number || '#'} — ${item.title}</strong>
        <span>${item.subtitle || ''}</span>
      </div>
      <span class="badge ${getStatusClass(item.status)}">${getStatusLabel(item.status)}</span>
      <div class="compact-study-actions">
        <button class="btn mini-btn" data-open-pdf="${areaId}">Abrir PDF</button>
        <button class="btn mini-btn primary" data-complete-item="${item.id}" data-item-type="${item.type}">Marcar como concluído</button>
      </div>
    </div>
  `).join('')

  $('#areaProgress').querySelector('.fill').style.width = (area.progress || 0) + '%'
  $('#areaStats').innerHTML = `
    <div style="margin-top:10px;">
      <div><strong>Progresso:</strong> ${area.progress || 0}%</div>
      <div><strong>Sessões:</strong> ${area.sessions.length}</div>
      <div><strong>Tempo total:</strong> ${calculateAreaTime(area)}min</div>
    </div>
    <div class="compact-study-list" style="margin-top:18px;">${listHtml}</div>
  `

  $('#areaStats').querySelectorAll('[data-open-pdf]').forEach((button) => {
    button.onclick = () => openStudyDocument(areaId)
  })

  $('#areaStats').querySelectorAll('[data-complete-item]').forEach((button) => {
    button.onclick = () => markStudyItemComplete(areaId, button.dataset.completeItem, button.dataset.itemType)
  })

  $('#areaSessionDate').value = todayISO()
  $('#areaSessionProgress').value = area.progress || 0

  renderMusicAreaHistory(areaId)
}

function calculateAreaTime(area){
  return area.sessions.reduce((sum, s) => sum + Number(s.minutes || 0), 0)
}

function renderMusicAreaHistory(areaId){
  const area = music.msa.subareas.find(a => a.id === areaId)
  if(!area) return
  
  const histEl = $('#areaSessionsHistory')
  histEl.innerHTML = ''
  
  if(area.sessions.length === 0){
    histEl.innerHTML = '<div style="color:#999;">Nenhuma sessão registrada</div>'
    return
  }
  
  area.sessions.slice().reverse().forEach((s, idx) => {
    const div = document.createElement('div')
    div.style.cssText = 'border:1px solid #ddd;padding:10px;margin:10px 0;border-radius:5px;'
    div.innerHTML = `
      <div><strong>${s.date || todayISO()}</strong> — ${s.minutes}min</div>
      <div style="font-size:0.9em;color:#666;">
        ${s.what ? `<div>📝 Estudou: ${s.what}</div>` : ''}
        ${s.learned ? `<div>💡 Aprendeu: ${s.learned}</div>` : ''}
        ${s.difficulties ? `<div>⚠️ Dificuldades: ${s.difficulties}</div>` : ''}
        ${s.next ? `<div>🎯 Próximo: ${s.next}</div>` : ''}
      </div>
    `
    histEl.appendChild(div)
  })
}

function saveAreaSession(){
  if(!currentAreaId) return
  
  const area = music.msa.subareas.find(a => a.id === currentAreaId)
  if(!area) return
  
  const date = $('#areaSessionDate').value || todayISO()
  const minutes = Number($('#areaSessionTime').value || 0)
  const what = $('#areaSessionWhat').value || ''
  const learned = $('#areaSessionLearned').value || ''
  const difficulties = $('#areaSessionDifficulties').value || ''
  const next = $('#areaSessionNext').value || ''
  const notes = $('#areaSessionNotes').value || ''
  const progress = Number($('#areaSessionProgress').value || 0)
  
  if(minutes <= 0){
    alert('Digite um tempo válido')
    return
  }
  
  area.progress = progress
  area.sessions.push({
    id: uid(),
    date,
    minutes,
    what,
    learned,
    difficulties,
    next,
    notes
  })
  
  save(STORAGE_KEYS.MUSIC, music)
  renderMusicArea(currentAreaId)
  
  // Reset form
  document.getElementById('areaSessionsForm').reset()
  $('#areaSessionDate').value = todayISO()
  $('#areaSessionProgress').value = area.progress
  
  alert('Sessão registrada!')
}


/* ---------- Dashboard ---------- */
function renderDashboard(){
  // todays prayers
  const today = todayISO()
  const todaysPlanned = prayers.filter(p=>p.enabled)
  const completed = prayerHistory.filter(h=>h.date===today).map(h=>h.prayerId)
  const doneCount = todaysPlanned.filter(p=>completed.includes(p.id)).length
  const total = todaysPlanned.length
  const pct = total? Math.round(doneCount/total*100) : 0
  $('#todayPrayersList').innerHTML = ''
  todaysPlanned.forEach(p=>{
    const el = document.createElement('div'); el.className='prayer-item'
    const isDone = completed.includes(p.id)
    el.innerHTML = `<div class="left"><div class="time">${p.time}</div><div class="meta"><div class="title">${p.title}</div></div></div><div class="right"><div class="status">${isDone? '✓':'⏰'}</div></div>`
    $('#todayPrayersList').appendChild(el)
  })
  $('#todaySummary').textContent = `${doneCount}/${total} concluídos — ${pct}%`
  $('#todayProgressBar .fill').style.width = pct+'%'

  // summary top
  $('#summaryPrayers').textContent = `${doneCount}/${total}`

  // studies summary
  const totalTime = sessions.reduce((s,it)=>s+Number(it.minutes||0),0)
  const hours = Math.floor(totalTime/60); const mins = totalTime%60
  $('#summaryTime').textContent = `${hours}h ${mins}m`
  // MSA progress: average of all areas progress
  const msaPct = calcMSAOverall()
  $('#summaryMSA').textContent = msaPct+'%'

  const level = getLevelInfo(gamification.xp)
  $('#summaryStreak').textContent = `${gamification.streak} dias`
  $('#dailyGoal').innerHTML = `Instrumento ativo: <strong>${gamification.selectedInstrument}</strong> · Nível ${level.level} · ${level.name} · XP ${gamification.xp}`
}

/* ---------- Calendar ---------- */
function renderCalendar(){
  const root = $('#calendarRoot'); root.innerHTML=''
  const now = new Date(); const year = now.getFullYear(); const month = now.getMonth()
  const first = new Date(year,month,1); const startDay = first.getDay()
  const days = new Date(year,month+1,0).getDate()
  // pad
  for(let i=0;i<startDay;i++){ const d=document.createElement('div'); d.className='cal-day'; d.innerHTML=''; root.appendChild(d)}
  for(let d=1; d<=days; d++){
    const dateStr = new Date(year,month,d).toISOString().slice(0,10)
    const day = document.createElement('div'); day.className='cal-day'
    day.innerHTML = `<div class="day-num">${d}</div><div class="indicators"></div>`
    const ind = day.querySelector('.indicators')
    const hasPrayer = prayerHistory.some(h=>h.date===dateStr)
    // Check if any music area has session on this date
    const hasStudy = music.msa.subareas.some(a => a.sessions.some(s=>s.date===dateStr))
    if(hasPrayer){ const i=document.createElement('div'); i.className='indicator-prayer'; ind.appendChild(i)}
    if(hasStudy){ const i=document.createElement('div'); i.className='indicator-study'; ind.appendChild(i)}
    day.onclick = ()=>showDayDetails(dateStr)
    root.appendChild(day)
  }
}

function showDayDetails(dateStr){
  const el = $('#dayDetails'); el.innerHTML = `<h4>${dateStr}</h4>`
  const prayersDone = prayerHistory.filter(h=>h.date===dateStr)
  const pdiv = document.createElement('div'); pdiv.innerHTML = `<strong>Orações:</strong>`
  prayersDone.forEach(p=>{ const pr = prayers.find(x=>x.id===p.prayerId) || {title:'(removido)'}; const r=document.createElement('div'); r.textContent=`${p.time} — ${pr.title}`; pdiv.appendChild(r)})
  el.appendChild(pdiv)
  
  // Music sessions
  const sdiv = document.createElement('div'); sdiv.innerHTML = `<strong>Estudos MSA:</strong>`
  music.msa.subareas.forEach(area => {
    const areaSessions = area.sessions.filter(s=>s.date===dateStr)
    areaSessions.forEach(s=>{ const r=document.createElement('div'); r.textContent = `[${area.name}] ${s.minutes}min — ${s.what}`; sdiv.appendChild(r)})
  })
  el.appendChild(sdiv)
}

/* ---------- Goals ---------- */
function renderGoals(){
  const el = $('#goalsList'); el.innerHTML=''
  goals.forEach(g=>{
    const node = document.createElement('div'); node.className='card'; node.innerHTML = `<div><strong>${g.title}</strong><div class="progress"><div class="fill" style="width:${g.progress||0}%"></div></div><div>${g.progress||0}%</div></div>`
    el.appendChild(node)
  })
}

function addGoal(){
  const title = prompt('Título da meta')||'Meta'
  const g = {id:uid(),title,progress:0}
  goals.push(g); save(STORAGE_KEYS.GOALS,goals); renderGoals()
}

/* ---------- Settings / Export / Import ---------- */
function exportData(){
  const data = {prayers,prayerHistory,goals,music,settings,notes}
  const blob = new Blob([JSON.stringify(data, null, 2)],{type:'application/json'})
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href=url; a.download='minha_jornada_backup.json'; a.click(); URL.revokeObjectURL(url)
}

function importData(file){
  const reader = new FileReader(); reader.onload = e => {
    try{ const obj = JSON.parse(e.target.result)
      if(obj.prayers) {prayers=obj.prayers; save(STORAGE_KEYS.PRAYERS,prayers)}
      if(obj.prayerHistory){prayerHistory=obj.prayerHistory; save(STORAGE_KEYS.PRAYER_HISTORY,prayerHistory)}
      if(obj.goals){goals=obj.goals; save(STORAGE_KEYS.GOALS,goals)}
      if(obj.music){music=obj.music; save(STORAGE_KEYS.MUSIC,music)}
      if(obj.settings){settings=obj.settings; save(STORAGE_KEYS.SETTINGS,settings)}
      alert('Importação concluída')
      refreshAllFull()
    }catch(err){alert('Arquivo inválido')}
  }
  reader.readAsText(file)
}

/* ---------- Notifications and scheduling ---------- */
async function requestNotificationPermission(){
  if(!('Notification' in window)) return false
  const p = await Notification.requestPermission()
  return p==='granted'
}

function scheduleCheck(){
  // run immediately
  checkAndNotify()
}

function checkAndNotify(){
  // only proceed when notifications enabled in settings and browser permission granted
  if(!settings.enableNotifications) return
  if(!("Notification" in window)) return
  if(Notification.permission !== 'granted') return
  const now = new Date(); const cur = now.toTimeString().slice(0,5); const today = todayISO()
  prayers.filter(p=>p.enabled).forEach(p=>{
    if(p.time===cur){
      // avoid duplicate notifications for same prayer in same day using p.lastNotified
      if(p.lastNotified === today) return
      // send notification
      try{
        const n = new Notification('🙏 Momento de oração', {body: `Está na hora da sua ${p.title}`})
        // optionally handle click
        n.onclick = ()=> window.focus()
        // record last notified date per prayer
        p.lastNotified = today
        save(STORAGE_KEYS.PRAYERS, prayers)
        renderPrayers()
      }catch(e){console.warn('notification failed',e)}
    }
  })
}

/* ---------- Helpers & bootstrap ---------- */
function refreshAll(){ renderPrayers(); renderPrayerHistory(); renderDashboard(); renderCalendar(); renderGoals(); renderProgress(); $('#notesArea').value = notes }
function refreshAllFull(){ refreshAll(); renderMusic() }

function initEvents(){
  $('#addPrayerBtn').addEventListener('click', ()=>openPrayerModal())
  $('#addGoalBtn').addEventListener('click', addGoal)
  
  // Logout button
  const logoutBtn = $('#logoutBtn')
  if(logoutBtn) {
    logoutBtn.addEventListener('click', doLogout)
  }
  
  // Music navigation
  const musicBackBtn = $('#musicBackBtn')
  if(musicBackBtn) {
    musicBackBtn.addEventListener('click', showMusicMain)
  }
  
  // Music area session form
  const areaSessionForm = document.getElementById('areaSessionsForm')
  if(areaSessionForm) {
    areaSessionForm.addEventListener('submit', e => {
      e.preventDefault()
      saveAreaSession()
    })
  }
  
  // notification buttons
  $('#enableNotificationsBtn').addEventListener('click', async ()=>{
    const granted = await requestNotificationPermission()
    settings.enableNotifications = granted
    save(STORAGE_KEYS.SETTINGS, settings)
    updateNotifUI()
  })
  $('#testNotificationBtn').addEventListener('click', ()=>{
    if(Notification.permission === 'granted'){
      try{ new Notification('🙏 Teste de notificação', {body: 'Esta é uma notificação de teste.'}) }catch(e){alert('Erro ao enviar notificação: '+e)}
    }else{
      alert('Permissão de notificações não concedida. Clique em Ativar notificações.')
    }
  })
  $('#testNotification10sBtn').addEventListener('click', ()=>{
    // schedule a test notification in 10 seconds
    setTimeout(()=>{
      if(Notification.permission === 'granted'){
        try{ new Notification('🙏 Momento de oração', {body: 'Teste de notificação funcionando!'}) }catch(e){console.warn(e)}
      } else {
        alert('Permissão de notificações não concedida.')
      }
    }, 10000)
    alert('Teste agendado em 10 segundos')
  })
  $('#exportBtn').addEventListener('click', exportData)
  $('#importBtn').addEventListener('click', ()=>$('#importFile').click())
  $('#importFile').addEventListener('change', e=>{ if(e.target.files[0]) importData(e.target.files[0]) })
  $('#backupBtn').addEventListener('click', exportData)
  const enableCheckbox = document.getElementById('enableNotifications')
  if(enableCheckbox){
    enableCheckbox.checked = settings.enableNotifications
    enableCheckbox.addEventListener('change', e=>{ settings.enableNotifications = e.target.checked; save(STORAGE_KEYS.SETTINGS,settings); updateNotifUI() })
  }
  $('#dailyGoalStudy').value = settings.dailyGoalStudy||30
  $('#dailyGoalStudy').addEventListener('change', e=>{ settings.dailyGoalStudy = Number(e.target.value); save(STORAGE_KEYS.SETTINGS,settings) })
  const instrumentSelect = $('#selectedInstrument')
  if(instrumentSelect){
    instrumentSelect.innerHTML = buildInstrumentOptions(settings.selectedInstrument || gamification.selectedInstrument || 'teclado')
    instrumentSelect.value = normalizeInstrumentKey(settings.selectedInstrument || gamification.selectedInstrument || 'teclado')
    instrumentSelect.addEventListener('change', async e => {
      await applySelectedInstrument(e.target.value)
    })
  }

  const areaInstrumentSelect = $('#instrumentSelect')
  if(areaInstrumentSelect){
    areaInstrumentSelect.innerHTML = buildInstrumentOptions(settings.selectedInstrument || gamification.selectedInstrument || 'teclado')
    areaInstrumentSelect.value = normalizeInstrumentKey(settings.selectedInstrument || gamification.selectedInstrument || 'teclado')
    areaInstrumentSelect.addEventListener('change', async e=>{
      const nextInstrument = normalizeInstrumentKey(e.target.value)
      await applySelectedInstrument(nextInstrument)
      if (StudyAppV2) {
        StudyAppV2.currentInstrument = nextInstrument
      }
      if (StudyApp) {
        StudyApp.currentInstrument = nextInstrument
      }
    })
  }
  $('#themeToggle').addEventListener('click', ()=>{ document.body.classList.toggle('dark'); settings.theme = document.body.classList.contains('dark')? 'dark':'light'; save(STORAGE_KEYS.SETTINGS,settings) })
  $('#saveNotes').addEventListener('click', ()=>{ notes = $('#notesArea').value; save(STORAGE_KEYS.NOTES,notes); alert('Anotações salvas') })
}

// initial load
document.addEventListener('DOMContentLoaded', async ()=>{
  // Verificar autenticação e sincronizar dados
  try {
    const authUser = await ensureAuthenticated();
    currentUser = authUser || window.currentUser || currentUser;

    // Verificar se usuário tem instrumento selecionado no banco e não redirecionar em loop
    if (!currentUser || !currentUser.instrumento) {
      if (window.location.pathname !== '/instrument-selection') {
        console.log('📍 Usuário sem instrumento, redirecionando para seleção');
        window.location.replace('/instrument-selection');
      }
      return;
    }

    if (window.location.pathname === '/instrument-selection') {
      console.log('✅ Usuário já tem instrumento salvo; indo para dashboard');
      window.location.replace('/dashboard');
      return;
    }

    await updateUserDisplay();
    await syncDataFromBackend();
  } catch (error) {
    console.error('Erro na inicialização:', error)
  }
  
  // apply theme
  if(settings.theme==='dark') document.body.classList.add('dark')
  initEvents(); 
  StudyAppV2.init(); // Inicializar Study App V2 para MSA, Método e Hinário
  refreshAllFull();
  // Show music main view initially
  showMusicMain()
  // start minute interval
  setInterval(()=>{ checkAndNotify(); renderDashboard(); updateNextPrayerUI() }, 1000*30)
  // initial UI update for notifications
  updateNotifUI(); updateNextPrayerUI()
})

function updateNotifUI(){
  const status = settings.enableNotifications && Notification && Notification.permission === 'granted'
  $('#notifStatus').textContent = status? '🟢 Notificações ativadas' : '🔴 Notificações desativadas'
}

function updateNextPrayerUI(){
  // compute next enabled prayer for today or tomorrow
  const now = new Date(); const cur = now.toTimeString().slice(0,5)
  const today = todayISO()
  // list of times greater than now today
  const upcoming = prayers.filter(p=>p.enabled).map(p=>({
    ...p,
    datetime: (()=>{
      const [hh,mm]=p.time.split(':').map(Number)
      const dt = new Date(); dt.setHours(hh,mm,0,0); return dt
    })()
  })).filter(p=>p.datetime.getTime() >= new Date().getTime()).sort((a,b)=>a.datetime-b.datetime)
  let next = null
  if(upcoming.length) next = upcoming[0]
  else{
    // next is tomorrow first enabled
    const first = prayers.filter(p=>p.enabled).sort((a,b)=>a.time.localeCompare(b.time))[0]
    if(first) next = first
  }
  $('#nextPrayer').textContent = next? (next.time + ' — ' + next.title) : '—'
}

// Public API helpers (save/load and explicit CRUD wrappers)
function saveAll(){
  save(STORAGE_KEYS.PRAYERS, prayers)
  save(STORAGE_KEYS.PRAYER_HISTORY, prayerHistory)
  save(STORAGE_KEYS.STUDIES, studies)
  save(STORAGE_KEYS.SESSIONS, sessions)
  save(STORAGE_KEYS.GOALS, goals)
  save(STORAGE_KEYS.MUSIC, music)
  save(STORAGE_KEYS.SETTINGS, settings)
  save(STORAGE_KEYS.NOTES, notes)
}

function loadAll(){
  prayers = load(STORAGE_KEYS.PRAYERS, prayers)
  prayerHistory = load(STORAGE_KEYS.PRAYER_HISTORY, prayerHistory)
  studies = load(STORAGE_KEYS.STUDIES, studies)
  sessions = load(STORAGE_KEYS.SESSIONS, sessions)
  goals = load(STORAGE_KEYS.GOALS, goals)
  music = load(STORAGE_KEYS.MUSIC, music)
  settings = load(STORAGE_KEYS.SETTINGS, settings)
  notes = load(STORAGE_KEYS.NOTES, notes)
  refreshAllFull()
}

function addPrayerItem({title,time,desc,enabled}={}){
  const p = {id:uid(), title: title||'Momento', time: time||'18:00', desc: desc||'', enabled: enabled===undefined? true: !!enabled}
  prayers.push(p); save(STORAGE_KEYS.PRAYERS,prayers); renderPrayers(); renderDashboard(); return p
}

function concludePrayer(prayerId, date){
  togglePrayerComplete(prayerId)
}

function editPrayerById(id, {title,time,desc,enabled}={}){
  const p = prayers.find(x=>x.id===id); if(!p) return false
  if(title!==undefined) p.title = title
  if(time!==undefined) p.time = time
  if(desc!==undefined) p.desc = desc
  if(enabled!==undefined) p.enabled = !!enabled
  save(STORAGE_KEYS.PRAYERS,prayers); renderPrayers(); renderDashboard(); return true
}

function deletePrayerById(id){
  const before = prayers.length
  prayers = prayers.filter(x=>x.id!==id)
  save(STORAGE_KEYS.PRAYERS,prayers); renderPrayers(); renderDashboard(); return prayers.length < before
}

function addStudyItem({name,module,progress,notes}={}){
  const s = {id:uid(), name: name||'MSA', module: module||'', progress: Number(progress||0), notes: notes||''}
  studies.push(s); save(STORAGE_KEYS.STUDIES,studies); renderStudies(); renderDashboard(); return s
}

function editStudyById(id, {name,module,progress,notes}={}){
  const s = studies.find(x=>x.id===id); if(!s) return false
  if(name!==undefined) s.name = name
  if(module!==undefined) s.module = module
  if(progress!==undefined) s.progress = Number(progress)
  if(notes!==undefined) s.notes = notes
  save(STORAGE_KEYS.STUDIES,studies); renderStudies(); renderDashboard(); return true
}

function deleteStudyById(id){
  const before = studies.length
  studies = studies.filter(x=>x.id!==id)
  save(STORAGE_KEYS.STUDIES,studies); renderStudies(); renderDashboard(); return studies.length < before
}

// expose some functions for dev/testing and external callers
window._mj = Object.assign(window._mj || {}, {
  renderPrayers, renderCalendar, togglePrayerComplete, renderDashboard,
  saveAll, loadAll,
  addPrayerItem, concludePrayer, editPrayerById, deletePrayerById,
  addStudyItem, editStudyById, deleteStudyById,
  prayers, prayerHistory, studies, sessions,
  music, renderMusic
})
