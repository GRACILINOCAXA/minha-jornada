import socket
import threading
import time
import traceback
import urllib.request

import webview
from werkzeug.serving import make_server

from backend.app import create_app
from backend.resource_paths import ensure_user_data_dir, get_resource_path


HOST = '127.0.0.1'
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
LOADING_PAGE = '''<!doctype html><html><head><meta charset="utf-8"><title>Minha Jornada</title>
<style>body{margin:0;background:#f5f1e8;color:#263238;font-family:Segoe UI,sans-serif;display:grid;place-items:center;height:100vh}
main{text-align:center}h1{font-size:34px;letter-spacing:1px;margin:0 0 12px}p{font-size:16px;color:#607078}</style></head>
<body><main><h1>MINHA JORNADA</h1><p>Carregando aplicação...</p></main></body></html>'''


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind((HOST, 0))
        return probe.getsockname()[1]


def wait_for_server(port, timeout=30):
    deadline = time.monotonic() + timeout
    health_url = f'http://{HOST}:{port}/api/health'
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                return response.status == 200
        except Exception:
            time.sleep(0.1)
    return False


def show_startup_error(message):
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('Minha Jornada', message)
        root.destroy()
    except Exception:
        pass


def write_startup_log(message):
    try:
        log_path = ensure_user_data_dir() / 'startup.log'
        with log_path.open('a', encoding='utf-8') as log_file:
            log_file.write(message + '\n')
    except Exception:
        pass


def main():
    server = None
    try:
        write_startup_log(f'Iniciando Minha Jornada; PID={__import__("os").getpid()}')
        app = create_app('production')
        port = find_free_port()
        server = make_server(HOST, port, app, threaded=True)
        write_startup_log(f'Servidor Flask iniciado em {HOST}:{port}')
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        window = webview.create_window(
            'Minha Jornada',
            html=LOADING_PAGE,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            resizable=True,
            min_size=(960, 640),
            text_select=True,
        )

        def load_application():
            if wait_for_server(port):
                window.load_url(f'http://{HOST}:{port}/login')
            else:
                window.load_html('<h1>Não foi possível iniciar o Minha Jornada.</h1><p>Tente fechar o aplicativo e abrir novamente.</p>')

        window.events.closed += lambda: server.shutdown()
        webview.start(load_application, gui='edgechromium', debug=False)
    except Exception:
        write_startup_log(traceback.format_exc())
        show_startup_error('Não foi possível iniciar o Minha Jornada.\n\nTente fechar o aplicativo e abrir novamente.')
    finally:
        if server is not None:
            server.shutdown()


if __name__ == '__main__':
    main()