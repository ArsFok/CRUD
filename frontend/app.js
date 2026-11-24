
const API_URL = "/api/movies";

const movieList = document.querySelector("#movies-list");
const movieForm = document.querySelector("#movie-form");
const statusMessage = document.querySelector("#status");
const refreshButton = document.querySelector("#refresh-button");


// Отображение сообщения пользователю
function showStatus(message, isError = false) {
    statusMessage.textContent = message;
    statusMessage.classList.toggle("error", isError);
}


// Создание карточки фильма
function createMovieCard(movie) {

    const card = document.createElement("article");
    card.className = "movie-card";

    const header = document.createElement("div");
    header.className = "movie-card-header";

    const id = document.createElement("span");
    id.className = "movie-id";
    id.textContent = `ID: ${movie.id}`;

    const status = document.createElement("span");
    status.className = "movie-status";

    if (movie.watched) {
        status.textContent = "Просмотрен";
        status.classList.add("watched");
    } else {
        status.textContent = "Не просмотрен";
        status.classList.add("not-watched");
    }

    header.append(id, status);

    const title = document.createElement("h3");
    title.textContent = movie.title;

    const details = document.createElement("p");
    details.textContent = `Год выпуска: ${movie.year}`;

    const rating = document.createElement("p");
    rating.textContent = `Оценка: ${movie.rating} / 10`;

    card.append(header, title, details, rating);

    return card;
}


// Получение фильмов из Backend
async function loadMovies() {

    movieList.textContent = "Загрузка фильмов...";

    try {

        const response = await fetch(API_URL);

        if (!response.ok) {
            throw new Error(`Ошибка сервера: ${response.status}`);
        }

        const movies = await response.json();

        movieList.replaceChildren();

        if (movies.length === 0) {

            const emptyMessage = document.createElement("p");
            emptyMessage.className = "empty-state";
            emptyMessage.textContent = "Коллекция пока пуста.";

            movieList.append(emptyMessage);

            return;
        }

        movies.forEach(movie => {
            const card = createMovieCard(movie);
            movieList.append(card);
        });

    } catch (error) {

        movieList.textContent = "Не удалось загрузить фильмы.";
        console.error(error);

    }
}


// Добавление фильма через POST
movieForm.addEventListener("submit", async (event) => {

    event.preventDefault();

    const movie = {
        title: document.querySelector("#title").value.trim(),
        year: Number(document.querySelector("#year").value),
        rating: Number(document.querySelector("#rating").value),
        watched: document.querySelector("#watched").checked
    };

    try {

        const response = await fetch(API_URL, {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(movie)

        });

        if (!response.ok) {

            const errorData = await response.json().catch(() => ({}));

            throw new Error(
                errorData.detail || `Ошибка сервера: ${response.status}`
            );
        }

        const createdMovie = await response.json();

        showStatus(
            `Фильм добавлен! Его ID: ${createdMovie.id}`
        );

        movieForm.reset();

        await loadMovies();

    } catch (error) {

        showStatus(error.message, true);

    }

});


// Ручное обновление коллекции
refreshButton.addEventListener("click", loadMovies);


// Загружаем фильмы при открытии сайта
loadMovies();
