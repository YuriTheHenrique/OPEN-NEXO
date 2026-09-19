let teclaDev = "";

document.addEventListener(
    "keydown",
    function(event){

        teclaDev += event.key.toUpperCase();


        if(teclaDev.length > 3){

            teclaDev = teclaDev.slice(-3);

        }


        if(teclaDev === "DEV"){

            alternarDevMode();

            teclaDev = "";

        }

    }
);

function mudarTema(tema){

    document.body.classList.remove(
        "tema-claro",
        "tema-dark",
        "tema-tomorrow-light",
        "tema-tomorrow-dark"
    );


    document.body.classList.add(
        "tema-" + tema
    );


    localStorage.setItem(
        "tema",
        tema
    );

    Object.values(graficos).forEach(grafico => {
        if (grafico) {
            grafico.update("none");
        }
    });

}

function carregarTema(){

    const tema =
        localStorage.getItem("tema")
        || "claro";


    mudarTema(tema);

}

carregarTema();

if(
    localStorage.getItem("devmode") === "true"
){

    document.body.classList.add(
        "devmode"
    );

}