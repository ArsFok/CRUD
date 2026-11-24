from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
from psycopg import sql

from db import get_connection

app = FastAPI()


# Модель создания и полной замены фильма
class MovieCreate(BaseModel):
    title: str
    year: int
    rating: float
    watched: bool


# Модель частичного обновления фильма
class MoviePatch(BaseModel):
    title: str | None = None
    year: int | None = None
    rating: float | None = None
    watched: bool | None = None


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


# PUT — полная замена фильма
@app.put("/api/movies/{movie_id}")
def replace_movie(movie_id: int, movie: MovieCreate):

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                UPDATE movies
                SET title = %s,
                    year = %s,
                    rating = %s,
                    watched = %s
                WHERE id = %s
                RETURNING id, title, year, rating, watched;
            """, (
                movie.title,
                movie.year,
                movie.rating,
                movie.watched,
                movie_id
            ))

            updated_movie = cursor.fetchone()

    if updated_movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return updated_movie


# PATCH — частичное обновление фильма
@app.patch("/api/movies/{movie_id}")
def update_movie(movie_id: int, movie: MoviePatch):

    update_data = movie.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        raise HTTPException(
            status_code=400,
            detail="No fields provided"
        )

    set_clause = sql.SQL(", ").join(
        sql.SQL("{} = %s").format(sql.Identifier(field))
        for field in update_data
    )

    query = sql.SQL("""
        UPDATE movies
        SET {}
        WHERE id = %s
        RETURNING id, title, year, rating, watched;
    """).format(set_clause)

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute(
                query,
                (*update_data.values(), movie_id)
            )

            updated_movie = cursor.fetchone()

    if updated_movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return updated_movie


# DELETE — удаление фильма
@app.delete("/api/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int):

    with get_connection() as connection:
        with connection.cursor() as cursor:

            cursor.execute("""
                DELETE FROM movies
                WHERE id = %s
                RETURNING id;
            """, (movie_id,))

            deleted_movie = cursor.fetchone()

    if deleted_movie is None:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    return Response(status_code=204)

app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)