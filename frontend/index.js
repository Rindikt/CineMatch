// index.js (Финальная версия с поддержкой статусов и личных оценок)
import { fetchData, displayError } from './api.js';
import { updateAuthUI, login, logout } from './auth.js';

let currentPage = 1;
let totalPages = 1;
const ITEMS_PER_PAGE = 20;

/**
 * Загрузка жанров для выпадающего списка
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
        displayError("Ошибка загрузки жанров: " + error.message);
    }
}

/**
 * Сброс всех фильтров
 */
function resetFilters() {
    const searchInput = document.getElementById('search_input');
    if (searchInput) {
        searchInput.value = '';
        searchInput.removeAttribute('data-last-query');
    }
    document.getElementById('genre_select').value = '';
    document.getElementById('year_min').value = '1900';
    document.getElementById('year_max').value = '';
    document.getElementById('rating_min').value = '1.0';
    document.getElementById('sort_select').value = 'rating';
    document.getElementById('direction_select').value = 'desc';

    currentPage = 1;
    const pageInput = document.getElementById('page_input');
    if (pageInput) pageInput.value = currentPage;

    searchOrFilter();
}

/**
 * Навигация по страницам
 */
function goToPage(newPage) {
    if (newPage >= 1 && newPage <= totalPages) {
        currentPage = newPage;
        const pageInput = document.getElementById('page_input');
        if (pageInput) pageInput.value = newPage;
        searchOrFilter();
    }
}

/**
 * Отрисовка пагинации
 */
function updatePaginationControls(totalItems) {
    const controlsDiv = document.getElementById('pagination_controls');
    if (!controlsDiv) return;

    controlsDiv.innerHTML = '';
    if (totalItems <= ITEMS_PER_PAGE) {
        totalPages = 1;
        return;
    }
    totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);

    const prevButton = document.createElement('button');
    prevButton.textContent = '←';
    prevButton.disabled = currentPage === 1;
    prevButton.onclick = () => goToPage(currentPage - 1);

    const pageInfo = document.createElement('span');
    pageInfo.textContent = ` ${currentPage} / ${totalPages} `;

    const nextButton = document.createElement('button');
    nextButton.textContent = '→';
    nextButton.disabled = currentPage >= totalPages;
    nextButton.onclick = () => goToPage(currentPage + 1);

    controlsDiv.append(prevButton, pageInfo, nextButton);
}

/**
 * Отрисовка списка фильмов
 */
function renderMovies(movies, totalItems) {
    const totalCountElem = document.getElementById('total_count');
    if (totalCountElem) totalCountElem.textContent = totalItems;

    const resultsDiv = document.getElementById('movie_results');
    if (!resultsDiv) return;
    resultsDiv.innerHTML = '';

    // ПРОВЕРКА ТОКЕНА
    const isAuthenticated = !!localStorage.getItem('token');

    if (!movies || movies.length === 0) {
        resultsDiv.innerHTML = '<p>Фильмы не найдены.</p>';
        return;
    }

    movies.forEach(movie => {
        const link = document.createElement('a');
        link.href = `movie_detail.html?id=${movie.id}`;
        link.style.textDecoration = 'none';

        const card = document.createElement('div');
        card.className = 'movie-card';

        // 1. Статус просмотра (показываем только если авторизован)
        let statusIcon = '';
        if (isAuthenticated) {
            if (movie.personal_status === 'watched' || movie.personal_status === 'completed') statusIcon = '✅ ';
            else if (movie.personal_status === 'watching') statusIcon = '👀 ';
            else if (movie.personal_status === 'planned') statusIcon = '⏳ ';
            else if (movie.personal_status === 'dropped') statusIcon = '🗑️ ';
        }

        // 2. Личная оценка (показываем только если авторизован)
        const myRatingHtml = (isAuthenticated && movie.personal_rating)
            ? `<span style="background: #6f42c1; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.8em; margin-left: 10px;">Моя: ${movie.personal_rating}</span>`
            : '';

        // Остальной код отрисовки без изменений...
        const popValue = (movie.popularity && typeof movie.popularity === 'number')
                         ? movie.popularity.toFixed(1) : '0.0';
        const rating = movie.display_rating || movie.rating || 'N/A';

        const genresText = (movie.genre_names && movie.genre_names.length > 0)
            ? movie.genre_names.join(', ')
            : 'Жанры не указаны';

        const posterUrl = movie.poster_url || (movie.poster_path ? `https://image.tmdb.org/t/p/w200${movie.poster_path}` : null);
        const posterHtml = posterUrl
            ? `<div class="poster-container"><img src="${posterUrl}" alt="${movie.title}"></div>`
            : `<div class="poster-container no-poster">Нет постера</div>`;

        card.innerHTML = `
            ${posterHtml}
            <div class="movie-info">
                <h4>${statusIcon}${movie.title} (${movie.release_year || '?'})</h4>
                <p style="font-size: 0.85em; color: #666; margin-bottom: 5px;">${genresText}</p>
                <p>⭐ ${rating} | ${myRatingHtml}</p>
            </div>
        `;
        link.appendChild(card);
        resultsDiv.appendChild(link);
    });

    updatePaginationControls(totalItems);
}

/**
 * Поиск фильмов по названию
 */
async function searchMovies(searchQuery) {
    try {
        const response = await fetchData('/movies/search', {
            query: searchQuery,
            page: currentPage,
            page_size: ITEMS_PER_PAGE
        });
        renderMovies(response.items, response.total || response.total_items || 0);
    } catch (error) {
        displayError("Ошибка поиска: " + error.message);
    }
}

/**
 * Фильтрация фильмов по параметрам
 */
async function fetchMovies() {
    try {
        const params = {
            page: currentPage,
            page_size: ITEMS_PER_PAGE,
            genre_ids: document.getElementById('genre_select').value,
            year_min: document.getElementById('year_min').value,
            year_max: document.getElementById('year_max').value,
            rating_min: document.getElementById('rating_min').value,
            sort_by: document.getElementById('sort_select').value,
            sort_direction: document.getElementById('direction_select').value
        };

        const response = await fetchData('/movies/filter', params);
        renderMovies(response.items, response.total || response.total_items || 0);
    } catch (error) {
        displayError("Ошибка фильтрации: " + error.message);
    }
}

/**
 * Главный переключатель: поиск или фильтрация
 */
function searchOrFilter() {
    const query = document.getElementById('search_input').value.trim();
    if (query) {
        searchMovies(query);
    } else {
        fetchMovies();
    }
}

// Экспорт функций в глобальную область видимости для HTML (onclick)
window.searchOrFilter = searchOrFilter;
window.resetFilters = resetFilters;
window.login = login;
window.logout = logout;
window.goToPage = goToPage;

// Инициализация страницы
window.onload = () => {
    updateAuthUI();
    loadGenres();
    searchOrFilter();

    // Слушатель изменения страницы вручную
    document.getElementById('page_input')?.addEventListener('change', (e) => {
        const val = parseInt(e.target.value);
        if (!isNaN(val)) goToPage(val);
    });

    // Живой поиск при вводе
    document.getElementById('search_input')?.addEventListener('input', () => {
        currentPage = 1; // Сбрасываем на первую страницу при новом поиске
        searchOrFilter();
    });
};