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

O projeto já tem a arquitetura inicial definida. A próxima meta é produzir a primeira ISO inicializável e instalável.

## Decisões técnicas atuais

- Base: **Debian 13 Trixie**
- Arquitetura inicial: **amd64**
- Desktop: **XFCE 4.20**
- Display server: **Xorg**
- Display manager: **LightDM**
- File manager: **Thunar**
- Terminal: **xfce4-terminal**
- Rede: **NetworkManager**
- Áudio: **PipeWire + WirePlumber**
- Init: **systemd**
- Bootloader: **GRUB**
- Build da ISO: **live-build**
- Instalador: **Calamares**
- Sistema de arquivos padrão da instalação: **ext4**

## Estrutura

```text
.
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
├── .gitignore
├── .github/
│   └── pull_request_template.md
├── docs/
│   ├── philosophy.md
│   ├── architecture.md
│   ├── roadmap.md
│   └── decisions/
│       ├── 0001-debian-base.md
│       ├── 0002-desktop.md
│       ├── 0003-build-and-installer.md
│       ├── 0004-initial-system-profile.md
│       ├── 0005-first-milestone.md
│       └── 0006-software-management.md
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

## Próxima meta

**Construir a primeira ISO funcional.**

Ela não precisa representar o Tip perfeito. Precisa ligar, abrir o XFCE, funcionar como desktop, iniciar o Calamares e instalar corretamente em uma máquina virtual.

Veja [docs/architecture.md](docs/architecture.md) para a arquitetura atual e [docs/roadmap.md](docs/roadmap.md) para a sequência planejada.
