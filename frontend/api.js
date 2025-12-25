const API_BASE_URL = 'http://127.0.0.1:8000';

export async function fetchData(endpoint, params = {}, method = 'GET', body = null) {
    const url = new URL(API_BASE_URL + endpoint);

    // Добавляем timestamp к КАЖДОМУ GET-запросу, чтобы избежать кеша браузера
    if (method === 'GET') {
        url.searchParams.append('_v', new Date().getTime());
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
        if (typeof body === 'string') headers['Content-Type'] = 'application/json';
        else if (body instanceof URLSearchParams) headers['Content-Type'] = 'application/x-www-form-urlencoded';
    }

    let response;
    try {
        response = await fetch(url, options);
    } catch (err) {
        throw new Error("Не удалось связаться с сервером");
    }

    // Логика автоматического обновления токена
    if (response.status === 401 && endpoint !== '/users/token' && endpoint !== '/users/refresh') {
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
            console.log("Access-токен протух, пробуем обновиться...");
            const refreshRes = await fetch(`${API_BASE_URL}/users/refresh`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${refreshToken}` }
            });

            if (refreshRes.ok) {
                const data = await refreshRes.json();
                localStorage.setItem('token', data.access_token);
                if (data.refresh_token) localStorage.setItem('refresh_token', data.refresh_token);

                // Повтор запроса
                options.headers['Authorization'] = `Bearer ${data.access_token}`;
                response = await fetch(url, options);
            } else {
                // Если рефреш не удался - чистим всё
                localStorage.removeItem('token');
                localStorage.removeItem('refresh_token');
            }
        }
    }

    if (!response.ok) {
        let errorMessage = response.statusText;
        try {
            const errorData = await response.json();
            errorMessage = errorData.detail || JSON.stringify(errorData);
        } catch (e) {}
        throw new Error(errorMessage);
    }

    return response.json();
}

export function displayError(message) {
    console.error("API Error:", message);
    const container = document.getElementById('movie_results') || document.body;
    let errorElement = document.getElementById('global_error_message');
    if (!errorElement) {
        errorElement = document.createElement('div');
        errorElement.id = 'global_error_message';
        errorElement.style = "color: red; font-weight: bold; padding: 10px; text-align: center; width: 100%;";
        container.prepend(errorElement);
    }
    errorElement.textContent = `⚠️ ${message}`;
    setTimeout(() => errorElement?.remove(), 5000);
}