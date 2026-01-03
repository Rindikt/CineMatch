import { fetchData } from './api.js';

// Переменная для хранения полного списка (чтобы не дергать базу при каждой букве поиска)
let allUsers = [];

export async function loadUsers() {
    const container = document.getElementById('user_list_body');
    if (!container) return;

    container.innerHTML = '<p style="text-align:center; padding: 20px;">Загрузка пользователей...</p>';

    try {
        // Получаем данные с сервера
        allUsers = await fetchData('/admin/users');

        if (!allUsers || allUsers.length === 0) {
            container.innerHTML = '<p style="text-align:center; padding: 20px;">Пользователей пока нет.</p>';
            return;
        }

        // Отрисовываем таблицу
        renderUserTable(allUsers);

    } catch (err) {
        container.innerHTML = `<p style="color:red; text-align:center; padding: 20px;">Ошибка загрузки: ${err.message}</p>`;
    }
}

// Отдельная функция для отрисовки (нужна и для первой загрузки, и для поиска)
function renderUserTable(users) {
    const container = document.getElementById('user_list_body');
    if (!container) return;

    if (users.length === 0) {
        container.innerHTML = '<p style="text-align:center; padding: 20px;">Пользователи не найдены</p>';
        return;
    }

    let html = `
        <table class="user-table" style="width:100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="border-bottom: 2px solid #eee; text-align: left; background: #f8f9fa;">
                    <th style="padding: 12px;">Email / Никнейм</th>
                    <th style="padding: 12px;">Роль</th>
                    <th style="padding: 12px;">Действие</th>
                </tr>
            </thead>
            <tbody>
    `;

    users.forEach(user => {
        html += `
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px;">
                    <strong>${user.nickname || 'Без ника'}</strong><br>
                    <small style="color: #666;">${user.email}</small>
                </td>
                <td style="padding: 12px;">
                    <select onchange="updateUserRole('${user.email}', this.value)" style="padding: 6px; border-radius: 4px; border: 1px solid #ddd;">
                        <option value="user" ${user.role === 'user' ? 'selected' : ''}>User</option>
                        <option value="admin" ${user.role === 'admin' ? 'selected' : ''}>Admin</option>
                    </select>
                </td>
                <td style="padding: 12px; display: flex; gap: 8px;">
                    <button onclick="deleteUser('${user.email}')" class="btn-sm" style="background: #ffebee; border: 1px solid #ffcdd2; color: #c62828; cursor: pointer; padding: 4px 8px; border-radius: 4px;">Удалить</button>
                </td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    container.innerHTML = html;
}

// ТА САМАЯ ФУНКЦИЯ ПОИСКА
export function filterUsers(query) {
    const lowerQuery = query.toLowerCase();

    // Фильтруем массив по email или никнейму
    const filtered = allUsers.filter(user => {
        const emailMatch = user.email.toLowerCase().includes(lowerQuery);
        const nicknameMatch = (user.nickname || '').toLowerCase().includes(lowerQuery);
        return emailMatch || nicknameMatch;
    });

    // Перерисовываем таблицу с результатами фильтрации
    renderUserTable(filtered);
}

export async function updateUserRole(email, newRole) {
    try {
        await fetchData(`/admin/users/update/${email}?user_status=${newRole}`, {}, 'PATCH');
        alert('Роль пользователя успешно обновлена');

        // Обновляем локальные данные, чтобы поиск работал корректно после смены роли
        const user = allUsers.find(u => u.email === email);
        if (user) user.role = newRole;

    } catch (err) {
        alert('Ошибка при обновлении роли: ' + err.message);
        loadUsers();
    }
}
export async function deleteUser(email) {
    if (!confirm(`Вы уверены, что хотите навсегда удалить пользователя ${email}?`)) {
        return;
    }

    try {
        await fetchData(`/admin/users/${email}`, {}, 'DELETE');

        // Удаляем из локального списка, чтобы UI обновился сразу
        allUsers = allUsers.filter(u => u.email !== email);

        // Перерисовываем таблицу (с учетом поиска, если он вбит)
        const currentQuery = document.getElementById('user_search_input')?.value || '';
        filterUsers(currentQuery);

        alert('Пользователь успешно удален');
    } catch (err) {
        alert('Ошибка при удалении: ' + err.message);
    }
}
window.deleteUser = deleteUser;
window.updateUserRole = updateUserRole;