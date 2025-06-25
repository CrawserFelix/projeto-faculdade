document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('chat-container');
  if (!container) return;

  const userId   = container.dataset.userId;
  const gestorId = container.dataset.gestorId;
  const chatBox  = document.getElementById('chat-box');
  const form     = document.getElementById('chat-form');
  const input    = document.getElementById('msg-input');

  if (!gestorId) {
    chatBox.innerHTML = '<p>Ainda não há gestor atribuído.</p>';
    return;
  }

  // Pega o CSRF token do cookie
  function getCookie(name) {
    const v = document.cookie.match('(^|;)\\s*'+name+'\\s*=\\s*([^;]+)');
    return v ? v.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  // Renderiza mensagens
  function renderMessages(msgs) {
    chatBox.innerHTML = '';
    msgs.forEach(m => {
      const div = document.createElement('div');
      div.className = (m.remetente == +userId)
        ? 'mensagem-enviada'
        : 'mensagem-recebida';
      const time = new Date(m.criado_em).toLocaleTimeString();
      div.innerHTML = `<small>[${time}]</small> ${m.conteudo}`;
      chatBox.appendChild(div);
    });
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // Busca a conversa
  async function fetchChat() {
    try {
      const res = await fetch(
        `/api/chat/?gestor=${gestorId}&usuario=${userId}`,
        { credentials: 'same-origin' }
      );
      if (res.ok) {
        const data = await res.json();
        renderMessages(data);
      } else {
        console.error('Falha ao buscar conversas:', res.status);
      }
    } catch (err) {
      console.error('Erro no fetchChat:', err);
    }
  }

  // Envia uma nova mensagem
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
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
          destinatario: gestorId,
          conteudo
        })
      });
      if (res.ok) {
        input.value = '';
        fetchChat();
      } else {
        console.error('Erro ao enviar:', await res.text());
      }
    } catch (err) {
      console.error('Erro no envio de mensagem:', err);
    }
  });

  // Loop de atualização
  fetchChat();
  setInterval(fetchChat, 3000);
});
