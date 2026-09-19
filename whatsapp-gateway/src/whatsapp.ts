import {
    logInfo,
    logWarn,
    logError,
} from "./logger.js";

import makeWASocket, {
    Browsers,
    DisconnectReason,
    useMultiFileAuthState,
} from "@whiskeysockets/baileys";

import { processarMensagensPendentes } from "./comms-service.js";
import qrcode from "qrcode-terminal";
import pino from "pino";
import { rm } from "node:fs/promises";

let socketAtual: ReturnType<typeof makeWASocket> | null = null;

let statusConexao = "disconnected";

let envioBloqueado = false;

let qrCodeAtual: string | null = null;

let resolverConexao: (() => void) | null = null;

let conexaoPronta = criarPromessaConexao();

let reinicializacaoManual = false;

function criarPromessaConexao() {
    return new Promise<void>((resolve) => {
        resolverConexao = resolve;
    });
}

export async function enviarMensagem(
    destinatario: string,
    texto: string,
) {
    await conexaoPronta;

    if (!socketAtual) {
        throw new Error("WhatsApp não está conectado.");
    }

    if (statusConexao !== "connected") {
        throw new Error("WhatsApp não está conectado.");
    }

    if (envioBloqueado) {
        throw new Error("Envio WhatsApp bloqueado para teste.");
    }

    await socketAtual.sendMessage(destinatario, {
        text: texto,
    });

    logInfo(
        `WhatsApp enviou mensagem para ${destinatario}.`,
    );
}

export function obterStatusWhatsApp() {
    return statusConexao;
}

export function obterSocketWhatsApp() {
    return socketAtual;
}

export function bloquearEnvioWhatsApp() {
    envioBloqueado = true;
    logWarn(
        "Envio WhatsApp BLOQUEADO para teste.",
    );
}

export function liberarEnvioWhatsApp() {
    envioBloqueado = false;
    logInfo(
        "Envio WhatsApp LIBERADO.",
    );
}

export function obterQRCode() {
    return qrCodeAtual;
}

export function limparQRCode() {
    qrCodeAtual = null;
}

// ============================================================
// CONTROLE MANUAL DA CONEXÃO
// ============================================================

export async function reconectarWhatsApp() {

    logInfo(
        "Reinicialização manual do WhatsApp solicitada.",
    );

    reinicializacaoManual = true;

    limparQRCode();

    if (socketAtual) {

        try {

            await socketAtual.ws?.close();

        } catch (error) {

            logWarn(
                "Não foi possível fechar o socket atual " +
                "durante a reconexão manual.",
            );

        }

        socketAtual = null;
    }

    statusConexao = "disconnected";

    conexaoPronta = criarPromessaConexao();

    await iniciarWhatsApp();
}


export async function resetarWhatsApp() {

    logWarn(
        "RESET DA SESSÃO DO WHATSAPP solicitado.",
    );

    reinicializacaoManual = true;

    limparQRCode();

    if (socketAtual) {

        try {

            await socketAtual.ws?.close();

        } catch (error) {

            logWarn(
                "Não foi possível fechar o socket atual " +
                "durante o reset.",
            );

        }

        socketAtual = null;
    }

    statusConexao = "disconnected";

    conexaoPronta = criarPromessaConexao();

    try {

        await rm("./auth", {
            recursive: true,
            force: true,
        });

        logInfo(
            "Sessão WhatsApp removida. " +
            "Um novo pareamento será necessário.",
        );

    } catch (error) {

        logError(
            "Erro ao remover a sessão do WhatsApp.",
            error instanceof Error
                ? error
                : undefined,
        );

        throw error;
    }

    reinicializacaoManual = false;

    await iniciarWhatsApp();
}

export async function iniciarWhatsApp() {
    logInfo("Iniciando cliente WhatsApp...");

    statusConexao = "connecting";

    const { state, saveCreds } = await useMultiFileAuthState(
        "./auth",
    );

    const socket = makeWASocket({
        auth: state,
        browser: Browsers.baileys("NEXO"),
        syncFullHistory: false,
        logger: pino({ level: "silent" }),
    });

    socketAtual = socket;

    socket.ev.on("creds.update", saveCreds);

    socket.ev.on("connection.update", async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            qrCodeAtual = qr;

            logInfo(
                "QR Code recebido. Aguardando pareamento do WhatsApp.",
            );

            qrcode.generate(qr, { small: true });
        }

        if (connection === "open") {
            statusConexao = "connected";
            reinicializacaoManual = false;

            limparQRCode();

            logInfo("WhatsApp conectado.");
            logInfo("WhatsApp pronto para envio.");

            if (resolverConexao) {
                resolverConexao();
                resolverConexao = null;
            }

            await processarMensagensPendentes();
        }

        if (connection === "close") {

            statusConexao = "disconnected";

            conexaoPronta = criarPromessaConexao();

            const statusCode =
                (lastDisconnect?.error as any)?.output?.statusCode;

            logWarn(
                `Conexão WhatsApp encerrada. Código: ${statusCode}.`,
            );


            // --------------------------------------------------------
            // REINICIALIZAÇÃO MANUAL
            // --------------------------------------------------------

            if (reinicializacaoManual) {

                logInfo(
                    "Reconexão automática ignorada. " +
                    "Reinicialização manual em andamento.",
                );

                return;
            }


            // --------------------------------------------------------
            // LOGOUT
            // --------------------------------------------------------

            if (
                statusCode === DisconnectReason.loggedOut
            ) {

                logError(
                    "WhatsApp desconectado por logout. " +
                    "Reconexão automática não será realizada.",
                );

                return;
            }


            // --------------------------------------------------------
            // RECONEXÃO AUTOMÁTICA
            // --------------------------------------------------------

            logInfo(
                "Tentando reconectar ao WhatsApp em 3 segundos.",
            );

            setTimeout(() => {

                if (
                    statusConexao === "disconnected" &&
                    !reinicializacaoManual
                ) {

                    iniciarWhatsApp();

                }

            }, 3000);
        }
    });

    return socket;

}

export async function listarGruposWhatsApp() {
    if (!socketAtual) {
        throw new Error("WhatsApp não está conectado.");
    }

    const grupos = await socketAtual.groupFetchAllParticipating();

    for (const grupo of Object.values(grupos)) {
        console.log(
            `GRUPO: ${grupo.subject} | ID: ${grupo.id}`,
        );
    }
}