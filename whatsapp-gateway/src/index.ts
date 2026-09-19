import {
    logInfo,
    logError,
} from "./logger.js";

import {
    iniciarWhatsApp,
} from "./whatsapp.js";

import {
    carregarFila,
} from "./message-queue.js";

import {
    iniciarApi,
} from "./api.js";

// ============================================================
// INICIALIZAÇÃO DO GATEWAY
// ============================================================

async function iniciarGateway() {

    logInfo(
        "WhatsApp Gateway do NEXO iniciando.",
    );

    try {

        // ----------------------------------------------------
        // CARREGA FILA PERSISTENTE
        // ----------------------------------------------------

        await carregarFila();

        // ----------------------------------------------------
        // INICIA API
        // ----------------------------------------------------

        iniciarApi();

        logInfo(
            "API do WhatsApp Gateway iniciada.",
        );

        // ----------------------------------------------------
        // INICIA WHATSAPP
        // ----------------------------------------------------

        await iniciarWhatsApp();

        logInfo(
            "Cliente WhatsApp iniciado.",
        );

    } catch (error) {

        logError(
            "Falha crítica durante a inicialização " +
            "do WhatsApp Gateway.",
            error,
        );

        process.exit(1);
    }
}

await iniciarGateway();