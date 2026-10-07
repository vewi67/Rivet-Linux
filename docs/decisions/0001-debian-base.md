# ADR 0001: Debian como base

- **Status:** Aceita
- **Data:** 2026-10-07

## Contexto

O Tip precisa de uma base sólida para que o projeto consiga concentrar esforço na experiência e na filosofia da distribuição, em vez de reconstruir componentes fundamentais sem necessidade.

## Decisão

O Tip será baseado em **Debian**.

## Consequências

### Positivas

- Aproveitamento de uma base Linux estabelecida.
- Menor necessidade de criar componentes fundamentais do zero.
- Acesso ao ecossistema de pacotes e ferramentas da base.
- Mais liberdade para construir a identidade do Tip nas camadas acima.

### Negativas

- Algumas decisões do Tip ficarão condicionadas às características e ao ciclo da base escolhida.
- Será necessário definir cuidadosamente quais componentes serão apenas configurados e quais receberão customização do Tip.
- O projeto continuará responsável pela integração e pelos testes da experiência final.

## Limite desta decisão

Esta ADR define apenas a **família de base**.

Ela não define ainda:

- a release Debian;
- o desktop;
- o instalador;
- o sistema de build;
- a seleção final de pacotes.

Essas decisões devem ser registradas separadamente quando forem tomadas.
