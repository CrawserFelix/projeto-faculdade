// Função para preencher a tabela com os registros de pontos
function popularTabela() {
    const pontosList = document.getElementById('pontos-list');

    registrosDePontos.forEach(registro => {
        const newRow = document.createElement('tr');
        newRow.innerHTML = `
            <td>${registro.data}</td>
            <td>${registro.entrada}</td>
            <td>${registro.pausa}</td>
            <td>${registro.retorno}</td>
            <td>${registro.saida}</td>
        `;
        pontosList.appendChild(newRow);
    });
}

// Chamando a função para popular a tabela
popularTabela();
