document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const conteudoInput = document.getElementById('conteudo');
  const destinatarioInput = document.getElementById('destinatario');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();  // evita o envio normal e o reload

    const conteudo = conteudoInput.value.trim();
    const destinatario = destinatarioInput.value;

    if (!conteudo) return;

    try {
      const res = await fetch('/api/chat/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({ destinatario, conteudo })
      });
      if (res.ok) {
        conteudoInput.value = '';
        // opcional: re-carregar histórico e scrollar
        fetchChat();  
      } else {
        console.error('Falha ao enviar:', await res.text());
      }
    } catch (err) {
      console.error('Erro de rede:', err);
    }
  });
});