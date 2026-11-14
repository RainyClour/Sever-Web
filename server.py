#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChemPharm A+ Hub — Self-Hosted Realtime Web Server (Python 3 + SQLite3 + SSE)
Dành cho sinh viên Dược - Trường Đại học Kỹ thuật Y - Dược Đà Nẵng (HĐC022143)
Không cần cài đặt thư viện ngoài (chỉ dùng Python 3 chuẩn có sẵn trên máy).
"""
import hashlib
import http.server
import json
import os
import socket
import socketserver
import sqlite3
import threading
import time
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT", os.environ.get("CHEM_PORT", "8080")))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public") if os.path.isdir(os.path.join(BASE_DIR, "public")) else BASE_DIR
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "chem_a_plus.db")

os.makedirs(DATA_DIR, exist_ok=True)
db_lock = threading.Lock()
sse_clients = []
sse_lock = threading.Lock()


def init_db():
    with db_lock:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                class_name TEXT DEFAULT '',
                pin_hash TEXT NOT NULL,
                created_at INTEGER NOT NULL,
                last_login INTEGER NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_state (
                username TEXT PRIMARY KEY,
                state_json TEXT NOT NULL,
                updated_at INTEGER NOT NULL,
                FOREIGN KEY(username) REFERENCES users(username)
            )
        """)
        conn.commit()
        conn.close()


def broadcast_sse(event_name, payload):
    msg = f"event: {event_name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n".encode("utf-8")
    with sse_lock:
        dead = []
        for wfile in sse_clients:
            try:
                wfile.write(msg)
                wfile.flush()
            except Exception:
                dead.append(wfile)
        for d in dead:
            sse_clients.remove(d)


class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


class ChemRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def _send_json(self, status_code, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/health":
            return self._send_json(200, {
                "status": "ok",
                "server": "ChemPharm A+ Self-Hosted Server",
                "timestamp": int(time.time() * 1000),
            })

        if parsed.path == "/api/state":
            qs = parse_qs(parsed.query)
            username = (qs.get("username", [""])[0]).strip().lower()
            if not username:
                return self._send_json(400, {"ok": False, "error": "Thiếu username"})
            with db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT state_json, updated_at FROM user_state WHERE username = ?", (username,))
                row = cur.fetchone()
                conn.close()
            if row:
                return self._send_json(200, {
                    "ok": True,
                    "username": username,
                    "state": json.loads(row[0]),
                    "updatedAt": row[1],
                })
            return self._send_json(200, {"ok": True, "username": username, "state": None, "updatedAt": 0})

        if parsed.path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()
            with sse_lock:
                sse_clients.append(self.wfile)
            try:
                self.wfile.write(b"event: connected\ndata: {\"status\":\"connected\"}\n\n")
                self.wfile.flush()
                while True:
                    time.sleep(15)
                    self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with sse_lock:
                    if self.wfile in sse_clients:
                        sse_clients.remove(self.wfile)
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            body = json.loads(raw)
        except Exception:
            return self._send_json(400, {"ok": False, "error": "Invalid JSON"})

        if parsed.path == "/api/register":
            username = str(body.get("username", "")).strip().lower()
            pin = str(body.get("pin", "")).strip()
            display_name = str(body.get("displayName", "")).strip()
            class_name = str(body.get("className", "")).strip()
            if not username or not pin or not display_name:
                return self._send_json(400, {"ok": False, "error": "Vui lòng điền đầy đủ họ tên, tài khoản và mật khẩu!"})
            pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
            now = int(time.time() * 1000)
            with db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT username FROM users WHERE username = ?", (username,))
                if cur.fetchone():
                    conn.close()
                    return self._send_json(409, {"ok": False, "error": "Tên đăng nhập đã tồn tại, vui lòng chọn tên khác!"})
                cur.execute(
                    "INSERT INTO users (username, display_name, class_name, pin_hash, created_at, last_login) VALUES (?, ?, ?, ?, ?, ?)",
                    (username, display_name, class_name, pin_hash, now, now),
                )
                conn.commit()
                conn.close()
            return self._send_json(200, {"ok": True, "username": username, "displayName": display_name, "className": class_name})

        if parsed.path == "/api/login":
            username = str(body.get("username", "")).strip().lower()
            pin = str(body.get("pin", "")).strip()
            if not username or not pin:
                return self._send_json(400, {"ok": False, "error": "Vui lòng nhập tên đăng nhập và mật khẩu!"})
            pin_hash = hashlib.sha256(pin.encode("utf-8")).hexdigest()
            now = int(time.time() * 1000)
            with db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT display_name, class_name, pin_hash FROM users WHERE username = ?", (username,))
                row = cur.fetchone()
                if not row:
                    conn.close()
                    return self._send_json(404, {"ok": False, "error": "Tài khoản chưa tồn tại! Vui lòng chuyển sang tab Đăng ký."})
                if row[2] != pin_hash:
                    conn.close()
                    return self._send_json(401, {"ok": False, "error": "Mật khẩu / Mã PIN không chính xác!"})
                cur.execute("UPDATE users SET last_login = ? WHERE username = ?", (now, username))
                conn.commit()
                conn.close()
                return self._send_json(200, {"ok": True, "username": username, "displayName": row[0], "className": row[1]})

        if parsed.path == "/api/state":
            username = str(body.get("username", "")).strip().lower()
            if not username:
                return self._send_json(400, {"ok": False, "error": "Thiếu username"})
            state_obj = body.get("state", {})
            now = int(time.time() * 1000)
            state_str = json.dumps(state_obj, ensure_ascii=False)
            with db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO user_state (username, state_json, updated_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(username) DO UPDATE SET state_json = excluded.state_json, updated_at = excluded.updated_at",
                    (username, state_str, now),
                )
                conn.commit()
                conn.close()
            broadcast_sse("state_updated", {"username": username, "updatedAt": now})
            return self._send_json(200, {"ok": True, "updatedAt": now})

        return self._send_json(404, {"ok": False, "error": "Not found"})


def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    init_db()
    lan_ip = get_lan_ip()
    print("=" * 68)
    print("  CHEMPHARM A+ HUB — MÁY CHỦ ÔN TẬP HÓA ĐẠI CƯƠNG - VÔ CƠ")
    print("=" * 68)
    print(f"  [+] Truy cập trên máy tính này : http://localhost:{PORT}")
    print(f"  [+] Truy cập từ Điện thoại/iPad: http://{lan_ip}:{PORT}")
    print(f"  [+] Cơ sở dữ liệu SQLite an toàn: {DB_PATH}")
    print("  [+] Nhấn Ctrl+C để dừng máy chủ.")
    print("=" * 68)
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ChemRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã dừng máy chủ an toàn.")
