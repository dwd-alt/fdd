import json
import os
import time
from datetime import datetime
import tempfile
import platform
import random
import threading

class VPNManager:
    def __init__(self):
        if platform.system() == 'Windows':
            self.status_file = os.path.join(tempfile.gettempdir(), 'vpn_status.json')
        else:
            self.status_file = '/tmp/vpn_status.json'
        
        self.status = {
            'connected': False,
            'server': None,
            'start_time': None,
            'public_ip': '127.0.0.1',
            'upload': '0 KB',
            'download': '0 KB',
            'method': 'none'
        }
        
        # Для симуляции трафика
        self.upload_kb = 0
        self.download_kb = 0
        self.traffic_thread = None
        self.stop_traffic = False
        
        self._load_status()
        
        # Запускаем фоновый поток для обновления трафика
        self._start_background_updates()
    
    def _load_status(self):
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
                    
                # Восстанавливаем счетчики трафика из статуса
                if self.status['connected']:
                    try:
                        self.upload_kb = int(str(self.status['upload']).split()[0])
                        self.download_kb = int(str(self.status['download']).split()[0])
                    except:
                        self.upload_kb = 0
                        self.download_kb = 0
        except Exception as e:
            print(f"Error loading status: {e}")
    
    def _save_status(self):
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            print(f"Error saving status: {e}")
    
    def _start_background_updates(self):
        """Фоновое обновление трафика"""
        def update_traffic():
            while not self.stop_traffic:
                if self.status['connected']:
                    # Добавляем случайный трафик
                    self.upload_kb += random.randint(5, 20)
                    self.download_kb += random.randint(20, 100)
                    
                    # Обновляем статус
                    self.status['upload'] = f"{self.upload_kb} KB"
                    self.status['download'] = f"{self.download_kb} KB"
                    
                    # Сохраняем каждые 10 обновлений
                    if random.random() < 0.1:
                        self._save_status()
                
                time.sleep(1)  # Обновляем каждую секунду
        
        self.stop_traffic = False
        self.traffic_thread = threading.Thread(target=update_traffic, daemon=True)
        self.traffic_thread.start()
    
    def get_status(self):
        """Получение текущего статуса"""
        # Если подключены, добавляем немного трафика для немедленного отображения
        if self.status['connected']:
            self.upload_kb += random.randint(1, 5)
            self.download_kb += random.randint(5, 25)
            self.status['upload'] = f"{self.upload_kb} KB"
            self.status['download'] = f"{self.download_kb} KB"
        
        return self.status
    
    def connect(self, server_name):
        try:
            # Сбрасываем счетчики трафика
            self.upload_kb = 0
            self.download_kb = 0
            
            # Генерируем демо IP
            server_names = {
                'ssh-tunnel': 'SSH Tunnel',
                'http-proxy': 'HTTP Proxy', 
                'us-east': 'USA East',
                'eu-west': 'Europe West',
                'free': 'Free Server'
            }
            
            # Генерируем реалистичный IP на основе сервера
            random.seed(server_name)  # Для детерминированных IP
            if 'us-east' in server_name:
                ip = f'104.238.{random.randint(130, 140)}.{random.randint(1, 254)}'
            elif 'eu-west' in server_name:
                ip = f'176.126.{random.randint(230, 240)}.{random.randint(1, 254)}'
            elif 'free' in server_name:
                ip = f'158.247.{random.randint(200, 210)}.{random.randint(1, 254)}'
            else:
                ip = f'192.168.{random.randint(1, 255)}.{random.randint(1, 254)}'
            
            random.seed()  # Сбрасываем seed
            
            self.status = {
                'connected': True,
                'server': server_names.get(server_name, server_name),
                'start_time': datetime.now().isoformat(),
                'public_ip': ip,
                'upload': '0 KB',
                'download': '0 KB',
                'method': 'demo'
            }
            
            self._save_status()
            
            # Логируем подключение
            print(f"VPN connected to {server_name} with IP {ip}")
            
            return {
                'success': True,
                'status': self.status,
                'message': f'✅ Подключено к {server_name}'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disconnect(self):
        try:
            previous_ip = self.status['public_ip']
            
            self.status = {
                'connected': False,
                'server': None,
                'start_time': None,
                'public_ip': '127.0.0.1',  # Локальный IP после отключения
                'upload': '0 KB',
                'download': '0 KB',
                'method': 'none'
            }
            
            # Сбрасываем счетчики
            self.upload_kb = 0
            self.download_kb = 0
            
            self._save_status()
            
            print(f"VPN disconnected, was connected to {previous_ip}")
            
            return {
                'success': True,
                'status': self.status,
                'message': '✅ VPN отключен'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_available_servers(self):
        return [
            {
                'id': 'ssh-tunnel', 
                'name': 'SSH Tunnel', 
                'location': 'Basic VPN',
                'type': 'ssh',
                'ping': f'{random.randint(10, 30)}ms'
            },
            {
                'id': 'http-proxy', 
                'name': 'HTTP Proxy', 
                'location': 'Web Proxy',
                'type': 'proxy',
                'ping': f'{random.randint(20, 50)}ms'
            },
            {
                'id': 'us-east', 
                'name': 'USA East', 
                'location': 'New York',
                'type': 'wireguard',
                'ping': f'{random.randint(30, 80)}ms'
            },
            {
                'id': 'eu-west', 
                'name': 'Europe West', 
                'location': 'Amsterdam',
                'type': 'wireguard',
                'ping': f'{random.randint(20, 60)}ms'
            },
            {
                'id': 'free', 
                'name': 'Free Server', 
                'location': 'Germany',
                'type': 'wireguard',
                'ping': f'{random.randint(40, 100)}ms'
            }
        ]
    
    def get_client_config(self):
        config = """[Interface]
PrivateKey = eCwJf1Hvj+FPyO9pizzkLpKQEIyI5Ph1gx6KSRJGXkE=
Address = 10.8.0.2/24
DNS = 1.1.1.1, 8.8.8.8
MTU = 1420

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = vpn.example.com:51820
PersistentKeepalive = 25"""
        
        return {
            'config': config,
            'qr_code_url': None,
            'note': 'Скопируйте этот конфиг в приложение WireGuard'
        }
    
    def __del__(self):
        """Очистка при завершении"""
        self.stop_traffic = True
        if self.traffic_thread:
            self.traffic_thread.join(timeout=1)
