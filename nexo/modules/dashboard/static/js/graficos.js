let dadosRestricoes = [];

let graficoRestricoes;

let filtroUsinaSelecionada = "todas";
let filtroTipoGrafico = "todas";
let modoGrafico = "restricao";

let requisicaoGrafico = 0;

async function carregarGraficoRestricoes() {

    /*
     * Cada chamada recebe um ID único.
     * Se outra chamada acontecer depois,
     * esta requisição fica automaticamente obsoleta.
     */
    const minhaRequisicao = ++requisicaoGrafico;

    console.log(
        "📊 Iniciando gráfico:",
        dataSelecionada,
        "requisição:",
        minhaRequisicao
    );


    /*
     * LIMPA IMEDIATAMENTE OS DADOS ANTIGOS
     */
    dadosRestricoes = [];


    /*
     * DESTRÓI IMEDIATAMENTE O GRÁFICO ANTERIOR
     */
    if (graficoRestricoes) {

        graficoRestricoes.destroy();

        graficoRestricoes = null;

    }


    try {

        const dataConsulta =
            dataSelecionada;


        const resposta =
            await fetch(
                `/api/grafico/restricoes?data=${encodeURIComponent(dataConsulta)}`
            );


        if (!resposta.ok) {

            throw new Error(
                `HTTP ${resposta.status}`
            );

        }


        const dados =
            await resposta.json();


        console.log(
            "📊 Resposta recebida:",
            dataConsulta,
            dados,
            "requisição:",
            minhaRequisicao
        );


        /*
         * Se outra requisição começou depois desta,
         * NÃO podemos renderizar esta resposta.
         */
        if (minhaRequisicao !== requisicaoGrafico) {

            console.log(
                "⚠️ Resposta descartada por ser antiga:",
                minhaRequisicao
            );

            return;
        }


        /*
         * Garante que sempre trabalharemos com array.
         */
        dadosRestricoes =
            Array.isArray(dados)
                ? dados
                : [];


        preencherFiltroUsinas(
            dadosRestricoes
        );


        renderizarGraficoRestricoes();


    } catch (erro) {

        /*
         * Só trata o erro se esta ainda for
         * a requisição vigente.
         */
        if (minhaRequisicao !== requisicaoGrafico) {
            return;
        }


        console.error(
            "❌ Erro ao carregar gráfico:",
            erro
        );


        dadosRestricoes = [];


        renderizarGraficoRestricoes();

    }

}

function preencherFiltroUsinas(dados){

    const select =
        document.getElementById("filtroUsina");

    const selectAuditoria =
        document.getElementById("filtroUsinaAuditoria");

    const usinas = [
        ...new Set(
            dados.map(item => item.usina)
        )
    ].sort();

    const valorAtual =
        filtroUsinaSelecionada;

    if(select){

        select.innerHTML = `
            <option value="todas">
                Todas as usinas
            </option>
        `;

        usinas.forEach(usina => {

            const option =
                document.createElement("option");

            option.value = usina;
            option.textContent = usina;

            select.appendChild(option);

        });

        if(
            usinas.includes(valorAtual)
            || valorAtual === "todas"
        ){

            select.value =
                valorAtual;

        }
        else {

            filtroUsinaSelecionada =
                "todas";

            select.value =
                "todas";

        }

    }

    if(selectAuditoria){

        const selecoesAtuais =
            Array.from(
                selectAuditoria.selectedOptions
            ).map(option => option.value);

        selectAuditoria.innerHTML = "";

        const optionTodas =
            document.createElement("option");

        optionTodas.value = "todas";
        optionTodas.textContent = "Todas as usinas";
        optionTodas.selected =
            selecoesAtuais.length === 0
            || selecoesAtuais.includes("todas");

        selectAuditoria.appendChild(optionTodas);

        usinas.forEach(usina => {

            const option =
                document.createElement("option");

            option.value = usina;
            option.textContent = usina;

            option.selected =
                selecoesAtuais.includes(usina);

            selectAuditoria.appendChild(option);

        });

    }

}

function aplicarFiltroUsina(){

    const select =
        document.getElementById("filtroUsina");

    filtroUsinaSelecionada =
        select.value;

    renderizarGraficoRestricoes();

}

function filtroGrafico(tipo){

    filtroTipoGrafico =
        tipo;

    renderizarGraficoRestricoes();

}

function alternarModoGrafico(modo) {

    modoGrafico = modo;

    const botaoRestricao =
        document.getElementById(
            "modoRestricao"
        );

    const botaoLimite =
        document.getElementById(
            "modoLimite"
        );


    botaoRestricao.classList.toggle(
        "active",
        modo === "restricao"
    );

    botaoLimite.classList.toggle(
        "active",
        modo === "limite"
    );


    renderizarGraficoRestricoes();

}

function renderizarGraficoRestricoes(){

    if(!dadosRestricoes.length){
        return;
    }

    let dados =
        [...dadosRestricoes];


    /*
     * FILTRO POR USINA
     */

    if(
        filtroUsinaSelecionada !== "todas"
    ){

        dados =
            dados.filter(
                item =>
                    item.usina ===
                    filtroUsinaSelecionada
            );

    }


    /*
     * FILTRO DE TIPO
     */

    if(
        filtroTipoGrafico === "restritas"
    ){

        const usinasRestritas = [
            ...new Set(
                dados.map(
                    item => item.usina
                )
            )
        ];

        dados =
            dados.filter(
                item =>
                    usinasRestritas.includes(
                        item.usina
                    )
            );

    }


    /*
     * TOP IMPACTO
     */

    if(
        filtroTipoGrafico === "top"
    ){

        const impactos = {};

        dados.forEach(item => {

            if(
                !impactos[item.usina]
            ){

                impactos[item.usina] =
                    0;

            }

            impactos[item.usina] +=
                Number(item.restricao) || 0;

        });

        const topUsinas =
            Object.entries(impactos)
            .sort(
                (a,b) =>
                    b[1] - a[1]
            )
            .slice(0,5)
            .map(
                item => item[0]
            );

        dados =
            dados.filter(
                item =>
                    topUsinas.includes(
                        item.usina
                    )
            );

    }


    /*
     * MONTA UMA SÉRIE
     * INDEPENDENTE PARA CADA USINA
     */

    const usinas = [
        ...new Set(
            dados.map(
                item => item.usina
            )
        )
    ];


    const datasets =
        usinas.map(usina => {

            const eventosUsina =
                dados
                .filter(
                    item =>
                        item.usina === usina
                )
                .sort(
                    (a,b) =>
                        new Date(a.data) -
                        new Date(b.data)
                );


            return {

                label: usina,

                data:
                    eventosUsina.map(
                        item => ({

                            x:
                                new Date(
                                    item.data
                                ),

                            y:
                                modoGrafico === "restricao"
                                    ? Number(item.restricao)
                                    : Number(item.limite)

                        })
                    ),

                tension:0.35,

                fill:false,

                spanGaps:false

            };

        });


    /*
     * DESTROI O GRÁFICO ANTERIOR
     */

    if (graficoRestricoes) {

        graficoRestricoes.data.datasets = datasets;

        graficoRestricoes.update();

        return;
    }


    /*
     * CRIA O NOVO GRÁFICO
     */

    graficoRestricoes =
        new Chart(

            document.getElementById(
                "graficoRestricaoUsinas"
            ),

            {

                type:"line",

                data:{

                    datasets:
                        datasets

                },

                options:{

                    responsive:true,

                    maintainAspectRatio:false,

                    interaction:{

                        mode:"nearest",

                        intersect:false

                    },

                    plugins:{

                        legend:{

                            position:"bottom"

                        }

                    },

                    scales:{

                        x:{

                            type:"time",

                            time:{

                                displayFormats:{

                                    minute:"HH:mm",

                                    hour:"HH:mm"

                                }

                            },

                            title:{

                                display:true,

                                text:"Horário"

                            }

                        },

                        y:{

                            beginAtZero:true,

                            title:{

                                display:true,

                                text:
                                    modoGrafico === "restricao"
                                        ? "MW restringidos"
                                        : "Limite de geração (MW)"

                            }

                        }

                    }

                }

            }

        );

}
