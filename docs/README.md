# NEXO

## Visão geral

NEXO é uma plataforma modular desenvolvida para integração, processamento e visualização de informações operacionais.

O projeto surgiu a partir do MVP SINOD, com o objetivo de transformar dados recebidos do SINapse em informações estruturadas, indicadores operacionais e dashboards para acompanhamento.

---

## Objetivos

- Integrar dados operacionais em tempo real.
- Centralizar informações provenientes do SINapse.
- Disponibilizar indicadores visuais.
- Criar uma arquitetura preparada para expansão de módulos.

---

## Arquitetura

O NEXO utiliza uma arquitetura modular organizada em:

- Core: componentes fundamentais do sistema.
- Modules: funcionalidades independentes.
- App: recursos de interface, templates e arquivos estáticos.

Mais detalhes em:
`docs/architecture.md`

---

## Tecnologias

- Python
- FastAPI
- SQLAlchemy
- Jinja2
- SQLite

---

## Estrutura do projeto

NEXO/
├── nexo/
│ ├── core/
│ ├── modules/
│ └── data/
│
├── app/
│ ├── templates/
│ └── static/
│
├── docs/
├── certs/
└── scripts auxiliares

---

## Ferramentas de desenvolvimento

SINSIM	Simulação de mensagens do SINapse
run.bat	Inicialização da aplicação
generate_cert.py	Criação de certificados
logs	Rastreamento de execução

---

## Módulos atuais

| Módulo | Descrição |
|---|---|
| dashboard | Interface de acompanhamento operacional |
| sinapse | Integração com dados do SINapse |
| ativos | Gestão de informações de ativos |
| teste | Ambiente de testes |

---

## Desenvolvimento

Consulte:

`docs/development-guide.md`

