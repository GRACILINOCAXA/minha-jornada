# Minha Jornada

Aplicação frontend simples para gerenciar lembretes de oração e acompanhar estudos do MSA (Método e Hábito). Os dados são persistidos em `localStorage` e podem ser exportados/importados.

Como usar
- Abra `index.html` no navegador (recomendado Chrome/Edge/Firefox).
- Permita notificações se quiser lembretes pelo navegador.

Recursos
- Lembretes de oração (adicionar/editar/excluir, marcar concluído, histórico)
- Estudos MSA (cadastrar estudos, barra de progresso)
- Registro de sessões de estudo (tempo, o que aprendeu)
- Calendário com indicadores de atividades
- Metas simples com barra de progresso
- Exportar/importar backup JSON
- Tema claro/escuro

Observações e próximos passos
- Atualmente as notificações funcionam enquanto a página está aberta. Para lembretes em segundo plano, integrar Service Worker + Push.
- Estrutura preparada para migrar os dados para backend (Firebase/Supabase/SQLite/Postgres).

Notificações (Windows)
- A aplicação usa a Notification API do navegador para exibir notificações nativas do sistema (Windows). Para funcionar:
	- Clique em `Configurações` → `🔔 Ativar notificações` e permita no navegador.
	- Ative notificações para cada oração (cada oração tem um botão Ativar/Desativar).
	- Use `Testar notificação` para confirmar que o Windows exibirá mensagens.
	- Observação: as notificações nativas são enviadas pelo navegador e só funcionarão enquanto o navegador estiver aberto (a página pode estar em segundo plano). Para notificações em segundo plano é necessário implementar Service Worker + Push.

Teste rápido
- Para testar uma notificação imediata use `Testar notificação` em Configurações.
- Para verificar envio futuro, use `Testar notificação em 10 segundos` — a notificação aparecerá em 10s (se a permissão estiver concedida).

