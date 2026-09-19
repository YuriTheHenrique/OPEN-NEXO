# ADR-001: Adoção de arquitetura modular

## Status

Aceito

## Data

Agosto de 2026

---

## Contexto

O NEXO iniciou como um MVP desenvolvido para demonstrar a transformação de dados operacionais recebidos do SINapse em informações estruturadas e dashboards.

Com a evolução do projeto, novas funcionalidades começaram a surgir, tornando necessário organizar melhor o código e separar responsabilidades.

Uma arquitetura concentrada em poucos arquivos dificultaria:

- manutenção;
- expansão;
- testes;
- inclusão de novas funcionalidades.

---

## Decisão

Adotar uma arquitetura modular organizada por domínio.

Cada funcionalidade deve possuir seu próprio módulo dentro de:

```
nexo/modules/
```

Exemplos atuais:

```
dashboard
sinapse
ativos
teste
```

---

## Consequências positivas

- Maior organização do código.
- Separação clara de responsabilidades.
- Facilidade para adicionar novos módulos.
- Redução de dependências entre funcionalidades.
- Melhor manutenção futura.

---

## Consequências negativas

- Maior quantidade de arquivos.
- Necessidade de padronização.
- Maior complexidade inicial em comparação com uma aplicação simples.

---

## Considerações futuras

Novos módulos devem seguir a estrutura definida no guia de desenvolvimento.

A arquitetura pode evoluir conforme novas necessidades surgirem.