from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from db import get_connection

app = FastAPI()


# Модель создания фильма
class MovieCreate(BaseModel):
    title: str
    year: int
    rating: float
    watched: bool


# GET — получение всех фильмов
@app.get("/api/movies")
def get_movies():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, title, year, rating, watched
                FROM movies
                ORDER BY id;
            """)

            movies = cursor.fetchall()

    return movies


# GET — получение фильма по ID
@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: int):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, title, year, rating, watched
                FROM movies
                WHERE id = %s;
            """, (movie_id,))

            movie = cursor.fetchone()

    if movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return movie


# POST — создание фильма
@app.post("/api/movies", status_code=201)
def create_movie(movie: MovieCreate):

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO movies (title, year, rating, watched)
                VALUES (%s, %s, %s, %s)
                RETURNING id, title, year, rating, watched;
            """, (
                movie.title,
                movie.year,
                movie.rating,
                movie.watched
            ))

            new_movie = cursor.fetchone()

    return new_movie
