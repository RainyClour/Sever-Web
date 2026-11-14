// ============================================================================
// DUMTP ChemA+ Studio — Cloud & Local Rust HTTP Server (Zero-Dependency Edition)
// Compatible out-of-the-box with Render.com, Fly.io, Railway, and Local Windows
// ============================================================================
use std::collections::HashMap;
use std::env;
use std::fs;
use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{SystemTime, UNIX_EPOCH};

struct AppStore {
    states: Mutex<HashMap<String, String>>,
    feedbacks: Mutex<Vec<String>>,
}

fn now_ms() -> u128 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .map(|d| d.as_millis())
        .unwrap_or(0)
}

fn load_html_file() -> Vec<u8> {
    for candidate in &["index.html", "public/index.html", "templates/index.html"] {
        if let Ok(bytes) = fs::read(candidate) {
            if !bytes.is_empty() {
                return bytes;
            }
        }
    }
    b"<!DOCTYPE html><html><head><meta charset='utf-8'><title>ChemA+ Studio</title></head><body><h2>Please upload index.html to the repository root!</h2></body></html>".to_vec()
}

fn send_response(stream: &mut TcpStream, status: &str, content_type: &str, body: &[u8]) {
    let header = format!(
        "HTTP/1.1 {}\r\nContent-Type: {}\r\nContent-Length: {}\r\nCache-Control: no-store, no-cache, must-revalidate\r\nAccess-Control-Allow-Origin: *\r\nConnection: close\r\n\r\n",
        status,
        content_type,
        body.len()
    );
    let _ = stream.write_all(header.as_bytes());
    let _ = stream.write_all(body);
    let _ = stream.flush();
}

fn handle_client(mut stream: TcpStream, store: Arc<AppStore>) {
    let mut buf = [0u8; 65536];
    let n = match stream.read(&mut buf) {
        Ok(n) if n > 0 => n,
        _ => return,
    };
    let req_str = String::from_utf8_lossy(&buf[..n]);
    let first_line = req_str.lines().next().unwrap_or("GET / HTTP/1.1");
    let parts: Vec<&str> = first_line.split_whitespace().collect();
    let method = *parts.first().unwrap_or(&"GET");
    let full_path = *parts.get(1).unwrap_or(&"/");
    let path = full_path.split('?').next().unwrap_or("/");

    if method == "GET" && (path == "/" || path == "/index.html") {
        let html = load_html_file();
        send_response(&mut stream, "200 OK", "text/html; charset=utf-8", &html);
        return;
    }

    if method == "GET" && path == "/manifest.json" {
        let data = fs::read("manifest.json")
            .or_else(|_| fs::read("public/manifest.json"))
            .unwrap_or_else(|_| b"{}".to_vec());
        send_response(&mut stream, "200 OK", "application/json; charset=utf-8", &data);
        return;
    }

    if method == "GET" && path == "/sw.js" {
        let data = fs::read("sw.js")
            .or_else(|_| fs::read("public/sw.js"))
            .unwrap_or_else(|_| b"".to_vec());
        send_response(&mut stream, "200 OK", "application/javascript; charset=utf-8", &data);
        return;
    }

    if path == "/api/health" {
        let json = format!(
            "{{\"status\":\"ok\",\"server\":\"DUMTP ChemA+ Rust Cloud Server\",\"timestamp\":{}}}",
            now_ms()
        );
        send_response(&mut stream, "200 OK", "application/json; charset=utf-8", json.as_bytes());
        return;
    }

    if path == "/api/feedback" && method == "POST" {
        let body_part = req_str.split("\r\n\r\n").nth(1).unwrap_or("{}").to_string();
        if let Ok(mut list) = store.feedbacks.lock() {
            list.push(body_part);
        }
        let resp = b"{\"ok\":true,\"recipient\":\"Rainmy2000@gmail.com\"}";
        send_response(&mut stream, "200 OK", "application/json; charset=utf-8", resp);
        return;
    }

    if path == "/api/state" {
        if method == "POST" {
            let body_part = req_str.split("\r\n\r\n").nth(1).unwrap_or("{}").to_string();
            if let Ok(mut map) = store.states.lock() {
                map.insert("latest".to_string(), body_part);
            }
            let resp = format!("{{\"ok\":true,\"updatedAt\":{}}}", now_ms());
            send_response(&mut stream, "200 OK", "application/json; charset=utf-8", resp.as_bytes());
            return;
        } else {
            let saved = store
                .states
                .lock()
                .ok()
                .and_then(|m| m.get("latest").cloned())
                .unwrap_or_else(|| "null".to_string());
            let resp = format!("{{\"ok\":true,\"state\":{}}}", saved);
            send_response(&mut stream, "200 OK", "application/json; charset=utf-8", resp.as_bytes());
            return;
        }
    }

    // Fallback: serve index.html for SPA routes
    let html = load_html_file();
    send_response(&mut stream, "200 OK", "text/html; charset=utf-8", &html);
}

fn main() {
    let port = env::var("PORT")
        .or_else(|_| env::var("CHEM_PORT"))
        .unwrap_or_else(|_| "8080".to_string());
    let bind_addr = format!("0.0.0.0:{}", port);

    println!("====================================================================");
    println!("  DUMTP CHEMA+ STUDIO — RUST CLOUD & LOCAL SERVER");
    println!("  Listening on http://{}", bind_addr);
    println!("====================================================================");

    let listener = TcpListener::bind(&bind_addr).expect("Failed to bind port");
    let store = Arc::new(AppStore {
        states: Mutex::new(HashMap::new()),
        feedbacks: Mutex::new(Vec::new()),
    });

    for stream in listener.incoming() {
        if let Ok(s) = stream {
            let st = Arc::clone(&store);
            thread::spawn(move || {
                handle_client(s, st);
            });
        }
    }
}
