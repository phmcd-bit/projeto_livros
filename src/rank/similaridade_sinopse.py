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
