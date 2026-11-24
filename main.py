from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel

from db import get_connection

app = FastAPI()


# Модель для создания и полной замены фильма
class MovieCreate(BaseModel):
    title: str
    year: int
    rating: float
    watched: bool


# Модель для частичного обновления фильма
class MoviePatch(BaseModel):
    title: str | None = None
    year: int | None = None
    rating: float | None = None
    watched: bool | None = None


# Временное хранилище для ещё не перенесённых операций
movies = [
    {
        "id": 1,
        "title": "Веном",
        "year": 2018,
        "rating": 6.7,
        "watched": False
    },
    {
        "id": 2,
        "title": "Дедпул",
        "year": 2016,
        "rating": 8.0,
        "watched": True
    }
]


# GET — получение всех фильмов из PostgreSQL
@app.get("/api/movies")
def get_movies():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, title, year, rating, watched
                FROM movies
                ORDER BY id;
            """)

            movies_from_db = cursor.fetchall()

    return movies_from_db


# GET — получение фильма по ID
@app.get("/api/movies/{movie_id}")
def get_movie(movie_id: int):

    for movie in movies:
        if movie["id"] == movie_id:
            return movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )


# POST — создание фильма
@app.post("/api/movies", status_code=201)
def create_movie(movie: MovieCreate):

    new_id = max(
        (item["id"] for item in movies),
        default=0
    ) + 1

    new_movie = movie.model_dump()
    new_movie["id"] = new_id

    movies.append(new_movie)

    return new_movie


# PUT — полная замена фильма
@app.put("/api/movies/{movie_id}")
def replace_movie(movie_id: int, movie: MovieCreate):

    for existing_movie in movies:
        if existing_movie["id"] == movie_id:

            existing_movie.update(movie.model_dump())

            return existing_movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )


# PATCH — частичное обновление фильма
@app.patch("/api/movies/{movie_id}")
def update_movie(movie_id: int, movie: MoviePatch):

    for existing_movie in movies:
        if existing_movie["id"] == movie_id:

            update_data = movie.model_dump(
                exclude_unset=True,
                exclude_none=True
            )

            if not update_data:
                raise HTTPException(
                    status_code=400,
                    detail="No fields provided"
                )

            existing_movie.update(update_data)

            return existing_movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )


# DELETE — удаление фильма
@app.delete("/api/movies/{movie_id}", status_code=204)
def delete_movie(movie_id: int):

    for movie in movies:
        if movie["id"] == movie_id:

            movies.remove(movie)

            return Response(status_code=204)

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )
