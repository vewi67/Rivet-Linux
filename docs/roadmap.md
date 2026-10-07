# Roadmap do Tip

O roadmap prioriza decisões e verificações antes da expansão do sistema.

## Fase 0: Fundação

**Status: em andamento**

- [x] Criar repositório
- [x] Definir nome: Tip
- [x] Definir base: Debian
- [x] Registrar filosofia
- [x] Registrar regras para contribuições e agentes
- [x] Registrar arquitetura inicial
- [ ] Definir release Debian alvo
- [ ] Definir desktop environment
- [ ] Definir instalador
- [ ] Definir sistema de build da ISO

## Fase 1: Primeiro sistema inicializável

Objetivo: produzir a menor imagem útil que represente corretamente a arquitetura escolhida.

- [ ] Configuração inicial do build
- [ ] Root filesystem reproduzível
- [ ] Boot funcional
- [ ] Ambiente gráfico
- [ ] Usuário inicial
- [ ] Rede
- [ ] Áudio
- [ ] Desligamento/reinício
- [ ] Primeiro teste em máquina virtual

## Fase 2: Primeira experiência do Tip

Objetivo: fazer o sistema parecer Tip, sem colocar enfeite por cima de uma base instável.

- [ ] Defaults do desktop
- [ ] Ferramentas essenciais
- [ ] Identidade visual
- [ ] Configurações simples
- [ ] Documentação de uso
- [ ] Teste em hardware real

## Fase 3: Ferramentas próprias

Criar apenas ferramentas que resolvam problemas identificados durante as fases anteriores.

- [ ] Identificar problemas recorrentes
- [ ] Projetar APIs/comportamentos
- [ ] Implementar ferramentas pequenas
- [ ] Adicionar testes
- [ ] Integrar à imagem

## Fase 4: Pré-alfa pública

- [ ] Reprodutibilidade verificada
- [ ] Testes automatizados mínimos
- [ ] Testes manuais documentados
- [ ] Instalação validada
- [ ] Upgrade validado
- [ ] Recuperação de falhas documentada
- [ ] Notas de versão

## Regra de escopo

Uma etapa não deve ser marcada como concluída apenas porque "funciona no computador de quem fez".

Ela precisa ter um caminho de reprodução e uma forma razoável de verificar o resultado.
