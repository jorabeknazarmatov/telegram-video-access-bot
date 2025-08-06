import sqlite3, json, random, os, dotenv
dotenv.load_dotenv()


class Users_DB:
    def __init__(self):
        self.post = ['key','name','movie_id','poster_id','desc','actors','category','imdb','kinopoisk','duration','country']
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
            key TEXT NOT NULL UNIQUE,
            user_id INTEGER REFERENCES users(id),
            movie_id TEXT NOT NULL UNIQUE,
            watched BOOLEAN NOT NULL DEFAULT FALSE
        )
        """)

        # type = film or serial
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS movies_info (
            key TEXT NOT NULL UNIQUE,
            imdb REAL,
            kinopoisk REAL,
            duration INTEGER NOT NULL,
            country TEXT NOT NULL
        )
        """)

        self.con.commit()

    def add_movie(self, data: dict):
        try:
            actors = json.dumps(data.get('actors', []))
            category = json.dumps(data.get('category', []))

            self.cur.execute(f"""
            INSERT INTO all_movie (key, name, movie_id, poster, desc, actors, category)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (data['key'], data['name'], data['movie_id'], data['poster_id'], data['desc'], actors, category))
            
            self.con.commit()
        except KeyError as e:
            print(f"❌ There is no required field: {e}")
        except sqlite3.Error as e:
            print(f"❌ SQL error: {e}")
        except Exception as e:
            print(f"❌ Unknown error: {e}")

    def add_info(self, data: dict):
        try:
            self.cur.execute("""
        INSERT INTO movies_info (key, imdb, kinopoisk, duration, country)
        VALUES (?, ?, ?, ?, ?)
        """,
        (data['key'], float(data['imdb']), float(data['kinopoisk']), int(data['duration']), data['country'])
        )
            self.con.commit()
        except KeyError as e:
            print(f"❌ There is no required field: {e}")
        except sqlite3.Error as e:
            print(f"❌ SQL error: {e}")
        except Exception as e:
            print(f"❌ Unknown error: {e}")

    
    def get_all_movies(self):
        self.cur.execute("""
            SELECT 
                all_movie.key,
                all_movie.name,
                all_movie.movie_id,
                all_movie.poster,
                all_movie.desc,
                all_movie.actors,
                all_movie.category,
                movies_info.imdb,
                movies_info.kinopoisk,
                movies_info.duration,
                movies_info.country
            FROM all_movie
            JOIN movies_info ON all_movie.key = movies_info.key
        """)
        movies = []
                
        for row in self.cur.fetchall():
            movie = dict(zip(self.post, row))
            movies.append(movie)
            
        return movies
    
    def get_movie(self, key: str):
        self.cur.execute("""
            SELECT 
                all_movie.key,
                all_movie.name,
                all_movie.movie_id,
                all_movie.poster,
                all_movie.desc,
                all_movie.actors,
                all_movie.category,
                movies_info.imdb,
                movies_info.kinopoisk,
                movies_info.duration,
                movies_info.country
            FROM all_movie
            JOIN movies_info ON all_movie.key = movies_info.key
            WHERE all_movie.key = ?
        """, (key,))
        data = self.cur.fetchone()
        if data is None:
            return None
        return dict(zip(self.post, data)) 

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
    movie_keys = [key[0] for key in database.get_all_movies()]
    
    while True:
        new_key = os.getenv('MOVIE_KEY')+"".join(random.choice("0123456789") for _ in range(5))
        
        if new_key not in movie_keys:
            return new_key   



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