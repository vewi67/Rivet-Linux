# Arquitetura do Tip

## Status

Documento inicial. Ele registra o que já foi decidido e separa isso do que ainda precisa ser definido.

## Fundamento

### Base do sistema

**Debian** é a base do Tip.

Isso é uma decisão de arquitetura, não apenas uma preferência. O Tip deve aproveitar o trabalho existente da base sempre que isso atender aos objetivos do projeto.

## Princípios arquiteturais

### 1. Aproveitar antes de substituir

Um componente existente do Debian deve ser mantido quando:

- atende ao objetivo;
- é suficientemente simples de administrar;
- tem manutenção adequada;
- não entra em conflito com a filosofia do Tip.

Um componente próprio só deve existir quando resolver um problema real do Tip melhor do que a solução existente.

### 2. Camadas claras

A arquitetura futura deve poder ser entendida aproximadamente assim:

```text
Debian
  ↓
Configuração e seleção de componentes
  ↓
Integrações do Tip
  ↓
Experiência do usuário
```

Cada camada precisa ter uma responsabilidade clara.

### 3. Falhas devem ser visíveis

O sistema de build e as ferramentas próprias não devem esconder falhas. Erros precisam aparecer cedo, com mensagens úteis.

### 4. Reprodutibilidade

Duas construções feitas a partir da mesma revisão e dos mesmos parâmetros devem buscar produzir o mesmo resultado, dentro das limitações normais do ecossistema de pacotes.

## Decisões ainda abertas

As seguintes decisões devem ser tomadas **antes da primeira ISO funcional**:

- versão/release Debian alvo;
- desktop environment;
- gerenciador de login;
- instalador;
- conjunto inicial de pacotes;
- política de atualizações;
- sistema de build da ISO;
- configuração padrão de rede;
- configuração de áudio;
- políticas de serviços em segundo plano;
- ferramentas próprias do Tip;
- estratégia de testes em máquina virtual e hardware real;
- identidade visual e assets distribuídos na ISO.

## O que não deve ser feito ainda

Não implementar agora:

- um package manager próprio;
- um instalador escrito do zero;
- um sistema de init próprio;
- um kernel próprio;
- ferramentas de configuração só por estética;
- uma coleção grande de scripts sem responsabilidade definida.

Essas coisas aumentariam a superfície de falha antes de o núcleo do Tip estar decidido.

## Critério de aceitação da arquitetura

Antes de começar a automatizar a geração da ISO, deve ser possível explicar:

1. o que vem do Debian;
2. o que é configuração do Tip;
3. o que é software próprio do Tip;
4. como a imagem é construída;
5. como ela é testada;
6. como uma mudança pode ser revertida.
