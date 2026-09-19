import { appendFile, mkdir } from "node:fs/promises";
import { join } from "node:path";

const DIRETORIO_LOGS = "./logs";

function dataAtual(): string {
    return new Intl.DateTimeFormat("sv-SE", {
        timeZone: "America/Sao_Paulo",
    }).format(new Date());
}

function horarioAtual(): string {
    return new Intl.DateTimeFormat("sv-SE", {
        timeZone: "America/Sao_Paulo",
        dateStyle: "short",
        timeStyle: "medium",
    }).format(new Date());
}

async function gravar(
    nivel: "INFO" | "WARN" | "ERROR",
    mensagem: string,
) {
    try {
        await mkdir(DIRETORIO_LOGS, {
            recursive: true,
        });

        const data = dataAtual();

        const arquivo = join(
            DIRETORIO_LOGS,
            `${data}.log`,
        );

        const linha =
            `[${horarioAtual()}] ` +
            `[${nivel}] ` +
            `${mensagem}\n`;

        await appendFile(
            arquivo,
            linha,
            "utf-8",
        );
    } catch (erro) {
        console.error(
            "Não foi possível gravar o log:",
            erro,
        );
    }
}

export function logInfo(mensagem: string) {
    console.log(mensagem);
    void gravar("INFO", mensagem);
}

export function logWarn(mensagem: string) {
    console.warn(mensagem);
    void gravar("WARN", mensagem);
}

export function logError(
    mensagem: string,
    erro?: unknown,
) {
    console.error(mensagem, erro ?? "");

    const detalhe =
        erro instanceof Error
            ? `${mensagem} | ${erro.stack ?? erro.message}`
            : erro
                ? `${mensagem} | ${String(erro)}`
                : mensagem;

    void gravar("ERROR", detalhe);
}