import { fetchData, displayError } from './api.js';

// --- УТИЛИТЫ ФОРМАТИРОВАНИЯ ---
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
 * ЛОГИКА УПРАВЛЕНИЯ ПРОГРЕССОМ (СТАТУС И ОЦЕНКА)
 */
async function setupUserActions(movie, movieId) {
    const section = document.getElementById('user_actions_section');
    if (!section) return;

    const token = localStorage.getItem('token');
    if (!token) {
        section.innerHTML = `<p style="color: #888; text-align: center;">Войдите, чтобы поставить оценку</p>`;
        return;
    }

    const prog = (movie.user_progress && movie.user_progress.length > 0) ? movie.user_progress[0] : null;

    section.innerHTML = `
        <div style="background: #f8f9fa; padding: 15px; border-radius: 10px; display: flex; flex-wrap: wrap; gap: 15px; align-items: flex-end;">
            <div style="flex: 1; min-width: 150px;">
                <label style="display: block; font-size: 12px; color: #666; margin-bottom: 5px;">Статус</label>
                <select id="user_status_select" style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ddd;">
                    <option value="">-- Выберите --</option>
                    <option value="planned" ${prog?.status === 'planned' ? 'selected' : ''}>📅 В планах</option>
                    <option value="watching" ${prog?.status === 'watching' ? 'selected' : ''}>👀 Смотрю</option>
                    <option value="completed" ${prog?.status === 'completed' ? 'selected' : ''}>✅ Просмотрено</option>
                    <option value="dropped" ${prog?.status === 'dropped' ? 'selected' : ''}>🗑️ Брошено</option>
                </select>
            </div>
            <div style="width: 80px;">
                <label style="display: block; font-size: 12px; color: #666; margin-bottom: 5px;">Оценка (1-10)</label>
                <input type="number" id="user_rating_input" min="1" max="10" step="1"
                       value="${prog?.personal_rating || ''}"
                       style="width: 100%; padding: 8px; border-radius: 5px; border: 1px solid #ddd;">
            </div>
            <button id="save_progress_btn" style="background: #007bff; color: white; border: none; padding: 9px 20px; border-radius: 5px; cursor: pointer; font-weight: bold;">
                Сохранить
            </button>
        </div>
    `;

        document.getElementById('save_progress_btn').onclick = async () => {
        const status = document.getElementById('user_status_select').value;
        const ratingInput = document.getElementById('user_rating_input').value;

        const payload = {
            status: status || null,
            // Преобразуем в число, чтобы бэкенд (pytest) принял как int
            personal_rating: ratingInput ? parseInt(ratingInput) : null
        };

        try {
            await fetchData(`/movies/${movieId}/progress`, {}, 'POST', JSON.stringify(payload));
            // Вместо alert лучше просто обновить данные
            location.href = location.href; // Это принудительно обновит страницу без кеша
        } catch (err) {
            alert("Ошибка: " + err.message);
        }
    };
}

/**
 * ГЛАВНЫЙ РЕНДЕР СТРАНИЦЫ
 */
async function renderPage() {
    const posterContainer = document.getElementById('movie_poster');
    const infoContainer = document.getElementById('movie_info_content');
    const urlParams = new URLSearchParams(window.location.search);
    const movieId = urlParams.get('id');

    if (!movieId) return;

    try {
        const movie = await fetchData(`/movies/${movieId}`);

        let currentUser = null;
        if (localStorage.getItem('token')) {
            currentUser = await fetchData('/users/me').catch(() => null);
        }

        // 1. Постер (Левая часть)
        posterContainer.innerHTML = `
            <div style="position: relative;">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450'}"
                     style="width: 100%; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);">

                ${currentUser?.role === 'admin' ? `
                    <button id="delete_movie_btn" style="margin-top: 15px; width: 100%; padding: 10px; background: transparent; color: #dc3545; border: 1px solid #dc3545; border-radius: 6px; cursor: pointer; font-size: 12px; font-weight: bold; transition: 0.3s;">
                        🗑️ Удалить фильм
                    </button>
                ` : ''}
            </div>
        `;

        // 2. Актеры (HTML)
        const actorsHtml = movie.actors?.map(item => {
            const photoUrl = item.actor.profile_path
                ? `https://image.tmdb.org/t/p/w185${item.actor.profile_path}`
                : 'https://via.placeholder.com/50x50?text=?';

            return `
                <div style="display: flex; align-items: center; gap: 12px; background: #fdfdfd; padding: 10px; border-radius: 10px; border: 1px solid #f0f0f0;">
                    <img src="${photoUrl}" style="width: 48px; height: 48px; border-radius: 50%; object-fit: cover; background: #eee;">
                    <div style="overflow: hidden;">
                        <a href="actor_detail.html?id=${item.actor.id}" style="text-decoration: none; color: #007bff; font-weight: bold; font-size: 14px; display: block;">
                            ${item.actor.name}
                        </a>
                        <div style="font-size: 12px; color: #777; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">${item.role_name}</div>
                    </div>
                </div>
            `;
        }).join('') || '<p>Список пуст</p>';

        // 3. Правая часть (с увеличенным паддингом)
        infoContainer.innerHTML = `
            <div style="padding-left: 10px;"> <div style="margin-bottom: 30px;">
                    <h1 style="margin: 0; font-size: 42px; color: #111; line-height: 1.1;">${movie.title}</h1>
                    <p style="margin: 10px 0; color: #888; font-size: 20px;">${movie.release_year}${movie.tagline ? ` — «${movie.tagline}»` : ''}</p>
                </div>

                <div style="margin-bottom: 40px;">
                    <h3 style="border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;">О фильме</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <style>
                            .info-row td { padding: 12px 15px; border-bottom: 1px solid #f9f9f9; font-size: 16px; }
                            .info-label { color: #888; width: 180px; }
                        </style>
                        <tbody class="info-row">
                            <tr><td class="info-label">Рейтинг TMDB</td><td style="font-weight: bold; color: #f39c12;">⭐ ${movie.rating}</td></tr>
                            <tr><td class="info-label">Жанры</td><td>${movie.genres?.map(g => g.genre.name).join(', ') || '—'}</td></tr>
                            <tr><td class="info-label">Длительность</td><td>${formatRuntime(movie.runtime_minutes)}</td></tr>
                            <tr><td class="info-label">Бюджет</td><td>${formatCurrency(movie.budget)}</td></tr>
                            <tr><td class="info-label">Сборы</td><td>${formatCurrency(movie.revenue)}</td></tr>
                        </tbody>
                    </table>
                </div>

                <div style="margin-bottom: 40px; padding: 0 10px;"> <h3 style="border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 15px;">Сюжет</h3>
                    <p style="line-height: 1.8; color: #333; font-size: 17px; text-align: justify; margin: 0;">
                        ${movie.description || 'Описание не заполнено.'}
                    </p>
                </div>

                <div style="padding: 0 10px;"> <h3 style="border-bottom: 2px solid #eee; padding-bottom: 10px; margin-bottom: 20px;">В главных ролях</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 15px;">
                        ${actorsHtml}
                    </div>
                </div>
            </div>
        `;

        // Инициализация
        await setupUserActions(movie, movieId);

        // Обработчик удаления
        const delBtn = document.getElementById('delete_movie_btn');
        if (delBtn) {
            delBtn.onclick = async () => {
                if (confirm(`Удалить фильм "${movie.title}"?`)) {
                    await fetchData(`/movies/${movie.tmdb_id}`, {}, 'DELETE');
                    window.location.href = 'index.html';
                }
            };
        }

    } catch (err) {
        displayError(err.message);
    }
}

window.onload = renderPage;