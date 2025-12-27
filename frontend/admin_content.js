import { fetchData } from './api.js';

const STORAGE_KEY = 'cine_admin_tasks';
let tasks = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');

// Рендеринг списка задач в истории
export function renderTasks() {
    const listContainer = document.getElementById('recent_tasks_list');
    if (!listContainer) return;

    if (tasks.length === 0) {
        listContainer.innerHTML = '<p style="color: #999; font-size: 12px; text-align: center; padding: 20px;">Задач еще не запускалось</p>';
        return;
    }

    listContainer.innerHTML = '';
    tasks.forEach(task => {
        const div = document.createElement('div');
        div.className = 'task-item';
        div.innerHTML = `
            <div style="display:flex; justify-content:space-between;">
                <strong>${task.name}</strong>
                <span style="color:#bbb; font-size:10px;">${task.time}</span>
            </div>
            <span class="task-id">${task.id}</span>
        `;
        div.onclick = () => checkTaskStatus(task.id);
        listContainer.appendChild(div);
    });
}

function saveTask(name, taskId) {
    tasks.unshift({ name, id: taskId, time: new Date().toLocaleTimeString() });
    if (tasks.length > 10) tasks.pop();
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
    renderTasks();
}

// Запуск задач (импорт, обновление и т.д.)
export async function runTask(type) {
    try {
        let res;
        let label = '';

        if (type === 'add_single') {
            const id = document.getElementById('add_tmdb_id').value;
            if(!id) return;
            label = `Импорт ID:${id}`;
            res = await fetchData(`/integrations/${id}`);
        }
        else if (type === 'update_single') {
            const id = document.getElementById('update_tmdb_id').value;
            if(!id) return;
            label = `Update ID:${id}`;
            res = await fetchData(`/integrations/update_movie/${id}`);
        }
        else if (type === 'pages_load') {
            const s = document.getElementById('start_page').value;
            const e = document.getElementById('end_page').value;
            label = `Страницы ${s}-${e}`;
            res = await fetchData(`/integrations/pages/${s}?start_page=${s}&end_page=${e}`);
        }
        else if (type === 'update_batch') {
            const b = document.getElementById('batch_size').value;
            label = `Batch (${b} шт.)`;
            res = await fetchData(`/integrations/update_movies?batch_size=${b}`);
        }

        if (res && res.task_id) {
            saveTask(label, res.task_id);
            checkTaskStatus(res.task_id);
        }
    } catch (err) {
        alert('Ошибка запуска: ' + err.message);
    }
}

// Проверка статуса в Celery
export async function checkTaskStatus(taskId) {
    const display = document.getElementById('status_display');
    const sVal = document.getElementById('status_val');
    const sRes = document.getElementById('status_res');

    if (!display) return;
    display.style.display = 'block';
    sVal.innerText = 'ЗАПРОС...';
    sVal.style.color = '#f39c12';

    try {
        const res = await fetchData(`/integrations/task_status/${taskId}`);
        sVal.innerText = res.status;

        if (res.status === 'SUCCESS') sVal.style.color = '#28a745';
        else if (res.status === 'FAILURE') sVal.style.color = '#dc3545';
        else sVal.style.color = '#f39c12';

        sRes.innerText = res.result ? JSON.stringify(res.result, null, 2) : 'Задача выполняется...';
    } catch (err) {
        sVal.innerText = 'ОШИБКА';
        sRes.innerText = 'Не удалось получить статус.';
    }
}