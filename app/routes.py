from flask import Blueprint, render_template, jsonify, request, session
from flask_socketio import emit
from .vpn_manager import VPNManager
import json

bp = Blueprint('main', __name__)
vpn_manager = VPNManager()


@bp.route('/')
def index():
    status = vpn_manager.get_status()
    return render_template('index.html', status=status)


@bp.route('/api/vpn/status', methods=['GET'])
def get_vpn_status():
    status = vpn_manager.get_status()
    return jsonify(status)


@bp.route('/api/vpn/connect', methods=['POST'])
def connect_vpn():
    data = request.json
    server = data.get('server', 'default')

    result = vpn_manager.connect(server)
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'VPN подключен',
            'status': result['status']
        })
    else:
        return jsonify({
            'success': False,
            'message': result.get('error', 'Ошибка подключения')
        }), 500


@bp.route('/api/vpn/disconnect', methods=['POST'])
def disconnect_vpn():
    result = vpn_manager.disconnect()
    if result['success']:
        return jsonify({
            'success': True,
            'message': 'VPN отключен',
            'status': result['status']
        })
    else:
        return jsonify({
            'success': False,
            'message': result.get('error', 'Ошибка отключения')
        }), 500


@bp.route('/api/servers', methods=['GET'])
def get_servers():
    servers = vpn_manager.get_available_servers()
    return jsonify({'servers': servers})


@bp.route('/api/vpn/config', methods=['GET'])
def get_vpn_config():
    config = vpn_manager.get_client_config()
    return jsonify(config)