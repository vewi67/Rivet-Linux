# Instruções para agentes do Tip

Estas regras valem para qualquer agente de IA que modificar este repositório.

## Prioridade

1. Preserve o comportamento e as decisões já documentadas.
2. Faça apenas a mudança necessária para a tarefa.
3. Não invente arquitetura para preencher lacunas.
4. Não apague ou reescreva arquivos sem necessidade.
5. Sempre valide o resultado depois da alteração.

## Antes de editar

Leia:

- `README.md`
- `CONTRIBUTING.md`
- `docs/philosophy.md`
- `docs/architecture.md`
- a ADR relacionada, quando existir

Depois identifique exatamente quais arquivos precisam mudar.

## Durante a edição

- Prefira alterações pequenas e localizadas.
- Preserve nomes, caminhos e interfaces existentes.
- Não adicione dependências sem justificar.
- Não execute mudanças destrutivas.
- Não force branches ou histórico.
- Não silencie erros.
- Não faça "limpeza" de código fora do escopo.

## Arquitetura

O Tip é baseado em Debian.

Decisões ainda não tomadas não podem ser tratadas como decisões tomadas. Em especial, não escolher silenciosamente desktop, instalador, sistema de build ou ferramentas próprias.

Quando uma mudança representar uma decisão arquitetural, primeiro documente a decisão ou peça que ela seja definida.

## Build e testes

Quando houver um sistema de build:

- falhas devem interromper o processo;
- resultados intermediários devem ser identificáveis;
- comandos destrutivos devem exigir uma justificativa clara;
- um build que não passou nos testes não deve ser marcado como concluído.

## Antes de terminar

Verifique:

- arquivos alterados;
- caminhos;
- referências entre arquivos;
- sintaxe dos arquivos modificados;
- testes disponíveis;
- documentação afetada.

Depois informe exatamente o que mudou e o que ainda não foi validado.

## Regra fundamental

**Não transforme uma tarefa pequena em uma reescrita do Tip.**
