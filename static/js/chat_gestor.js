document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('chat-container');
  if (!container) return;

  const userId   = container.dataset.userId;
  const profId   = container.dataset.profId;
  const chatBox  = document.getElementById('chat-box');
  const form     = document.getElementById('chat-form');
  const input    = document.getElementById('conteudo');

  // Função para ler o CSRF do cookie
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  // Renderiza a lista de mensagens
  function renderMessages(msgs) {
    chatBox.innerHTML = '';
    msgs.forEach(m => {
      const div = document.createElement('div');
      div.className = m.remetente == userId
        ? 'mensagem minha'
        : 'mensagem deles';
      const time = new Date(m.criado_em).toLocaleTimeString();
      div.innerHTML = `<small>[${time}]</small> <p>${m.conteudo}</p>`;
      chatBox.appendChild(div);
    });
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Busca as mensagens via API
  async function fetchConversa() {
    try {
      const res = await fetch(
        `/api/chat/?gestor=${userId}&usuario=${profId}`
      );
      if (res.ok) {
        const data = await res.json();
        renderMessages(data);
      }
    } catch (e) {
      console.error('Erro ao buscar conversa', e);
    }
  }

  // Envia nova mensagem
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const conteudo = input.value.trim();
    if (!conteudo) return;

    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({
          destinatario: profId,
          conteudo
        })
      });
      if (res.ok) {
        input.value = '';
        fetchConversa();
      } else {
        console.error('Falha ao enviar:', await res.text());
      }
    } catch (e) {
      console.error('Erro ao enviar mensagem', e);
    }
  });

  // Loop de atualização
  fetchConversa();
  setInterval(fetchConversa, 3000);
});
