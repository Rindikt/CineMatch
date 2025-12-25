// api.js
const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Универсальная функция для запросов (поддерживает GET, POST и Токены)
 */
export async function fetchData(endpoint, params = {}, method = 'GET', body = null) {
    const url = new URL(API_BASE_URL + endpoint);

    if (method === 'GET') {
        url.searchParams.append('_t', new Date().getTime());
        Object.keys(params).forEach(key => {
            if (params[key] !== undefined && params[key] !== null && params[key] !== '') {
                url.searchParams.append(key, params[key]);
            }
        });
    }

    const headers = {};
    const token = localStorage.getItem('token');

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const options = { method, headers };

    if (body) {
        options.body = body;
        // ИСПРАВЛЕНО: Явно указываем тип контента для JSON-строк
        if (typeof body === 'string') {
            headers['Content-Type'] = 'application/json';
        } else if (body instanceof URLSearchParams) {
            headers['Content-Type'] = 'application/x-www-form-urlencoded';
        }
    }

    const response = await fetch(url, options);

    if (!response.ok) {
        let errorMessage = response.statusText;
        try {
            const errorData = await response.json();
            errorMessage = typeof errorData.detail === 'object'
                ? JSON.stringify(errorData.detail)
                : errorData.detail;
        } catch (e) {
            // Ошибка парсинга JSON от сервера
        }

        if (response.status === 401) {
            localStorage.removeItem('token');
        }

        throw new Error(errorMessage || `Ошибка ${response.status}`);
    }

    return response.json();
}

export function displayError(message) {
    const container = document.getElementById('movie_results') ||
                      document.getElementById('movie_detail_container') ||
                      document.body;

    let errorElement = document.getElementById('global_error_message');
    if (!errorElement) {
        errorElement = document.createElement('p');
        errorElement.id = 'global_error_message';
        errorElement.className = 'error';
        errorElement.style.color = 'red';
        errorElement.style.fontWeight = 'bold';
    }

    container.prepend(errorElement);
    errorElement.innerHTML = `⚠️ Ошибка: ${message}`;
}