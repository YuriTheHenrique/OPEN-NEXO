# Guia de Desenvolvimento do NEXO

## Objetivo

Este documento define padrões e boas práticas para evolução do NEXO.

O objetivo é manter o projeto organizado, modular e preparado para crescimento futuro.

---

# Organização dos módulos

Novas funcionalidades devem ser criadas dentro de:

```text
nexo/modules/
```

Cada módulo deve possuir responsabilidades bem definidas.

Estrutura recomendada:

```text
modulo/
├── __init__.py
├── router.py
├── services.py
├── models.py
├── schemas.py
└── events.py
```

---

# Responsabilidade dos arquivos

## router.py

Responsável pela comunicação externa.

Deve conter:

- endpoints;
- recebimento de dados;
- respostas HTTP;
- validações iniciais.

Evitar:

- regras complexas de negócio;
- consultas extensas ao banco;
- processamento pesado.

---

## services.py

Local onde devem ficar as regras de negócio.

Exemplos:

- processamento de informações;
- cálculos;
- validações;
- orquestração de operações.

---

## models.py

Define estruturas persistidas no banco.

Responsável por:

- tabelas;
- relacionamentos;
- modelos SQLAlchemy.

---

## schemas.py

Define estruturas de entrada e saída de dados.

Exemplos:

- modelos Pydantic;
- validação de payloads;
- contratos da API.

---

## events.py

Define eventos relacionados ao módulo.

Utilizado para comunicação desacoplada entre componentes.

---

# Comunicação entre módulos

O NEXO utiliza eventos internos para evitar dependência direta entre módulos.

Preferir:

```text
Módulo A
   |
   v
Evento
   |
   v
Módulo B
```

Evitar:

```text
Módulo A
   |
   v
Import direto
   |
   v
Módulo B
```

A comunicação por eventos permite adicionar novas funcionalidades sem alterar módulos existentes.

---

# Banco de dados

A camada de banco deve utilizar os componentes existentes em:

```text
nexo/core/db.py
```

Regras:

- utilizar SQLAlchemy;
- evitar acesso direto ao banco dentro de routers;
- manter modelos dentro dos módulos responsáveis.

---

# Logs

Toda funcionalidade relevante deve gerar informações de log.

Os logs devem auxiliar:

- diagnóstico;
- acompanhamento operacional;
- identificação de falhas.

A configuração central fica em:

```text
nexo/core/logging.py
```

---

# Novas funcionalidades

Ao adicionar uma nova funcionalidade:

1. Definir o objetivo do módulo.
2. Criar a estrutura do módulo.
3. Implementar regras em services.
4. Criar endpoints necessários.
5. Registrar eventos quando necessário.
6. Atualizar documentação.

---

# Padrão de commits

Preferir commits pequenos e objetivos.

Exemplos:

```text
Adiciona integração inicial com SINapse

Corrige criação do banco SQLite

Refatora estrutura do dashboard

Adiciona novo indicador operacional
```

Evitar:

```text
Alterações diversas

Mudanças

Atualizações
```

---

# Documentação

Toda funcionalidade relevante deve atualizar a documentação correspondente.

Exemplos:

Nova arquitetura:

```text
docs/architecture.md
```

Nova decisão:

```text
docs/decisions/
```

Novo módulo:

```text
docs/modules/
```

---

# Princípios do projeto

## Clareza antes de complexidade

Soluções simples e compreensíveis devem ser priorizadas.

## Evolução gradual

O NEXO deve crescer conforme as necessidades reais surgirem.

## Código legível

O código deve ser escrito pensando na manutenção futura.

## Responsabilidade definida

Cada componente deve possuir uma função clara dentro do sistema.