# ADR 0006: Gerenciamento de software e atualizações

- Status: Aceita
- Data: 2026-10-07

## Gerenciamento de pacotes

O Tip usará **APT + dpkg**, herdados do Debian.

Não haverá package manager próprio na primeira versão.

## Interface

A primeira ISO terá:

- APT para quem prefere terminal;
- Synaptic como interface gráfica simples para pacotes.

No futuro, uma ferramenta própria só será criada se existir um problema de usabilidade que essas soluções não resolvam bem.

## Flatpak

Flatpak não será obrigatório nem instalado por padrão na primeira ISO.

A prioridade será o repositório Debian, porque isso reduz duplicação de sistemas de atualização e de fontes de software.

Flatpak poderá ser oferecido posteriormente como opção documentada.

## Atualizações

O Tip usará as atualizações oficiais do Debian para a release Trixie.

Não haverá um serviço de atualização próprio nesta fase.

As atualizações de segurança e correções devem permanecer compatíveis com o fluxo normal do Debian.

## Repositórios de terceiros

A ISO não adicionará repositórios de terceiros por padrão.

Repositórios externos poderão ser adicionados pelo usuário.

## Shell

O shell padrão será **Bash**, seguindo o Debian.

O terminal não será removido ou escondido da interface.

## Política

O Tip deve ter poucas fontes de software, claras e previsíveis.

**Uma ferramenta conhecida e confiável é preferível a uma camada própria sem necessidade.**
