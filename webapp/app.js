const API_BASE = window.location.origin;

let tg = window.Telegram?.WebApp;
if (tg) {
    tg.expand();
    tg.ready();
}

function getUserId() {
    return tg?.initDataUnsafe?.user?.id || null;
}

async function apiGet(path) {
    const res = await fetch(`${API_BASE}${path}`);
    return res.json();
}

function showProfile() {
    const userId = getUserId();
    const content = document.getElementById('content');

    if (!userId) {
        content.innerHTML = `
            <div class="empty-state">
                <div class="emoji">🔒</div>
                <p>Откройте Mini App через Telegram бота</p>
            </div>
        `;
        return;
    }

    apiGet(`/api/user/${userId}`).then(user => {
        if (user.error) {
            content.innerHTML = `<div class="empty-state"><p>Пользователь не найден</p></div>`;
            return;
        }
        content.innerHTML = `
            <div class="card">
                <h3>👤 ${user.full_name}</h3>
                <p>Username: @${user.username || 'не указан'}</p>
                <p>Телефон: ${user.phone || 'не указан'}</p>
                <p>Зарегистрирован: ${user.created_at}</p>
            </div>
        `;
    });
}

function showOrders() {
    const userId = getUserId();
    const content = document.getElementById('content');

    if (!userId) {
        content.innerHTML = `<div class="empty-state"><div class="emoji">🔒</div><p>Войдите через бота</p></div>`;
        return;
    }

    apiGet(`/api/user/${userId}/orders`).then(orders => {
        if (!orders.length) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">📋</div>
                    <p>У вас пока нет заказов</p>
                </div>
            `;
            return;
        }
        content.innerHTML = orders.map(o => `
            <div class="card">
                <h3>№${o.id} — ${o.order_type} <span class="badge">${o.status}</span></h3>
                <p>${o.description}</p>
                <p>Бюджет: ${o.budget || 'не указан'}</p>
                <p>${o.created_at}</p>
            </div>
        `).join('');
    });
}

function showPortfolio() {
    const content = document.getElementById('content');

    apiGet('/api/portfolio').then(items => {
        if (!items.length) {
            content.innerHTML = `
                <div class="empty-state">
                    <div class="emoji">📂</div>
                    <p>Портфолио скоро появится</p>
                </div>
            `;
            return;
        }
        content.innerHTML = items.map(item => `
            <div class="card">
                <h3>${item.title}</h3>
                <p>${item.description || ''}</p>
                <p>Тип: ${item.order_type || 'не указан'}</p>
                ${item.site_url ? `<a href="${item.site_url}" target="_blank">🔗 Смотреть сайт</a>` : ''}
            </div>
        `).join('');
    });
}

document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        const page = this.dataset.page;
        if (page === 'profile') showProfile();
        else if (page === 'orders') showOrders();
        else if (page === 'portfolio') showPortfolio();
    });
});

document.getElementById('orderBtn').addEventListener('click', () => {
    if (tg) {
        tg.sendData(JSON.stringify({ action: 'order' }));
        tg.close();
    }
});

document.getElementById('feedbackBtn').addEventListener('click', () => {
    if (tg) {
        tg.sendData(JSON.stringify({ action: 'feedback' }));
        tg.close();
    }
});

showProfile();
