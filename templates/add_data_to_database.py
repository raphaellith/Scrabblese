from datahandling.database_writer import ScrabbleseDatabaseWriter

# The maximum number of games to be inserted into the database before the program terminates
MAX_GAMES_TO_INSERT = 0

scrabblese_analyser = ScrabbleseDatabaseWriter()

# Ingest scraped games into the local SQLite cache.
scrabblese_analyser.scrape_and_cache_scrabble_games(scrape_listed_games=False, max_games_to_insert=MAX_GAMES_TO_INSERT)
