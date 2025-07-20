import sqlite3, json, random, os, dotenv
dotenv.load_dotenv()


class Users_DB:
    def __init__(self):
        self.con = sqlite3.connect("data.db")
        self.cur = self.con.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            language TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS all_movie (
            key TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            movie_id TEXT NOT NULL UNIQUE,
            poster TEXT NOT NULL,
            desc TEXT NOT NULL,
            actors TEXT,
            category TEXT NOT NULL,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS watched_movies (
            key INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            movie_id TEXT NOT NULL UNIQUE,
            watched BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)
        self.con.commit()

    def add_movie(self, key: str, name: str, movie_id: str, poster_id: str, desc: str, actors: list, category: list):
        self.cur.execute(f'INSERT INTO all_movie (key, name, movie_id, poster, desc, actors, category) VALUES (?, ?, ?, ?, ?, ?, ?)', (key, name, movie_id, poster_id, desc, json.dumps(actors), json.dumps(category)))
        self.con.commit()
    
    def get_all_movies(self):
        self.cur.execute("SELECT * FROM all_movie")
        return self.cur.fetchall()
    
    def get_movie(self, key: str):
        self.cur.execute(f'SELECT * FROM all_movie WHERE key = ?', (key,))
        return self.cur.fetchone()

    def mark_movie_as_watched(self, user_id: int, key: str):
        # Tekshiramiz: yozuv mavjudmi?
        self.cur.execute("""
            SELECT id FROM watched_movies
            WHERE user_id = ? AND key = ?
        """, (user_id, key))
        exists = self.cur.fetchone()
        
        if exists:
            # Mavjud bo‘lsa — statusni yangilaymiz
            self.cur.execute("""
                UPDATE watched_movies
                SET watched = TRUE
                WHERE user_id = ? AND key = ?
            """, (user_id, key))
        else:
            # Yo‘q bo‘lsa — yangi yozuv qo‘shamiz
            self.cur.execute("""
                INSERT INTO watched_movies (user_id, key, watched)
                VALUES (?, ?, TRUE)
            """, (user_id, key))
        
        self.con.commit()

    def delete_movie(self, key: str):
        self.cur.execute("DELETE FROM watched_movies WHERE key = ?", (key,))
        self.cur.execute("DELETE FROM all_movie WHERE key = ?", (key,))
        self.con.commit()

    def get_all_watched(self, user_id: int):
        self.cur.execute(f"SELECT * FROM watched_movies WHERE user_id = ? AND watched = TRUE", (user_id,))
        return self.cur.fetchall()
    
    def add_user(self, user_id: int, user_name: str, language: str = "uz"):
        if language not in ("uz", "ru", "en"):
            return ValueError("Noto‘g‘ri til!")
        self.cur.execute(f"INSERT INTO users (id, name, language) VALUES (?, ?, ?)", (user_id, user_name, language))
        self.con.commit()
    
    def find_user(self, user_id: int):
        self.cur.execute(f"SELECT * FROM users WHERE id = ?", (user_id,))
        return self.cur.fetchone()

    def get_all_user(self):
        self.cur.execute("SELECT * FROM users")
        return self.cur.fetchall()


database = Users_DB()

def key_generate():
    movies = [key[0] for key in database.get_all_movies()]
    
    while True:
        key = os.getenv('MOVIE_KEY')+"".join(random.choice("0123456789") for _ in range(5))
        
        if key not in movies:
            break
    
    return key



# database.get_all_movies()

# data = Users_DB()
# data.add_user(1546, 'Tohir', 'ru')
# data.add_user(1548, 'Tohir', 'tj')
# data.add_user(1544, 'Bobur')
# data.add_user(1542, 'G`iyos')
# print(data.find_user(1542))
# print(type(data.find_user(1542)))
# print(data.get_all_user())
# print(type(data.get_all_user()))

# data.add_movie(545499, 49494949)
# data.add_movie(545493, 49494945)
# print(data.get_movie(545493))
# data.watched_movie(1542, 545499, True)
# data.watched_movie(1542, 545493, True)
# print(data.get_all_watched(1542))