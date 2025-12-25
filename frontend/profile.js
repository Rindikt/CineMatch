import { fetchData, displayError } from './api.js';

async function loadProfile() {
    try {
        const user = await fetchData('/users/me');

        // Заполняем шапку профиля
        document.getElementById('user_nickname').textContent = user.nickname;
        document.getElementById('user_email').textContent = user.email;
        document.getElementById('avatar_letter').textContent = user.nickname.charAt(0).toUpperCase();

        const content = document.getElementById('profile_content');
        const categories = [
            { id: 'watching', title: 'Смотрю сейчас', emoji: '👀' },
            { id: 'planned', title: 'В планах', emoji: '📅' },
            { id: 'completed', title: 'Просмотрено', emoji: '✅' },
            { id: 'dropped', title: 'Брошено', emoji: '🗑️' }
        ];

        let hasAnyData = false;

        content.innerHTML = categories.map(cat => {
            const items = user[cat.id] || [];
            if (items.length === 0) return '';
            hasAnyData = true;

            return `
                <div class="status-section" id="section_${cat.id}">
                    <div class="status-header" onclick="document.getElementById('section_${cat.id}').classList.toggle('collapsed')">
                        <div class="status-title">
                            <span>${cat.emoji}</span> ${cat.title}
                            <span style="color: #999; font-weight: normal; margin-left: 8px;">${items.length}</span>
                        </div>
                        <div class="arrow">▼</div>
                    </div>
                    <div class="status-content">
                        <table class="profile-table">
                            <thead>
                                <tr>
                                    <th>Название фильма</th>
                                    <th style="width: 120px;">Моя оценка</th>
                                    <th style="width: 100px; text-align: right;">Год</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${items.map(item => `
                                    <tr>
                                        <td>
                                            <a href="movie_detail.html?id=${item.movie_id}"
                                               style="text-decoration: none; color: #000; font-weight: 600; transition: 0.2s;"
                                               onmouseover="this.style.textDecoration='underline'; this.style.color='#007bff'"
                                               onmouseout="this.style.textDecoration='none'; this.style.color='#000'">
                                                ${item.movie ? item.movie.title : 'Загрузка...'}
                                            </a>
                                        </td>
                                        <td>
                                            ${item.personal_rating ? `<span class="rating-badge">⭐ ${item.personal_rating}</span>` : '<span style="color: #ccc;">—</span>'}
                                        </td>
                                        <td style="text-align: right; color: #666;">
                                            ${item.movie ? item.movie.release_year : '—'}
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }).join('');

        if (!hasAnyData) {
            content.innerHTML = `<div style="text-align:center; padding: 50px; color: #888;">Ваш список пока пуст</div>`;
        }

    } catch (error) {
        console.error(error);
        displayError("Ошибка загрузки профиля.");
    }
}

window.onload = loadProfile;