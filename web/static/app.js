const robotIpInput = document.getElementById('robot-ip');
const saveIpButton = document.getElementById('save-ip');
const connectResult = document.getElementById('connect-result');
const actionResult = document.getElementById('action-result');
const processList = document.getElementById('process-list');
const faceName = document.getElementById('face-name');
const llmHistory = document.getElementById('llm-history');

async function fetchJson(path, opts = {}) {
  const res = await fetch(path, opts);
  return res.json();
}

async function loadInfo() {
  const info = await fetchJson('/api/info');
  robotIpInput.value = info.robot_ip || '';
}

async function updateStatus() {
  const status = await fetchJson('/api/status');
  const processes = status.processes || {};
  if (Object.keys(processes).length === 0) {
    processList.textContent = 'Aucun processus actif.';
  } else {
    processList.textContent = Object.entries(processes)
      .map(([name, proc]) => `${name}: ${proc.running ? 'EN COURS' : 'TERMINE'} (PID ${proc.pid || '-'})`)
      .join('\n');
  }

  try {
    const face = await fetchJson('/api/last_face');
    faceName.textContent = face.name || 'Aucun visage récent détecté';
  } catch (err) {
    faceName.textContent = 'Impossible de récupérer le visage';
  }

  try {
    const history = await fetchJson('/api/llm_history');
    if (history.history) {
      llmHistory.textContent = history.history
        .map(item => `${item.role}: ${item.content}`)
        .join('\n');
    } else {
      llmHistory.textContent = 'Aucun historique disponible.';
    }
  } catch (err) {
    llmHistory.textContent = 'Impossible de récupérer l’historique LLM';
  }
}

async function performAction(action) {
  actionResult.textContent = 'En cours...';
  const response = await fetchJson('/api/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ action }),
  });

  if (response.ok) {
    actionResult.textContent = `Action démarrée: ${action}`;
  } else {
    actionResult.textContent = response.message || response.error || 'Erreur d’exécution';
  }

  setTimeout(() => {
    actionResult.textContent = '';
  }, 4000);
}

saveIpButton.addEventListener('click', async () => {
  connectResult.textContent = 'Vérification en cours...';
  const ip = robotIpInput.value.trim();
  if (!ip) {
    connectResult.textContent = 'Veuillez entrer une adresse IP valide.';
    return;
  }

  const response = await fetchJson('/api/connect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ip }),
  });

  if (response.ok) {
    connectResult.textContent = response.message || 'Connexion réussie.';
  } else {
    connectResult.textContent = response.message || response.error || 'Échec de la connexion.';
  }

  setTimeout(() => {
    connectResult.textContent = '';
  }, 5000);
});

for (const button of document.querySelectorAll('[data-action]')) {
  button.addEventListener('click', () => performAction(button.dataset.action));
}

loadInfo();
updateStatus();
setInterval(updateStatus, 5000);
