import json
import os
import time
from datetime import datetime
import tempfile
import platform
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
        self._load_status()
        
        # Для симуляции трафика
        self._traffic_thread = None
        self._stop_traffic = False
    
    def _load_status(self):
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    self.status = json.load(f)
        except:
            pass
    
    def _save_status(self):
        try:
            with open(self.status_file, 'w') as f:
                json.dump(self.status, f, indent=2)
        except:
            pass
    
    def get_status(self):
        return self.status
    
    def connect(self, server_name):
        try:
            # Останавливаем предыдущую симуляцию
            self._stop_traffic_sim()
            
            # Демо IP на основе сервера
            demo_ips = {
                'ssh-tunnel': '192.168.1.100',
                'http-proxy': '10.0.0.50',
                'us-east': '104.238.130.180',
                'eu-west': '176.126.237.114',
                'free': '158.247.209.142'
            }
            
            self.status = {
                'connected': True,
                'server': server_name,
                'start_time': datetime.now().isoformat(),
                'public_ip': demo_ips.get(server_name, '203.0.113.1'),
                'upload': '0 KB',
                'download': '0 KB',
                'method': 'demo'
            }
            
            self._save_status()
            
            # Запускаем симуляцию трафика
            self._start_traffic_sim()
            
            return {
                'success': True,
                'status': self.status,
                'message': f'Подключено к {server_name} (демо)'
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def disconnect(self):
        try:
            self._stop_traffic_sim()
            
            self.status = {
                'connected': False,
                'server': None,
                'start_time': None,
                'public_ip': '127.0.0.1',
                'upload': '0 KB',
                'download': '0 KB',
                'method': 'none'
            }
            
            self._save_status()
            return {'success': True, 'status': self.status}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _start_traffic_sim(self):
        """Запуск симуляции трафика"""
        self._stop_traffic = False
        self._traffic_thread = threading.Thread(target=self._simulate_traffic)
        self._traffic_thread.daemon = True
        self._traffic_thread.start()
    
    def _stop_traffic_sim(self):
        """Остановка симуляции трафика"""
        self._stop_traffic = True
        if self._traffic_thread:
            self._traffic_thread.join(timeout=1)
    
    def _simulate_traffic(self):
        """Симуляция роста трафика"""
        import random
        
        upload = 0
        download = 0
        
        while not self._stop_traffic and self.status['connected']:
            try:
                upload += random.randint(1, 10)
                download += random.randint(5, 50)
                
                self.status['upload'] = f"{upload} KB"
                self.status['download'] = f"{download} KB"
                
                # Сохраняем каждые 10 секунд
                if random.random() < 0.1:
                    self._save_status()
                
                time.sleep(1)
            except:
                break
    
    def get_available_servers(self):
        return [
            {'id': 'ssh-tunnel', 'name': 'SSH Tunnel', 'location': 'Basic VPN', 'type': 'ssh'},
            {'id': 'http-proxy', 'name': 'HTTP Proxy', 'location': 'Web Proxy', 'type': 'proxy'},
            {'id': 'us-east', 'name': 'USA East', 'location': 'New York', 'type': 'wireguard'},
            {'id': 'eu-west', 'name': 'Europe West', 'location': 'Amsterdam', 'type': 'wireguard'},
            {'id': 'free', 'name': 'Free Server', 'location': 'Germany', 'type': 'wireguard'}
        ]
    
    def get_client_config(self):
        return {
            'config': """[Interface]
PrivateKey = eCwJf1Hvj+FPyO9pizzkLpKQEIyI5Ph1gx6KSRJGXkE=
Address = 10.8.0.2/24
DNS = 1.1.1.1

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0
Endpoint = demo.vpn.server:51820
PersistentKeepalive = 25""",
            'qr_code_url': None
        }
