# Contribuindo com o Tip

O Tip está em fase de fundação. Nesta fase, estabilidade do projeto significa **tomar decisões com cuidado antes de escrever código**.

## Regras obrigatórias

1. Leia a documentação em `docs/` antes de alterar a arquitetura.
2. Não introduza uma nova tecnologia, daemon, framework ou camada apenas porque ela parece interessante.
3. Não substitua componentes do Debian sem uma razão documentada.
4. Mudanças de arquitetura devem primeiro atualizar a documentação da decisão.
5. Nunca remover uma funcionalidade existente sem documentar a razão e a alternativa.
6. Evite mudanças gigantes e difíceis de revisar.
7. Um agente não deve apagar ou reescrever arquivos que não são necessários para a tarefa.
8. Antes de marcar uma tarefa como concluída, verifique arquivos alterados, caminhos e referências quebradas.
9. Scripts de build precisam falhar de forma explícita. Não mascarar erros com `|| true` ou equivalentes sem justificativa.
10. O estado do repositório deve continuar reproduzível por outra pessoa.

## Agentes de IA

Agentes podem ajudar a implementar o Tip, mas **não são autoridade sobre a arquitetura**.

Um agente deve:

- trabalhar somente no escopo da tarefa;
- explicar mudanças que afetem outras áreas;
- preservar decisões já documentadas;
- preferir uma pequena alteração correta a uma grande alteração especulativa;
- parar quando uma decisão de arquitetura ainda não foi tomada.

### Regra anti-caos

Se uma tarefa exigir escolher entre duas arquiteturas que ainda não estão documentadas, **não invente uma terceira**. Registre a decisão necessária e aguarde a definição do projeto.

## Antes de enviar uma mudança

Confirme:

- o arquivo está no lugar esperado;
- não há arquivos acidentalmente alterados;
- referências para caminhos existentes continuam válidas;
- a documentação continua coerente;
- o projeto ainda pode ser construído ou testado conforme o estágio atual.

## Filosofia

O objetivo não é fazer o Tip parecer complexo.

O objetivo é fazer o computador parecer simples **sem tirar o controle do usuário**.
