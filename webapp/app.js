const API_BASE = window.location.origin;
const tg = window.Telegram?.WebApp;

if (tg) {
  tg.expand();
  tg.ready();
  document.documentElement.setAttribute(
    'data-theme',
    tg.colorScheme === 'dark' ? 'dark' : 'light'
  );
}

function getUserId() {
  return tg?.initDataUnsafe?.user?.id || null;
}

function getFullName() {
  const u = tg?.initDataUnsafe?.user;
  return u ? `${u.first_name || ''} ${u.last_name || ''}`.trim() : null;
}

async function apiGet(path) {
  try {
    const res = await fetch(`${API_BASE}${path}`);
    return await res.json();
  } catch {
    return null;
  }
}

function showLoading() {
  document.getElementById('content').innerHTML = `
    <div style="text-align:center;padding:48px 16px;color:var(--text-secondary)">
      <div style="width:32px;height:32px;margin:0 auto 12px;border:3px solid var(--border);border-top-color:var(--primary);border-radius:50%;animation:spin 0.8s linear infinite"></div>
      <p>Загрузка...</p>
    </div>
    <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
  `;
}

async function showProfile() {
  showLoading();
  const userId = getUserId();

  if (!userId) {
    document.getElementById('content').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0110 0v4"/></svg>
        </div>
        <h3>Авторизация</h3>
        <p>Откройте Mini App через Telegram бота</p>
      </div>
    `;
    return;
  }

  const user = await apiGet(`/api/user/${userId}`);
  const orders = await apiGet(`/api/user/${userId}/orders`);

  const initial = (getFullName() || '?')[0].toUpperCase();

  document.getElementById('content').innerHTML = `
    <div class="card">
      <div class="profile-info">
        <div class="profile-avatar">${initial}</div>
        <div class="profile-name">${user?.full_name || getFullName() || 'Пользователь'}</div>
        <div class="profile-username">@${user?.username || tg?.initDataUnsafe?.user?.username || 'не указан'}</div>
        <div class="profile-stats">
          <div class="stat">
            <div class="stat-value">${orders ? orders.length : 0}</div>
            <div class="stat-label">Заказы</div>
          </div>
          <div class="stat">
            <div class="stat-value">${user?.phone ? '✓' : '—'}</div>
            <div class="stat-label">Телефон</div>
          </div>
          <div class="stat">
            <div class="stat-value">${user?.created_at ? new Date(user.created_at).toLocaleDateString('ru') : '—'}</div>
            <div class="stat-label">На сайте</div>
          </div>
        </div>
      </div>
    </div>
  `;
}

async function showOrders() {
  showLoading();
  const userId = getUserId();

  if (!userId) {
    document.getElementById('content').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        </div>
        <h3>Авторизация</h3>
        <p>Войдите через бота</p>
      </div>
    `;
    return;
  }

  const orders = await apiGet(`/api/user/${userId}/orders`);

  if (!orders || !orders.length) {
    document.getElementById('content').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></svg>
        </div>
        <h3>Нет заказов</h3>
        <p>Нажмите «Заказать сайт» внизу</p>
      </div>
    `;
    return;
  }

  const statusMap = { new: 'Новый', in_progress: 'В работе', done: 'Готов' };
  const badgeMap = { new: 'badge-new', in_progress: 'badge-progress', done: 'badge-done' };

  document.getElementById('content').innerHTML = orders.map(o => `
    <div class="card">
      <div class="card-header">
        <span class="card-title">№${o.id} — ${o.order_type}</span>
        <span class="badge ${badgeMap[o.status] || 'badge-new'}">${statusMap[o.status] || o.status}</span>
      </div>
      <div class="card-subtitle">${o.description}</div>
      <div class="card-meta">
        ${o.budget ? `<span>💰 ${o.budget} ₽</span>` : ''}
        <span>📅 ${new Date(o.created_at).toLocaleDateString('ru')}</span>
      </div>
    </div>
  `).join('');
}

async function showPortfolio() {
  showLoading();
  const items = await apiGet('/api/portfolio');

  if (!items || !items.length) {
    document.getElementById('content').innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="4" width="20" height="16" rx="2"/><circle cx="9" cy="10" r="2"/><path d="M22 14l-4-4-6 6-4-4-4 4"/></svg>
        </div>
        <h3>Портфолио</h3>
        <p>Скоро здесь появятся наши работы</p>
      </div>
    `;
    return;
  }

  document.getElementById('content').innerHTML = items.map(item => `
    <div class="card">
      <div class="card-header">
        <span class="card-title">${item.title}</span>
        ${item.order_type ? `<span class="badge badge-new">${item.order_type}</span>` : ''}
      </div>
      ${item.description ? `<div class="card-subtitle">${item.description}</div>` : ''}
      ${item.site_url ? `<a class="card-link" href="${item.site_url}" target="_blank">🔗 Смотреть сайт</a>` : ''}
    </div>
  `).join('');
}

document.querySelectorAll('.nav-item').forEach(btn => {
  btn.addEventListener('click', function () {
    document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
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
