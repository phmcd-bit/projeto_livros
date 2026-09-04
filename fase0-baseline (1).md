# Fase 0 — Baseline honesto

**Status:** concluída
**Fonte do histórico:** Skoob (sem API pública, extraído manualmente via screenshots da estante)
**Tamanho:** 52 livros lidos

## Estreiteza por eixo

| Eixo | Estreiteza | Distribuição dominante |
|---|---|---|
| País do autor | 0,234 | Reino Unido (29%), EUA (23%), Canadá (17%), Brasil (17%) — 86% em 4 países; demais (México, Países Baixos, Alemanha, França, Irlanda, Japão, Tchéquia) com 1 livro cada |
| Forma | 0,225 | Romance (52%), híbrido/quadrinho-mangá-teatro (27%), novela (10%), não-ficção narrativa (6%), contos (6%) — poesia e ensaio em 0% |
| Porte da editora | 0,119 | Média (58%), multinacional (25%), independente (17%) |

**Ressalva metodológica:** a estreiteza foi calculada normalizando pela entropia máxima das categorias que *já apareceram* no histórico, não pelo catálogo completo (que ainda não existe até a Fase 2). Isso tende a subestimar a estreiteza real — o número deve subir quando houver um catálogo de referência.

## Achado principal

O eixo mais estreito é **geografia do autor**: a leitura é quase inteiramente anglófona (Reino Unido/EUA/Canadá) mais um núcleo de autores brasileiros, com presença apenas pontual (1 livro cada) de outros países. **Forma** vem colada, com romance dominando. **Porte da editora**, ao contrário do que o documento do projeto previa como padrão típico, é o eixo *menos* estreito — a leitura passa mais por editoras de porte médio nacional do que por grandes multinacionais.

## Dados brutos

`data/raw/historico_leitura.csv` — colunas: `titulo, autor, data_leitura, nota, abandonei, editora, porte_editora, pais_autor, forma`

Pendências conhecidas nos dados:
- `fonte_descoberta` não preenchida (não bloqueante — só necessária na Fase 6 de avaliação)
- 4 editoras classificadas por porte com baixa confiança (Universo dos Livros, VR, Farol HQ, Maurício de Sousa) — valores atribuídos, não verificados
- Eixo geografia calculado só até nível país; idioma original e década ainda não categorizados

## Histórico de revisões
- v2: corrigido país do autor de Franz Kafka (Alemanha → Tchéquia); adicionados "Daisy Jones & The Six" e "A Metamorfose"; total subiu de 50 para 52 livros
