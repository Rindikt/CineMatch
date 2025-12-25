// movieDetail.js
import { fetchData, displayError } from './api.js';

function formatRuntime(totalMinutes) {
    if (!totalMinutes || totalMinutes <= 0) return '—';
    const hours = Math.floor(totalMinutes / 60);
    const minutes = totalMinutes % 60;
    return hours > 0 ? `${hours} ч ${minutes} мин` : `${minutes} мин`;
}

function formatCurrency(amount) {
    if (!amount || amount <= 0) return '—';
    return new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD', maximumFractionDigits: 0,
    }).format(amount);
}

/**
 * ЛОГИКА УПРАВЛЕНИЯ ПРОГРЕССОМ
 */
function setupUserActions(movie, movieId) {
    const section = document.getElementById('user_actions_section');
    const statusSelect = document.getElementById('status_select');
    const ratingInput = document.getElementById('personal_rating');
    const saveBtn = document.getElementById('save_progress_btn');
    const msg = document.getElementById('save_status_msg');

    if (!section) return; // Защита, если элемента нет в HTML

    if (localStorage.getItem('token')) {
        section.style.display = 'block';
    }

    if (movie.user_progress && movie.user_progress.length > 0) {
        const prog = movie.user_progress[0];
        statusSelect.value = prog.status || "";
        ratingInput.value = prog.personal_rating || "";
    }

    const checkStatus = () => {
        const status = statusSelect.value;
        // ТВОЕ УСЛОВИЕ: Оценка доступна только если статус не пустой и не 'planned'
        const canRate = status && status !== 'planned';

        if (!canRate) {
            ratingInput.disabled = true;
            ratingInput.value = '';
            ratingInput.style.opacity = '0.5';
        } else {
            ratingInput.disabled = false;
            ratingInput.style.opacity = '1';
        }
    };

    statusSelect.addEventListener('change', checkStatus);
    checkStatus();

    saveBtn.onclick = async () => {
        msg.textContent = "Сохранение...";
        msg.style.color = "black";

        const payload = {
            status: statusSelect.value || null,
            personal_rating: (ratingInput.value && !ratingInput.disabled) ? parseInt(ratingInput.value) : null
        };

        try {
            // Отправляем на твою новую объединенную ручку
            await fetchData(`/movies/${movieId}/progress`, {}, 'POST', JSON.stringify(payload));

            msg.textContent = "✅ Сохранено!";
            msg.style.color = "green";
        } catch (e) {
            console.error(e);
            msg.textContent = "❌ Ошибка: " + e.message;
            msg.style.color = "red";
        }
    };
}

async function loadMovieDetailContent(movieId) {
    try {
        const movie = await fetchData(`/movies/${movieId}`);
        const container = document.getElementById('movie_detail_container');

        // Инициализируем блок прогресса
        setupUserActions(movie, movieId);

        const genreList = movie.genres.map(g => g.genre.name).join(', ');
        const actorListHtml = movie.actors.map(item => `
            <li class="actor-item">
                ${item.actor?.profile_url ? `<img src="${item.actor.profile_url}" class="actor-photo">` : '<div class="actor-no-photo">Нет фото</div>'}
                <div class="actor-info">
                    <a href="actor_detail.html?id=${item.actor?.id}"><strong>${item.actor?.name}</strong></a>
                    <p>Роль: ${item.role_name}</p>
                </div>
            </li>
        `).join('');

        container.innerHTML = `
            <div class="detail-view">
                ${movie.poster_url ? `<img src="${movie.poster_url}" alt="${movie.title}">` : ''}
                <div class="movie-info-content">
                    <h2>${movie.title} (${movie.release_year})</h2>
                    ${movie.tagline ? `<p><strong>Слоган:</strong> <em>"${movie.tagline}"</em></p>` : ''}
                    <p>⭐ <strong>Рейтинг:</strong> ${movie.rating}</p>
                    <p><strong>Жанры:</strong> ${genreList || '—'}</p>
                    <p><strong>Время:</strong> ${formatRuntime(movie.runtime_minutes)}</p>
                    <p><strong>Бюджет:</strong> ${formatCurrency(movie.budget)}</p>
                    <p><strong>Сборы:</strong> ${formatCurrency(movie.revenue)}</p>
                    <h4>Описание</h4>
                    <p>${movie.description || 'Описание отсутствует.'}</p>
                    <h4>Актерский состав:</h4>
                    <ul class="actor-list">${actorListHtml || 'Нет данных'}</ul>
                </div>
            </div>
        `;
    } catch (error) {
        displayError(`Ошибка: ${error.message}`);
    }
}

window.onload = () => {
    const movieId = new URLSearchParams(window.location.search).get('id');
    movieId ? loadMovieDetailContent(movieId) : displayError('ID фильма не указан.');
};