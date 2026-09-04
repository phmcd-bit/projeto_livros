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
    sinopse         TEXT,       -- NULL até ser preenchida (Fase 1, passo 2)
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
    forma           TEXT
);

CREATE INDEX IF NOT EXISTS idx_obra_pais   ON obra(pais_autor);
CREATE INDEX IF NOT EXISTS idx_obra_forma  ON obra(forma);
CREATE INDEX IF NOT EXISTS idx_leitura_pais  ON leitura(pais_autor);
