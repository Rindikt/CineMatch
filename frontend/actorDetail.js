// actorDetail.js
import { fetchData, displayError } from './api.js';

// --- Функции для страницы деталей актера ---

async function loadActorDetailContent(actorId) {
    try {
        const actor = await fetchData(`/actors/${actorId}`);
        const actorMovies = await fetchData(`/actors/${actorId}/movies`);

        const container = document.getElementById('actor_detail_container');

        const profilePhoto = actor.profile_url
            ? `<img src="${actor.profile_url}" alt="${actor.name}">`
            : `<div class="actor-info-left no-photo" style="max-width: 250px;">Нет фото</div>`;

        // Получаем значения полей
        const biography = actor.biography || 'Нет биографии.';
        const deathday = actor.deathday;
        const popularity = actor.popularity;

        // Условный вывод Даты смерти (только если она есть)
        const deathdayHtml = deathday
            ? `<p><strong>Дата смерти:</strong> ${deathday}</p>`
            : '';

        // Условный вывод Популярности/Рейтинга (если она есть)
        // Используем toFixed(2) для форматирования числа
        const popularityHtml = (popularity !== null && popularity !== undefined)
            ? `<p><strong>Рейтинг (TMDB):</strong> ${popularity.toFixed(2)}</p>`
            : '';


        // Генерация списка фильмов актера
        const movieListHtml = actorMovies.map(movie => {
            const moviePoster = movie.poster_url
                ? `<img src="${movie.poster_url}" alt="${movie.title}">`
                : `<div class="no-poster">Нет постера</div>`;

            // Ссылка обратно на страницу деталей фильма
            return `
                <a href="movie_detail.html?id=${movie.id}" class="movie-card-small">
                    ${moviePoster}
                    <div style="font-size: 0.9em; padding-top: 5px;">${movie.title} (${movie.release_year})</div>
                </a>
            `;
        }).join('');

        container.innerHTML = `
            <div class="actor-page-wrapper">
                <div class="actor-header-flex">
                    <div class="actor-info-left">
                        ${profilePhoto}
                    </div>

                    <div class="actor-info-right">
                        <h2>${actor.name}</h2>
                        <p><strong>Дата рождения:</strong> ${actor.birthday || 'Неизвестно'}</p>
                        ${deathdayHtml}
                        ${popularityHtml}

                        <h4>Биография:</h4>
                        <p>${biography}</p>
                    </div>
                </div>

                <h4 style="padding-top: 15px;">Фильмография:</h4>
                ${movieListHtml ? `<div class="movie-list">${movieListHtml}</div>` : '<p>Нет данных о фильмах.</p>'}
            </div>
        `;

    } catch (error) {
        // Указываем ошибку в контейнере и в консоли
        displayError(`Ошибка загрузки деталей актера: ${error.message}`);
        document.getElementById('actor_detail_container').innerHTML = `<p class="error">Ошибка загрузки деталей актера: ${error.message}</p>`;
    }
}

// ❗ Точка входа для actor_detail.html ❗
window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    const actorId = urlParams.get('id');

    if (actorId) {
        loadActorDetailContent(actorId);
    } else {
        displayError('ID актера не указан.');
    }
};