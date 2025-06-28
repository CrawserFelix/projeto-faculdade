// static/js/folha.js

document.addEventListener('DOMContentLoaded', () => {
  // Seleciona todos os campos de hora na tabela
  document.querySelectorAll('#folha-tabela input[type="time"]').forEach(input => {
    // Garante que o <td> pai seja position: relative para posicionar o botão
    const td = input.closest('td');
    if (td) td.style.position = 'relative';

    // Se não houver data-original no template, define agora com o valor inicial
    if (!input.dataset.original) {
      input.dataset.original = input.value;
    }

    // Dá padding right para não ficar sob o botão de limpar
    input.style.paddingRight = '25px';

    // Cria o botão de limpar (X)
    const btnClear = document.createElement('button');
    btnClear.type = 'button';
    btnClear.className = 'clear-time';
    btnClear.title = 'Limpar horário';
    btnClear.innerHTML = '&times;';
    if (td) td.appendChild(btnClear);

    // Destaca o campo quando o valor for diferente do original
    input.addEventListener('input', () => {
      if (input.value !== input.dataset.original) {
        input.classList.add('campo-editado');
      } else {
        input.classList.remove('campo-editado');
      }
    });

    // Ao clicar no X, limpa o campo e sinaliza exclusão se for registro existente
    btnClear.addEventListener('click', () => {
      // Limpa o valor e dispara o evento de input para realçar a borda
      input.value = '';
      input.dispatchEvent(new Event('input'));

      // Se for um registro já existente, adiciona um hidden para exclusão
      if (input.name.startsWith('registro_')) {
        const id = input.name.split('_')[1];  // ex: registro_17 → ['registro','17']
        const hiddenField = document.createElement('input');
        hiddenField.type = 'hidden';
        hiddenField.name = `excluir_${id}`;   // ex: excluir_17
        hiddenField.value = '1';
        input.form.appendChild(hiddenField);
      }
    });
  });
});
