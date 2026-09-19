import {
    logInfo,
    logWarn,
    logError,
} from "./logger.js";

import { enviarMensagem } from "./whatsapp.js";

import {
    adicionarMensagem,
    obterPrimeiraMensagem,
    removerPrimeiraMensagem,
    removerMensagemExpirada,
    obterQuantidadeMensagens,
    mensagemExpirada,
} from "./message-queue.js";

let processandoFila = false;

const RETRY_INICIAL_MS = 5000;
const RETRY_MAX_MS = 60000;

// ============================================================
// RECEBIMENTO DE MENSAGEM
// ============================================================

export async function enviarMensagemComms(
    destinatario: string,
    texto: string,
) {
    const mensagem = await adicionarMensagem(
        destinatario,
        texto,
    );

    logInfo(
        `Mensagem recebida pelo COMMS. ` +
        `ID: ${mensagem.id}. ` +
        `Destinatário: ${mensagem.destinatario}.`,
    );

    await processarFila();
}

// ============================================================
// PROCESSAMENTO DA FILA
// ============================================================

async function processarFila() {

    if (processandoFila) {
        return;
    }

    processandoFila = true;

    try {

        while (obterQuantidadeMensagens() > 0) {

            const mensagem =
                obterPrimeiraMensagem();

            if (!mensagem) {
                break;
            }

            // ------------------------------------------------
            // EXPIRAÇÃO ANTES DA TENTATIVA
            // ------------------------------------------------

            if (mensagemExpirada(mensagem)) {

                logWarn(
                    `Mensagem ${mensagem.id} expirou ` +
                    `após 5 minutos na fila. ` +
                    `Ela será descartada e não será enviada.`,
                );

                await removerMensagemExpirada();

                continue;
            }

            // ------------------------------------------------
            // RETRY
            // ------------------------------------------------

            let tentativa = 0;

            let esperaMs =
                RETRY_INICIAL_MS;

            while (true) {

                tentativa++;

                try {

                    logInfo(
                        `Tentando enviar mensagem ` +
                        `${mensagem.id}. ` +
                        `Tentativa ${tentativa}.`,
                    );

                    await enviarMensagem(
                        mensagem.destinatario,
                        mensagem.texto,
                    );

                    await removerPrimeiraMensagem();

                    logInfo(
                        `Mensagem ${mensagem.id} ` +
                        `enviada com sucesso e removida ` +
                        `da fila.`,
                    );

                    break;

                } catch (error) {

                    logError(
                        `Falha ao enviar mensagem ` +
                        `${mensagem.id}. ` +
                        `Tentativa ${tentativa}.`,
                        error,
                    );

                    // ----------------------------------------
                    // VERIFICA EXPIRAÇÃO APÓS A FALHA
                    // ----------------------------------------

                    if (mensagemExpirada(mensagem)) {

                        logWarn(
                            `Mensagem ${mensagem.id} atingiu ` +
                            `o limite de 5 minutos após uma ` +
                            `tentativa de envio. ` +
                            `Ela será descartada.`,
                        );

                        await removerMensagemExpirada();

                        break;
                    }

                    // ----------------------------------------
                    // AGUARDA ANTES DO RETRY
                    // ----------------------------------------

                    logInfo(
                        `Mensagem ${mensagem.id} aguardando ` +
                        `${esperaMs / 1000}s para nova tentativa.`,
                    );

                    await new Promise(
                        (resolve) =>
                            setTimeout(
                                resolve,
                                esperaMs,
                            ),
                    );

                    // ----------------------------------------
                    // VERIFICA EXPIRAÇÃO DURANTE A ESPERA
                    // ----------------------------------------

                    if (mensagemExpirada(mensagem)) {

                        logWarn(
                            `Mensagem ${mensagem.id} expirou ` +
                            `durante a espera pelo próximo retry. ` +
                            `Ela será descartada.`,
                        );

                        await removerMensagemExpirada();

                        break;
                    }

                    esperaMs = Math.min(
                        esperaMs * 2,
                        RETRY_MAX_MS,
                    );
                }
            }
        }

    } finally {

        processandoFila = false;
    }
}

// ============================================================
// PROCESSAMENTO DE MENSAGENS PENDENTES
// ============================================================

export async function processarMensagensPendentes() {

    logInfo(
        `COMMS verificando mensagens pendentes. ` +
        `Quantidade: ${obterQuantidadeMensagens()}.`,
    );

    await processarFila();
}