# ADR 0002: XFCE como desktop inicial

- Status: Aceita
- Data: 2026-10-07

## Contexto

A primeira versão do Tip precisa ser utilizável rapidamente, funcionar bem em hardware variado e manter a interface simples sem bloquear a personalização.

## Decisão

O desktop inicial do Tip será XFCE 4.20, sobre Xorg.

## Por que XFCE

- É leve e adequado para hardware modesto.
- Tem uma interface convencional e fácil de entender.
- O gerenciador de janelas XFWM oferece recursos de organização de janelas sem exigir outro compositor.
- O desktop é modular e bastante configurável.
- O conjunto existe diretamente no Debian 13.

O Tip não tentará criar um desktop próprio na primeira versão.

## Componentes principais

- Desktop: XFCE
- Display server: Xorg
- Display manager: LightDM
- File manager: Thunar
- Terminal: xfce4-terminal
- Network UI: NetworkManager + applet GTK

## Decisão futura

Wayland poderá ser avaliado depois, mas não entra na primeira versão por necessidade de estabilidade e velocidade de entrega.
