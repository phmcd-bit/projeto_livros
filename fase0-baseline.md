# Fase 0 — Baseline honesto

**Status:** concluída
**Fonte do histórico:** Skoob (sem API pública, extraído manualmente via screenshots da estante)
**Tamanho:** 50 livros lidos

## Estreiteza por eixo

| Eixo | Estreiteza | Distribuição dominante |
|---|---|---|
| País do autor | 0,23 | Reino Unido (30%), EUA (22%), Canadá (18%), Brasil (18%) — 88% em 4 países |
| Forma | 0,23 | Romance (52%), híbrido/quadrinho-mangá-teatro (28%) — poesia e ensaio em 0% |
| Porte da editora | 0,14 | Média (60%), multinacional (24%), independente (16%) |

**Ressalva metodológica:** a estreiteza foi calculada normalizando pela entropia máxima das categorias que *já apareceram* no histórico, não pelo catálogo completo (que ainda não existe até a Fase 2). Isso tende a subestimar a estreiteza real — o número deve subir quando houver um catálogo de referência.

## Achado principal

O eixo mais estreito é **geografia do autor**: a leitura é quase inteiramente anglófona (Reino Unido/EUA/Canadá) mais um núcleo de autores brasileiros, com presença apenas pontual (1 livro cada) de outros países. **Forma** vem colada, com romance dominando. **Porte da editora**, ao contrário do que o documento do projeto previa como padrão típico, é o eixo *menos* estreito — a leitura passa mais por editoras de porte médio nacional do que por grandes multinacionais.

## Dados brutos

`data/raw/historico_leitura.csv` — colunas: `titulo, autor, data_leitura, nota, abandonei, editora, porte_editora, pais_autor, forma`

Pendências conhecidas nos dados:
- `fonte_descoberta` não preenchida (não bloqueante — só necessária na Fase 6 de avaliação)
- 4 editoras classificadas por porte com baixa confiança (Universo dos Livros, VR, Farol HQ, Maurício de Sousa) — valores atribuídos, não verificados
- Eixo geografia calculado só até nível país; idioma original e década ainda não categorizados
