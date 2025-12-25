import { fetchData, displayError } from './api.js';

async function loadProfile() {
    try {
        const user = await fetchData('/users/me');
        document.getElementById('user_nickname').textContent = `Профиль пользователя: ${user.nickname}`;

        const content = document.getElementById('profile_content');

        // Все 4 категории из твоего WatchStatus
        const categories = [
            { id: 'watching', title: '👀 СМОТРЮ' },
            { id: 'planned', title: '📅 ЗАПЛАНИРОВАНО' },
            { id: 'completed', title: '✅ ПРОСМОТРЕНО' },
            { id: 'dropped', title: '🗑️ БРОШЕНО' }
        ];

        let hasAnyData = false;

        content.innerHTML = categories.map(cat => {
            const items = user[cat.id] || [];
            if (items.length === 0) return '';

            hasAnyData = true;

            return `
                <div class="status-header">${cat.title} (${items.length})</div>
                <table class="profile-table">
                    <thead>
                        <tr>
                            <th style="width: 50px;">#</th>
                            <th>Название фильма</th>
                            <th style="width: 100px;">Моя оценка</th>
                            <th style="width: 150px;">Год</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${items.map((item, index) => {
                            // Обращаемся к вложенному объекту movie
                            const title = item.movie ? item.movie.title : 'Без названия';
                            const year = item.movie ? item.movie.release_year : '—';
                            const rating = item.personal_rating || '--';

                            return `
                            <tr>
                                <td>${index + 1}</td>
                                <td><a href="movie_detail.html?id=${item.movie_id}">${title}</a></td>
                                <td>⭐ ${rating}</td>
                                <td>${year}</td>
                            </tr>`;
                        }).join('')}
                    </tbody>
                </table>
            `;
        }).join('');

        if (!hasAnyData) {
            content.innerHTML = '<p style="text-align:center; margin-top:20px;">Ваш список пока пуст. Добавьте что-нибудь на странице фильма!</p>';
        }

    } catch (error) {
        displayError("Не удалось загрузить профиль.");
        console.error(error);
    }
}

window.onload = loadProfile;