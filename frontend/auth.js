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

export function updateAuthUI() {
    const token = localStorage.getItem('token');
    const authContainer = document.querySelector('.auth-controls');
    if (!authContainer) return;

    // Общий стиль для кнопок
    const btnStyle = `
        padding: 8px 16px;
        margin-left: 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s ease;
        border: 1px solid #007bff;
        font-family: 'Segoe UI', sans-serif;
    `;

    const primaryBtn = `background: #007bff; color: white; ${btnStyle}`;
    const outlineBtn = `background: white; color: #007bff; ${btnStyle}`;

    if (token) {
        authContainer.innerHTML = `
            <button style="${outlineBtn}"
                    onmouseover="this.style.background='#f0f7ff'"
                    onmouseout="this.style.background='white'"
                    onclick="location.href='profile.html'">
                👤 Мой Профиль
            </button>
            <button style="${primaryBtn}"
                    onmouseover="this.style.background='#0056b3'"
                    onmouseout="this.style.background='#007bff'"
                    onclick="window.logout()">
                🚪 Выйти
            </button>
        `;
    } else {
        authContainer.innerHTML = `
            <button style="${outlineBtn}"
                    onmouseover="this.style.background='#f0f7ff'"
                    onmouseout="this.style.background='white'"
                    onclick="window.login()">
                🔑 Войти
            </button>
            <button style="${primaryBtn}"
                    onmouseover="this.style.background='#0056b3'"
                    onmouseout="this.style.background='#007bff'"
                    onclick="window.register()">
                📝 Регистрация
            </button>
        `;
    }
}



// Прокидываем в window, чтобы HTML видел функции
window.login = login;
window.logout = logout;
window.register = register;