import { fetchData, displayError } from './api.js';
import { updateAuthUI, login, logout, register } from './auth.js';

let currentPage = 1;
let isSearchMode = false;

// Пробрасываем функции в window, чтобы они были доступны везде
window.updateAuthUI = updateAuthUI;
window.login = login;
window.logout = logout;
window.register = register;

function saveState() {
    const state = {
        currentPage,
        isSearchMode,
        searchQuery: document.getElementById('search_input')?.value || '',
        filters: {
            genre: document.getElementById('genre_select')?.value || '',
            year_min: document.getElementById('year_min')?.value || '1900',
            year_max: document.getElementById('year_max')?.value || '',
            rating_min: document.getElementById('rating_min')?.value || '1.0',
            sort_by: document.getElementById('sort_by')?.value || 'popularity',
            direction: document.getElementById('direction')?.value || 'desc'
        }
    };
    localStorage.setItem('movie_list_state', JSON.stringify(state));
}

function restoreState() {
    const saved = localStorage.getItem('movie_list_state');
    if (!saved) return false;
    const state = JSON.parse(saved);
    currentPage = state.currentPage || 1;
    isSearchMode = state.isSearchMode || false;

    if (state.searchQuery) document.getElementById('search_input').value = state.searchQuery;
    if (state.filters) {
        document.getElementById('genre_select').value = state.filters.genre;
        document.getElementById('year_min').value = state.filters.year_min;
        document.getElementById('year_max').value = state.filters.year_max;
        document.getElementById('rating_min').value = state.filters.rating_min;
        document.getElementById('sort_by').value = state.filters.sort_by;
        document.getElementById('direction').value = state.filters.direction;
    }
    return true;
}

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
function renderMovies(data, total) {
    const container = document.getElementById('movie_results');
    const countDisplay = document.getElementById('results_count');

    // 1. Извлекаем массив фильмов и общее количество корректно
    // Если data — это уже массив (items), используем его, иначе ищем внутри .items
    const moviesList = Array.isArray(data) ? data : (data?.items || []);
    const totalItems = total || data?.total_items || 0;

    if (countDisplay) {
        countDisplay.innerText = totalItems > 0 ? `Найдено: ${totalItems}` : `Ничего не найдено`;
    }

    if (!container) return;
    container.innerHTML = '';

    if (moviesList.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 50px; color: #888;">Список пуст</div>`;
        return;
    }

    // Применяем стиль сетки к контейнеру, чтобы карточки не сжимались
    container.style.display = "grid";
    container.style.gridTemplateColumns = "repeat(auto-fill, minmax(200px, 1fr))";
    container.style.gap = "30px";

    moviesList.forEach(movie => {
        const progress = (movie.user_progress && movie.user_progress.length > 0) ? movie.user_progress[0] : null;

        const statusMap = {
            'completed': { txt: '✅ Просмотрено', color: '#28a745' },
            'watching': { txt: '👀 Смотрю', color: '#007bff' },
            'planned': { txt: '📅 В планах', color: '#ffc107' },
            'dropped': { txt: '🗑️ Брошено', color: '#dc3545' }
        };

        let statusBadge = '';
        let personalRate = '';

        if (progress) {
            const s = statusMap[progress.status] || { txt: progress.status, color: '#6c757d' };
            statusBadge = `<div style="background: ${s.color}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 10px; margin-top: 5px; display: inline-block;">${s.txt}</div>`;
            if (progress.personal_rating) {
                personalRate = `<div style="color: #ff9800; font-weight: bold; font-size: 13px;">Моя: ⭐ ${progress.personal_rating}</div>`;
            }
        }

        const card = document.createElement('div');
        // Возвращаем белую подложку и тени для нормального размера
        card.style = `cursor: pointer; transition: 0.3s; background: white; border-radius: 12px; padding: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);`;

        card.innerHTML = `
            <div style="position: relative; overflow: hidden; border-radius: 10px; aspect-ratio: 2/3;">
                <img src="${movie.poster_url || 'https://via.placeholder.com/300x450'}" style="width: 100%; height: 100%; object-fit: cover; display: block;">
                <div style="position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); color: white; padding: 2px 8px; border-radius: 5px; font-weight: bold; font-size: 12px;">
                    ⭐ ${movie.rating ? movie.rating.toFixed(1) : '0.0'}
                </div>
            </div>
            <div style="padding: 12px 5px;">
                <div style="font-weight: bold; font-size: 16px; color: #000; margin-bottom: 4px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;" title="${movie.title}">
                    ${movie.title}
                </div>
                <div style="color: #888; font-size: 13px;">${movie.release_year} • ${movie.genres?.[0]?.genre?.name || 'Кино'}</div>
                <div style="min-height: 45px; margin-top: 8px;">
                    ${personalRate}
                    ${statusBadge}
                </div>
            </div>
        `;

        card.onclick = () => window.location.href = `movie_detail.html?id=${movie.id}`;
        card.onmouseover = () => { card.style.transform = 'translateY(-5px)'; card.style.boxShadow = '0 8px 20px rgba(0,0,0,0.15)'; };
        card.onmouseout = () => { card.style.transform = 'translateY(0)'; card.style.boxShadow = '0 2px 8px rgba(0,0,0,0.05)'; };
        container.appendChild(card);
    });

    // 2. Вызываем пагинацию с корректным числом
    renderPagination(totalItems);
}

/**
 * 3. ПАГИНАЦИЯ
 */
function renderPagination(total) {
    const container = document.getElementById('pagination');
    if (!container) return;
    container.innerHTML = '';

    const pageSize = 20;
    const totalPages = Math.ceil(total / pageSize);

    if (totalPages <= 1) return;

    container.style.display = 'flex';
    container.style.justifyContent = 'center';
    container.style.alignItems = 'center';
    container.style.gap = '10px';
    container.style.marginTop = '30px';

    // --- Кнопка "В САМОЕ НАЧАЛО" (<<) ---
    const btnFirst = document.createElement('button');
    btnFirst.innerHTML = '« Первая';
    btnFirst.disabled = (currentPage === 1);
    btnFirst.onclick = () => {
        currentPage = 1;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    container.appendChild(btnFirst);

    // --- Кнопка "Назад" ---
    const btnPrev = document.createElement('button');
    btnPrev.innerText = '‹ Назад';
    btnPrev.disabled = (currentPage === 1);
    btnPrev.onclick = () => {
        currentPage--;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    container.appendChild(btnPrev);

    // --- Индикатор текущей страницы ---
    const pageInfo = document.createElement('span');
    pageInfo.innerText = `Страница ${currentPage} из ${totalPages}`;
    pageInfo.style.fontWeight = 'bold';
    pageInfo.style.margin = '0 15px';
    container.appendChild(pageInfo);

    // --- Кнопка "Вперед" ---
    const btnNext = document.createElement('button');
    btnNext.innerText = 'Далее ›';
    btnNext.disabled = (currentPage === totalPages);
    btnNext.onclick = () => {
        currentPage++;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    container.appendChild(btnNext);

    // --- Кнопка "В САМЫЙ КОНЕЦ" (>>) ---
    const btnLast = document.createElement('button');
    btnLast.innerHTML = 'Последняя »';
    btnLast.disabled = (currentPage === totalPages);
    btnLast.onclick = () => {
        currentPage = totalPages;
        isSearchMode ? searchMovies() : fetchMovies();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    container.appendChild(btnLast);
}

/**
 * 4. ПОИСК
 */
async function searchMovies() {
    isSearchMode = true;
    saveState();
    const query = document.getElementById('search_input')?.value.trim();
    try {
        // Исправлено: твой бэкенд ждет параметр 'search'
        const response = await fetchData('/movies/search', { search: query, page: currentPage });
        renderMovies(response, response.total_items);
    } catch (error) {
        displayError("Ошибка поиска");
    }
}

/**
 * 5. ФИЛЬТРАЦИЯ
 */
async function fetchMovies() {
    isSearchMode = false;
    saveState();
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
        renderMovies(response, response.total_items);
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

window.onload = async () => {
    // 1. Сначала жанры
    await loadGenres();

    // 2. ВОТ ЭТА СТРОЧКА: она должна быть здесь и без ошибок
    if (typeof updateAuthUI === 'function') {
        updateAuthUI();
    } else {
        console.error("Функция updateAuthUI не найдена! Проверь импорт.");
    }

    // 3. Восстановление состояния (localStorage)
    restoreState();

    // 4. Загрузка фильмов
    if (isSearchMode && document.getElementById('search_input')?.value.trim()) {
        searchMovies();
    } else {
        fetchMovies();
    }
};

window.resetFilters = () => {
    localStorage.removeItem('movie_list_state');
    document.getElementById('search_input').value = '';
    document.getElementById('genre_select').value = '';
    document.getElementById('year_min').value = '1900';
    document.getElementById('year_max').value = '';
    currentPage = 1;
    fetchMovies();
};