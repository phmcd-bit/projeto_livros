"""
Cria o banco db/livros.sqlite a partir do schema da Fase 1 e carrega:
- data/raw/catalogo_semente.csv  -> tabela obra
- data/raw/historico_leitura.csv -> tabela leitura

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


def criar_schema(conn):
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())


def carregar_catalogo(conn):
    with open(CATALOGO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["titulo"], r["autor"], r["idioma_original"], r["pais_autor"],
                int(r["ano_premio"]) if r["ano_premio"] else None,
                r["tipo_premio"], r["editora_fonte"], r["forma"], r["premio"],
            )
            for r in reader
        ]
    conn.executemany(
        """INSERT OR IGNORE INTO obra
           (titulo, autor, idioma_original, pais_autor, ano_premio, tipo_premio, editora_fonte, forma, premio)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    return len(rows)


def carregar_historico(conn):
    with open(HISTORICO_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                r["titulo"], r["autor"], r["data_leitura"],
                float(r["nota"]) if r["nota"] else None,
                int(r["abandonei"]) if r["abandonei"] else 0,
                r["editora"], r["porte_editora"], r["pais_autor"], r["forma"],
            )
            for r in reader
        ]
    conn.executemany(
        """INSERT INTO leitura
           (titulo, autor, data_leitura, nota, abandonei, editora, porte_editora, pais_autor, forma)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        rows,
    )
    return len(rows)


if __name__ == "__main__":
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    criar_schema(conn)
    n_obras = carregar_catalogo(conn)
    n_leituras = carregar_historico(conn)
    conn.commit()
    print(f"banco criado em {DB_PATH}")
    print(f"obras carregadas: {n_obras}")
    print(f"leituras carregadas: {n_leituras}")
    conn.close()
