
from db import get_connection


def main():

    with get_connection() as connection:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT id, title, year, rating, watched
                FROM movies
                ORDER BY id;
            """)

            movies = cursor.fetchall()

    print("Соединение с PostgreSQL успешно!")

    for movie in movies:
        print(movie)


if __name__ == "__main__":
    main()
