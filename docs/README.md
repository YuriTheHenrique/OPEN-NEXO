# Documentação do NEXO

Esta pasta contém a documentação técnica do NEXO (Núcleo de Execução Operacional).

O NEXO é uma plataforma modular desenvolvida em Python, baseada em FastAPI, SQLAlchemy e SQLite, com arquitetura orientada a plugins e carregamento dinâmico de módulos.

---

## Documentação

### Arquitetura

Descrição da arquitetura interna do NEXO, incluindo Core, Loader, sistema de plugins, módulos, persistência e princípios de desacoplamento.

[Arquitetura](architecture.md)

### Guia de desenvolvimento

Orientações para desenvolvimento, organização de módulos, criação de plugins e utilização dos componentes da plataforma.

[Guia de Desenvolvimento](development-guide.md)

### Roadmap

Funcionalidades planejadas, melhorias futuras e evolução prevista para o projeto.

[Roadmap](roadmap.md)

### Glossário

Termos, conceitos e nomenclaturas utilizados no projeto.

[Glossário](glossary.md)

### Decisões arquiteturais

Registro das principais decisões técnicas e arquiteturais tomadas durante o desenvolvimento do NEXO.

[Decisões Arquiteturais](decisions/)

---

## Organização

A documentação acompanha a estrutura modular do projeto.

```text
docs/
├── README.md
├── architecture.md
├── development-guide.md
├── roadmap.md
├── glossary.md
└── decisions/
```

---

## Arquitetura em resumo

O NEXO é dividido conceitualmente em:

```text
NEXO
│
├── Core
│   ├── Inicialização
│   ├── Loader
│   ├── Persistência
│   └── Infraestrutura
│
├── Modules
│   ├── Funcionalidades
│   ├── Plugins
│   ├── Modelos
│   └── Serviços
│
└── App
    ├── Interface
    ├── Templates
    └── Arquivos estáticos
```

O Core fornece a infraestrutura da plataforma, enquanto os módulos concentram as funcionalidades de negócio.

O `loader.py` realiza a descoberta e integração dos módulos disponíveis, permitindo que novas funcionalidades sejam adicionadas sem a necessidade de alterar manualmente o núcleo da aplicação.

Mais detalhes estão disponíveis em [Arquitetura](architecture.md).

---

## Desenvolvimento

Para informações sobre como desenvolver e adicionar funcionalidades ao NEXO, consulte:

[Guia de Desenvolvimento](development-guide.md)

---

## Projeto

O NEXO utiliza uma arquitetura projetada para evolução incremental e modularidade.

Novos recursos devem, sempre que possível, ser implementados como módulos independentes, mantendo o Core estável e reduzindo o acoplamento entre funcionalidades.

---

## Licença

O NEXO é distribuído sob a licença Apache License 2.0.

Consulte o arquivo [`LICENSE`](../LICENSE) na raiz do projeto para os termos completos da licença.
