COMMS envia mensagem
         │
Gateway grava no message-queue.json
         │
   Tenta enviar
         │
         ├── sucesso ──> remove da fila
         │
         └── falha
                │
              retry
    5s → 10s → 20s → 40s → 60s...
                │
       ainda dentro de 5 min?
         │              │
        SIM            NÃO
         │              │
       tenta        descarta
     novamente    e registra log