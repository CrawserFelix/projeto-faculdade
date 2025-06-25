document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('chart').getContext('2d');
  let chart = null;

  async function loadData() {
    const prof = document.getElementById('filtro-profissional').value;
    const mes  = document.getElementById('filtro-mes').value;
    const ano  = document.getElementById('filtro-ano').value;
    const res  = await fetch(
      `/dashboard/data/?profissional=${prof}&mes=${mes}&ano=${ano}`
    );
    const json = await res.json();
    const labels = json.realizado.map(d => d.dia);

    // Dados séries
    const datasets = [
      {
        label: 'Entrada Esperada',
        data: labels.map(() => json.esperado.entrada),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Entrada Realizada',
        data: json.realizado.map(d => d.entrada || null),
        fill: false,
      },
      {
        label: 'Pausa Início',
        data: labels.map(() => json.esperado.intervalo_inicio),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Pausa Realizada',
        data: json.realizado.map(d => d.pausa || null),
        fill: false,
      },
      {
        label: 'Saída Esperada',
        data: labels.map(() => json.esperado.saida),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Saída Realizada',
        data: json.realizado.map(d => d.saida || null),
        fill: false,
      }
    ];

    const config = {
      type: 'line',
      data: { labels, datasets },
      options: { scales: { y: { beginAtZero: false } } }
    };

    if (chart) chart.destroy();
    chart = new Chart(ctx, config);
  }

  // Listeners
  document.getElementById('dashboard-atualizar').addEventListener('click', loadData)
  loadData();
});