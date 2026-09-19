# Arquitetura do NEXO

O NEXO (Núcleo de Execução Operacional) é uma plataforma modular desenvolvida em Python, baseada em FastAPI, SQLAlchemy e SQLite.

A arquitetura foi projetada para permitir que funcionalidades sejam adicionadas como módulos independentes, sem exigir alterações no núcleo da aplicação.

O princípio central é:

> O Core fornece infraestrutura. Os módulos fornecem funcionalidades.

---

## 1. Visão geral

A aplicação é organizada em três áreas principais:

```text
NEXO
│
├── Core
│   ├── Inicialização da aplicação
│   ├── Loader
│   ├── Banco de dados
│   ├── Configuração
│   ├── Eventos e infraestrutura
│   └── Serviços compartilhados
│
├── Modules
│   ├── Ativos
│   ├── COMMS
│   ├── ONS
│   ├── SINAPSE
│   └── Outros módulos
│
└── App
    ├── Interface web
    ├── Templates
    ├── Arquivos estáticos
    └── Recursos compartilhados da aplicação
```

O Core não deve conhecer individualmente os módulos de negócio.

A descoberta e integração dos módulos é realizada dinamicamente pelo sistema de plugins.

---

## 2. Core

O Core contém os componentes responsáveis pela infraestrutura do NEXO.

Entre suas responsabilidades estão:

- inicialização da aplicação;
- configuração;
- gerenciamento da persistência;
- carregamento dos módulos;
- registro de rotas fornecidas pelos módulos;
- registro de tarefas em segundo plano;
- infraestrutura compartilhada;
- mecanismos de integração entre componentes.

O Core deve permanecer independente das regras específicas de cada módulo.

### Estrutura aproximada

```text
nexo/
└── core/
    ├── app.py
    ├── loader.py
    └── outros componentes de infraestrutura
```

A estrutura pode evoluir conforme a necessidade do projeto.

---

## 3. Loader

O `loader.py` é responsável pela descoberta e integração dos módulos disponíveis.

Localização:

```text
nexo/core/loader.py
```

Durante a inicialização da aplicação, o loader procura os módulos disponíveis em:

```text
nexo/modules/
```

A partir da estrutura encontrada, o loader pode identificar e carregar componentes fornecidos pelos módulos, como:

- `models.py`;
- `plugin.py`;
- rotas;
- cards da página inicial;
- integrações;
- tarefas em segundo plano.

Isso permite que o Core permaneça desacoplado dos módulos de negócio.

### Fluxo simplificado

```text
                 Inicialização
                       │
                       ▼
                    core/app.py
                       │
                       ▼
                   core/loader.py
                       │
             ┌─────────┼─────────┐
             │         │         │
             ▼         ▼         ▼
          Módulo A  Módulo B  Módulo C
             │         │         │
             └─────────┼─────────┘
                       │
                       ▼
                NEXO inicializado
```

O objetivo é permitir que um módulo seja adicionado sem a necessidade de criar imports específicos no Core.

---

## 4. Sistema de plugins

Os módulos do NEXO seguem um modelo de plugins.

Um módulo pode fornecer diferentes componentes conforme sua necessidade.

Uma estrutura típica é:

```text
nexo/modules/
└── modulo/
    ├── __init__.py
    ├── plugin.py
    ├── models.py
    ├── router.py
    ├── services.py
    ├── schemas.py
    └── events.py
```

Nem todos os arquivos são obrigatórios.

Cada módulo deve possuir somente os componentes necessários para sua funcionalidade.

### `plugin.py`

O `plugin.py` é utilizado para declarar a integração do módulo com o NEXO.

Conforme a necessidade do módulo, ele pode fornecer informações como:

- identificação do módulo;
- rotas;
- cards da página inicial;
- integrações;
- tarefas em segundo plano;
- configurações específicas;
- outros recursos reconhecidos pelo loader.

### `models.py`

Quando necessário, o módulo pode fornecer modelos SQLAlchemy através de `models.py`.

O loader identifica esses modelos e os integra à camada de persistência da aplicação.

### Tarefas em segundo plano

Módulos que necessitam executar tarefas periódicas ou contínuas podem disponibilizar:

```python
get_background_tasks()
```

O loader identifica essa função e registra as tarefas durante a inicialização da aplicação.

---

## 5. Princípio de desacoplamento

O Core não deve possuir imports diretos dos módulos de negócio.

Evitar:

```python
from nexo.modules.sinapse import ...
from nexo.modules.ativos import ...
from nexo.modules.comms import ...
```

O módulo deve ser descoberto pelo loader.

Isso permite que os módulos sejam:

- adicionados;
- removidos;
- modificados;
- desenvolvidos de forma independente;

sem exigir alterações no núcleo da aplicação.

O objetivo é manter a seguinte relação:

```text
                CORE
                  │
                  │ infraestrutura
                  ▼
               LOADER
                  │
        ┌─────────┼─────────┐
        ▼         ▼         ▼
      Módulo    Módulo    Módulo
        A         B         C
```

Dependências entre módulos devem ser utilizadas somente quando realmente necessárias e, preferencialmente, através de interfaces, eventos ou mecanismos de integração definidos pela aplicação.

---

## 6. Módulos

Os módulos concentram as regras de negócio do NEXO.

Localização:

```text
nexo/modules/
```

Cada módulo deve ser responsável por uma área funcional específica.

Exemplos:

```text
nexo/modules/
├── ativos/
├── comms/
├── ons/
└── sinapse/
```

Um módulo pode conter:

```text
router.py
```

Responsável pelas rotas HTTP relacionadas ao módulo.

```text
services.py
```

Responsável pelas regras e operações internas do módulo.

```text
models.py
```

Responsável pelos modelos de persistência.

```text
schemas.py
```

Responsável pelos modelos de entrada e saída de dados.

```text
events.py
```

Responsável por eventos e integrações internas quando utilizados.

```text
plugin.py
```

Responsável pela declaração da integração do módulo com o Core.

Nenhum desses componentes precisa existir quando não for necessário.

---

## 7. Persistência

A camada de persistência utiliza SQLAlchemy sobre SQLite por padrão.

A aplicação mantém a persistência desacoplada das regras de negócio, permitindo que os módulos utilizem modelos próprios sem que o Core precise conhecer previamente cada modelo.

A configuração da persistência deve permanecer centralizada na infraestrutura da aplicação.

O uso de SQLite atende ao funcionamento local e pode ser substituído ou expandido conforme os requisitos de implantação.

---

## 8. Aplicação

O `app.py` é responsável pela inicialização da aplicação e pela coordenação dos componentes de infraestrutura.

Seu papel inclui, entre outros:

- criar a aplicação FastAPI;
- inicializar o ciclo de vida da aplicação;
- inicializar a persistência;
- executar o carregamento dos módulos;
- iniciar tarefas de infraestrutura;
- disponibilizar a aplicação para execução.

A aplicação não deve registrar manualmente cada módulo de negócio.

O fluxo esperado é:

```text
app.py
  │
  ├── Inicialização
  │
  ├── Banco de dados
  │
  ├── Loader
  │      │
  │      ├── Descobre módulos
  │      ├── Carrega plugins
  │      ├── Carrega modelos
  │      ├── Registra rotas
  │      └── Registra tarefas
  │
  └── Aplicação pronta
```

---

## 9. Interface web

A interface web é fornecida pela camada de aplicação e pelos recursos específicos de cada módulo.

Os módulos podem disponibilizar:

- páginas;
- APIs;
- cards;
- indicadores;
- dashboards;
- integrações;
- recursos específicos de sua área funcional.

A interface deve consumir as funcionalidades através das APIs e componentes fornecidos pela aplicação, evitando acoplamento direto às estruturas internas dos módulos.

---

## 10. Exemplo: módulo SINAPSE

O SINAPSE é um exemplo de módulo funcional do NEXO.

Seu fluxo pode ser representado de forma simplificada como:

```text
Entrada
   │
   ▼
Router
   │
   ▼
Parser / validação
   │
   ▼
Services
   │
   ├──────────────► Persistência
   │
   └──────────────► Eventos / integrações
                         │
                         ▼
                    Outros recursos
```

O SINAPSE utiliza os recursos fornecidos pelo Core, mas suas regras de negócio permanecem dentro do próprio módulo.

Esse modelo permite que outros módulos sejam desenvolvidos seguindo o mesmo princípio sem precisar reproduzir a implementação interna do SINAPSE.

---

## 11. Comunicação entre componentes

A comunicação dentro do NEXO pode ocorrer através de diferentes mecanismos, conforme o caso:

- chamadas internas;
- APIs;
- eventos;
- tarefas em segundo plano;
- camada de persistência;
- integrações fornecidas pelos plugins.

A escolha do mecanismo deve considerar o nível de acoplamento necessário.

O objetivo é evitar que um módulo precise conhecer detalhes internos de outro módulo para executar sua função.

---

## 12. Fluxo geral da arquitetura

De forma simplificada:

```text
                         NEXO
                           │
              ┌────────────┴────────────┐
              │                         │
             Core                       App
              │                         │
              │                         ├── Interface
              │                         ├── Templates
              │                         └── Static
              │
           Loader
              │
      ┌───────┼────────┐
      │       │        │
      ▼       ▼        ▼
   Módulo   Módulo   Módulo
      A       B        C
      │       │        │
      └───────┼────────┘
              │
       APIs / Eventos /
        Integrações
              │
              ▼
          Persistência
```

---

## 13. Princípios arquiteturais

A arquitetura do NEXO segue alguns princípios fundamentais.

### Modularidade

Cada funcionalidade deve permanecer concentrada em seu próprio módulo sempre que possível.

### Desacoplamento

O Core não deve depender diretamente das regras de negócio dos módulos.

### Autodescoberta

Novos módulos devem poder ser integrados através do mecanismo de loader sem alterações manuais no Core.

### Responsabilidade única

Cada componente deve possuir uma responsabilidade clara.

### Extensibilidade

A arquitetura deve permitir a criação de novos módulos sem a necessidade de modificar a estrutura fundamental da aplicação.

### Separação de infraestrutura e negócio

O Core fornece infraestrutura.

Os módulos implementam as regras de negócio.

### Evolução incremental

A arquitetura deve permitir que novos recursos sejam adicionados sem exigir refatorações amplas da aplicação existente.

---

## 14. Objetivo arquitetural

O objetivo final é manter o NEXO como uma plataforma extensível na qual o núcleo permaneça pequeno e estável, enquanto novas funcionalidades possam ser desenvolvidas como módulos independentes.

Em termos simplificados:

```text
              CORE ESTÁVEL
                   │
                 LOADER
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    PLUGIN       PLUGIN      PLUGIN
       │           │           │
       ▼           ▼           ▼
   FUNÇÃO A     FUNÇÃO B    FUNÇÃO C
```

Dessa forma, o crescimento da aplicação ocorre principalmente pela adição de módulos, e não pelo aumento da complexidade do núcleo.
