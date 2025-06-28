document.addEventListener('DOMContentLoaded', () => {
  // 1) Exibir mini-formulário ao clicar em "Adicionar Registro"
  document.querySelectorAll('.botao-adicionar-registro')
    .forEach(botao => {
      botao.addEventListener('click', () => {
        const celula = botao.parentElement;
        botao.style.display = 'none';
        celula.querySelector('.form-adicionar').style.display = 'inline';
      });
  });

  // 2) Cancelar adição: esconder formulário e voltar botão
  document.querySelectorAll('.btn-cancelar-registro')
    .forEach(btn => {
      btn.addEventListener('click', () => {
        const formDiv = btn.closest('.form-adicionar');
        const celula = formDiv.parentElement;
        formDiv.style.display = 'none';
        celula.querySelector('.botao-adicionar-registro').style.display = 'inline';
      });
  });

  // 3) Salvar novo registro via AJAX
  document.querySelectorAll('.btn-salvar-registro')
    .forEach(btn => {
      btn.addEventListener('click', () => {
        const formDiv = btn.closest('.form-adicionar');
        const celula = formDiv.parentElement;
        const linha = celula.closest('tr');

        // Obtém data da linha e valores do formulário
        const dataDia = linha.dataset.date;  // "2025-06-23"
        const tipo = formDiv.querySelector('select[name="tipo_novo"]').value;
        const hora = formDiv.querySelector('input[name="hora_nova"]').value;
        if (!hora) { alert("Informe um horário."); return; }

        // Define URL e CSRF
        const profId = document
          .getElementById('folha-tabela')
          .dataset.profId;
        const url = `/folhas/${profId}/adicionar/`;
        const csrfToken = document
          .querySelector('input[name=csrfmiddlewaretoken]')
          .value;

        // Prepara FormData
        const dados = new FormData();
        dados.append('data', dataDia);
        dados.append('tipo', tipo);
        dados.append('hora', hora);

        fetch(url, {
          method: 'POST',
          headers: { 'X-CSRFToken': csrfToken },
          body: dados
        })
        .then(res => {
          if (!res.ok) throw new Error("Falha ao criar registro.");
          return res.json();
        })
        .then(json => {
          // Atualiza célula correspondente ao tipo
          const celTipo = linha.querySelector(`td[data-tipo="${json.tipo}"]`);
          celTipo.innerHTML = `
            <input type="time"
                   name="registro_${json.id}"
                   value="${json.hora}">
            <input type="checkbox"
                   name="editar_${json.id}">`;

          // Esconder form e reexibir botão
          formDiv.style.display = 'none';
          celula.querySelector('.botao-adicionar-registro')
                .style.display = 'inline';
        })
        .catch(err => {
          console.error(err);
          alert("Erro ao adicionar registro.");
          formDiv.style.display = 'none';
          celula.querySelector('.botao-adicionar-registro')
                .style.display = 'inline';
        });
  });
});
});