function conectarDashboardWS(){

    const protocolo =
        window.location.protocol === "https:"
            ? "wss:"
            : "ws:";

    const socket = new WebSocket(
        `${protocolo}//${window.location.host}/api/dashboard/ws`
    );

    socket.onopen = function(){

        console.log(
            "Dashboard WebSocket conectado."
        );
        document.getElementById("sistema").innerText =
            "🟢 ONLINE";
    };

    socket.onmessage = async function(event){

        const mensagem =
            JSON.parse(event.data);

        if(
            mensagem.tipo ===
            "sinapse.restricao.recebida"
        ){

            console.log(
                "Atualização recebida pelo Event Bus:",
                mensagem.dados
            );

            await atualizarUsinasIncremental();
            await carregarStatus();
            await carregarGraficoRestricoes();

        }

    };

    socket.onclose = function(){

        document.getElementById("sistema").innerText =
            "🟡 RECONECTANDO";
        console.log(
            "Dashboard WebSocket desconectado. Tentando novamente..."
        );

        setTimeout(
            conectarDashboardWS,
            3000
        );

    };

    socket.onerror = function(erro){

        document.getElementById("sistema").innerText =
            "🟡 RECONECTANDO";
        console.error(
            "Erro no Dashboard WebSocket:",
            erro
        );

    };

}

conectarDashboardWS();
