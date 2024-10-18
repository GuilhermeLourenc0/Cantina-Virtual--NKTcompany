// Função para pegar o horário de Brasília usando uma API externa
async function obterHorarioBrasilia() {
    try {
        const response = await fetch('http://worldtimeapi.org/api/timezone/America/Sao_Paulo');
        const data = await response.json();
        
        // Formatando a data e hora para exibir no formato adequado
        const dateTime = new Date(data.datetime);
        const horarioBrasilia = dateTime.toLocaleTimeString('pt-BR');

        // Exibindo o horário no elemento HTML
        document.getElementById('horario').textContent = "Horário de Brasília: " + horarioBrasilia;
    } catch (error) {
        console.error("Erro ao obter o horário de Brasília:", error);
    }
}

// Atualiza o horário a cada segundo
setInterval(obterHorarioBrasilia, 1000);

// Pega o horário logo na primeira execução
obterHorarioBrasilia();