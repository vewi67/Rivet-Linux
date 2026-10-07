# Tip Linux

> **Seu computador. Suas regras.**

Tip é uma distribuição Linux baseada em Debian, construída com uma ideia simples:

**COMPUTADOR É TEU, MEXE NO QUE TU QUER.**

O Tip quer ser simples sem ser limitado. A pessoa deve conseguir usar o sistema sem precisar conhecer Linux profundamente, mas também deve continuar tendo controle real sobre o computador.

## Princípios

- **Controle:** o sistema não deve esconder decisões importantes do usuário.
- **Simplicidade:** tarefas comuns precisam ser fáceis de descobrir e executar.
- **Liberdade:** configurações e componentes não devem ser artificialmente bloqueados.
- **Leveza:** evitar software, serviços e camadas desnecessárias.
- **Compatibilidade:** priorizar o ecossistema Debian e soluções amplamente suportadas.
- **Clareza:** preferir comportamento previsível a automações mágicas.

## Estado atual

**Pré-alfa.**

Este repositório contém a fundação e as decisões iniciais do projeto. Ainda não existe uma imagem instalável do Tip.

## Base

- Debian
- Arquitetura de sistema ainda em definição detalhada
- Desktop, instalador, seleção de pacotes e componentes próprios serão decididos antes da implementação da imagem

## Estrutura

```text
.
├── README.md
├── CONTRIBUTING.md
├── .gitignore
├── docs/
│   ├── philosophy.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── decisions/
│       └── 0001-debian-base.md
├── build/
│   └── README.md
├── config/
│   └── README.md
└── scripts/
    └── README.md
```

## Regra de ouro para desenvolvimento

> **Não implementar antes de definir. Não substituir uma solução estável sem motivo. Não quebrar o que já funciona para ganhar complexidade.**

O Tip será construído em etapas pequenas, verificáveis e reversíveis.

## Status das decisões

| Área | Situação |
| --- | --- |
| Nome | Definido |
| Base | **Debian** |
| Filosofia | Definida |
| Desktop | Em decisão |
| Instalador | Em decisão |
| Sistema de build | Em decisão |
| Seleção de pacotes | Em decisão |
| Ferramentas próprias | Em decisão |
| Identidade visual | Em andamento |
| ISO | Ainda não iniciada |

Veja [docs/architecture.md](docs/architecture.md) para a arquitetura atual e [docs/roadmap.md](docs/roadmap.md) para a sequência planejada.
