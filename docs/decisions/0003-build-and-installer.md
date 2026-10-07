# ADR 0003: live-build e Calamares

- Status: Aceita
- Data: 2026-10-07

## Contexto

O objetivo imediato do Tip é chegar a um sistema inicializável e instalável o mais cedo possível, sem criar uma cadeia de build própria antes de termos uma ISO funcional.

## Decisão

### Build

Usaremos Debian live-build para construir a imagem.

### Instalação

A ISO usará Calamares como instalador gráfico.

### Boot

A primeira imagem terá como alvo amd64 e suportará inicialização por UEFI, mantendo BIOS/legacy quando suportado pelo fluxo do build.

### Repositórios

A imagem usará as suites do Debian explicitamente por nome, começando com:

- trixie
- trixie-updates
- trixie-security

As seções necessárias serão main, contrib, non-free e non-free-firmware.

## Por que não escrever nosso próprio instalador

Calamares já fornece uma estrutura de instalação gráfica adequada a sistemas baseados em Debian. O Tip deve customizar a experiência e a configuração, não reconstruir particionamento, criação de usuário e instalação de sistema do zero.

## Por que não criar nosso próprio sistema de build

live-build já resolve a construção de sistemas Live baseados em Debian. Começar com ele reduz código próprio e acelera a chegada da primeira ISO.

## Regra

Qualquer substituição futura de live-build ou Calamares precisa demonstrar um problema concreto que não possa ser resolvido pela configuração existente.
