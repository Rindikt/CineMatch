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
        formData.append('nickname', email);
        formData.append('password', password);

        const data = await fetchData('/users/token', {}, 'POST', formData);
        localStorage.setItem('token', data.access_token);
        location.reload();
    } catch (error) {
        alert("Ошибка входа: " + error.message);
    }
}

export function logout() {
    localStorage.removeItem('token');
    location.reload();
}

export function updateAuthUI() {
    const token = localStorage.getItem('token');
    const authContainer = document.querySelector('.auth-controls');
    if (!authContainer) return;

    if (token) {
        // Если пользователь вошел — показываем Профиль и Выход
        authContainer.innerHTML = `
            <button onclick="location.href='profile.html'">👤 Мой Профиль</button>
            <button onclick="window.logout()">🚪 Выйти</button>
        `;
    } else {
        // ЕСЛИ ТОКЕНА НЕТ (тот самый else) — показываем Войти и Регистрацию
        authContainer.innerHTML = `
            <button onclick="window.login()">🔑 Войти</button>
            <button onclick="window.register()">📝 Регистрация</button>
        `;
    }
}

// Прокидываем в window, чтобы HTML видел функции
window.login = login;
window.logout = logout;
window.register = register;