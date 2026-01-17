#!/usr/bin/env python3
import subprocess
import os


def generate_keys():
    keys_dir = 'wireguard/keys'
    configs_dir = 'wireguard/configs'

    os.makedirs(keys_dir, exist_ok=True)
    os.makedirs(configs_dir, exist_ok=True)

    # Генерация приватного ключа
    private_key = subprocess.run(
        'wg genkey',
        shell=True,
        capture_output=True,
        text=True
    ).stdout.strip()

    # Генерация публичного ключа
    public_key = subprocess.run(
        f'echo "{private_key}" | wg pubkey',
        shell=True,
        capture_output=True,
        text=True,
        shell=True
    ).stdout.strip()

    # Сохранение ключей
    with open(f'{keys_dir}/private.key', 'w') as f:
        f.write(private_key)

    with open(f'{keys_dir}/public.key', 'w') as f:
        f.write(public_key)

    print(f"Приватный ключ: {private_key}")
    print(f"Публичный ключ: {public_key}")

    # Пример конфига сервера
    server_config = f"""[Interface]
Address = 10.0.0.1/24
ListenPort = 51820
PrivateKey = {private_key}
PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o eth0 -j MASQUERADE

[Peer]
# Client 1
PublicKey = CLIENT_PUBLIC_KEY
AllowedIPs = 10.0.0.2/32
"""

    with open(f'{configs_dir}/server.conf', 'w') as f:
        f.write(server_config)

    print("\nСгенерирован пример конфига сервера в wireguard/configs/server.conf")
    print("Замените CLIENT_PUBLIC_KEY на публичный ключ клиента")


if __name__ == '__main__':
    generate_keys()