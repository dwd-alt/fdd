// static/script.js
let currentStatus = null;
let selectedServer = 'ssh-tunnel';
let statusUpdateInterval;
let trafficUpdateInterval;

// Показать уведомление
function showAlert(message, type = 'success') {
    // Создаем элемент уведомления
    const alert = document.createElement('div');
    alert.className = `alert ${type}`;
    alert.innerHTML = `
        <strong>${type === 'success' ? '✅' : '❌'}</strong>
        ${message}
        <button onclick="this.parentElement.remove()" style="float:right;background:none;border:none;cursor:pointer;color:inherit;">×</button>
    `;

    // Добавляем в начало контейнера
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);

        // Автоудаление через 5 секунд
        setTimeout(() => {
            if (alert.parentElement) {
                alert.remove();
            }
        }, 5000);
    }
}

// Форматирование времени
function formatUptime(startTime) {
    if (!startTime) return '00:00:00';

    try {
        const start = new Date(startTime);
        const now = new Date();
        const diff = Math.floor((now - start) / 1000);

        const hours = Math.floor(diff / 3600);
        const minutes = Math.floor((diff % 3600) / 60);
        const seconds = diff % 60;

        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    } catch (e) {
        return '00:00:00';
    }
}

// Обновление статуса
async function updateStatus() {
    try {
        const response = await fetch('/api/vpn/status');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        currentStatus = data;

        // Обновляем UI
        updateUI(data);

        return data;
    } catch (error) {
        console.error('Ошибка обновления статуса:', error);
        showAlert('Не удалось обновить статус', 'error');
        return null;
    }
}

// Обновление UI
function updateUI(data) {
    if (!data) return;

    // Основная информация
    const connectionStatus = document.getElementById('connectionStatus');
    const serverName = document.getElementById('serverName');
    const ipAddress = document.getElementById('ipAddress');
    const method = document.getElementById('method');
    const uploadStats = document.getElementById('uploadStats');
    const downloadStats = document.getElementById('downloadStats');
    const uptime = document.getElementById('uptime');

    if (connectionStatus) connectionStatus.textContent = data.connected ? 'Подключен' : 'Отключен';
    if (serverName) serverName.textContent = data.server || 'Не выбран';
    if (ipAddress) ipAddress.textContent = data.public_ip || 'Неизвестно';
    if (method) method.textContent = data.method || '-';
    if (uploadStats) uploadStats.textContent = data.upload || '0 B';
    if (downloadStats) downloadStats.textContent = data.download || '0 B';
    if (uptime) uptime.textContent = formatUptime(data.start_time);

    // Статус индикатор и кнопки
    const indicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');

    if (indicator && statusText) {
        if (data.connected) {
            indicator.classList.add('connected');
            statusText.textContent = 'Защищено';
        } else {
            indicator.classList.remove('connected');
            statusText.textContent = 'Не защищено';
        }
    }

    if (connectBtn) connectBtn.disabled = data.connected;
    if (disconnectBtn) disconnectBtn.disabled = !data.connected;
}

// Частое обновление трафика при подключении
function startFastTrafficUpdates() {
    stopFastTrafficUpdates(); // Останавливаем предыдущие

    trafficUpdateInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/vpn/status');
            if (response.ok) {
                const data = await response.json();

                // Обновляем только трафик
                const uploadElement = document.getElementById('uploadStats');
                const downloadElement = document.getElementById('downloadStats');

                if (uploadElement) uploadElement.textContent = data.upload || '0 B';
                if (downloadElement) downloadElement.textContent = data.download || '0 B';
            }
        } catch (error) {
            console.error('Ошибка обновления трафика:', error);
        }
    }, 2000); // Каждые 2 секунды
}

function stopFastTrafficUpdates() {
    if (trafficUpdateInterval) {
        clearInterval(trafficUpdateInterval);
        trafficUpdateInterval = null;
    }
}

// Загрузка серверов
async function loadServers() {
    try {
        const response = await fetch('/api/servers');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        const serverList = document.getElementById('serverList');
        if (!serverList) return;

        serverList.innerHTML = '';

        data.servers.forEach(server => {
            const serverElement = document.createElement('div');
            serverElement.className = 'server-item';
            serverElement.innerHTML = `
                <input type="radio" name="server" id="server_${server.id}"
                       value="${server.id}" ${selectedServer === server.id ? 'checked' : ''}>
                <label for="server_${server.id}">
                    <strong>${server.name}</strong>
                    <span>
                        ${server.location}
                        <span class="server-type ${server.type}">${server.type}</span>
                        ${server.ping ? `<span class="ping">${server.ping}</span>` : ''}
                    </span>
                </label>
            `;

            serverElement.querySelector('input').addEventListener('change', (e) => {
                if (e.target.checked) {
                    selectedServer = e.target.value;
                    console.log('Selected server:', selectedServer);
                }
            });

            serverList.appendChild(serverElement);
        });
    } catch (error) {
        console.error('Ошибка загрузки серверов:', error);
        showAlert('Не удалось загрузить список серверов', 'error');
    }
}

// Подключение к VPN
async function connectVPN() {
    const connectBtn = document.getElementById('connectBtn');
    if (!connectBtn) return;

    const originalText = connectBtn.innerHTML;

    connectBtn.disabled = true;
    connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Подключение...';

    try {
        const response = await fetch('/api/vpn/connect', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ server: selectedServer })
        });

        const data = await response.json();
        if (data.success) {
            showAlert(data.message || 'VPN успешно подключен!');
            await updateStatus();
            startFastTrafficUpdates();
        } else {
            showAlert('Ошибка подключения: ' + (data.error || 'Неизвестная ошибка'), 'error');
        }
    } catch (error) {
        showAlert('Ошибка сети: ' + error.message, 'error');
    } finally {
        connectBtn.disabled = false;
        connectBtn.innerHTML = originalText;
    }
}

// Отключение от VPN
async function disconnectVPN() {
    if (!confirm('Вы уверены, что хотите отключиться от VPN?')) return;

    const disconnectBtn = document.getElementById('disconnectBtn');
    if (!disconnectBtn) return;

    const originalText = disconnectBtn.innerHTML;

    disconnectBtn.disabled = true;
    disconnectBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Отключение...';

    try {
        const response = await fetch('/api/vpn/disconnect', {
            method: 'POST'
        });

        const data = await response.json();
        if (data.success) {
            showAlert(data.message || 'VPN отключен!');
            await updateStatus();
            stopFastTrafficUpdates();
        } else {
            showAlert('Ошибка отключения: ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('Ошибка сети: ' + error.message, 'error');
    } finally {
        disconnectBtn.disabled = false;
        disconnectBtn.innerHTML = originalText;
    }
}

// Показать/скрыть конфиг
async function toggleConfig() {
    const configSection = document.getElementById('configSection');
    const showConfigBtn = document.getElementById('showConfigBtn');

    if (!configSection || !showConfigBtn) return;

    if (configSection.style.display === 'none' || !configSection.style.display) {
        showConfigBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Загрузка...';

        try {
            const response = await fetch('/api/vpn/config');
            const data = await response.json();

            const configText = document.getElementById('configText');
            if (configText) configText.value = data.config;

            configSection.style.display = 'block';
            showConfigBtn.innerHTML = '<i class="fas fa-cog"></i> Скрыть конфиг';
        } catch (error) {
            showAlert('Ошибка загрузки конфигурации', 'error');
            showConfigBtn.innerHTML = '<i class="fas fa-cog"></i> WireGuard Config';
        }
    } else {
        configSection.style.display = 'none';
        showConfigBtn.innerHTML = '<i class="fas fa-cog"></i> WireGuard Config';
    }
}

// Инициализация
async function init() {
    console.log('Инициализация VPN Dashboard...');

    // Загружаем начальные данные
    await Promise.all([updateStatus(), loadServers()]);

    // Обновляем статус каждые 10 секунд
    statusUpdateInterval = setInterval(updateStatus, 10000);

    // Обновляем время работы каждую секунду если подключены
    setInterval(() => {
        if (currentStatus && currentStatus.connected && currentStatus.start_time) {
            const uptime = document.getElementById('uptime');
            if (uptime) {
                uptime.textContent = formatUptime(currentStatus.start_time);
            }
        }
    }, 1000);

    console.log('VPN Dashboard успешно инициализирован');
}

// Очистка интервалов при закрытии страницы
window.addEventListener('beforeunload', () => {
    if (statusUpdateInterval) clearInterval(statusUpdateInterval);
    if (trafficUpdateInterval) clearInterval(trafficUpdateInterval);
});

// Когда DOM загружен
document.addEventListener('DOMContentLoaded', () => {
    // Назначаем обработчики событий
    const connectBtn = document.getElementById('connectBtn');
    const disconnectBtn = document.getElementById('disconnectBtn');
    const showConfigBtn = document.getElementById('showConfigBtn');

    if (connectBtn) {
        connectBtn.addEventListener('click', connectVPN);
    }

    if (disconnectBtn) {
        disconnectBtn.addEventListener('click', disconnectVPN);
    }

    if (showConfigBtn) {
        showConfigBtn.addEventListener('click', toggleConfig);
    }

    // Инициализируем приложение
    init();
});