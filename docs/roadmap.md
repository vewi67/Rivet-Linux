# Roadmap do Tip

O roadmap prioriza uma ISO utilizável rapidamente. Complexidade só entra depois que o caminho básico estiver funcionando.

## Fase 0: Fundação

**Status: concluída**

- [x] Criar repositório
- [x] Definir nome: Tip
- [x] Definir base: Debian 13 Trixie
- [x] Registrar filosofia
- [x] Registrar regras para contribuições e agentes
- [x] Registrar arquitetura inicial
- [x] Definir arquitetura amd64
- [x] Definir XFCE + Xorg
- [x] Definir LightDM, NetworkManager e PipeWire
- [x] Definir live-build
- [x] Definir Calamares
- [x] Definir perfil inicial de aplicativos
- [x] Definir critérios da primeira ISO

## Fase 1: Primeira ISO funcional

**Status: próxima**

Objetivo: ter um sistema que inicializa, abre o desktop e pode ser instalado em uma VM.

- [ ] Criar configuração mínima do live-build
- [ ] Configurar fontes e repositórios Debian
- [ ] Definir seleção inicial de pacotes
- [ ] Configurar identidade inicial do Tip
- [ ] Integrar Calamares
- [ ] Gerar primeira ISO
- [ ] Testar boot em VM
- [ ] Testar XFCE
- [ ] Testar rede
- [ ] Testar áudio
- [ ] Testar instalação
- [ ] Testar primeiro boot instalado
- [ ] Testar atualização do sistema

## Fase 2: Primeira experiência do Tip

- [ ] Refinar defaults do XFCE
- [ ] Identidade visual
- [ ] Ferramentas simples do Tip
- [ ] Documentação de uso
- [ ] Teste em hardware real

## Fase 3: Ferramentas próprias

Criar apenas ferramentas que resolvam problemas identificados durante o uso.

- [ ] Identificar problemas reais
- [ ] Projetar soluções
- [ ] Implementar pequenas ferramentas
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

Uma etapa não está concluída apenas porque funciona na máquina de quem fez.

Ela precisa ter um caminho de reprodução e uma forma razoável de verificar o resultado.
