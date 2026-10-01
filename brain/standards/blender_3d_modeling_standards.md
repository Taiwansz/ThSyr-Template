# Padroes de Modelagem 3D por Referencia com IA e Blender

Documento mestre de execucao, controle de qualidade e verificacao de ativos 3D baseados em referencias visuais, com suporte a Blender e conexao MCP.

## 1. Compromisso Principal de Construcao
O objetivo e construir uma interpretacao 3D convincente, modular e utilizavel da referencia. Um arquivo que apenas abre no software nao constitui entrega valida.

### Ordem Obrigatoria de Prioridades:
1. **Cobertura correta do escopo solicitado:** Atender integralmente as pecas requeridas.
2. **Silhueta e proporcoes:** A forma externa e a relacao de escala devem corresponder a referencia antes de qualquer detalhamento.
3. **Volumes principais e integracao:** As massas primarias devem se conectar de forma organica ou estruturalmente coerente.
4. **Caracteristicas identificadoras:** Elementos-chave (cristais, runas, frisos, chanfros, telhados).
5. **Materiais, cores e acabamento:** PBR, texturas estilizadas ou shaders procedurais fiéis a paleta.
6. **Organizacao e apresentacao:** Colecoes nomeadas no Blender, origem nos pes/ponto de encaixe, transformacoes aplicadas (`Ctrl+A` -> Apply All Transforms).
7. **Adequacao tecnica e portabilidade:** Exportacao limpa para GLB/FBX sem erros de escala ou normais invertidas.

## 2. Regras Rígidas para Agentes e IA
- **Proibicao de Alucinacao de Validacao:** Se a IA nao possui acesso ativo ao Blender ou ao viewport (via script headless ou MCP), e proibido afirmar que o modelo foi renderizado, verificado ou que ficou visualmente identico.
- **Topologia Limpa:** Preferencia estrita por quads em superficies planas/subdividiveis. Evitar n-gons em zonas de deformacao ou curvatura.
- **Origem e Pivô de Modulos:** Modulos arquiteturais e plataformas devem ter seu ponto de pivô (`Origin`) rigorosamente alinhado ao grid (em $Z=0$ ou no ponto exato de encaixe modular).
- **Consistencia com a Direcao de Arte:** Em projetos 3D e desenvolvimento de jogos, respeitar o aspecto estilizado, cores luminosas e evitar modelos genericos de baixa complexidade desconectados da fantasia visual.
