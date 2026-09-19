import {
    logInfo,
    logWarn,
    logError,
} from "./logger.js";

import {
    readFile,
    writeFile,
} from "node:fs/promises";

import { existsSync } from "node:fs";

export interface MensagemPendente {
    id: number;
    destinatario: string;
    texto: string;
    criadaEm: string;
}

// ============================================================
// CONFIGURAÇÃO
// ============================================================

const TEMPO_EXPIRACAO_MENSAGEM_MS =
    5 * 60 * 1000;

// ============================================================
// FILA PERSISTENTE
// ============================================================

const arquivoFila =
    "./data/message-queue.json";

let fila: MensagemPendente[] = [];

let proximoId = 1;

// ============================================================
// CARREGAMENTO DA FILA
// ============================================================

export async function carregarFila() {

    try {

        if (!existsSync("./data")) {

            await import("node:fs/promises").then(
                (fs) =>
                    fs.mkdir("./data", {
                        recursive: true,
                    }),
            );
        }

        if (!existsSync(arquivoFila)) {

            await salvarFila();

            logInfo(
                "Fila persistente criada. " +
                "Nenhuma mensagem pendente.",
            );

            return;
        }

        const conteudo =
            await readFile(
                arquivoFila,
                "utf-8",
            );

        if (!conteudo.trim()) {

            logInfo(
                "Fila persistente encontrada, " +
                "mas está vazia.",
            );

            return;
        }

        fila = JSON.parse(conteudo);

        if (fila.length > 0) {

            proximoId =
                Math.max(
                    ...fila.map(
                        (mensagem) =>
                            mensagem.id,
                    ),
                ) + 1;
        }

        logInfo(
            `Fila persistente carregada. ` +
            `Mensagens pendentes: ${fila.length}.`,
        );

        if (fila.length > 0) {

            for (const mensagem of fila) {

                logInfo(
                    `Mensagem pendente recuperada. ` +
                    `ID: ${mensagem.id}. ` +
                    `Destinatário: ${mensagem.destinatario}.`,
                );
            }
        }

    } catch (error) {

        logError(
            "Erro ao carregar a fila persistente.",
            error,
        );

        throw error;
    }
}

// ============================================================
// PERSISTÊNCIA
// ============================================================

async function salvarFila() {

    await writeFile(
        arquivoFila,
        JSON.stringify(
            fila,
            null,
            2,
        ),
        "utf-8",
    );
}

// ============================================================
// ADICIONAR MENSAGEM
// ============================================================

export async function adicionarMensagem(
    destinatario: string,
    texto: string,
) {

    const mensagem: MensagemPendente = {

        id: proximoId++,

        destinatario,

        texto,

        criadaEm:
            new Date().toISOString(),
    };

    fila.push(mensagem);

    try {

        await salvarFila();

        logInfo(
            `Mensagem persistida na fila. ` +
            `ID: ${mensagem.id}. ` +
            `Destinatário: ${mensagem.destinatario}.`,
        );

    } catch (error) {

        logError(
            `Falha ao persistir mensagem ` +
            `${mensagem.id} na fila.`,
            error,
        );

        throw error;
    }

    return mensagem;
}

// ============================================================
// PRIMEIRA MENSAGEM
// ============================================================

export function obterPrimeiraMensagem() {

    return fila[0];
}

// ============================================================
// VERIFICA EXPIRAÇÃO
// ============================================================

export function mensagemExpirada(
    mensagem: MensagemPendente,
): boolean {

    const criadaEm =
        new Date(
            mensagem.criadaEm,
        ).getTime();

    const idade =
        Date.now() - criadaEm;

    return (
        idade >=
        TEMPO_EXPIRACAO_MENSAGEM_MS
    );
}

// ============================================================
// REMOVER MENSAGEM EXPIRADA
// ============================================================

export async function removerMensagemExpirada() {

    const mensagem = fila[0];

    if (!mensagem) {
        return;
    }

    fila.shift();

    try {

        await salvarFila();

        logWarn(
            `Mensagem descartada por expiração. ` +
            `ID: ${mensagem.id}. ` +
            `Destinatário: ${mensagem.destinatario}. ` +
            `Tempo máximo de espera: 5 minutos.`,
        );

    } catch (error) {

        logError(
            `Falha ao remover mensagem expirada ` +
            `${mensagem.id} da fila.`,
            error,
        );

        throw error;
    }
}

// ============================================================
// REMOVER PRIMEIRA MENSAGEM
// ============================================================

export async function removerPrimeiraMensagem() {

    const mensagem = fila[0];

    if (!mensagem) {
        return;
    }

    fila.shift();

    try {

        await salvarFila();

        logInfo(
            `Mensagem removida da fila persistente ` +
            `após envio. ` +
            `ID: ${mensagem.id}. ` +
            `Destinatário: ${mensagem.destinatario}.`,
        );

    } catch (error) {

        logError(
            `Falha ao atualizar a fila após remover ` +
            `a mensagem ${mensagem.id}.`,
            error,
        );

        throw error;
    }
}

// ============================================================
// QUANTIDADE
// ============================================================

export function obterQuantidadeMensagens() {

    return fila.length;
}