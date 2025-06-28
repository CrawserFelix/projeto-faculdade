document.addEventListener('DOMContentLoaded', () => {
  // Seleciona todos os inputs de horário na tabela de folha
  document.querySelectorAll('#folha-tabela input[type="time"]').forEach(input => {
    // Garante que o <td> pai tenha position:relative para posicionar o botão
    const td = input.closest('td');
    td.style.position = 'relative';

    // Se não houver data-original no template, armazena agora o valor inicial
    if (!input.dataset.original) {
      input.dataset.original = input.value;
    }

    // Ajusta padding do input para não ficar embaixo do botão
    input.style.paddingRight = '25px';

    // Cria o botão de limpar (X)
    const btnClear = document.createElement('button');
    btnClear.type = 'button';
    btnClear.className = 'clear-time';
    btnClear.title = 'Limpar horário';
    btnClear.innerHTML = '&times;';
    td.appendChild(btnClear);

    // Quando o gestor altera o valor, compara com o original e destaca
    input.addEventListener('input', () => {
      if (input.value !== input.dataset.original) {
        input.classList.add('campo-editado');
      } else {
        input.classList.remove('campo-editado');
      }
    });

    // Ao clicar no X, limpa o campo e dispara o evento de input
    btnClear.addEventListener('click', () => {
      input.value = '';
      input.dispatchEvent(new Event('input'));
    });
  });
});
