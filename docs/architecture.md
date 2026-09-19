# Arquitetura do NEXO

## Visão geral

O NEXO utiliza uma arquitetura modular baseada em separação de responsabilidades.

O sistema é dividido em três áreas principais:

- **Core**: componentes fundamentais e compartilhados.
- **Modules**: funcionalidades específicas do domínio.
- **App**: camada de apresentação e recursos web.

---

# Estrutura do projeto

```text
NEXO
│
├── app
│   ├── templates
│   └── static
│
├── nexo
│   │
│   ├── core
│   │   ├── app.py
│   │   ├── db.py
│   │   ├── logging.py
│   │   └── events
│   │
│   ├── data
│   │
│   └── modules
│       ├── ativos
│       ├── dashboard
│       ├── sinapse
│       └── teste
```

---

# Core

O pacote `core` contém os serviços fundamentais do NEXO.

Ele concentra componentes utilizados por diferentes módulos da aplicação.

## app.py

Responsável pela criação e configuração da aplicação FastAPI.

Responsabilidades:

- inicialização do sistema;
- registro dos módulos;
- configuração da aplicação;
- carregamento dos componentes principais.

---

## db.py

Responsável pela camada de persistência de dados.

Tecnologias utilizadas:

- SQLAlchemy;
- SQLite.

Bancos atuais:

```text
nexo.db
restricoes.db
```

---

## logging.py

Centraliza a configuração de logs da aplicação.

Objetivos:

- rastreabilidade;
- diagnóstico de problemas;
- acompanhamento da execução.

---

# Sistema de eventos

Local:

```text
nexo/core/events
```

O NEXO possui uma camada interna de eventos para comunicação entre componentes.

A utilização de eventos reduz o acoplamento entre módulos, permitindo que funcionalidades sejam adicionadas sem criar dependências diretas entre elas.

## bus.py

Responsável pela distribuição dos eventos registrados no sistema.

## register.py

Responsável pelo registro de handlers e consumidores de eventos.

## types.py

Define tipos e estruturas utilizadas pelos eventos.

---

# Módulos

Cada funcionalidade do NEXO é organizada em um módulo independente.

Estrutura esperada:

```text
modules/
    modulo/
        router.py
        services.py
        models.py
        schemas.py
        events.py
```

Responsabilidades comuns:

- `router.py`: endpoints e comunicação externa.
- `services.py`: regras de negócio.
- `models.py`: modelos persistidos.
- `schemas.py`: estruturas de dados.
- `events.py`: comunicação baseada em eventos.

---

# Módulo SINAPSE

Local:

```text
nexo/modules/sinapse
```

Responsável pela integração com o SINapse.

## Componentes

### router.py

Define os endpoints responsáveis pelo recebimento das informações.

### parser.py

Interpreta e transforma os dados recebidos.

### models.py

Define os modelos utilizados para persistência.

### services.py

Contém regras de processamento e tratamento dos dados.

---

## Fluxo do módulo SINAPSE

```text
SINapse
   |
   v
router
   |
   v
parser
   |
   v
services
   |
   v
database
```

---

# Módulo Dashboard

Local:

```text
nexo/modules/dashboard
```

Responsável pela disponibilização dos dados operacionais para visualização.

## Componentes

- `router.py`
- `services.py`
- `state.py`
- `events.py`

Responsabilidades:

- disponibilizar informações para a interface;
- processar indicadores;
- manter estado dos dados apresentados;
- reagir a eventos do sistema.

---

# Módulo Ativos

Local:

```text
nexo/modules/ativos
```

Responsável pelo gerenciamento das informações relacionadas aos ativos operacionais.

---

# Fluxo geral do sistema

```text
                 SINAPSE
                    |
                    v
              Módulo Sinapse
                    |
                    v
              Banco de Dados
                    |
                    v
          Eventos internos NEXO
                    |
          +---------+---------+
          |                   |
          v                   v
     Dashboard             Outros módulos
```

---

# Princípios arquiteturais

O NEXO segue alguns princípios:

## Modularidade

Cada funcionalidade deve permanecer isolada em seu próprio módulo.

## Baixo acoplamento

Módulos devem evitar dependências diretas entre si sempre que possível.

## Expansibilidade

A arquitetura deve permitir novos módulos e integrações futuras.

## Separação de responsabilidades

Interface, regras de negócio, persistência e integração devem permanecer organizadas em camadas distintas.