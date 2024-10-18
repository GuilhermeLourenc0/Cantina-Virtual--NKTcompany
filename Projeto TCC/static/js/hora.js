async function obterHorarioBrasilia() {
    try {
        const response = await fetch('http://worldtimeapi.org/api/timezone/America/Sao_Paulo');
        const data = await response.json();
        
        // Formatando a data e hora para exibir no formato adequado
        const dateTime = new Date(data.datetime);
        const horarioBrasilia = dateTime.toLocaleTimeString('pt-BR');

        // Exibindo o horário no elemento HTML
        document.getElementById('horario').textContent = "Horário de Brasília: " + horarioBrasilia;

        // Verificando se o horário está dentro do intervalo permitido
        const horaAtual = dateTime.getHours();
        const podeFazerPedido = (horaAtual >= 7 && horaAtual < 10);

        const botaoPedido = document.getElementById('getTimeButton');
        botaoPedido.disabled = !podeFazerPedido; // Desabilita o botão se não puder fazer pedidos

        if (!podeFazerPedido) {
            alert("Os pedidos só podem ser feitos entre 7h e 10h da manhã.");
        }
    } catch (error) {
        console.error("Erro ao obter o horário de Brasília:", error);
    }
}

// Atualiza o horário a cada segundo
setInterval(obterHorarioBrasilia, 1000);

// Pega o horário logo na primeira execução
obterHorarioBrasilia();
