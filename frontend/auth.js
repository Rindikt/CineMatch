import { fetchData } from './api.js';

export async function register() {
    const email = prompt("Введите Email:");
    const nickname = prompt("Введите никнейм:");
    const password = prompt("Введите пароль:");

    if (!email || !nickname || !password) return;

    try {
        const userData = {
            email: email,
            nickname: nickname,
            password: password
        };

        // ИСПРАВЛЕНИЕ: Обязательно используем JSON.stringify
        // Это превратит объект в строку, и api.js правильно установит Content-Type
        await fetchData('/users/register', {}, 'POST', JSON.stringify(userData));

        alert("Регистрация успешна! Теперь вы можете войти.");
        await login();
    } catch (error) {
        alert("Ошибка регистрации: " + error.message);
    }
}

export async function login() {
    const email = prompt("Введите Email/Никнейм:");
    const password = prompt("Введите пароль:");
    if (!email || !password) return;

    try {
        const formData = new URLSearchParams();
        formData.append('username', email);
        formData.append('password', password);

        const data = await fetchData('/users/token', {}, 'POST', formData);

        // ВАЖНО: сохраняем оба ключа!
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);

        location.reload();
    } catch (error) {
        alert("Ошибка входа: " + error.message);
    }
}

export function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token'); // Чистим оба
    location.reload();
}

export async function updateAuthUI() {
    const authContainer = document.getElementById('auth_container') || document.getElementById('auth-links');
    if (!authContainer) return;

    const token = localStorage.getItem('token');

    const btnStyle = "padding: 10px 20px; border-radius: 8px; border: 1px solid #007bff; cursor: pointer; font-weight: bold; transition: 0.2s; text-decoration: none; display: inline-flex; align-items: center; justify-content: center;";
    const primaryBtn = `background: #007bff; color: white; ${btnStyle}`;
    const outlineBtn = `background: white; color: #007bff; ${btnStyle}`;
    const adminBtn = `background: #28a745; color: white; border-color: #28a745; ${btnStyle}`;

    if (token) {
        try {
            // Запрашиваем твой UserProfileResponse
            const userProfile = await fetchData('/users/me');

            let buttonsHtml = `<div style="display: flex; gap: 10px;">`;

            // Если роль из твоего бэкенда "admin" — рисуем кнопку
            if (userProfile.role === 'admin') {
                buttonsHtml += `
                    <a href="admin.html" style="${adminBtn}"
                       onmouseover="this.style.background='#218838'"
                       onmouseout="this.style.background='#28a745'">
                        ⚙️ Админка
                    </a>
                `;
            }

            buttonsHtml += `
                <button style="${outlineBtn}"
                        onmouseover="this.style.background='#f0f7ff'"
                        onmouseout="this.style.background='white'"
                        onclick="location.href='profile.html'">
                    👤 ${userProfile.nickname}
                </button>
                <button style="${primaryBtn}"
                        onmouseover="this.style.background='#0056b3'"
                        onmouseout="this.style.background='#007bff'"
                        onclick="window.logout()">
                    🚪 Выйти
                </button>
            </div>`;

            authContainer.innerHTML = buttonsHtml;
        } catch (err) {
            console.error("Ошибка сессии:", err);
            // Если токен плохой, показываем кнопки входа
            showGuestButtons(authContainer, outlineBtn, primaryBtn);
        }
    } else {
        showGuestButtons(authContainer, outlineBtn, primaryBtn);
    }
}
function showGuestButtons(container, outline, primary) {
    container.innerHTML = `
        <div style="display: flex; gap: 10px;">
            <button style="${outline}" onclick="window.login()">🔑 Войти</button>
            <button style="${primary}" onclick="window.register()">📝 Регистрация</button>
        </div>
    `;
}


// Прокидываем в window, чтобы HTML видел функции
window.login = login;
window.logout = logout;
window.register = register;