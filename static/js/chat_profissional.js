  document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('chat-container');
    const gestorId = container.dataset.gestorId;
    const userId = container.dataset.userId;
    const chatBox = document.getElementById('chat-box');
    const form = document.getElementById('chat-form');
    const input = document.getElementById('msg-input');

    if (!gestorId) return;

    function renderMessages(msgs) {
      chatBox.innerHTML = '';
      msgs.forEach(m => {
        const div = document.createElement('div');
        div.className = (m.remetente == userId) ? 'mensagem-enviada' : 'mensagem-recebida';
        const time = new Date(m.criado_em).toLocaleTimeString();
        div.textContent = `[${time}] ${m.conteudo}`;
        chatBox.appendChild(div);
      });
      chatBox.scrollTop = chatBox.scrollHeight;
    }

    async function fetchChat() {
      try {
        const res = await fetch(`/api/chat/${gestorId}/`);
        if (res.ok) {
          const data = await res.json();
          renderMessages(data);
        }
      } catch (e) {
        console.error('Erro ao buscar chat', e);
      }
    }

    form.addEventListener('submit', async e => {
      e.preventDefault();
      const conteudo = input.value.trim();
      if (!conteudo) return;
      try {
        await fetch('/api/chat/', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ destinatario: gestorId, conteudo })
        });
        input.value = '';
        fetchChat();
      } catch (e) {
        console.error('Erro ao enviar mensagem', e);
      }
    });

    fetchChat();
    setInterval(fetchChat, 3000);
  });