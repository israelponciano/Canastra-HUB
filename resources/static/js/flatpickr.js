// Captura a data atual corretamente no horário local
const hoje = new Date();
const ano = hoje.getFullYear();
const mes = String(hoje.getMonth() + 1).padStart(2, '0'); // Ajuste do mês
const dia = String(hoje.getDate()).padStart(2, '0'); // Ajuste do dia

// Formata a data corretamente como YYYY-MM-DD
const dataFormatada = `${dia}-${mes}-${ano}`;

// Define o valor do input como a data atual
document.getElementById("#datepicker").value = dataFormatada;

flatpickr("#datepicker", {
    dateFormat: "d/m/Y",
    disableMobile: true, // Impede a abertura do calendário nativo no celular
    locale: "pt"
});
