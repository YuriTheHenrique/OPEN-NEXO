from datetime import datetime
from nexo.modules.sinapse.models import Restricao
from nexo.core.events.bus import event_bus
from nexo.core.events.types import SINAPSE_RESTRICAO_RECEBIDA



def process_eventos(db, evento):
    """Processa um lote de eventos (mesmo comportamento do handler /sinapse).

    Recebe a sessão (db) e o payload (evento) — pode ser dict ou list — e
    executa parse, conversões, persists e logs exatamente como no código legado.
    Retorna o dicionário de resposta idêntico ao handler antigo.
    """

    import json
    from nexo.modules.sinapse.parser import parse_mensagem
    from datetime import timezone

    # escrita inicial no log (mesma ordem e formato do legado)
    with open("NEXO.log", "a", encoding="utf-8") as f:
        f.write(f"\n[{datetime.now()}]\n")
        f.write(
            f"Recebidos: {len(evento) if isinstance(evento, list) else 1} evento(s)\n\n"
        )

        # normalização dict -> list (mesma posição que no legado: depois do log inicial)
        if isinstance(evento, dict):
            evento = [evento]

        for indice, item in enumerate(evento, start=1):
            f.write(f"Evento {indice}\n")
            f.write(
                json.dumps(
                    item,
                    indent=4,
                    ensure_ascii=False
                )
            )
            f.write("\n\n")

    print("========== NEXO RECEBEU ==========")
    print(evento)

    if not evento:
        return {"recebido": True, "mensagem": "Lista vazia recebida"}

    ## CONTROLE DAS RESTRIÇÕES PROCESSADAS
    # Guarda cada restrição junto com a informação de que ela acabou
    # de ser confirmada. Essa informação será utilizada pelo COMMS
    # para disparar a mensagem somente na transição Pendente -> Confirmada.

    restricoes_salvas = []

    for item in evento:
        try:
            dados_extraidos = parse_mensagem(item["mensagem"], db=db)

            dados = item.copy()

            dados["dataRecebimento"] = (
                datetime.now()
                .astimezone()
                .isoformat()
            )

            dados.update(dados_extraidos)

            # Normaliza datas
            for campo in ["dataAtualizacao", "dataCadastro"]:
                if dados.get(campo):
                    data = datetime.fromisoformat(
                        dados[campo].replace("Z", "+00:00")
                    )
                    dados[campo] = data.astimezone(timezone.utc).isoformat()

            # Padroniza status
            dados["status"] = dados["status"].capitalize()

            # Procura se a restrição já existe
            restricao = (
                db.query(Restricao)
                .filter(Restricao.codigo == dados["codigo"])
                .first()
            )

            if restricao:
                ## DETECÇÃO DA TRANSIÇÃO DE STATUS DA RESTRIÇÃO
                # Guarda o status anterior antes de atualizar o registro.
                # Isso permite identificar exatamente quando uma restrição
                # passa de Pendente para Confirmada.

                status_anterior = restricao.status

                restricao.status = dados["status"]
                restricao.dataAtualizacao = dados["dataAtualizacao"]

                # Mantém o horário original de recebimento.
                # Esse horário será utilizado posteriormente pelo COMMS
                # na mensagem enviada após a confirmação.

                # Mantém os dados atuais sempre sincronizados
                restricao.mensagem = dados.get("mensagem")
                restricao.motivo = dados.get("motivo")

                if "potencia_restricao" in dados:
                    restricao.potencia_restricao = dados["potencia_restricao"]

                if "potencia_observada" in dados:
                    restricao.potencia_observada = dados["potencia_observada"]

                if "evento" in dados:
                    restricao.evento = dados["evento"]

            else:
                ## REGISTRO DE UMA NOVA RESTRIÇÃO
                # A primeira chegada cria o registro e preserva o horário
                # em que a restrição entrou no NEXO.

                restricao = Restricao(**dados)
                db.add(restricao)

                status_anterior = None

            restricoes_salvas.append(
                {
                    "restricao": restricao,
                    "confirmada_agora": (
                        restricao.status == "Confirmada"
                        and (
                            status_anterior == "Pendente"
                            or status_anterior is None
                        )
                    )
                }
            )

        except Exception as erro:
            print(f"Erro ao processar {item.get('codigo')}")
            print(erro)

            with open("NEXO.log", "a", encoding="utf-8") as f:
                f.write("ERRO NO PROCESSAMENTO\n")
                f.write(f"Código: {item.get('codigo')}\n")
                f.write(f"Mensagem: {item.get('mensagem')}\n")
                f.write(f"Erro: {erro}\n\n")

            continue

    # grava tudo de uma vez
    db.commit()

    # publica somente o que realmente foi salvo
    for item_salvo in restricoes_salvas:

        restricao = item_salvo["restricao"]
        confirmada_agora = item_salvo["confirmada_agora"]

        db.refresh(restricao)

        ## PUBLICAÇÃO DA RESTRIÇÃO NO EVENT BUS
        # Publica os dados operacionais da restrição após o commit.
        # O evento informa também se esta atualização representa
        # uma nova confirmação recebida pela SINAPSE.


        event_bus.publish(
            SINAPSE_RESTRICAO_RECEBIDA,
            {
                "id": restricao.id,
                "codigo": restricao.codigo,

                "dataAtualizacao": restricao.dataAtualizacao,
                "dataCadastro": restricao.dataCadastro,
                "dataRecebimento": restricao.dataRecebimento,

                "origem": restricao.origem,
                "destino": restricao.destino,
                "idLocalOperacao": restricao.idLocalOperacao,

                "mensagem": restricao.mensagem,
                "motivo": restricao.motivo,
                "informacaoAdicional": restricao.informacaoAdicional,

                "status": restricao.status,
                "confirmada_agora": confirmada_agora,

                "usina": restricao.usina,
                "apelido": restricao.apelido,
                "capacidade": restricao.capacidade,
                "regiao": restricao.regiao,
                "tipo_geracao": restricao.tipo_geracao,

                "potencia_observada": restricao.potencia_observada,
                "potencia_restricao": restricao.potencia_restricao,

                "evento": restricao.evento
            }
        )

    with open("NEXO.log", "a", encoding="utf-8") as f:
        f.write(f"Processamento concluído: {len(restricoes_salvas)} restrição(ões) salva(s)\n")
        for item_salvo in restricoes_salvas:
            restricao = item_salvo["restricao"]

            f.write(
                f" - {restricao.usina} | "
                f"{restricao.evento} | "
                f"{restricao.potencia_restricao} MW\n"
            )
        f.write("\n")

    return {"recebido": True, "quantidade": len(restricoes_salvas)}
