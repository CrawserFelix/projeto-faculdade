function atualizarRelogio() {
    const relogioElement = document.getElementById("relogio");
    const dataAtual = new Date();
    const hora = dataAtual.getHours().toString().padStart(2, "0");
    const minutos = dataAtual.getMinutes().toString().padStart(2, "0");
    const segundos = dataAtual.getSeconds().toString().padStart(2, "0");
    const horaFormatada = `${hora}:${minutos}:${segundos}`;
    relogioElement.textContent = horaFormatada;
}

// Atualiza o relógio a cada segundo
setInterval(atualizarRelogio, 1000);