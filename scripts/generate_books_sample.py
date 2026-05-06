"""Génère data/sample/books_sample.csv — 100 lignes, 10 colonnes (démo livres)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "sample" / "books_sample.csv"

RNG = np.random.default_rng(42)

GENRES = ["Roman", "Essai", "SF", "Fantasy", "Polar", "Biographie", "Jeunesse", "Poésie"]
FORMATS = ["Broché", "Relié", "Poche", "Numérique"]
PUBLISHERS = [
    "Gallimard",
    "Actes Sud",
    "Flammarion",
    "Le Livre de Poche",
    "Bragelonne",
    "Points",
    "Le Masque",
    "Albin Michel",
]

# Catalogue synthétique (titres / auteurs réalistes pour la démo)
_CATALOG: list[tuple[str, str, str, str, int]] = [
    ("Les Misérables", "Victor Hugo", "Roman", "Penguin Classics", 1862),
    ("1984", "George Orwell", "SF", "Gallimard", 1949),
    ("L'Étranger", "Albert Camus", "Roman", "Gallimard", 1942),
    ("Le Petit Prince", "Antoine de Saint-Exupéry", "Jeunesse", "Gallimard", 1943),
    ("Harry Potter à l'école des sorciers", "J.K. Rowling", "Fantasy", "Gallimard", 1997),
    ("Orgueil et Préjugés", "Jane Austen", "Roman", "Le Livre de Poche", 1813),
    ("Fondation", "Isaac Asimov", "SF", "Denöel", 1951),
    ("Dune", "Frank Herbert", "SF", "Robert Laffont", 1965),
    ("Le Nom de la rose", "Umberto Eco", "Polar", "Grasset", 1980),
    ("L'Art de la guerre", "Sun Tzu", "Essai", "Payot", -500),
    ("Crime et Châtiment", "Fiodor Dostoïevski", "Roman", "Gallimard", 1866),
    ("Anna Karénine", "Léon Tolstoï", "Roman", "Gallimard", 1877),
    ("Moby-Dick", "Herman Melville", "Roman", "Gallimard", 1851),
    ("Cent ans de solitude", "Gabriel García Márquez", "Roman", "Gallimard", 1967),
    ("Le Vieux et la Mer", "Ernest Hemingway", "Roman", "Gallimard", 1952),
    ("Kafka sur le rivage", "Haruki Murakami", "Roman", "10/18", 2002),
    ("Ne tirez pas sur l'oiseau moqueur", "Harper Lee", "Roman", "Le Livre de Poche", 1960),
    ("Beloved", "Toni Morrison", "Roman", "Christian Bourgois", 1987),
    ("Les Hauts de Hurlevent", "Emily Brontë", "Roman", "Le Livre de Poche", 1847),
    ("Jane Eyre", "Charlotte Brontë", "Roman", "Le Livre de Poche", 1847),
    ("Germinal", "Émile Zola", "Roman", "Flammarion", 1885),
    ("Madame Bovary", "Gustave Flaubert", "Roman", "Flammarion", 1857),
    ("Les Fleurs du mal", "Charles Baudelaire", "Poésie", "Gallimard", 1857),
    ("Paradis perdu", "John Milton", "Poésie", "Gallimard", 1667),
    ("Hamlet", "William Shakespeare", "Roman", "Gallimard", 1603),
    ("Macbeth", "William Shakespeare", "Roman", "Gallimard", 1606),
    ("Le Rouge et le Noir", "Stendhal", "Roman", "Le Livre de Poche", 1830),
    ("La Chartreuse de Parme", "Stendhal", "Roman", "Gallimard", 1839),
    ("À la recherche du temps perdu", "Marcel Proust", "Roman", "Gallimard", 1913),
    ("Les Confessions", "Jean-Jacques Rousseau", "Biographie", "Gallimard", 1782),
    ("Discours de la méthode", "René Descartes", "Essai", "Flammarion", 1637),
    ("Critique de la raison pure", "Emmanuel Kant", "Essai", "Vrin", 1781),
    ("Le Deuxième Sexe", "Simone de Beauvoir", "Essai", "Gallimard", 1949),
    ("Une chambre à soi", "Virginia Woolf", "Essai", "10/18", 1929),
    ("Mrs Dalloway", "Virginia Woolf", "Roman", "10/18", 1925),
    ("La Condition humaine", "André Malraux", "Roman", "Gallimard", 1933),
    ("L'Étrange Défaite", "Marc Bloch", "Essai", "Gallimard", 1946),
    ("La Société du spectacle", "Guy Debord", "Essai", "Gallimard", 1967),
    ("Surveiller et punir", "Michel Foucault", "Essai", "Gallimard", 1975),
    ("Le Capital au XXIe siècle", "Thomas Piketty", "Essai", "Seuil", 2013),
    ("Sapiens", "Yuval Noah Harari", "Essai", "Albin Michel", 2011),
    ("Homo Deus", "Yuval Noah Harari", "Essai", "Albin Michel", 2015),
    ("Factfulness", "Hans Rosling", "Essai", "Flammarion", 2018),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Essai", "Flammarion", 2011),
    ("Clean Code", "Robert C. Martin", "Essai", "Pearson", 2008),
    ("Design Patterns", "GoF", "Essai", "Pearson", 1994),
    ("Introduction aux algorithmes", "Cormen et al.", "Essai", "Dunod", 2009),
    ("Deep Learning", "Goodfellow et al.", "Essai", "Pearson", 2016),
    ("Pattern Recognition and ML", "Christopher Bishop", "Essai", "Springer", 2006),
]


def main() -> None:
    n_cat = len(_CATALOG)
    books_meta = pd.DataFrame(
        {
            "book_id": [f"B{i:03d}" for i in range(1, n_cat + 1)],
            "title": [t for t, *_ in _CATALOG],
            "author": [a for _, a, *_ in _CATALOG],
            "genre_ref": [g for _, _, g, *_ in _CATALOG],
            "publisher_ref": [p for _, _, _, p, *_ in _CATALOG],
            "year_ref": [y for *_, y in _CATALOG],
        }
    )

    choice = RNG.integers(0, n_cat, size=100)
    readers = RNG.integers(1, 31, size=100)
    ratings = RNG.integers(1, 6, size=100)

    base = books_meta.iloc[choice].reset_index(drop=True)
    base["reader_id"] = readers.astype(str)
    base["book_id"] = base["book_id"].astype(str)
    base["rating"] = ratings.astype(float)

    # Dates de notation aléatoires (2023–2025)
    ordinals = RNG.integers(
        pd.Timestamp("2023-01-01").toordinal(),
        pd.Timestamp("2026-01-01").toordinal(),
        size=100,
    )
    base["rated_at"] = [pd.Timestamp.fromordinal(int(o)).strftime("%Y-%m-%d") for o in ordinals]

    # Variantes légères sur genre / éditeur pour réalisme
    genres = [
        GENRES[RNG.integers(0, len(GENRES))] if RNG.random() > 0.65 else g
        for g in base["genre_ref"]
    ]
    publishers = [
        PUBLISHERS[RNG.integers(0, len(PUBLISHERS))] if RNG.random() > 0.7 else p
        for p in base["publisher_ref"]
    ]

    out = pd.DataFrame(
        {
            "reader_id": base["reader_id"],
            "book_id": base["book_id"],
            "rating": base["rating"],
            "rated_at": base["rated_at"],
            "title": base["title"],
            "author": base["author"],
            "genre": genres,
            "publisher": publishers,
            "publication_year": base["year_ref"].astype(int),
            "format": list(RNG.choice(FORMATS, size=100)),
        }
    )

    assert out.shape == (100, 10)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False, encoding="utf-8")
    print(f"Écrit {OUT} ({out.shape[0]} lignes × {out.shape[1]} colonnes)")


if __name__ == "__main__":
    main()
