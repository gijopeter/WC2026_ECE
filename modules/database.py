import sqlite3
import pandas as pd

DB_NAME = "worldcup.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS players (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS games (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        stage TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        poll_no INTEGER UNIQUE,
        game_id INTEGER,  -- NULL for general poll
        question_text TEXT,
        FOREIGN KEY (game_id) REFERENCES games(id)
    );
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        option_text TEXT,
        points INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS selections (
        player_id INTEGER,
        question_id INTEGER,
        option_id INTEGER
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS results (
        question_id INTEGER UNIQUE,
        correct_option_id INTEGER
    )
    """)


    # Add group_name column if missing
    c.execute("PRAGMA table_info(games)")
    columns = [col[1] for col in c.fetchall()]

    if "group_name" not in columns:
        c.execute("ALTER TABLE games ADD COLUMN group_name TEXT")


    # Add points_incorrect column if missing
    c.execute("PRAGMA table_info(options)")
    columns = [col[1] for col in c.fetchall()]

    if "points_incorrect" not in columns:
        c.execute(
            "ALTER TABLE options ADD COLUMN points_incorrect INTEGER DEFAULT 0"
        ) 


    c.execute("PRAGMA table_info(questions)")
    columns = [col[1] for col in c.fetchall()]

    if "selection_type" not in columns:
        c.execute(
            "ALTER TABLE questions ADD COLUMN selection_type TEXT DEFAULT 'single'"
        )        

    conn.commit()
    conn.close()


# ---------- CRUD FUNCTIONS ----------

def add_player(name):
    conn = get_connection()
    conn.execute("INSERT OR IGNORE INTO players (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()


def get_players():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM players", conn)
    conn.close()
    return df


def add_game(name, stage, group_name=None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO games (name, stage, group_name) VALUES (?, ?, ?)",
        (name, stage, group_name)
    )
    conn.commit()
    conn.close()


def get_games():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM games", conn)
    conn.close()
    return df


def add_question(game_id, question_text, poll_no, selection_type="single"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO questions 
        (poll_no, game_id, question_text, selection_type)
        VALUES (?, ?, ?, ?)
        """,
        (poll_no, game_id, question_text, selection_type)
    )
    conn.commit()
    conn.close()


def get_questions():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM questions", conn)
    conn.close()
    return df


def add_option(question_id, option_text, points, points_incorrect):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO options
        (question_id, option_text, points, points_incorrect)
        VALUES (?, ?, ?, ?)
        """,
        (question_id, option_text, points, points_incorrect)
    )

    conn.commit()
    conn.close()
    

def get_options(question_id):
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM options WHERE question_id = ?", conn, params=(question_id,))
    conn.close()
    return df


def save_selection(player_id, question_id, option_id):
    conn = get_connection()
    conn.execute("""
        DELETE FROM selections
        WHERE player_id = ? AND question_id = ?
    """, (player_id, question_id))

    conn.execute("""
        INSERT INTO selections (player_id, question_id, option_id)
        VALUES (?, ?, ?)
    """, (player_id, question_id, option_id))

    conn.commit()
    conn.close()

def delete_player_selection_for_question(player_id, question_id):
    conn = get_connection()
    conn.execute(
        """
        DELETE FROM selections
        WHERE player_id = ? AND question_id = ?
        """,
        (player_id, question_id)
    )
    conn.commit()
    conn.close()


def add_selection_without_delete(player_id, question_id, option_id):
    conn = get_connection()

    conn.execute(
        """
        INSERT INTO selections (player_id, question_id, option_id)
        VALUES (?, ?, ?)
        """,
        (player_id, question_id, option_id)
    )

    conn.commit()
    conn.close()    


def save_results_for_question(question_id, correct_option_ids):
    conn = get_connection()

    conn.execute(
        "DELETE FROM results WHERE question_id = ?",
        (question_id,)
    )

    for option_id in correct_option_ids:
        conn.execute(
            """
            INSERT INTO results (question_id, correct_option_id)
            VALUES (?, ?)
            """,
            (question_id, option_id)
        )

    conn.commit()
    conn.close()

def get_results():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM results", conn)
    conn.close()
    return df    

def calculate_leaderboard():
    conn = get_connection()

    query = """
    SELECT
        p.name AS player,
        SUM(
            CASE
                WHEN r.correct_option_id IS NOT NULL
                THEN o.points
                ELSE COALESCE(o.points_incorrect, 0)
            END
        ) AS score
    FROM selections s
    JOIN players p ON s.player_id = p.id
    JOIN options o ON s.option_id = o.id
    LEFT JOIN results r
        ON s.question_id = r.question_id
        AND s.option_id = r.correct_option_id
    WHERE s.question_id IN (
        SELECT DISTINCT question_id FROM results
    )
    GROUP BY p.name
    ORDER BY score DESC
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

# -------------------------
# DELETE FUNCTIONS
# -------------------------

def delete_player(player_id):
    conn = get_connection()
    conn.execute("DELETE FROM players WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()


def delete_game(game_id):
    conn = get_connection()
    conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
    conn.commit()
    conn.close()

def delete_question(question_id):
    conn = get_connection()
    conn.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()

def delete_option(option_id):
    conn = get_connection()
    conn.execute("DELETE FROM options WHERE id = ?", (option_id,))
    conn.commit()
    conn.close()   

def get_saved_selections_for_question(question_id):
    conn = get_connection()

    query = """
    SELECT 
        p.name AS player,
        q.poll_no,
        q.question_text,
        o.option_text AS selected_option
    FROM selections s
    JOIN players p ON s.player_id = p.id
    JOIN questions q ON s.question_id = q.id
    JOIN options o ON s.option_id = o.id
    WHERE s.question_id = ?
    ORDER BY p.name
    """

    df = pd.read_sql(query, conn, params=(question_id,))
    conn.close()
    return df    

def delete_selections_for_question(question_id):
    conn = get_connection()
    conn.execute(
        "DELETE FROM selections WHERE question_id = ?",
        (question_id,)
    )
    conn.commit()
    conn.close()

def get_teams():
    return pd.DataFrame({
        "name": [
            "Algeria",
            "Argentina",
            "Australia",
            "Austria",
            "Belgium",
            "Bosnia and Herzegovina",
            "Brazil",
            "Cabo Verde",
            "Canada",
            "Colombia",
            "Congo DR",
            "Croatia",
            "Curaçao",
            "Czechia",
            "Côte d'Ivoire",
            "Ecuador",
            "Egypt",
            "England",
            "France",
            "Germany",
            "Ghana",
            "Haiti",
            "IR Iran",
            "Iraq",
            "Japan",
            "Jordan",
            "Korea Republic",
            "Mexico",
            "Morocco",
            "Netherlands",
            "New Zealand",
            "Norway",
            "Panama",
            "Paraguay",
            "Portugal",
            "Qatar",
            "Saudi Arabia",
            "Scotland",
            "Senegal",
            "South Africa",
            "Spain",
            "Sweden",
            "Switzerland",
            "Tunisia",
            "Türkiye",
            "USA",
            "Uruguay",
            "Uzbekistan"
        ]
    }) 

def calculate_poll_scores():
    conn = get_connection()

    query = """
    SELECT
        q.poll_no,
        q.question_text,
        p.name AS player,
        o.option_text AS selected_option,
        CASE
            WHEN s.option_id = r.correct_option_id
            THEN o.points
            ELSE COALESCE(o.points_incorrect, 0)
        END AS score
    FROM selections s
    JOIN players p ON s.player_id = p.id
    JOIN questions q ON s.question_id = q.id
    JOIN options o ON s.option_id = o.id
    JOIN results r ON s.question_id = r.question_id
    ORDER BY q.poll_no, p.name
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df


def calculate_cumulative_trend(last_n_polls=5, top_n_players=7):
    conn = get_connection()

    query = """
    SELECT
        q.poll_no,
        p.name AS player,
        CASE
            WHEN s.option_id = r.correct_option_id
            THEN o.points
            ELSE COALESCE(o.points_incorrect, 0)
        END AS score
    FROM selections s
    JOIN players p ON s.player_id = p.id
    JOIN questions q ON s.question_id = q.id
    JOIN options o ON s.option_id = o.id
    JOIN results r ON s.question_id = r.question_id
    ORDER BY q.poll_no
    """

    df = pd.read_sql(query, conn)
    conn.close()

    if df.empty:
        return df

    total_scores = (
        df.groupby("player")["score"]
        .sum()
        .sort_values(ascending=False)
        .head(top_n_players)
        .index
        .tolist()
    )

    last_polls = (
        df["poll_no"]
        .drop_duplicates()
        .sort_values()
        .tail(last_n_polls)
        .tolist()
    )

    trend_df = df[
        (df["player"].isin(total_scores)) &
        (df["poll_no"].isin(last_polls))
    ]

    trend_df = (
        trend_df.groupby(["poll_no", "player"])["score"]
        .sum()
        .reset_index()
    )

    trend_df["cumulative_score"] = (
        trend_df.sort_values("poll_no")
        .groupby("player")["score"]
        .cumsum()
    )

    return trend_df

def export_leaderboard_to_excel(output_path="data/leaderboard_snapshot.xlsx"):
    import os
    import pandas as pd

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    leaderboard = calculate_leaderboard()
    poll_scores = calculate_poll_scores()
    trend = calculate_cumulative_trend(last_n_polls=5, top_n_players=7)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        leaderboard.to_excel(writer, sheet_name="Leaderboard", index=False)
        poll_scores.to_excel(writer, sheet_name="PollScores", index=False)
        trend.to_excel(writer, sheet_name="Trend", index=False)

    return output_path