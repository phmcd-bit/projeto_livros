# Registro completo do projeto — Sistema de Recomendação de Livros

Este documento explica, passo a passo e em detalhe, tudo o que foi feito no projeto até agora: decisões tomadas, arquivos criados, código completo e resultados obtidos. Serve como referência única para retomar o projeto a qualquer momento.

---

## 0. Contexto do projeto

Objetivo original (definido no documento de especificação `projeto-recomendacao-livros.md`): construir um sistema de recomendação de livros cujo objetivo não é prever o que o usuário mais vai gostar, mas **maximizar gostar sujeito a uma distância mínima do histórico de leitura** — ou seja, combater ativamente o viés de bolha, popularidade e cânone literário.

O projeto é dividido em fases:
- **Fase 0** — Baseline honesto (medir a "estreiteza" atual da própria leitura)
- **Fase 1** — Recomendação ruim ponta a ponta (fazer o pipeline inteiro funcionar, mesmo que mal)
- Fase 2 em diante — catálogo real, enriquecimento via LLM, diversificação via MMR, grafo de serendipidade, agente de feedback (ainda não iniciadas)

Este documento cobre **Fase 0** (concluída) e **Fase 1** (concluída) em detalhe.

---

## 1. Estrutura de pastas do repositório

```
recomendacao-livros/
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── historico_leitura.csv       ← histórico de leitura pessoal (Fase 0)
│   │   └── catalogo_semente.csv        ← catálogo semente (Fase 1)
│   └── interim/
│       ├── sinopses_historico.csv      ← sinopses consolidadas do histórico
│       ├── sinopses_historico_lote1-4.csv  ← lotes brutos (histórico do processo)
│       ├── sinopses_catalogo.csv       ← sinopses consolidadas do catálogo
│       └── sinopses_catalogo_lote1-8.csv   ← lotes brutos (histórico do processo)
├── db/
│   └── livros.sqlite                   ← banco gerado (NÃO vai pro git, está no .gitignore)
├── src/
│   ├── ingest/
│   │   ├── seed_catalogo.py            ← gera catalogo_semente.csv
│   │   └── load_db.py                  ← carrega os CSVs no SQLite
│   ├── schema/
│   │   └── schema_fase1.sql            ← schema mínimo do banco (Fase 1)
│   └── rank/
│       └── similaridade_sinopse.py     ← calcula similaridade e gera as recomendações
└── docs/
    ├── fase0-baseline.md               ← resumo de fechamento da Fase 0
    └── registro-completo.md            ← este arquivo
```

**Lógica de pastas:**
- `data/raw/` → dados brutos/fonte, editados manualmente por você
- `data/interim/` → dados processados por mim (sinopses, resultados intermediários)
- `src/ingest/` → scripts que geram ou carregam dados
- `src/schema/` → definição do banco
- `src/rank/` → scripts de ranking/similaridade/recomendação
- `db/` → banco SQLite gerado — nunca comitar, está no `.gitignore`, é recriado a qualquer momento rodando `load_db.py`
- `docs/` → documentação e resumos de cada fase

---

## 2. Fase 0 — Baseline honesto

### 2.1 Objetivo

Medir, antes de qualquer recomendação, o quão "estreita" já é a sua leitura ao longo de eixos de diversidade (país do autor, forma literária, porte da editora), pra ter um número de referência que a Fase 6 (avaliação) vai comparar depois de o sistema estar rodando.

### 2.2 Fonte dos dados

Seu histórico de leitura está no **Skoob**, que não tem API pública. A exportação foi feita **manualmente**:
1. Você enviou 4 capturas de tela da sua estante "lido" no Skoob
2. Eu li os livros visíveis em cada captura (título, autor quando aparecia, nota em estrelas)
3. Você esclareceu o significado das cores de marcador do Skoob: **verde = lido**, **azul = quero ler**, **laranja = lendo agora** — só os verdes entraram no histórico
4. Ao longo da conversa, você foi corrigindo e completando manualmente o CSV (editando localmente e reenviando), e eu fui sincronizando

### 2.3 Estrutura de `data/raw/historico_leitura.csv`

| Coluna | Descrição |
|---|---|
| `titulo` | Título do livro |
| `autor` | Autor |
| `data_leitura` | Ano/mês de leitura (você preencheu com o ano) |
| `nota` | Sua nota no Skoob (0-5) |
| `abandonei` | 1 se abandonou, 0 se terminou |
| `editora` | Nome da editora/selo |
| `porte_editora` | Classificação: `multinacional`, `media` ou `independente` |
| `pais_autor` | País de origem do autor |
| `forma` | `romance`, `novela`, `contos`, `poesia`, `ensaio`, `hibrido` ou `nao_ficcao_narrativa` |

Coluna `fonte_descoberta` (como você descobriu o livro — booktok, amigo, etc.) foi **decidida propositalmente não preencher agora**: não entra na fórmula de estreiteza, só é necessária na Fase 6 (avaliação comparativa depois/antes do sistema).

### 2.4 Processo de correção iterativa

O histórico passou por várias rodadas de revisão, todas registradas na conversa:
- Identificação de um título ilegível numa captura → confirmado como **"O Jardim Secreto"** (Frances Hodgson Burnett), via nome parcial do autor visível na capa ("...NCES HODGSON BURNETT")
- Correção do país de **Franz Kafka**: estava como "Alemanha", corrigido para **"Tchéquia"** (nasceu em Praga, então Império Austro-Húngaro — escrevia em alemão, mas não era alemão)
- Correção do título da Clarice Lispector: estava catalogado erroneamente como uma biografia ("Clarice"), corrigido para **"Perto do Coração Selvagem"** (romance de estreia da própria Clarice)
- Adição de "Daisy Jones & The Six" e "A Metamorfose" com pesquisa da editora **Paralela** (confirmada como selo do Grupo Companhia das Letras, 70% Penguin Random House → `multinacional`)
- Adição de 5 livros extras via nova captura (Junji Ito, Heartstopper volumes 1-4)
- Correção da editora da Turma da Mônica Jovem: de "Maurício de Sousa" para **"MilkShakespeare"**

**Tamanho final: 52 livros lidos.**

### 2.5 Mapeamento editora → porte

Como o CSV tinha o **nome real** de cada editora (não a categoria), foi feita uma pesquisa individual via `web_search` pra classificar cada uma em `multinacional`, `media` ou `independente`, com nível de confiança registrado:

| Editora | Porte | Confiança | Observação |
|---|---|---|---|
| Seguinte | multinacional | alta | selo do Grupo Companhia das Letras (70% Penguin Random House) |
| Companhia das Letrinhas | multinacional | alta | idem |
| Paralela | multinacional | alta | idem |
| Scipione | multinacional | alta | Grupo Cogna/Somos Educação |
| Ática | multinacional | alta | Grupo Cogna/Somos Educação |
| Moderna | multinacional | alta | Grupo Santillana (PRISA, Espanha) |
| Harperkids | multinacional | alta | HarperCollins (EUA) |
| LeYa | multinacional | alta | grupo multi-país (origem portuguesa) |
| Rocco, Record, Nova Fronteira, BestBolso, Nova Era, Galera, FTD, Ciranda Cultural, Principis, Intrínseca, WMF Martins Fontes, Pé da Letra, Darkside, Faro Editorial, Lafonte | media / independente | media | conhecimento geral, não verificado individualmente por busca |
| Universo dos Livros, VR, Farol HQ, Maurício de Sousa | (atribuído) | **baixa** | chute — vale conferir manualmente |

Esse mapeamento foi feito diretamente em código Python (rodado no chat, não salvo como script separado — pode ser recriado se necessário).

### 2.6 Fórmula de estreiteza

Para cada eixo (país do autor, forma, porte da editora), calculei a **entropia de Shannon normalizada**:

```python
import numpy as np
from collections import Counter

def estreiteza(rows, campo):
    valores = [r[campo] for r in rows if r[campo].strip()]
    contagem = Counter(valores)
    total = sum(contagem.values())
    dist = np.array([v/total for v in contagem.values()])
    H = -(dist * np.log(dist)).sum()          # entropia de Shannon
    H_max = np.log(len(contagem))              # entropia máxima possível
    estreiteza = 1 - H / H_max                  # 0 = totalmente diverso, 1 = totalmente concentrado
    return estreiteza
```

**Ressalva metodológica importante:** `H_max` foi calculado usando o número de categorias que **já apareceram no seu histórico**, não o número de categorias que existem no mundo (isso só será possível na Fase 2, com um catálogo de referência). Isso tende a **subestimar** a estreiteza real.

### 2.7 Resultados finais (52 livros)

| Eixo | Estreiteza | Distribuição dominante |
|---|---|---|
| País do autor | **0,234** | Reino Unido (29%), EUA (23%), Canadá (17%), Brasil (17%) — 86% em 4 países |
| Forma | **0,225** | Romance (52%), híbrido (27%), novela (10%), não-ficção narrativa (6%), contos (6%) — poesia e ensaio em 0% |
| Porte da editora | **0,119** | Média (58%), multinacional (25%), independente (17%) |

**Achado principal:** geografia é o eixo mais estreito (leitura quase inteiramente anglófona + núcleo brasileiro). Porte da editora, ao contrário do que o documento original previa como padrão típico, é o eixo *menos* estreito.

Resumo de fechamento salvo em `docs/fase0-baseline.md`.

---

## 3. Fase 1 — Recomendação ruim, ponta a ponta

### 3.1 Objetivo

Segundo o documento original: **produzir 10 sugestões, mesmo que ruins, de ponta a ponta**, antes de qualquer refinamento — pra evitar a armadilha de passar meses num pipeline sem nunca gerar uma recomendação de fato.

Decisão explícita sua: usar um catálogo semente **menor** (150-300 obras) em vez dos ~5.000 do documento original, porque scraping automatizado de Open Library/Wikidata é trabalho de Fase 2 e exige ferramentas que não tenho disponíveis neste ambiente (rede restrita a domínios de pacotes, sem acesso geral à web via código).

### 3.2 Catálogo semente

**Fontes escolhidas:**
1. **International Booker Prize** — vencedores, finalistas e lista longa, 2016 a 2026 (levantado via `web_search` e `web_fetch` na página oficial do prêmio)
2. **Núcleo Jabuti + clássicos brasileiros** — vencedores recentes do Jabuti (Romance Literário) mais um núcleo de clássicos da literatura brasileira, baseado em conhecimento geral (**não verificado item a item por busca nesta sessão** — vale conferir antes de usar em produção)

**Por que o Booker Internacional é uma boa semente:** cobre dezenas de idiomas/países diferentes e já vem naturalmente publicado por editoras independentes de tradução (Fitzcarraldo Editions, Charco Press, Tilted Axis Press, And Other Stories, Peirene Press, etc.) — exatamente o tipo de diversidade que o projeto busca.

**Script completo:** `src/ingest/seed_catalogo.py`

```python
"""
Monta o catálogo semente da Fase 1 (~150-300 obras) a partir de:
- International Booker Prize (vencedores, shortlist, longlist 2016-2026)
- Prêmio Jabuti - Romance Literário (núcleo de vencedores recentes, conhecimento geral)

Fonte: pesquisa manual (web_search/web_fetch) + conhecimento geral, NÃO é scraping
automatizado. Ver docs/fase1-catalogo-semente.md para notas de confiança.
"""
import csv

# cada item: (titulo, autor, idioma_original, pais_autor, ano_premio, tipo, editora_uk, forma)
# tipo: vencedor | finalista | lista_longa
booker = [
    # 2026
    ("Taiwan Travelogue", "Yáng Shuāng-zǐ", "chinês (mandarim)", "Taiwan", 2026, "vencedor", "And Other Stories", "romance"),
    ("The Nights Are Quiet in Tehran", "Shida Bazyar", "alemão", "Alemanha", 2026, "finalista", "Scribe UK", "romance"),
    ("She Who Remains", "Rene Karabash", "búlgaro", "Bulgária", 2026, "finalista", "Peirene Press", "romance"),
    ("The Director", "Daniel Kehlmann", "alemão", "Alemanha", 2026, "finalista", "riverrun", "romance"),
    ("On Earth As It Is Beneath", "Ana Paula Maia", "português", "Brasil", 2026, "finalista", "Charco Press", "romance"),
    ("The Witch", "Marie NDiaye", "francês", "França", 2026, "finalista", "MacLehose Press", "romance"),
    ("We Are Green and Trembling", "Gabriela Cabezón Cámara", "espanhol", "Argentina", 2026, "lista_longa", "Harvill", "romance"),
    ("The Remembered Soldier", "Anjet Daanje", "holandês", "Países Baixos", 2026, "lista_longa", "Scribe UK", "romance"),
    ("The Deserters", "Mathias Énard", "francês", "França", 2026, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Small Comfort", "Ia Genberg", "sueco", "Suécia", 2026, "lista_longa", "Wildfire Books", "romance"),
    ("The Duke", "Matteo Melchiorre", "italiano", "Itália", 2026, "lista_longa", "Foundry Editions", "romance"),
    ("Women Without Men", "Shahrnush Parsipur", "persa", "Irã", 2026, "lista_longa", "Penguin", "contos"),
    ("The Wax Child", "Olga Ravn", "dinamarquês", "Dinamarca", 2026, "lista_longa", "Viking", "romance"),
    # 2025
    ("Heart Lamp", "Banu Mushtaq", "canarês (kannada)", "Índia", 2025, "vencedor", "And Other Stories", "contos"),
    ("On the Calculation of Volume I", "Solvej Balle", "dinamarquês", "Dinamarca", 2025, "finalista", "Faber", "romance"),
    ("Small Boat", "Vincent Delecroix", "francês", "França", 2025, "finalista", "Small Axes", "romance"),
    ("Under the Eye of the Big Bird", "Hiromi Kawakami", "japonês", "Japão", 2025, "finalista", "Granta Books", "romance"),
    ("Perfection", "Vincenzo Latronico", "italiano", "Itália", 2025, "finalista", "Fitzcarraldo Editions", "romance"),
    ("A Leopard-Skin Hat", "Anne Serre", "francês", "França", 2025, "finalista", "Lolli Editions", "romance"),
    ("The Book of Disappearance", "Ibtisam Azem", "árabe", "Palestina", 2025, "lista_longa", "And Other Stories", "romance"),
    ("There's a Monster Behind the Door", "Gaëlle Bélem", "francês", "Reunião (França)", 2025, "lista_longa", "Bullaun Press", "romance"),
    ("Solenoid", "Mircea Cărtărescu", "romeno", "Romênia", 2025, "lista_longa", "Pushkin Press", "romance"),
    ("Reservoir Bitches", "Dahlia de la Cerda", "espanhol", "México", 2025, "lista_longa", "Scribe UK", "contos"),
    ("Hunchback", "Saou Ichikawa", "japonês", "Japão", 2025, "lista_longa", "Viking", "romance"),
    ("Eurotrash", "Christian Kracht", "alemão", "Suíça", 2025, "lista_longa", "Serpent's Tail", "romance"),
    ("On a Woman's Madness", "Astrid Roemer", "holandês", "Suriname", 2025, "lista_longa", "Tilted Axis Press", "romance"),
    # 2024
    ("Kairos", "Jenny Erpenbeck", "alemão", "Alemanha", 2024, "vencedor", "Granta Books", "romance"),
    ("Not a River", "Selva Almada", "espanhol", "Argentina", 2024, "finalista", "Charco Press", "romance"),
    ("The Details", "Ia Genberg", "sueco", "Suécia", 2024, "finalista", "Wildfire Books", "romance"),
    ("Mater 2-10", "Hwang Sok-yong", "coreano", "Coreia do Sul", 2024, "finalista", "Scribe UK", "romance"),
    ("Crooked Plow", "Itamar Vieira Junior", "português", "Brasil", 2024, "finalista", "Verso Fiction", "romance"),
    ("What I'd Rather Not Think About", "Jente Posthuma", "holandês", "Países Baixos", 2024, "finalista", "Scribe UK", "romance"),
    ("Simpatía", "Rodrigo Blanco Calderón", "espanhol", "Venezuela", 2024, "lista_longa", "Seven Stories Press UK", "romance"),
    ("White Nights", "Urszula Honek", "polonês", "Polônia", 2024, "lista_longa", "MTO Press", "contos"),
    ("A Dictator Calls", "Ismail Kadare", "albanês", "Albânia", 2024, "lista_longa", "Harvill Secker", "romance"),
    ("The Silver Bone", "Andrey Kurkov", "russo", "Ucrânia", 2024, "lista_longa", "MacLehose Press", "romance"),
    ("Lost on Me", "Veronica Raimo", "italiano", "Itália", 2024, "lista_longa", "Virago", "romance"),
    ("The House on Via Gemito", "Domenico Starnone", "italiano", "Itália", 2024, "lista_longa", "Europa Editions", "romance"),
    ("Undiscovered", "Gabriela Wiener", "espanhol", "Peru", 2024, "lista_longa", "Pushkin Press", "nao_ficcao_narrativa"),
    # 2023
    ("Time Shelter", "Georgi Gospodinov", "búlgaro", "Bulgária", 2023, "vencedor", "Weidenfeld & Nicolson", "romance"),
    ("Boulder", "Eva Baltasar", "catalão", "Espanha", 2023, "finalista", "And Other Stories", "romance"),
    ("Standing Heavy", "GauZ'", "francês", "Costa do Marfim", 2023, "finalista", "Hachette", "romance"),
    ("Still Born", "Guadalupe Nettel", "espanhol", "México", 2023, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Gospel According to the New World", "Maryse Condé", "francês", "Guadalupe", 2023, "finalista", "World Editions", "romance"),
    ("Whale", "Cheon Myeong-kwan", "coreano", "Coreia do Sul", 2023, "finalista", "Europa Editions", "romance"),
    ("Ninth Building", "Zou Jingzhi", "chinês (mandarim)", "China", 2023, "lista_longa", "Honford Star", "nao_ficcao_narrativa"),
    ("Pyre", "Perumal Murugan", "tâmil", "Índia", 2023, "lista_longa", "Pushkin Press", "romance"),
    ("While We Were Dreaming", "Clemens Meyer", "alemão", "Alemanha", 2023, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Jimi Hendrix Live In Lviv", "Andrey Kurkov", "russo", "Ucrânia", 2023, "lista_longa", "Quercus", "romance"),
    ("Is Mother Dead", "Vigdis Hjorth", "norueguês", "Noruega", 2023, "lista_longa", "Verso", "romance"),
    # 2022
    ("Tomb of Sand", "Geetanjali Shree", "hindi", "Índia", 2022, "vencedor", "Tilted Axis Press", "romance"),
    ("Cursed Bunny", "Bora Chung", "coreano", "Coreia do Sul", 2022, "finalista", "Honford Star", "contos"),
    ("A New Name: Septology VI-VII", "Jon Fosse", "norueguês", "Noruega", 2022, "finalista", "Fitzcarraldo Editions", "romance"),
    ("Heaven", "Mieko Kawakami", "japonês", "Japão", 2022, "finalista", "Picador", "romance"),
    ("Elena Knows", "Claudia Piñeiro", "espanhol", "Argentina", 2022, "finalista", "Charco Press", "romance"),
    ("The Books of Jacob", "Olga Tokarczuk", "polonês", "Polônia", 2022, "finalista", "Fitzcarraldo Editions", "romance"),
    ("After the Sun", "Jonas Eika", "dinamarquês", "Dinamarca", 2022, "lista_longa", "Lolli Editions", "contos"),
    ("Paradais", "Fernanda Melchor", "espanhol", "México", 2022, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Love in the Big City", "Sang Young Park", "coreano", "Coreia do Sul", 2022, "lista_longa", "Tilted Axis Press", "romance"),
    ("Happy Stories, Mostly", "Norman Erikson Pasaribu", "indonésio", "Indonésia", 2022, "lista_longa", "Tilted Axis Press", "contos"),
    ("Phenotypes", "Paulo Scott", "português", "Brasil", 2022, "lista_longa", "And Other Stories", "romance"),
    # 2021
    ("At Night All Blood Is Black", "David Diop", "francês", "França/Senegal", 2021, "vencedor", "Pushkin Press", "romance"),
    ("The Dangers of Smoking in Bed", "Mariana Enríquez", "espanhol", "Argentina", 2021, "finalista", "Granta Books", "contos"),
    ("The Employees", "Olga Ravn", "dinamarquês", "Dinamarca", 2021, "finalista", "Lolli Editions", "romance"),
    ("When We Cease to Understand the World", "Benjamín Labatut", "espanhol", "Chile", 2021, "finalista", "Pushkin Press", "hibrido"),
    ("In Memory of Memory", "Maria Stepanova", "russo", "Rússia", 2021, "finalista", "Fitzcarraldo Editions", "hibrido"),
    ("The Perfect Nine", "Ngũgĩ wa Thiong'o", "gikuyu", "Quênia", 2021, "lista_longa", "Harvill Secker", "poesia"),
    ("Minor Detail", "Adania Shibli", "árabe", "Palestina", 2021, "lista_longa", "Fitzcarraldo Editions", "romance"),
    ("Summer Brother", "Jaap Robben", "holandês", "Países Baixos", 2021, "lista_longa", "World Editions", "romance"),
    # 2020
    ("The Discomfort of Evening", "Lucas Rijneveld", "holandês", "Países Baixos", 2020, "vencedor", "Faber & Faber", "romance"),
    ("The Enlightenment of The Greengage Tree", "Shokoofeh Azar", "persa", "Irã", 2020, "finalista", "Europa Editions", "romance"),
    ("The Adventures of China Iron", "Gabriela Cabezón Cámara", "espanhol", "Argentina", 2020, "finalista", "Charco Press", "romance"),
    ("Hurricane Season", "Fernanda Melchor", "espanhol", "México", 2020, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Memory Police", "Yōko Ogawa", "japonês", "Japão", 2020, "finalista", "Harvill Secker", "romance"),
    ("The Eighth Life", "Nino Haratischvili", "alemão", "Geórgia", 2020, "lista_longa", "Scribe UK", "romance"),
    ("Little Eyes", "Samanta Schweblin", "espanhol", "Argentina", 2020, "lista_longa", "Oneworld", "romance"),
    ("Mac and His Problem", "Enrique Vila-Matas", "espanhol", "Espanha", 2020, "lista_longa", "Harvill Secker", "romance"),
    # 2019
    ("Celestial Bodies", "Jokha Alharthi", "árabe", "Omã", 2019, "vencedor", "Sandstone Press", "romance"),
    ("The Years", "Annie Ernaux", "francês", "França", 2019, "finalista", "Fitzcarraldo Editions", "nao_ficcao_narrativa"),
    ("The Pine Islands", "Marion Poschmann", "alemão", "Alemanha", 2019, "finalista", "Serpent's Tail", "romance"),
    ("Drive Your Plow Over the Bones of the Dead", "Olga Tokarczuk", "polonês", "Polônia", 2019, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Shape of the Ruins", "Juan Gabriel Vásquez", "espanhol", "Colômbia", 2019, "finalista", "MacLehose Press", "romance"),
    ("The Remainder", "Alia Trabucco Zerán", "espanhol", "Chile", 2019, "finalista", "And Other Stories", "romance"),
    ("Mouthful of Birds", "Samanta Schweblin", "espanhol", "Argentina", 2019, "lista_longa", "Oneworld", "contos"),
    ("At Dusk", "Hwang Sok-yong", "coreano", "Coreia do Sul", 2019, "lista_longa", "Scribe", "romance"),
    # 2018
    ("Flights", "Olga Tokarczuk", "polonês", "Polônia", 2018, "vencedor", "Fitzcarraldo Editions", "hibrido"),
    ("Vernon Subutex 1", "Virginie Despentes", "francês", "França", 2018, "finalista", "MacLehose Press", "romance"),
    ("The White Book", "Han Kang", "coreano", "Coreia do Sul", 2018, "finalista", "Portobello Books", "hibrido"),
    ("The World Goes On", "László Krasznahorkai", "húngaro", "Hungria", 2018, "finalista", "Tuskar Rock Press", "contos"),
    ("Frankenstein in Baghdad", "Ahmed Saadawi", "árabe", "Iraque", 2018, "finalista", "Oneworld", "romance"),
    ("The 7th Function of Language", "Laurent Binet", "francês", "França", 2018, "lista_longa", "Harvill Secker", "romance"),
    ("Go, Went, Gone", "Jenny Erpenbeck", "alemão", "Alemanha", 2018, "lista_longa", "Portobello Books", "romance"),
    # 2017
    ("A Horse Walks into a Bar", "David Grossman", "hebraico", "Israel", 2017, "vencedor", "Jonathan Cape", "romance"),
    ("Compass", "Mathias Énard", "francês", "França", 2017, "finalista", "Fitzcarraldo Editions", "romance"),
    ("The Unseen", "Roy Jacobsen", "norueguês", "Noruega", 2017, "finalista", "MacLehose Press", "romance"),
    ("Mirror, Shoulder, Signal", "Dorthe Nors", "dinamarquês", "Dinamarca", 2017, "finalista", "Graywolf Press", "romance"),
    ("Fever Dream", "Samanta Schweblin", "espanhol", "Argentina", 2017, "finalista", "Riverhead Books", "romance"),
    ("The Traitor's Niche", "Ismail Kadare", "albanês", "Albânia", 2017, "lista_longa", "Harvill Secker", "romance"),
    ("Black Moses", "Alain Mabanckou", "francês", "Congo-Brazzaville", 2017, "lista_longa", "The New Press", "romance"),
    # 2016
    ("The Vegetarian", "Han Kang", "coreano", "Coreia do Sul", 2016, "vencedor", "Granta Books", "romance"),
    ("A General Theory of Oblivion", "José Eduardo Agualusa", "português", "Angola", 2016, "finalista", "Harvill Secker", "romance"),
    ("The Story of the Lost Child", "Elena Ferrante", "italiano", "Itália", 2016, "finalista", "Europa Editions", "romance"),
    ("A Whole Life", "Robert Seethaler", "alemão", "Áustria", 2016, "finalista", "Picador", "novela"),
    ("Man Tiger", "Eka Kurniawan", "indonésio", "Indonésia", 2016, "lista_longa", "Verso", "romance"),
    ("Tram 83", "Fiston Mwanza Mujila", "francês", "Rep. Dem. do Congo", 2016, "lista_longa", "Deep Vellum Publishing", "romance"),
    ("A Cup of Rage", "Raduan Nassar", "português", "Brasil", 2016, "lista_longa", "New Directions Publishing", "novela"),
    ("Ladivine", "Marie NDiaye", "francês", "França", 2016, "lista_longa", "MacLehose Press", "romance"),
]

# núcleo Jabuti - Romance Literário (conhecimento geral, ANO = ano de premiação, NÃO verificado
# item a item via busca nesta sessão - conferir antes de usar em produção)
jabuti = [
    ("Torto Arado", "Itamar Vieira Junior", "português", "Brasil", 2020, "vencedor", "Todavia", "romance"),
    ("Marrom e Amarelo", "Paulo Scott", "português", "Brasil", 2020, "finalista", "Alfaguara", "romance"),
    ("A Palavra que Resta", "Stênio Gardel", "português", "Brasil", 2021, "vencedor", "Companhia das Letras", "romance"),
    ("O Som do Rugido da Onça", "Micheliny Verunschk", "português", "Brasil", 2021, "finalista", "Companhia das Letras", "romance"),
    ("Água Viva", "Clarice Lispector", "português", "Brasil", 1973, "classico", "Rocco", "romance"),
    ("A Hora da Estrela", "Clarice Lispector", "português", "Brasil", 1977, "classico", "Rocco", "romance"),
    ("Grande Sertão: Veredas", "Guimarães Rosa", "português", "Brasil", 1956, "classico", "Nova Fronteira", "romance"),
    ("Vidas Secas", "Graciliano Ramos", "português", "Brasil", 1938, "classico", "Record", "romance"),
    ("Quarto de Despejo", "Carolina Maria de Jesus", "português", "Brasil", 1960, "classico", "Ática", "nao_ficcao_narrativa"),
    ("Becos da Memória", "Conceição Evaristo", "português", "Brasil", 2006, "classico", "Companhia das Letras", "romance"),
    ("Um Defeito de Cor", "Ana Maria Gonçalves", "português", "Brasil", 2006, "classico", "Record", "romance"),
    ("K. Relato de uma Busca", "Bernardo Kucinski", "português", "Brasil", 2011, "classico", "Cosac Naify", "nao_ficcao_narrativa"),
]

todos = booker + jabuti

path = "data/raw/catalogo_semente.csv"
with open(path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["titulo", "autor", "idioma_original", "pais_autor", "ano_premio", "tipo_premio", "editora_fonte", "forma", "premio"])
    for t, a, idi, pa, ano, tipo, ed, forma in booker:
        writer.writerow([t, a, idi, pa, ano, tipo, ed, forma, "International Booker Prize"])
    for t, a, idi, pa, ano, tipo, ed, forma in jabuti:
        writer.writerow([t, a, idi, pa, ano, tipo, ed, forma, "Jabuti - Romance Literário"])

print(f"catálogo semente: {len(todos)} obras")
print(f"Booker: {len(booker)} | Jabuti: {len(jabuti)}")
```

**Resultado:** `data/raw/catalogo_semente.csv` com **119 obras** (107 do Booker Internacional + 12 do núcleo Jabuti/clássicos).

### 3.3 Schema SQLite

Schema mínimo — não é o schema completo do documento original (esse vem só na Fase 2+, com tabelas de editora, prêmios, grafo de co-ocorrência etc). Aqui só o suficiente pra guardar catálogo + histórico e calcular similaridade.

**Arquivo:** `src/schema/schema_fase1.sql`

```sql
-- Schema mínimo da Fase 1 (recomendação ruim ponta a ponta).
-- Não é o schema completo do documento (esse vem na Fase 2+, com tabelas de
-- editora, prêmios, grafo de co-ocorrência etc). Aqui só o suficiente pra:
--   1. guardar o catálogo semente
--   2. guardar o histórico de leitura
--   3. depois calcular similaridade de sinopse e gerar recomendações

CREATE TABLE IF NOT EXISTS obra (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT NOT NULL,
    autor           TEXT,
    idioma_original TEXT,
    pais_autor      TEXT,
    ano_premio      INTEGER,
    tipo_premio     TEXT,       -- vencedor | finalista | lista_longa | classico
    editora_fonte   TEXT,
    forma           TEXT,
    premio          TEXT,       -- ex: "International Booker Prize"
    sinopse         TEXT,       -- preenchida manualmente via pesquisa (Fase 1, passo 2)
    confianca_sinopse TEXT,     -- alta | media | baixa
    UNIQUE(titulo, autor)
);

CREATE TABLE IF NOT EXISTS leitura (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo          TEXT NOT NULL,
    autor           TEXT,
    data_leitura    TEXT,
    nota            REAL,
    abandonei       INTEGER DEFAULT 0,
    editora         TEXT,
    porte_editora   TEXT,
    pais_autor      TEXT,
    forma           TEXT,
    sinopse         TEXT,       -- preenchida manualmente via pesquisa (Fase 1, passo 2)
    confianca_sinopse TEXT      -- alta | media | baixa
);

CREATE INDEX IF NOT EXISTS idx_obra_pais   ON obra(pais_autor);
CREATE INDEX IF NOT EXISTS idx_obra_forma  ON obra(forma);
CREATE INDEX IF NOT EXISTS idx_leitura_pais  ON leitura(pais_autor);
```

### 3.4 Loader (carrega os CSVs no banco)

**Arquivo:** `src/ingest/load_db.py`

```python
"""
Cria o banco db/livros.sqlite a partir do schema da Fase 1 e carrega:
- data/raw/catalogo_semente.csv      -> tabela obra
- data/interim/sinopses_catalogo.csv -> sinopses da tabela obra
- data/raw/historico_leitura.csv     -> tabela leitura
- data/interim/sinopses_historico.csv -> sinopses da tabela leitura

Rodar da raiz do projeto: python3 src/ingest/load_db.py
"""
import csv
import sqlite3
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DB_PATH = RAIZ / "db" / "livros.sqlite"
SCHEMA_PATH = RAIZ / "src" / "schema" / "schema_fase1.sql"
CATALOGO_CSV = RAIZ / "data" / "raw" / "catalogo_semente.csv"
HISTORICO_CSV = RAIZ / "data" / "raw" / "historico_leitura.csv"
SINOPSES_HISTORICO_CSV = RAIZ / "data" / "interim" / "sinopses_historico.csv"
SINOPSES_CATALOGO_CSV = RAIZ / "data" / "interim" / "sinopses_catalogo.csv"


def criar_schema(conn):
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())


def carregar_sinopses(caminho):
    if not caminho.exists():
        return {}
    with open(caminho, newline="", encoding="utf-8") as f:
        return {(r["titulo"], r["autor"]): (r["sinopse"], r["confianca"]) for r in csv.DictReader(f)}


def carregar_catalogo(conn):
    sinopses = carregar_sinopses(SINOPSES_CATALOGO_CSV)
    with open(CATALOGO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            sinopse, confianca = sinopses.get((r["titulo"], r["autor"]), (None, None))
            rows.append((
                r["titulo"], r["autor"], r["idioma_original"], r["pais_autor"],
                int(r["ano_premio"]) if r["ano_premio"] else None,
                r["tipo_premio"], r["editora_fonte"], r["forma"], r["premio"],
                sinopse, confianca,
            ))
    conn.executemany(
        """INSERT OR IGNORE INTO obra
           (titulo, autor, idioma_original, pais_autor, ano_premio, tipo_premio, editora_fonte, forma, premio, sinopse, confianca_sinopse)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    n_com_sinopse = sum(1 for r in rows if r[9])
    return len(rows), n_com_sinopse


def carregar_historico(conn):
    sinopses = carregar_sinopses(SINOPSES_HISTORICO_CSV)
    with open(HISTORICO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            sinopse, confianca = sinopses.get((r["titulo"], r["autor"]), (None, None))
            rows.append((
                r["titulo"], r["autor"], r["data_leitura"],
                float(r["nota"]) if r["nota"] else None,
                int(r["abandonei"]) if r["abandonei"] else 0,
                r["editora"], r["porte_editora"], r["pais_autor"], r["forma"],
                sinopse, confianca,
            ))
    conn.executemany(
        """INSERT INTO leitura
           (titulo, autor, data_leitura, nota, abandonei, editora, porte_editora, pais_autor, forma, sinopse, confianca_sinopse)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    n_com_sinopse = sum(1 for r in rows if r[9])
    return len(rows), n_com_sinopse


if __name__ == "__main__":
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    criar_schema(conn)
    n_obras, n_obras_sinopse = carregar_catalogo(conn)
    n_leituras, n_leituras_sinopse = carregar_historico(conn)
    conn.commit()
    print(f"banco criado em {DB_PATH}")
    print(f"obras carregadas: {n_obras} ({n_obras_sinopse} com sinopse)")
    print(f"leituras carregadas: {n_leituras} ({n_leituras_sinopse} com sinopse)")
    conn.close()
```

**Resultado do último `python3 src/ingest/load_db.py`:**
```
banco criado em db/livros.sqlite
obras carregadas: 119 (119 com sinopse)
leituras carregadas: 52 (52 com sinopse)
```

### 3.5 Sinopses

O `catalogo_semente.csv` só tinha metadados (título, autor, idioma, país, forma) — **sem o texto da sinopse**, que é o que a similaridade da Fase 1 precisa comparar. Não há acesso automatizado a APIs de sinopse (Google Books, Open Library) neste ambiente, então as sinopses foram **escritas manualmente**, em lotes de ~15, com apoio de `web_search` para os títulos menos conhecidos (obras brasileiras de nicho, mangá, lançamentos 2025/2026 do Booker) e conhecimento geral para os clássicos e títulos bem documentados.

**Regra de proveniência seguida:** cada sinopse foi escrita com palavras próprias (nunca copiada de nenhuma fonte), com uma coluna `confianca`:
- **alta** — livro bem conhecido ou confirmado por busca
- **media** — enredo geral conhecido, detalhes não checados
- **baixa** — pouca informação disponível, sinopse aproximada

**Processo:**
- Histórico (52 livros): 4 lotes → consolidados em `data/interim/sinopses_historico.csv`
- Catálogo semente (119 obras): 8 lotes → consolidados em `data/interim/sinopses_catalogo.csv`

Um ajuste feito no meio do caminho: o `load_db.py` originalmente só carregava sinopse pra tabela `leitura`; foi expandido pra também carregar sinopse pra tabela `obra`, e o schema ganhou a coluna `confianca_sinopse` nas duas tabelas.

Dois bugs de matching encontrados e corrigidos durante o processo:
- "Spencer Johnson" (correto) vs "Spencer Jhonson" (como está no seu CSV) — ajustado pra bater
- "Go, Went, Gone" e "Mirror, Shoulder, Signal" perderam as vírgulas dos títulos ao salvar o CSV de sinopses — corrigido manualmente

### 3.6 Similaridade de sinopse (geração das recomendações)

**Decisão técnica importante:** o documento original sugere `sentence-transformers` (embeddings semânticos) pra essa etapa, mas isso exige baixar modelos do Hugging Face, e a rede deste ambiente é restrita a domínios de pacotes (pypi, npm, github etc.) — não inclui `huggingface.co`. Por isso, a Fase 1 usa **TF-IDF + similaridade de cosseno**, uma técnica clássica de sobreposição de palavras, sem entender semântica/sinônimos. Isso é consistente com o espírito da Fase 1 ("recomendação ruim, ponta a ponta") — a técnica melhor (embeddings) fica pra Fase 2+.

**Lógica do algoritmo:**
1. Monta um "perfil de gosto" = média dos vetores TF-IDF das sinopses de livros que você deu **nota ≥ 4** no histórico
2. Compara esse perfil com a sinopse de cada uma das 119 obras do catálogo (excluindo as que você já leu)
3. Retorna as 10 mais similares por cosseno

**Arquivo:** `src/rank/similaridade_sinopse.py`

```python
"""
Fase 1 - Recomendação ruim, ponta a ponta.

Método: TF-IDF + similaridade de cosseno sobre as sinopses (sem diversificação,
sem embeddings semânticos - isso é proposital, é o "ruim" da Fase 1).

Lógica:
1. Perfil de gosto = média dos vetores TF-IDF das sinopses de livros que o
   usuário deu nota >= 4 no histórico.
2. Compara esse perfil com a sinopse de cada obra do catálogo semente que
   ainda não foi lida.
3. Retorna as 10 obras mais similares.

Rodar da raiz do projeto: python3 src/rank/similaridade_sinopse.py
"""
import sqlite3
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

RAIZ = Path(__file__).resolve().parents[2]
DB_PATH = RAIZ / "db" / "livros.sqlite"

NOTA_MINIMA_PERFIL = 4.0
N_RECOMENDACOES = 10

# stopwords básicas em português (lista curta, sem depender de pacote externo)
STOPWORDS_PT = [
    "a", "o", "as", "os", "um", "uma", "uns", "umas", "de", "da", "do", "das", "dos",
    "em", "no", "na", "nos", "nas", "para", "por", "com", "sem", "sobre", "entre",
    "e", "ou", "mas", "que", "se", "sua", "seu", "suas", "seus", "ao", "aos", "à", "às",
    "é", "foi", "ser", "são", "está", "estão", "como", "mais", "muito", "já", "não",
    "quando", "onde", "num", "numa", "pelo", "pela", "pelos", "pelas", "ele", "ela",
    "eles", "elas", "isso", "esse", "essa", "este", "esta", "após", "até",
]


def carregar_dados(conn):
    leituras = conn.execute(
        "SELECT titulo, autor, nota, sinopse FROM leitura WHERE sinopse IS NOT NULL"
    ).fetchall()
    obras = conn.execute(
        "SELECT titulo, autor, pais_autor, forma, sinopse FROM obra WHERE sinopse IS NOT NULL"
    ).fetchall()
    return leituras, obras


def montar_perfil(leituras, vectorizer, matriz_leituras):
    indices_alta_nota = [
        i for i, (_, _, nota, _) in enumerate(leituras)
        if nota is not None and nota >= NOTA_MINIMA_PERFIL
    ]
    if not indices_alta_nota:
        raise ValueError("Nenhum livro com nota >= 4 encontrado no histórico.")
    perfil = matriz_leituras[indices_alta_nota].mean(axis=0)
    perfil = np.asarray(perfil)
    return perfil, len(indices_alta_nota)


def already_lido(titulo, autor, leituras):
    lidos = {(t.strip().lower(), a.strip().lower()) for t, a, _, _ in leituras}
    return (titulo.strip().lower(), autor.strip().lower()) in lidos


def main():
    conn = sqlite3.connect(DB_PATH)
    leituras, obras = carregar_dados(conn)
    conn.close()

    textos_leituras = [s for *_x, s in leituras]
    textos_obras = [s for *_x, s in obras]

    vectorizer = TfidfVectorizer(stop_words=STOPWORDS_PT)
    matriz_geral = vectorizer.fit_transform(textos_leituras + textos_obras)
    matriz_leituras = matriz_geral[: len(textos_leituras)]
    matriz_obras = matriz_geral[len(textos_leituras):]

    perfil, n_livros_perfil = montar_perfil(leituras, vectorizer, matriz_leituras)

    similaridades = cosine_similarity(perfil, matriz_obras)[0]

    candidatos = []
    for (titulo, autor, pais, forma, _sinopse), sim in zip(obras, similaridades):
        if already_lido(titulo, autor, leituras):
            continue
        candidatos.append((sim, titulo, autor, pais, forma))

    candidatos.sort(reverse=True)

    print(f"Perfil montado com {n_livros_perfil} livros (nota >= {NOTA_MINIMA_PERFIL})\n")
    print(f"Top {N_RECOMENDACOES} recomendações (Fase 1 - sem diversificação):\n")
    for i, (sim, titulo, autor, pais, forma) in enumerate(candidatos[:N_RECOMENDACOES], 1):
        print(f"{i:2d}. [{sim:.3f}] {titulo} - {autor} ({pais}, {forma})")


if __name__ == "__main__":
    main()
```

### 3.7 Resultado final da Fase 1

```
Perfil montado com 30 livros (nota >= 4.0)

Top 10 recomendações (Fase 1 - sem diversificação):

 1. [0.115] A Leopard-Skin Hat - Anne Serre (França, romance)
 2. [0.091] Summer Brother - Jaap Robben (Países Baixos, romance)
 3. [0.082] The Vegetarian - Han Kang (Coreia do Sul, romance)
 4. [0.072] Pyre - Perumal Murugan (Índia, romance)
 5. [0.070] Love in the Big City - Sang Young Park (Coreia do Sul, romance)
 6. [0.069] Heaven - Mieko Kawakami (Japão, romance)
 7. [0.067] The Unseen - Roy Jacobsen (Noruega, romance)
 8. [0.061] Phenotypes - Paulo Scott (Brasil, romance)
 9. [0.061] Marrom e Amarelo - Paulo Scott (Brasil, romance)
10. [0.060] A Horse Walks into a Bar - David Grossman (Israel, romance)
```

**Scores baixos (0,06-0,12 numa escala 0-1) são esperados** — é literalmente a "recomendação ruim" que a Fase 1 pede, porque TF-IDF só pega sobreposição de palavras, não significado.

### 3.8 Limitações identificadas (a resolver na Fase 2+)

1. **Duplicata não resolvida:** "Marrom e Amarelo" (edição brasileira, Alfaguara) e "Phenotypes" (edição inglesa, And Other Stories) são **o mesmo livro** de Paulo Scott, e os dois aparecem separadamente no top 10. A Fase 2 vai precisar de uma lógica de deduplicação por obra (não por edição).
2. **Falsos negativos prováveis:** "On Earth As It Is Beneath" (Ana Paula Maia, também brasileira, tematicamente próxima de vários livros do seu perfil) não apareceu no top 10 — mostra o limite de um método que não entende sinônimos/paráfrase.
3. Sinopses do catálogo com confiança `media`/`baixa` (a maioria dos lançamentos 2025/2026) podem conter imprecisões que afetam a qualidade da similaridade.
4. 4 editoras do histórico com porte atribuído por chute, não verificado: Universo dos Livros, VR, Farol HQ, Maurício de Sousa.

---

## 4. Estado atual do repositório

```
recomendacao-livros/
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── historico_leitura.csv        (52 livros)
│   │   └── catalogo_semente.csv         (119 obras)
│   └── interim/
│       ├── sinopses_historico.csv       (consolidado, 52)
│       ├── sinopses_historico_lote1.csv até lote4.csv
│       ├── sinopses_catalogo.csv        (consolidado, 119)
│       └── sinopses_catalogo_lote1.csv até lote8.csv
├── db/
│   └── livros.sqlite                    (gerado, não vai pro git)
├── src/
│   ├── ingest/
│   │   ├── seed_catalogo.py
│   │   └── load_db.py
│   ├── schema/
│   │   └── schema_fase1.sql
│   └── rank/
│       └── similaridade_sinopse.py
└── docs/
    ├── fase0-baseline.md
    └── registro-completo.md             (este arquivo)
```

**Como recriar o banco do zero, em qualquer máquina que clone o repo:**
```bash
python3 src/ingest/load_db.py
```

---

## 5. Próximos passos (Fase 2 em diante, ainda não iniciados)

Segundo o plano original do documento:
- **Fase 2** — Catálogo real via dumps do Open Library (dezenas/centenas de milhares de obras), resolvendo o problema de deduplicação por edição
- **Fase 3** — Enriquecimento via LLM (metadados que a API não fornece: registro de prosa, estrutura narrativa)
- **Fase 4** — Diversificação via MMR (Maximal Marginal Relevance) + penalização por popularidade + cota por eixo
- **Fase 5** — Grafo de co-ocorrência/serendipidade
- **Fase 6** — Avaliação: métricas offline + feedback em dois eixos (gostei × diferente) por livro lido, comparando com a estreiteza baseline calculada na Fase 0
