# Scrabblese

Scrabblese scrapes annotated Scrabble games, caches raw game content and parsed words in SQLite,
and plots Scrabble-vs-English probability comparisons.

## Cache-first pipeline

`Main.py` now runs this flow:

1. Scrape game records from Cross-Tables.
2. Store each game once in `scrabble.db` via Peewee entities.
3. Parse/cached per-game word frequencies.
4. Fill missing ngrams.dev probabilities for cached words.
5. Export probabilities to `Files/probabilities.csv` and plot.

## Run

```bash
python Main.py
```
