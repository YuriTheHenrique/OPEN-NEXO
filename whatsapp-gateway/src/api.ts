import { createServer } from "node:http";

import { enviarMensagemComms } from "./comms-service.js";

import {
    obterStatusWhatsApp,
    obterQRCode,
    reconectarWhatsApp,
    resetarWhatsApp,
} from "./whatsapp.js";

import {
    obterQuantidadeMensagens,
} from "./message-queue.js";

import {
    logInfo,
    logWarn,
    logError,
} from "./logger.js";

const PORTA = 8100;

export function iniciarApi() {

    const server = createServer(
        async (req, res) => {

            // ========================================================
            // STATUS DO GATEWAY
            // ========================================================

            if (
                req.method === "GET" &&
                req.url === "/status"
            ) {
                const status =
                    obterStatusWhatsApp();

                const mensagensPendentes =
                    obterQuantidadeMensagens();

                const conectado =
                    status === "connected";

                res.writeHead(
                    conectado ? 200 : 503,
                    {
                        "Content-Type":
                            "application/json",
                    },
                );

                res.end(
                    JSON.stringify({
                        ok: conectado,

                        whatsapp: {
                            status,
                            conectado,
                        },

                        fila: {
                            pendentes:
                                mensagensPendentes,
                        },

                        uptime: Math.floor(
                            process.uptime(),
                        ),
                    }),
                );

                return;
            }

            // ========================================================
            // QR CODE
            // ========================================================

            if (
                req.method === "GET" &&
                req.url === "/qr"
            ) {
                const qr =
                    obterQRCode();

                res.writeHead(200, {
                    "Content-Type":
                        "application/json",
                });

                res.end(
                    JSON.stringify({
                        ok: true,
                        disponivel: qr !== null,
                        qr,
                    }),
                );

                return;
            }

            // ========================================================
            // RECONEXÃO MANUAL
            // ========================================================

            if (
                req.method === "POST" &&
                req.url === "/reconnect"
            ) {

                try {

                    logInfo(
                        "Gateway API -> " +
                        "Solicitação de reconexão manual do WhatsApp.",
                    );

                    await reconectarWhatsApp();

                    res.writeHead(200, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: true,
                            mensagem:
                                "Reconexão do WhatsApp iniciada.",
                        }),
                    );

                } catch (error) {

                    logError(
                        "Gateway API -> " +
                        "Erro ao reconectar o WhatsApp.",
                        error instanceof Error
                            ? error
                            : undefined,
                    );

                    res.writeHead(500, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: false,
                            erro:
                                "Erro ao reconectar o WhatsApp.",
                        }),
                    );
                }

                return;
            }


            // ========================================================
            // RESET DA SESSÃO
            // ========================================================

            if (
                req.method === "POST" &&
                req.url === "/reset"
            ) {

                try {

                    logWarn(
                        "Gateway API -> " +
                        "RESET da sessão do WhatsApp solicitado.",
                    );

                    await resetarWhatsApp();

                    res.writeHead(200, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: true,
                            mensagem:
                                "Sessão do WhatsApp removida. " +
                                "Novo pareamento será necessário.",
                        }),
                    );

                } catch (error) {

                    logError(
                        "Gateway API -> " +
                        "Erro ao resetar a sessão do WhatsApp.",
                        error instanceof Error
                            ? error
                            : undefined,
                    );

                    res.writeHead(500, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: false,
                            erro:
                                "Erro ao resetar a sessão do WhatsApp.",
                        }),
                    );
                }

                return;
            }

            // --------------------------------------------------------
            // ENDPOINT INVÁLIDO
            // --------------------------------------------------------

            if (
                req.method !== "POST" ||
                req.url !== "/messages"
            ) {

                logWarn(
                    "Gateway API -> Endpoint não encontrado. " +
                    `Método: ${req.method}. ` +
                    `URL: ${req.url}.`,
                );

                res.writeHead(404, {
                    "Content-Type":
                        "application/json",
                });

                res.end(
                    JSON.stringify({
                        ok: false,
                        erro:
                            "Endpoint não encontrado.",
                    }),
                );

                return;
            }

            try {

                // ------------------------------------------------
                // RECEBIMENTO DO CORPO
                // ------------------------------------------------

                let corpo = "";

                for await (
                    const chunk of req
                ) {
                    corpo += chunk;
                }

                // ------------------------------------------------
                // PARSE DO JSON
                // ------------------------------------------------

                let dados: any;

                try {

                    dados = JSON.parse(
                        corpo,
                    );

                } catch (error) {

                    logError(
                        "Gateway API -> " +
                        "JSON inválido recebido.",
                        error instanceof Error
                            ? error
                            : undefined,
                    );

                    res.writeHead(400, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: false,
                            erro:
                                "JSON inválido.",
                        }),
                    );

                    return;
                }

                // ------------------------------------------------
                // VALIDAÇÃO
                // ------------------------------------------------

                if (
                    typeof dados.grupo !==
                        "string" ||
                    typeof dados.mensagem !==
                        "string"
                ) {

                    logWarn(
                        "Gateway API -> " +
                        "Campos obrigatórios ausentes " +
                        "ou inválidos.",
                    );

                    res.writeHead(400, {
                        "Content-Type":
                            "application/json",
                    });

                    res.end(
                        JSON.stringify({
                            ok: false,
                            erro:
                                "Campos 'grupo' e " +
                                "'mensagem' são obrigatórios.",
                        }),
                    );

                    return;
                }

                // ------------------------------------------------
                // MENSAGEM RECEBIDA
                // ------------------------------------------------

                logInfo(
                    "Gateway API -> " +
                    "Mensagem recebida. " +
                    `Grupo: ${dados.grupo}. ` +
                    `Tamanho: ${dados.mensagem.length} caracteres.`,
                );

                // ------------------------------------------------
                // ENVIA PARA O SERVIÇO DO COMMS
                // ------------------------------------------------

                await enviarMensagemComms(
                    dados.grupo,
                    dados.mensagem,
                );

                // ------------------------------------------------
                // RESPOSTA
                // ------------------------------------------------

                res.writeHead(202, {
                    "Content-Type":
                        "application/json",
                });

                res.end(
                    JSON.stringify({
                        ok: true,
                    }),
                );

                logInfo(
                    "Gateway API -> " +
                    "Mensagem aceita e colocada " +
                    "no processamento.",
                );

            } catch (error) {

                // ------------------------------------------------
                // ERRO INTERNO
                // ------------------------------------------------

                logError(
                    "Gateway API -> " +
                    "Erro ao processar mensagem.",
                    error instanceof Error
                        ? error
                        : undefined,
                );

                res.writeHead(500, {
                    "Content-Type":
                        "application/json",
                });

                res.end(
                    JSON.stringify({
                        ok: false,
                        erro:
                            "Erro interno ao processar mensagem.",
                    }),
                );
            }
        },
    );

    // ============================================================
    // INICIALIZAÇÃO DA API
    // ============================================================

    server.listen(
        PORTA,
        "127.0.0.1",
        () => {

            logInfo(
                "Gateway API -> " +
                `API ouvindo em ` +
                `http://127.0.0.1:${PORTA}.`,
            );
        },
    );

    return server;
}