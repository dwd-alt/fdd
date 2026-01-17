import subprocess
import json
import os
import threading
import time
from datetime import datetime
import requests
import tempfile
import platform


class VPNManager:
    def __init__(self):
        # Используем временную папку в зависимости от ОС
        if platform.system() == 'Windows':
            temp_dir = tempfile.gettempdir()
            self.status_file = os.path.join(temp_dir, 'vpn_status.json')
        else:
            self.status_file = '/tmp/vpn_status.json'

        print(f"Status file path: {self.status_file}")  # Для отладки

        self.current_connection = None
        self.status = {
            'connected': False,
            'server': None,
            'start_time': None,
            'public_ip': None,
            'upload': 0,
            'download': 0,
            'method': None
        }
        self.load_status()

    def load_status(self):
        try:
            print(f"Loading status from: {self.status_file}")  # Для отладки
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    self.status = json.load(f)
                print(f"Status loaded: {self.status}")  # Для отладки
            else:
                print("Status file does not exist, using default")  # Для отладки
        except Exception as e:
            print(f"Error loading status: {e}")  # Для отладки
            # Создаем новый файл с дефолтными значениями
            self.status = {
                'connected': False,
                'server': None,
                'start_time': None,
                'public_ip': self._get_public_ip(),
                'upload': 0,
                'download': 0,
                'method': None
            }
            self.save_status()

    def save_status(self):
        try:
            print(f"Saving status to: {self.status_file}")  # Для отладки
            # Создаем папку если не существует
            os.makedirs(os.path.dirname(self.status_file), exist_ok=True)

            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(self.status, f, ensure_ascii=False, indent=2)
            print(f"Status saved: {self.status}")  # Для отладки
        except Exception as e:
            print(f"Error saving status: {e}")  # Для отладки

    def get_status(self):
        # Обновляем IP если нужно
        if not self.status['public_ip'] or self.status['connected']:
            try:
                self.status['public_ip'] = self._get_public_ip()
            except:
                pass
        return self.status

    def connect(self, server_name):
        try:
            print(f"Connecting to server: {server_name}")  # Для отладки

            # Метод 1: SSH туннель (демо режим)
            if server_name in ['ssh-tunnel', 'free']:
                return self._connect_demo(server_name, 'ssh_tunnel')

            # Метод 2: HTTP прокси (демо режим)
            elif server_name == 'http-proxy':
                return self._connect_demo(server_name, 'http_proxy')

            # Метод 3: WireGuard (демо режим)
            else:
                return self._connect_demo(server_name, 'wireguard')

        except Exception as e:
            error_msg = f"Connection error: {str(e)}"
            print(error_msg)  # Для отладки
            return {'success': False, 'error': error_msg}

    def _connect_demo(self, server_name, method):
        """Демо подключение - работает везде"""
        try:
            # Имитация задержки подключения
            time.sleep(1)

            # Генерируем демо IP
            demo_ip = self._get_demo_ip(server_name)

            self.status = {
                'connected': True,
                'server': f"{server_name} ({method})",
                'start_time': datetime.now().isoformat(),
                'public_ip': demo_ip,
                'upload': "0 KB",
                'download': "0 KB",
                'method': method
            }

            self.save_status()

            # Имитация обновления трафика в фоне
            self._start_traffic_simulation()

            return {
                'success': True,
                'status': self.status,
                'message': f'Подключено к {server_name} (демо-режим)'
            }

        except Exception as e:
            return {'success': False, 'error': f"Demo connection error: {str(e)}"}

    def disconnect(self):
        try:
            print("Disconnecting VPN")  # Для отладки

            # Останавливаем симуляцию трафика
            self._stop_traffic_simulation()

            # Получаем текущий реальный IP
            current_ip = self._get_public_ip()

            self.status = {
                'connected': False,
                'server': None,
                'start_time': None,
                'public_ip': current_ip,
                'upload': "0 KB",
                'download': "0 KB",
                'method': None
            }

            self.save_status()

            return {
                'success': True,
                'status': self.status,
                'message': 'VPN отключен'
            }

        except Exception as e:
            error_msg = f"Disconnection error: {str(e)}"
            print(error_msg)  # Для отладки
            return {'success': False, 'error': error_msg}

    def _get_public_ip(self):
        """Получение реального IP адреса"""
        try:
            # Пробуем разные сервисы
            services = [
                'https://api.ipify.org?format=json',
                'https://ifconfig.me/ip',
                'http://checkip.amazonaws.com'
            ]

            for service in services:
                try:
                    response = requests.get(service, timeout=3)
                    if response.status_code == 200:
                        if 'json' in service:
                            return response.json().get('ip', 'Неизвестно')
                        else:
                            return response.text.strip()
                except:
                    continue

            # Если все сервисы не ответили
            return "127.0.0.1"

        except Exception as e:
            print(f"Error getting public IP: {e}")  # Для отладки
            return "127.0.0.1"

    def _get_demo_ip(self, server_name):
        """Генерация демо IP адресов для разных серверов"""
        import random
        import hashlib

        # Создаем детерминированный IP на основе имени сервера
        hash_obj = hashlib.md5(server_name.encode())
        hash_int = int(hash_obj.hexdigest(), 16)

        # Генерируем IP в разных диапазонах
        ranges = [
            (104, 238, 130),  # USA
            (176, 126, 237),  # Europe
            (139, 162, 119),  # Asia
            (158, 247, 209),  # Other
        ]

        range_idx = hash_int % len(ranges)
        base_range = ranges[range_idx]

        # Последний октет на основе хэша
        last_octet = 100 + (hash_int % 155)

        return f"{base_range[0]}.{base_range[1]}.{base_range[2]}.{last_octet}"

    # Переменные для симуляции трафика
    _traffic_thread = None
    _stop_traffic = False

    def _start_traffic_simulation(self):
        """Запуск симуляции трафика в фоновом потоке"""
        if self._traffic_thread and self._traffic_thread.is_alive():
            self._stop_traffic_simulation()

        self._stop_traffic = False
        self._traffic_thread = threading.Thread(target=self._simulate_traffic)
        self._traffic_thread.daemon = True
        self._traffic_thread.start()
        print("Traffic simulation started")  # Для отладки

    def _stop_traffic_simulation(self):
        """Остановка симуляции трафика"""
        self._stop_traffic = True
        if self._traffic_thread:
            self._traffic_thread.join(timeout=1)
        print("Traffic simulation stopped")  # Для отладки

    def _simulate_traffic(self):
        """Симуляция роста трафика"""
        import random

        upload_kb = 0
        download_kb = 0

        while not self._stop_traffic and self.status['connected']:
            try:
                # Добавляем случайный трафик
                upload_kb += random.randint(1, 10)
                download_kb += random.randint(5, 50)

                # Обновляем статус
                self.status['upload'] = f"{upload_kb} KB"
                self.status['download'] = f"{download_kb} KB"

                # Сохраняем каждые 10 обновлений
                if random.random() < 0.1:
                    self.save_status()

                # Ждем 0.5-2 секунды
                time.sleep(random.uniform(0.5, 2))

            except Exception as e:
                print(f"Error in traffic simulation: {e}")  # Для отладки
                break

    def get_available_servers(self):
        """Список доступных серверов (демо версия)"""
        return [
            {
                'id': 'ssh-tunnel',
                'name': 'SSH Tunnel',
                'location': 'Basic VPN (Demo)',
                'type': 'ssh',
                'ping': '15 ms'
            },
            {
                'id': 'http-proxy',
                'name': 'HTTP Proxy',
                'location': 'Web Proxy (Demo)',
                'type': 'proxy',
                'ping': '25 ms'
            },
            {
                'id': 'us-east',
                'name': 'USA East',
                'location': 'New York (Demo)',
                'type': 'wireguard',
                'ping': '45 ms'
            },
            {
                'id': 'eu-west',
                'name': 'Europe West',
                'location': 'Amsterdam (Demo)',
                'type': 'wireguard',
                'ping': '35 ms'
            },
            {
                'id': 'free',
                'name': 'Free Server',
                'location': 'Germany (Demo)',
                'type': 'wireguard',
                'ping': '55 ms'
            }
        ]

    def get_client_config(self):
        """Генерация демо конфига для WireGuard"""
        # Пример конфига для демонстрации
        demo_config = f"""[Interface]
PrivateKey = eCwJf1Hvj+FPyO9pizzkLpKQEIyI5Ph1gx6KSRJGXkE=
Address = 10.8.0.2/24
DNS = 1.1.1.1, 8.8.8.8
MTU = 1420

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = {self._get_demo_ip('demo')}:51820
PersistentKeepalive = 25"""

        return {
            'config': demo_config,
            'qr_code_url': '#',
            'note': 'Это демонстрационный конфиг. Для реального использования настройте свой WireGuard сервер.'
        }