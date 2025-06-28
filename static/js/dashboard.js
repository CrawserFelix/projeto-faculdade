document.addEventListener('DOMContentLoaded', () => {
  const ctx = document.getElementById('chart').getContext('2d');
  let chart = null;

  // Converte "HH:MM" → número de horas em ponto flutuante (ex: "08:30" → 8.5)
  function timeStringToDecimal(t) {
    if (!t) return null;
    const [h, m] = t.split(':').map(Number);
    return h + m / 60;
  }

  async function loadData() {
    const prof = document.getElementById('filtro-profissional').value;
    const mes  = document.getElementById('filtro-mes').value;
    const ano  = document.getElementById('filtro-ano').value;

    if (!prof) {
      alert("Por favor, selecione um profissional.");
      return;
    }

    const res  = await fetch(`/dashboard/data/?profissional=${prof}&mes=${mes}&ano=${ano}`);
    const json = await res.json();

    // Gera labels de dias
    const labels = json.realizado.map(d => d.dia);

    // Converte dados de esperado/realizado para decimais
    const esperadoEnt  = timeStringToDecimal(json.esperado.entrada);
    const esperadoPausa= timeStringToDecimal(json.esperado.inicio_intervalo);
    const esperadoSaida= timeStringToDecimal(json.esperado.saida);

    const realizadoEnt  = json.realizado.map(d => timeStringToDecimal(d.entrada));
    const realizadoPausa= json.realizado.map(d => timeStringToDecimal(d.pausa));
    const realizadoSaida= json.realizado.map(d => timeStringToDecimal(d.saida));

    // Monta datasets
    const datasets = [
      {
        label: 'Entrada Esperada',
        data: labels.map(() => esperadoEnt),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Entrada Realizada',
        data: realizadoEnt,
        fill: false,
      },
      {
        label: 'Pausa Esperada',
        data: labels.map(() => esperadoPausa),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Pausa Realizada',
        data: realizadoPausa,
        fill: false,
      },
      {
        label: 'Saída Esperada',
        data: labels.map(() => esperadoSaida),
        borderDash: [5,5],
        fill: false,
      },
      {
        label: 'Saída Realizada',
        data: realizadoSaida,
        fill: false,
      }
    ];

    // Configurações do gráfico, formatando ticks do eixo Y de volta para HH:MM
    const config = {
      type: 'line',
      data: { labels, datasets },
      options: {
        scales: {
          y: {
            beginAtZero: false,
            ticks: {
              callback: function(val) {
                // val é em horas decimais → converte para HH:MM
                const h = Math.floor(val);
                const m = Math.round((val - h) * 60);
                const hh = String(h).padStart(2, '0');
                const mm = String(m).padStart(2, '0');
                return `${hh}:${mm}`;
              }
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        plugins: {
          tooltip: {
            callbacks: {
              label: context => {
                const val = context.parsed.y;
                const h = Math.floor(val);
                const m = Math.round((val - h) * 60);
                const hh = String(h).padStart(2, '0');
                const mm = String(m).padStart(2, '0');
                return `${context.dataset.label}: ${hh}:${mm}`;
              }
            }
          }
        }
      }
    };

    if (chart) chart.destroy();
    chart = new Chart(ctx, config);

    // Preenche tabela de dias
    const tbody = document.querySelector('#dashboard-table tbody');
    tbody.innerHTML = '';
    json.realizado.forEach(dia => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${dia.dia}</td>
        <td>${dia.entrada || '–'}</td>
        <td>${dia.pausa   || '–'}</td>
        <td>${dia.retorno || '–'}</td>
        <td>${dia.saida   || '–'}</td>
      `;
      tbody.appendChild(tr);
    });

    // Exibe métricas
    document.getElementById('metrica-atrasos').textContent = `Atrasos: ${json.atrasos}`;
    document.getElementById('metrica-extras').textContent  = `Horas Extras: ${json.horas_extras}`;
    document.getElementById('metrica-faltas').textContent  = `Faltas: ${json.faltas}`;
  }

  document.getElementById('dashboard-atualizar').addEventListener('click', loadData);
  loadData();
});
