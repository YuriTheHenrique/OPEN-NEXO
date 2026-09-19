const graficos = {};
window.graficos = graficos;

let dataSelecionada = obterDataLocal();

let fp = null;


/* =========================================================
   CONVERSÃO DE DATA
   ========================================================= */

function formatarDataAPI(data) {

    return (
        data.getFullYear() +
        "-" +
        String(data.getMonth() + 1).padStart(2, "0") +
        "-" +
        String(data.getDate()).padStart(2, "0")
    );

}


/* =========================================================
   ALTERAÇÃO CENTRALIZADA DA DATA
   ========================================================= */

async function selecionarData(data) {

    if (!data) {
        return;
    }

    dataSelecionada =
        formatarDataAPI(data);

    console.log(
        "📅 Nova data selecionada:",
        dataSelecionada
    );


    /*
     * Atualiza o campo visual do Flatpickr
     *
     * false = não dispara o onChange.
     * Nós mesmos chamaremos a atualização abaixo.
     */
    if (fp) {
        fp.setDate(data, false);
    }


    /*
     * Atualiza todo o dashboard explicitamente.
     */
    await atualizarDashboard();


    /*
     * Se a visão de auditoria estiver aberta,
     * atualiza também a tabela.
     */
    const visaoRestricoes =
        document.getElementById("visaoRestricoes");

    if (
        visaoRestricoes &&
        visaoRestricoes.style.display !== "none" &&
        typeof carregarTabelaAuditoria === "function"
    ) {
        await carregarTabelaAuditoria();
    }

}


/* =========================================================
   FLATPICKR
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const seletorData =
        document.getElementById("seletorData");


    if (!seletorData) {

        console.error(
            "❌ Elemento #seletorData não encontrado."
        );

        return;
    }


    fp = flatpickr(
        seletorData,
        {

            dateFormat: "d/m/Y",

            locale: "pt",

            defaultDate: new Date(),

            maxDate: "today",


            onChange: function (selectedDates) {

                if (!selectedDates.length) {
                    return;
                }

                /*
                 * O usuário escolheu uma data
                 * diretamente no calendário.
                 */
                selecionarData(
                    selectedDates[0]
                );

            }

        }
    );


    /* =====================================================
       BOTÃO DIA ANTERIOR
       ===================================================== */

    const btnAnterior =
        document.getElementById("btnDataAnterior");

    if (btnAnterior) {

        btnAnterior.addEventListener(
            "click",
            async function () {

                console.log("⬅️ Dia anterior");

                const atual =
                    fp.selectedDates[0] ||
                    new Date();

                const anterior =
                    new Date(atual);

                anterior.setDate(
                    anterior.getDate() - 1
                );

                await selecionarData(
                    anterior
                );

            }
        );

    }


    /* =====================================================
       BOTÃO PRÓXIMO DIA
       ===================================================== */

    const btnProxima =
        document.getElementById("btnDataProxima");

    if (btnProxima) {

        btnProxima.addEventListener(
            "click",
            async function () {

                console.log("➡️ Próximo dia");

                const atual =
                    fp.selectedDates[0] ||
                    new Date();

                const proximo =
                    new Date(atual);

                proximo.setDate(
                    proximo.getDate() + 1
                );


                /*
                 * Não permite passar de hoje.
                 */
                const hoje =
                    new Date();

                hoje.setHours(
                    0, 0, 0, 0
                );

                if (proximo > hoje) {
                    proximo.setTime(
                        hoje.getTime()
                    );
                }


                await selecionarData(
                    proximo
                );

            }
        );

    }


    /* =====================================================
       BOTÃO HOJE
       ===================================================== */

    const btnHoje =
        document.getElementById("btnDataHoje");

    if (btnHoje) {

        btnHoje.addEventListener(
            "click",
            async function () {

                const hoje =
                    new Date();

                await selecionarData(
                    hoje
                );

            }
        );

    } else {

        console.error(
            "Elemento #btnDataHoje não encontrado."
        );
    atualizarDashboard();

    }
});


async function atualizarUsinas() {

    const resposta = await fetch(
        `/api/usinas?data=${dataSelecionada}`
    );

    const usinas = await resposta.json();

    const painel = document.getElementById("painelUsinas");

    let html = "";

    usinas.forEach(usina => {

        const id = usina.usina
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-zA-Z0-9]/g, "");

        let valor = "";

        if (
            usina.evento === "RESTRICAO" &&
            usina.potencia_restricao !== null &&
            usina.potencia_restricao !== undefined &&
            usina.capacidade
        ) {

            valor = `
                <div class="info-operacao">

                    <h6>
                        Geração limitada
                    </h6>

                    <small>
                        Capacidade disponível
                    </small>

                    <strong>
                        ${usina.potencia_restricao} MW
                    </strong>

                    <small>
                        ${usina.capacidade} MW instalados
                    </small>

                </div>
            `;

        } else {

            valor = `
                <div class="info-operacao">

                    <h6>
                        Sem restrição
                    </h6>

                    <small>
                        Capacidade disponível
                    </small>

                    <strong>
                        ${usina.capacidade} MW
                    </strong>

                </div>
            `;
        }

        html += `

            <div class="usina-card">

                <div class="card usina-card-content">

                    <div class="mb-2">

                        <img
                            src="${usina.logo || '/static/logos/default.png'}"
                            class="logo-usina"
                        >

                        <h5 class="titulo-usina">
                            ${usina.apelido}
                        </h5>

                        <div class="tipo-geracao">
                            ${usina.tipo_geracao}
                        </div>

                    </div>


                    <div class="grafico-container">

                        <canvas id="grafico-${id}">
                        </canvas>

                    </div>


                    <div id="valor-${id}">

                        ${valor}

                    </div>


                    <div class="dev-indicator">

                        ID Evento:
                        ${usina.id_evento || "-"}

                        <br>

                        Evento:
                        ${usina.evento || "-"}

                        <br>

                        Status:
                        ${usina.status || "-"}

                    </div>


                    <div class="info-horario">

                        Recebimento<br>

                        ${
                            usina.dataCadastro
                            ? new Date(usina.dataCadastro)
                                .toLocaleTimeString("pt-BR")
                            : "-"
                        }

                        <br><br>

                        Atualização<br>

                        ${
                            usina.dataAtualizacao
                            ? new Date(usina.dataAtualizacao)
                                .toLocaleTimeString("pt-BR")
                            : "-"
                        }

                    </div>


                    <hr>


                    <small>

                        Capacidade:
                        ${usina.capacidade} MW

                    </small>


                    <br>


                    <small>

                        Status:
                        ${usina.status}

                    </small>


                <button
                    type="button"
                    class="history-button"
                    onclick="abrirHistorico('${usina.usina}')">

                    <svg
                        viewBox="0 0 24 24"
                        width="15"
                        height="15"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                        stroke-linejoin="round">

                        <path d="M3 12a9 9 0 1 0 3-6.7"></path>
                        <polyline points="3 4 3 9 8 9"></polyline>
                        <line x1="12" y1="7" x2="12" y2="12"></line>
                        <line x1="12" y1="12" x2="16" y2="15"></line>

                    </svg>

                    Histórico

                </button>

                

                </div>

            </div>

        `;
    });


    /*
     * Primeiro cria todos os cards.
     * Depois cria os gráficos.
     */
    painel.innerHTML = html;


    /*
     * Evita gráficos antigos sobrando no objeto
     * quando o painel for reconstruído.
     */
    Object.keys(graficos).forEach(id => {

        if (graficos[id]) {
            graficos[id].destroy();
        }

        delete graficos[id];

    });


    usinas.forEach(usina => {

        criarRosca(usina);

    });
}

async function atualizarUsinasIncremental() {

    const resposta = await fetch(
        `/api/usinas?data=${dataSelecionada}`
    );

    const usinas = await resposta.json();

    usinas.forEach(usina => {

        const id = usina.usina
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .replace(/[^a-zA-Z0-9]/g, "");

        const bloco = document.getElementById(
            "valor-" + id
        );

        const canvas = document.getElementById(
            "grafico-" + id
        );

        if (!bloco || !canvas) {
            return;
        }

        let valor;

        if (
            usina.evento === "RESTRICAO" &&
            usina.potencia_restricao !== null &&
            usina.potencia_restricao !== undefined &&
            usina.capacidade
        ) {

            valor = `
                <div class="info-operacao">
                    <h6>Geração limitada</h6>

                    <small>
                        Capacidade disponível
                    </small>

                    <strong>
                        ${usina.potencia_restricao} MW
                    </strong>

                    <small>
                        ${usina.capacidade} MW instalados
                    </small>
                </div>
            `;

        } else {

            valor = `
                <div class="info-operacao">
                    <h6>Sem restrição</h6>

                    <small>
                        Capacidade disponível
                    </small>

                    <strong>
                        ${usina.capacidade} MW
                    </strong>
                </div>
            `;
        }

        bloco.innerHTML = valor;


        const grafico = graficos[
            "grafico-" + id
        ];

        if (grafico) {

            let disponivel = 100;
            let reduzido = 0;

            if (
                usina.potencia_restricao !== null &&
                usina.potencia_restricao !== undefined &&
                usina.capacidade
            ) {

                disponivel =
                    (
                        usina.potencia_restricao /
                        usina.capacidade
                    ) * 100;

                reduzido =
                    100 - disponivel;
            }

            grafico.data.datasets[0].data = [
                disponivel,
                reduzido
            ];

            grafico.update();
        }


        const card = canvas.closest(".card");

        if (!card) {
            return;
        }


        const infoHorario =
            card.querySelector(".info-horario");

        if (infoHorario) {

            infoHorario.innerHTML = `
                Recebimento<br>

                ${
                    usina.dataCadastro
                    ? new Date(
                        usina.dataCadastro
                    ).toLocaleTimeString("pt-BR")
                    : "-"
                }

                <br><br>

                Atualização<br>

                ${
                    usina.dataAtualizacao
                    ? new Date(
                        usina.dataAtualizacao
                    ).toLocaleTimeString("pt-BR")
                    : "-"
                }
            `;
        }


        const smalls =
            card.querySelectorAll("small");

        const statusElement =
            Array.from(smalls).find(
                elemento =>
                    elemento.textContent
                        .trim()
                        .startsWith("Status:")
            );

        if (statusElement) {

            statusElement.innerHTML = `
                Status:
                ${usina.status || "-"}
            `;
        }

    });
}

function criarRosca(usina){


    let disponivel = 100;

    let reduzido = 0;


    if(
        usina.evento === "RESTRICAO" &&
        usina.potencia_restricao !== null &&
        usina.capacidade
    ){

        disponivel =
        (
            usina.potencia_restricao /
            usina.capacidade
        ) * 100;


        reduzido =
        100 - disponivel;

    }



    const id =
    "grafico-" +
    usina.usina
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g,"")
    .replace(/[^a-zA-Z0-9]/g,"");



    const canvas =
    document.getElementById(id);



    if(!canvas){
        return;
    }


    const textoCentral = {

        id: "textoCentral",

        afterDraw(chart) {

            const { ctx } = chart;

            const meta = chart.getDatasetMeta(0);

            if (!meta.data.length) return;

            const x = meta.data[0].x;
            const y = meta.data[0].y;

            ctx.save();

            ctx.textAlign = "center";
            ctx.textBaseline = "middle";

           ctx.font =
                "600 16px 'Geist', sans-serif";

            ctx.fillStyle =
                getComputedStyle(
                    document.documentElement
                ).getPropertyValue("--text");

            const percentual = chart.data.datasets[0].data[0];

            ctx.fillText(
                percentual.toFixed(1) + "%",
                x,
                y
            );

            ctx.restore();

        }

    };

    graficos[id] = new Chart(
        canvas,
        {

        type: "doughnut",


        data: {

            labels: [
                "Disponível",
                "Redução"
            ],


            datasets: [
                // cor da rosca
                {

                data: [
                    disponivel,
                    reduzido
                ],

                backgroundColor: [
                    "#4F8EF7",
                    "#495057"
                ],

                borderWidth: 0

                }

            ]

        },

        plugins: [textoCentral],

        options: {

            responsive:true,

            maintainAspectRatio:false,

            animation:{
                duration:800
            },

            cutout:"72%",


            plugins: 
            {

                legend:{
                    display:false
                }

            }
            

        }

    });


}

async function abrirHistorico(usina){

    const resposta =
        await fetch(
            "/api/historico/" +
            encodeURIComponent(usina) +
            `?data=${dataSelecionada}`
        );

    const dados =
        await resposta.json();


    document.getElementById(
        "tituloHistorico"
    ).innerText = usina;


    let html="";


    dados.forEach(item=>{

        html += `

        <div>

        ${new Date(item.data)
        .toLocaleString("pt-BR")}

        <br>

        ${item.status}

        -

        ${item.potencia ?? "-"} MW

        </div>

        <hr>

        `;

    });


    document.getElementById(
        "corpoHistorico"
    ).innerHTML = html;


    const modal =
        document.getElementById(
            "modalHistorico"
        );

    modal.classList.add("show");

}

function fecharHistorico() {

    const modal =
        document.getElementById(
            "modalHistorico"
        );

    modal.classList.remove("show");

}


document
    .getElementById("modalHistorico")
    .addEventListener(
        "click",
        evento => {

            if (
                evento.target.id ===
                "modalHistorico"
            ) {

                fecharHistorico();

            }

        }
    );


document.addEventListener(
    "keydown",
    evento => {

        if (evento.key === "Escape") {

            fecharHistorico();

        }

    }
);