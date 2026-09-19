# ADR-002: Uso de eventos internos para comunicação entre módulos

## Status

Aceito

## Data

Agosto de 2026

---

## Contexto

Com a criação de múltiplos módulos independentes, surgiu a necessidade de comunicação entre componentes.

Uma abordagem baseada em chamadas diretas entre módulos poderia criar dependências fortes.

Exemplo de problema:

```
Dashboard importa Sinapse

Sinapse importa Dashboard

Resultado:
alto acoplamento
```

Esse modelo dificultaria alterações futuras.

---

## Decisão

Implementar um sistema interno de eventos.

Local:

```
nexo/core/events
```

Os módulos podem publicar e consumir eventos sem conhecer diretamente outros módulos.

Fluxo:

```
Módulo A
    |
    v
 Evento
    |
    v
Módulo B
```

---

## Consequências positivas

- Menor acoplamento.
- Maior flexibilidade.
- Facilidade para adicionar consumidores.
- Melhor separação entre funcionalidades.

---

## Consequências negativas

- Fluxo menos direto de entender inicialmente.
- Necessidade de documentar eventos existentes.
- Maior cuidado com rastreamento e logs.

---

## Considerações futuras

O sistema de eventos pode evoluir para suportar:

- filas assíncronas;
- eventos persistidos;
- integração com sistemas externos.