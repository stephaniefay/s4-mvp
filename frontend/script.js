const API = 'http://localhost:8000';

// ── Stars Decoration ──────────────────────────────────────────────────
(function spawnStars() {
  const container = document.getElementById('stars');
  if (!container) return;
  for (let i = 0; i < 60; i++) {
    const s = document.createElement('div');
    s.className = 'star';
    s.style.cssText = `
      left:${Math.random()*100}%;
      top:${Math.random()*100}%;
      --dur:${3+Math.random()*5}s;
      --delay:${Math.random()*6}s;
      --op:${0.2+Math.random()*0.5};
    `;
    container.appendChild(s);
  }
})();

// ── Event Listener para o Enter no campo de busca ─────────────────────
document.addEventListener('DOMContentLoaded', () => {
    const queryInput = document.getElementById('query');
    if (queryInput) {
        queryInput.addEventListener('keydown', (event) => {
            if (event.key === 'Enter') {
                buscar();
            }
        });
    }
});

// ── Tabs ─────────────────────────────────────────────────────────────
function mostrarAba(nome, el) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + nome).classList.add('active');
  el.classList.add('active');
}

// ── Loading helper ───────────────────────────────────────────────────
function loading(msg = 'O corvo consulta os arquivos ancestrais...') {
  return `<div class="loading-rune">
    <div class="rune-spinner">🜂</div>
    <p>${msg}</p>
  </div>`;
}

function erro(msg) {
  return `<div class="error-scroll">⚠ ${msg}</div>`;
}

// ── RECOMENDAÇÃO ─────────────────────────────────────────────────────
async function buscar() {
  const query = document.getElementById('query').value.trim();
  const div   = document.getElementById('resultado-rec');

  if (!query) {
    div.innerHTML = erro('Nenhum nome foi sussurrado ao corvo.');
    return;
  }

  div.innerHTML = loading();
  document.getElementById('btn-buscar').disabled = true;

  try {
    const resp = await fetch(API + '/recomendar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ query, top_n: 10 })
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      div.innerHTML = erro(err.detail || `Erro ${resp.status}.`);
      return;
    }

    const data = await resp.json();

    let html = `
      <p class="section-heading">Tomos revelados pelo grimório</p>
      <div class="ref-box">
        O corvo encontrou: <strong>${data.referencia.link
          ? `<a href="${esc(data.referencia.link)}" target="_blank" rel="noopener noreferrer" class="ref-link">${esc(data.referencia.titulo)}</a>`
          : esc(data.referencia.titulo)
        }</strong>
      </div>`;

    data.recomendacoes.forEach((livro, i) => {
      const simPct = Math.round(livro.similaridade * 100);
      
      const badgeClass = livro.popularidade === 'Média' ? 'Media' : livro.popularidade;
      const badgeLabel = `Popularidade ${livro.popularidade}`;
      const tituloHtml = livro.link
        ? `<a href="${esc(livro.link)}" target="_blank" rel="noopener noreferrer" class="book-link" title="Abrir no Goodreads">${esc(livro.titulo)}</a>`
        : esc(livro.titulo);

      html += `
        <div class="book-card" style="animation-delay:${i*0.05}s">
          <span class="book-rank">${i + 1}</span>
          <div class="book-info">
            <div class="book-title">${tituloHtml}</div>
            <div class="book-meta">✍ ${esc(livro.autor)} &nbsp;·&nbsp; ⭐ ${livro.rating}</div>
          </div>
          <div class="book-right" data-tooltip="Similaridade: ${simPct}% com a sua busca">
            <span class="badge ${badgeClass}" title="Classificação de engajamento no Goodreads">
              ${badgeLabel}
            </span>
            <div class="sim-bar-wrap">
              <div class="sim-bar" style="width:${simPct}%"></div>
            </div>
            <span class="sim-label">${simPct}%</span>
          </div>
        </div>`;
    });

    div.innerHTML = html;

  } catch (e) {
    div.innerHTML = erro('Não foi possível contactar o servidor. Verifique se a API está ativa na porta 8000.');
  } finally {
    document.getElementById('btn-buscar').disabled = false;
  }
}

// ── CLASSIFICAÇÃO ────────────────────────────────────────────────────
async function classificar() {
  const rating = parseFloat(document.getElementById('rating').value);
  const count  = parseInt(document.getElementById('count').value);
  const pages  = parseInt(document.getElementById('pages').value) || 300;
  const div    = document.getElementById('resultado-clf');

  if (isNaN(rating) || isNaN(count)) {
    div.innerHTML = erro('Preencha ao menos a avaliação e o número de avaliações.');
    return;
  }

  div.innerHTML = loading('O oráculo medita sobre o destino deste tomo...');
  document.getElementById('btn-clf').disabled = true;

  try {
    const resp = await fetch(API + '/classificar', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ rating, num_avaliacoes: count, num_paginas: pages })
    });

    if (!resp.ok) {
      const err = await resp.json().catch(() => ({}));
      div.innerHTML = erro(err.detail || `Erro ${resp.status}.`);
      return;
    }

    const data = await resp.json();
    const pop  = data.popularidade;
    const probas = data.probabilidades;

    const descricoes = {
      Alta:  'Este tomo repousa nos altares mais venerados da biblioteca.',
      Média: 'Um tomo de boa reputação entre os leitores do reino.',
      Baixa: 'Uma obra ainda aguardando seu momento de ser descoberta.'
    };

    const cores = { Alta: '#7ecb8a', Media: '#88b0d8', Baixa: '#c47a6a' };
    const badgeKey = pop === 'Média' ? 'Media' : pop;

    let probaHtml = '';
    for (const [cls, prob] of Object.entries(probas).sort((a,b) => b[1]-a[1])) {
      const fillColor = cores[cls === 'Média' ? 'Media' : cls] || '#c8a84b';
      probaHtml += `
        <div class="prob-row">
          <span class="prob-name">${cls}</span>
          <div class="prob-track">
            <div class="prob-fill" style="width:${Math.round(prob*100)}%;background:${fillColor}"></div>
          </div>
          <span class="prob-val">${(prob*100).toFixed(1)}%</span>
        </div>`;
    }

    div.innerHTML = `
      <div class="grimoire">
        <div class="corner tl"></div><div class="corner tr"></div>
        <div class="corner bl"></div><div class="corner br"></div>
        <div class="class-result">
          <div class="class-rune class-${badgeKey}">${pop}</div>
          <p class="class-subtitle">${descricoes[pop] || ''}</p>
          <div class="prob-bars">${probaHtml}</div>
        </div>
      </div>`;

  } catch (e) {
    div.innerHTML = erro('Não foi possível contactar o servidor. Verifique se a API está ativa na porta 8000.');
  } finally {
    document.getElementById('btn-clf').disabled = false;
  }
}

// ── Utils ────────────────────────────────────────────────────────────
function esc(str) {
  return String(str)
    .replace(/&/g,'&amp;')
    .replace(/</g,'&lt;')
    .replace(/>/g,'&gt;')
    .replace(/"/g,'&quot;');
}