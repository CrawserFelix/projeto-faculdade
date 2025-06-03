// Máscara para CPF
function aplicarMascaraCPF(campo) {
    let value = campo.value.replace(/\D/g, "");

    if (value.length > 3 && value.length <= 6) {
        value = value.replace(/(\d{3})(\d+)/, "$1.$2");
    } else if (value.length > 6 && value.length <= 9) {
        value = value.replace(/(\d{3})(\d{3})(\d+)/, "$1.$2.$3");
    } else if (value.length > 9) {
        value = value.replace(/(\d{3})(\d{3})(\d{3})(\d+)/, "$1.$2.$3-$4");
    }

    campo.value = value;
}

// Validação de CPF
function validarCPF(cpf) {
    cpf = cpf.replace(/\D/g, '');
    if (cpf.length !== 11 || /^(\d)\1+$/.test(cpf)) return false;

    let soma = 0;
    for (let i = 0; i < 9; i++) soma += parseInt(cpf.charAt(i)) * (10 - i);
    let dig1 = 11 - (soma % 11);
    dig1 = dig1 >= 10 ? 0 : dig1;
    if (parseInt(cpf.charAt(9)) !== dig1) return false;

    soma = 0;
    for (let i = 0; i < 10; i++) soma += parseInt(cpf.charAt(i)) * (11 - i);
    let dig2 = 11 - (soma % 11);
    dig2 = dig2 >= 10 ? 0 : dig2;

    return parseInt(cpf.charAt(10)) === dig2;
}

// Validação de e-mail
function validarEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Máscara para telefone
function aplicarMascaraTelefone(campo) {
    let valor = campo.value.replace(/\D/g, "");

    if (valor.length > 10) {
        valor = valor.replace(/^(\d{2})(\d{5})(\d{4}).*/, "($1) $2-$3");
    } else if (valor.length > 6) {
        valor = valor.replace(/^(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3");
    } else if (valor.length > 2) {
        valor = valor.replace(/^(\d{2})(\d{0,5})/, "($1) $2");
    } else {
        valor = valor.replace(/^(\d*)/, "($1");
    }

    campo.value = valor;
}

// Máscara para remuneração
function aplicarMascaraRemuneracao(campo) {
    let valor = campo.value.replace(/\D/g, "");
    valor = (parseInt(valor) / 100).toFixed(2) + "";
    valor = valor.replace(".", ",");
    valor = valor.replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1.");
    campo.value = valor;
}

// Validação da remuneração
function validarRemuneracao(valor) {
    // Remove todos os pontos de milhar e troca a vírgula por ponto
    valor = valor.replace(/\./g, "").replace(",", ".");

    return !isNaN(parseFloat(valor)) && isFinite(valor);
}


// Quando o DOM estiver pronto
document.addEventListener("DOMContentLoaded", function () {
    // Referências aos campos
    const cpfInput = document.getElementById("cpf");
    const emailInput = document.getElementById("email");
    const senhaInput = document.getElementById("senha");
    const telefoneInput = document.getElementById("telefone");
    const remuneracaoInput = document.getElementById("remuneracao");
    const erroCPF = document.getElementById("erroCPF");
    const form = document.getElementById("cadastroForm");

    // Aplicar máscaras ao digitar
    cpfInput.addEventListener("input", function () {
        aplicarMascaraCPF(this);
        erroCPF.textContent = "";
    });

    telefoneInput.addEventListener("input", function () {
        aplicarMascaraTelefone(this);
    });

    remuneracaoInput.addEventListener("input", function () {
        aplicarMascaraRemuneracao(this);
    });

    // Validação ao enviar o formulário
    form.addEventListener("submit", function (e) {
        let erro = false;

        const cpf = cpfInput.value;
        const email = emailInput.value;
        const senha = senhaInput.value;
        const remuneracao = remuneracaoInput.value;

        if (!validarCPF(cpf)) {
            erroCPF.textContent = "CPF inválido.";
            cpfInput.focus();
            erro = true;
        }

        if (!validarEmail(email)) {
            alert("E-mail inválido.");
            emailInput.focus();
            erro = true;
        }

        if (senha.length < 6) {
            alert("A senha deve ter pelo menos 6 caracteres.");
            senhaInput.focus();
            erro = true;
        }

        if (!validarRemuneracao(remuneracao)) {
            alert("Remuneração inválida. Use apenas números (ex: 2500,00).");
            remuneracaoInput.focus();
            erro = true;
        }

        if (erro) e.preventDefault(); // Impede envio se houver erros
    });
});
