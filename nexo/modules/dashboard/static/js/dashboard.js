async function atualizarDashboard() {

    await atualizarUsinas();
    await carregarGraficoRestricoes();
    await carregarStatus();

    // Se a visão PDP estiver aberta, atualiza imediatamente
    const visaoPDP = document.getElementById("visaoPDP");

    if (
        visaoPDP &&
        visaoPDP.style.display !== "none"
    ) {
        await carregarVisaoPDP();
    }

}


async function carregarStatus() {
    console.log("📊 STATUS → data enviada:", dataSelecionada);

    const resposta = await fetch(`/api/status?data=${dataSelecionada}`);
    const dados = await resposta.json();

    console.log("📊 STATUS → resposta:", dados);

    document.getElementById("usinas").innerText = dados.usinas_monitoradas;
    document.getElementById("eventos").innerText = dados.eventos_recebidos;
    document.getElementById("tempoResposta").innerText = dados.tempo_resposta_medio || "--";

    if (dados.ultimo_evento) {
        const data = new Date(dados.ultimo_evento);
        const formatada = data.toLocaleString("pt-BR", {
            day: "2-digit", month: "2-digit", year: "numeric",
            hour: "2-digit", minute: "2-digit", second: "2-digit"
        });
        document.getElementById("ultimo").innerText = formatada;
    } else {
        document.getElementById("ultimo").innerText = "-";
    }
}


atualizarDashboard();