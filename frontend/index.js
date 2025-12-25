import { fetchData, displayError } from './api.js';
import { updateAuthUI, login, logout, register } from './auth.js';

let currentPage = 1;
let isSearchMode = false;

window.login = login;
window.logout = logout;
window.register = register;

/**
 * 1. ЗАГРУЗКА ЖАНРОВ
 */
async function loadGenres() {
    try {
        const genres = await fetchData('/genres');
        const select = document.getElementById('genre_select');
        if (!select) return;
        select.innerHTML = '<option value="">Все жанры</option>';
        genres.forEach(genre => {
            const option = document.createElement('option');
            option.value = genre.id;
            option.textContent = genre.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error("Ошибка жанров:", error);
    }
}

/**
 * 2. ОТРИСОВКА КАРТОЧЕК
 */
function renderMovies(movies, total) {
    const container = document.getElementById('movie_results');
    const countDisplay = document.getElementById('results_count');

    if (countDisplay) {
        countDisplay.innerText = total > 0 ? `Найдено: ${total}` : `Ничего не найдено`;
    }

    if (!container) return;
    container.innerHTML = '';

    const moviesList = Array.isArray(movies) ? movies : (movies?.items || []);

    if (moviesList.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 50px; color: #888;">Список пуст</div>`;
        return;
    }

    moviesList.forEach(movie => {
        // Проверяем прогресс (у тебя в Python это Movie.user_progress)
        const progress = (movie.user_progress && movie.user_progress.length > 0) ? movie.user_progress[0] : null;

        let statusBadge = '';
        let personalRate = '';

        if (progress) {
            const statusMap = {
                'completed': { txt: '✅ Просмотрено', color: '#28a745' },
                'watching': { txt: '👀 Смотрю', color: '#007bff' },
                'planned': { txt: '📅 В планах', color: '#ffc107' },
                'dropped': { txt: '🗑️ Брошено', color: '#dc3545' }
            };
            const s = statusMap[progress.status] || { txt: progress.status, color: '#6c757d' };
            statusBadge = `<div style="background: ${s.color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-top: 5px; display: inline-block;">${s.txt}</div>`;

            if (progress.personal_rating) {
                personalRate = `<div style="color: #ff9800; font-weight: bold; font-size: 13px;">Моя: ⭐ ${progress.personal_rating}</div>`;
            }
        }

        const card = document.createElement('div');
        card.style = `cursor: pointer; transition: 0.3s; background: white; border-radius: 12px;`;
        card.innerHTML = `
            <div style="position: relative; overflow: hidden; border-radius: 10px; aspect-ratio: 2/3; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px;">
                    ⭐ ${movie.rating ? movie.rating.toFixed(1) : '0.0'}
                </div>
            </div>
            <div style="padding: 12px 0;">
                <div style="font-weight: bold; font-size: 15px; color: #000; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
                    ${movie.title}
                </div>
                <div style="color: #888; font-size: 12px;">${movie.release_year} • ${movie.genres?.[0]?.genre?.name || 'Кино'}</div>
                <div style="min-height: 40px; margin-top: 5px;">
                    ${personalRate}
                    ${statusBadge}
                </div>
            </div>
        `;

        card.onclick = () => window.location.href = `movie_detail.html?id=${movie.id}`;
        card.onmouseover = () => card.style.transform = 'translateY(-5px)';
        card.onmouseout = () => card.style.transform = 'translateY(0)';
        container.appendChild(card);
    });

    // ВАЖНО: Возвращаем вызов пагинации!
    renderPagination(total);
}

/**
 * 3. ПАГИНАЦИЯ
 */
function renderPagination(total) {
    const pagination = document.getElementById('pagination');
    if (!pagination) return;
    pagination.innerHTML = '';

    const totalPages = Math.ceil(total / 20);
    if (totalPages <= 1) return;

    const nav = document.createElement('div');
    // Центрируем и оформляем контейнер
    nav.style = "display: flex; gap: 10px; align-items: center; justify-content: center; margin: 40px 0; padding-bottom: 20px;";

    const createBtn = (text, isDisabled, onClick) => {
        const btn = document.createElement('button');
        btn.innerText = text;
        // Стили кнопки: синяя рамка, белый фон
        btn.style = `
            padding: 8px 18px;
            border: 1px solid #007bff;
            border-radius: 6px;
            background: ${isDisabled ? '#eee' : 'white'};
            color: ${isDisabled ? '#999' : '#007bff'};
            cursor: ${isDisabled ? 'not-allowed' : 'pointer'};
            font-weight: 600;
            transition: 0.3s;
        `;
        btn.disabled = isDisabled;
        if (!isDisabled) {
            btn.onclick = onClick;
            btn.onmouseover = () => { btn.style.background = '#007bff'; btn.style.color = 'white'; };
            btn.onmouseout = () => { btn.style.background = 'white'; btn.style.color = '#007bff'; };
        }
        return btn;
    };

    nav.appendChild(createBtn('← Назад', currentPage === 1, () => {
        currentPage--;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo(0, 0);
    }));

    const info = document.createElement('span');
    info.innerText = `Стр. ${currentPage} / ${totalPages}`;
    info.style = "font-size: 14px; color: #555; font-weight: 500;";
    nav.appendChild(info);

    nav.appendChild(createBtn('Вперед →', currentPage >= totalPages, () => {
        currentPage++;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo(0, 0);
    }));

    pagination.appendChild(nav);
}

/**
 * 4. ПОИСК
 */
async function searchMovies() {
    isSearchMode = true;
    const query = document.getElementById('search_input')?.value.trim();
    try {
        // Исправлено: твой бэкенд ждет параметр 'search'
        const response = await fetchData('/movies/search', { search: query, page: currentPage });
        renderMovies(response.items, response.total_items);
    } catch (error) {
        displayError("Ошибка поиска");
    }
}

/**
 * 5. ФИЛЬТРАЦИЯ
 */
async function fetchMovies() {
    isSearchMode = false;
    try {
        const params = {
            page: currentPage,
            page_size: 20,
            genre_ids: document.getElementById('genre_select')?.value || '',
            year_min: document.getElementById('year_min')?.value || 1900,
            year_max: document.getElementById('year_max')?.value || '',
            rating_min: document.getElementById('rating_min')?.value || 1.0,
            sort_by: document.getElementById('sort_by')?.value || 'popularity',
            direction: document.getElementById('direction')?.value || 'desc'
        };

        const response = await fetchData('/movies/filter', params);
        renderMovies(response.items, response.total_items);
    } catch (error) {
        displayError("Ошибка загрузки");
    }
}

/**
 * 6. ГЛОБАЛЬНЫЕ КОМАНДЫ
 */
window.searchOrFilter = () => {
    currentPage = 1;
    const query = document.getElementById('search_input')?.value.trim();
    if (query) searchMovies(); else fetchMovies();
};

window.resetFilters = () => {
    document.getElementById('search_input').value = '';
    document.getElementById('genre_select').value = '';
    document.getElementById('year_min').value = '1900';
    document.getElementById('year_max').value = '';
    currentPage = 1;
    fetchMovies();
};

window.onload = () => {
    updateAuthUI();
    loadGenres();
    fetchMovies();
};