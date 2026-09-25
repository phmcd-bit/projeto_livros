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
