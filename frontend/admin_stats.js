import { fetchData } from './api.js';

// Объект для хранения ссылок на графики (чтобы удалять старые при обновлении)
let charts = {};

export async function initStats() {
    try {
        const data = await fetchData('/admin/stats');
        const d = data.different_data; // Для краткости

        // 1. СТАТИСТИКА БАЗЫ
        // Линейный график
        renderMainChart(document.getElementById('mainChart'), d.movies_list);

        // Горизонтальные бары (Жанры и Рейтинг TMDB)
        renderBarChart('genreChart', d.genres_list, 'movie_count', 'Фильмов', '#36a2eb');
        renderBarChart('ratingChart', d.rating_list, 'avg_rating', 'Рейтинг TMDB', '#ffce56');

        // Таблица жанров (общая)
        renderFullTable(d.genres_list, d.rating_list);

        // 2. АКТИВНОСТЬ ПОЛЬЗОВАТЕЛЕЙ
        // Просмотры и Оценки юзеров по жанрам
        renderBarChart('userViewsChart', d.user_views_by_genre, 'views_count', 'Просмотры', '#4bc0c0');
        renderBarChart('userRatingsChart', d.user_ratings_by_genre, 'avg_rating', 'Оценка юзеров', '#9966ff');

        // Таблицы ТОП-10
        renderSimpleTable('top_views_table', d.top_10_views, 'views_count', 'Просмотров', 'user_rating');
        renderSimpleTable('top_dropped_table', d.top_10_dropped_movies || [], 'views_count', 'Брошено', 'user_rating');

        // Итоговые цифры в карточках
        renderSummary(data.total_stats);

    } catch (err) {
        console.error('Ошибка при загрузке аналитики:', err);
    }
}

// --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

function renderMainChart(ctx, list) {
    if (!ctx) return;
    if (charts['main']) charts['main'].destroy();

    charts['main'] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: list.map(i => i.created_at),
            datasets: [{
                label: 'Добавлено фильмов',
                data: list.map(i => i.movie_count),
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true,
                tension: 0.3
            }]
        },
        options: { responsive: true, maintainAspectRatio: false }
    });
}

// Универсальная функция для всех Bar-графиков
function renderBarChart(canvasId, list, key, label, color) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || !list) return;

    if (charts[canvasId]) charts[canvasId].destroy();

    const sorted = [...list].sort((a, b) => b[key] - a[key]);

    charts[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: sorted.map(i => i.name),
            datasets: [{
                label: label,
                data: sorted.map(i => i[key]),
                backgroundColor: color,
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } }
        }
    });
}

function renderFullTable(genres, ratings) {
    const container = document.getElementById('genre_table_container');
    if (!container) return;

    const combined = genres.map(g => {
        const r = ratings.find(ri => ri.name === g.name);
        return { name: g.name, count: g.movie_count, avg: r ? r.avg_rating : 0 };
    }).sort((a, b) => b.count - a.count);

    let html = `
        <table style="width:100%; border-collapse: collapse; font-size: 14px;">
            <thead>
                <tr style="background: #f8f9fa; border-bottom: 2px solid #eee; text-align: left;">
                    <th style="padding: 12px;">Жанр</th>
                    <th style="padding: 12px; text-align: center;">Фильмов в базе</th>
                    <th style="padding: 12px; text-align: center;">Рейтинг TMDB</th>
                </tr>
            </thead>
            <tbody>`;

    combined.forEach(item => {
        html += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px;">${item.name}</td>
                <td style="padding: 12px; text-align: center; font-weight: bold;">${item.count}</td>
                <td style="padding: 12px; text-align: center;">${item.avg}</td>
            </tr>`;
    });
    container.innerHTML = html + '</tbody></table>';
}

function renderSimpleTable(containerId, list, valKey, valLabel, ratingKey = null) {
    const container = document.getElementById(containerId);
    if (!container) return;

    let html = `
        <table style="width:100%; font-size: 13px; border-collapse: collapse;">
            <thead>
                <tr style="border-bottom: 2px solid #eee; text-align: left; color: #666;">
                    <th style="padding: 8px;">Фильм</th>
                    <th style="padding: 8px; text-align: center;">${valLabel}</th>
                    ${ratingKey ? '<th style="padding: 8px; text-align: right;">Рейтинг</th>' : ''}
                </tr>
            </thead>
            <tbody>`;

    list.forEach(item => {
        html += `
            <tr style="border-bottom: 1px solid #f9f9f9;">
                <td style="padding: 8px;">${item.name}</td>
                <td style="padding: 8px; text-align: center; font-weight: bold;">${item[valKey]}</td>
                ${ratingKey ? `
                    <td style="padding: 8px; text-align: right;">
                        <span style="color: #ffc107;">★</span> ${item[ratingKey] || 0}
                    </td>` : ''}
            </tr>`;
    });

    container.innerHTML = html + (list.length ? '</tbody></table>' : '<tr><td colspan="3" style="padding:20px; text-align:center; color:#ccc;">Данных пока нет</td></tr></tbody></table>');
}

function renderSummary(stats) {
    const m = document.getElementById('stat_total_movies');
    const u = document.getElementById('stat_total_users');
    if (m) m.innerText = stats.total_movies;
    if (u) u.innerText = stats.total_users;
}