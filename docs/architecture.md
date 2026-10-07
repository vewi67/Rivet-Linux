# Arquitetura do Tip

## Status

Arquitetura inicial definida. O foco imediato é produzir uma primeira ISO utilizável rapidamente.

## Fundação

### Base do sistema

**Debian 13 Trixie** é a base do Tip.

O Tip acompanha a release stable escolhida por nome de suite, usando as atualizações oficiais correspondentes. A release atual de referência é Trixie.

## Perfil inicial

- Arquitetura: amd64
- Desktop: XFCE 4.20
- Display server: Xorg
- Display manager: LightDM
- File manager: Thunar
- Terminal: xfce4-terminal
- Rede: NetworkManager
- Áudio: PipeWire + WirePlumber
- Init: systemd
- Initramfs: initramfs-tools
- Bootloader: GRUB
- Filesystem padrão: ext4

## Build e instalação

O sistema será construído com **Debian live-build** e instalado com **Calamares**.

A primeira imagem deve funcionar em UEFI e, quando suportado pelo fluxo do build, BIOS/legacy.

## Repositórios Debian

A configuração deve usar explicitamente:

- trixie
- trixie-updates
- trixie-security

Com as seções necessárias:

- main
- contrib
- non-free
- non-free-firmware

Firmware não livre poderá ser incluído quando necessário para hardware suportado.

## Software inicial

O objetivo é ter um desktop usável sem transformar a ISO em um depósito de aplicativos.

Software inicial previsto:

- Firefox ESR
- LibreOffice Writer e Calc
- GParted
- Synaptic
- utilitários principais do XFCE
- ferramentas básicas de diagnóstico e rede

Steam, Wine e grandes toolchains de desenvolvimento não serão instalados por padrão.

## Princípios arquiteturais

### 1. Aproveitar antes de substituir

Um componente existente do Debian deve ser mantido quando atende ao objetivo do Tip.

### 2. Camadas claras

```text
Debian
  ↓
Configuração e seleção de componentes
  ↓
Integrações do Tip
  ↓
Experiência do usuário
```

### 3. Falhas devem ser visíveis

O sistema de build e as ferramentas próprias não devem esconder falhas.

### 4. Reprodutibilidade

Mudanças no build devem ser versionadas e reproduzíveis.

### 5. Simplicidade primeiro

Quando uma solução simples e comprovada resolve o problema, ela é a opção padrão.

## O que não entra agora

Não implementar:

- package manager próprio;
- instalador escrito do zero;
- sistema de init próprio;
- kernel próprio;
- desktop próprio;
- coleção de scripts sem responsabilidade definida;
- otimizações agressivas antes de medir.

## Fase seguinte

A próxima implementação deve transformar esta arquitetura em uma **primeira configuração live-build mínima**, seguida de build e teste em VM.

A ISO será tratada como artefato de teste, não como release final.
