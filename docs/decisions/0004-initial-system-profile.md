# ADR 0004: Perfil inicial do sistema

- Status: Aceita
- Data: 2026-10-07

## Objetivo

Definir o conjunto mínimo de decisões do sistema necessário para construir a primeira ISO utilizável.

## Base

- Debian 13 Trixie
- Arquitetura inicial: amd64
- Kernel: kernel Debian padrão
- Init: systemd
- Initramfs: initramfs-tools
- Bootloader: GRUB
- Sistema de arquivos padrão do instalador: ext4

O Tip não terá kernel ou init próprios na primeira versão.

## Sessão gráfica

- Xorg
- XFCE
- LightDM
- Thunar
- xfce4-terminal

## Serviços

- NetworkManager para rede
- PipeWire + WirePlumber para áudio
- Serviços do Debian somente quando necessários ao funcionamento do sistema ou hardware

A regra geral é não ativar daemons extras apenas para adicionar recursos.

## Software inicial

A primeira ISO deve conter somente ferramentas necessárias para um computador desktop utilizável.

### Incluído

- Firefox ESR
- LibreOffice Writer e Calc
- utilitários básicos do XFCE
- utilitários de arquivo e armazenamento necessários
- GParted
- Synaptic
- ferramentas básicas de diagnóstico e rede

### Não incluído por padrão

- Steam
- Wine
- dezenas de aplicativos multimídia
- ferramentas de desenvolvimento grandes
- serviços de telemetria próprios
- software duplicado com a mesma função

O usuário poderá instalar esses componentes depois.

## Idioma e localização

A instalação deve oferecer pt-BR e inglês, mas não deve assumir que todo usuário será brasileiro.

O idioma da sessão instalada seguirá a escolha feita no instalador.

## Atualizações

O sistema seguirá as atualizações normais do Debian para a release escolhida. O Tip não terá um mecanismo de atualização próprio na primeira versão.

## Segurança

- Manter o modelo de privilégios do Debian.
- Usuário normal sem acesso root permanente.
- Operações administrativas via sudo/polkit.
- Não criar autenticação própria.

## Filosofia aplicada

A ISO deve entregar um sistema pronto para uso sem transformar pronto para uso em cheio de coisas que o usuário não pediu.
