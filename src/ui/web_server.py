"""
Embedded Lightweight HTTP Web Server & REST API
Serves real-time telemetry metrics and web dashboard using Python's standard library.
"""

import json
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class TelemetryHandler(BaseHTTPRequestHandler):
    cpu_monitor = None
    mem_monitor = None
    disk_monitor = None
    net_monitor = None
    proc_monitor = None
    alert_engine = None
    static_dir = os.path.join(os.path.dirname(__file__), "..", "web_static")

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file(os.path.join(self.static_dir, "index.html"), "text/html")
        elif self.path == "/api/metrics":
            self.serve_metrics()
        elif self.path == "/api/processes":
            self.serve_processes()
        elif self.path == "/api/alerts":
            self.serve_alerts()
        else:
            self.send_error(404, "Endpoint not found")

    def serve_file(self, filepath, content_type):
        try:
            with open(filepath, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Error reading file: {e}")

    def serve_metrics(self):
        try:
            cpu_m = self.cpu_monitor.get_metrics()
            mem_m = self.mem_monitor.get_metrics()
            disk_m = self.disk_monitor.get_metrics()
            net_m = self.net_monitor.get_metrics()
            procs = self.proc_monitor.get_top_processes(limit=10, sort_by="cpu")
            alerts = self.alert_engine.evaluate(cpu_m, mem_m, disk_m, net_m)

            payload = {
                "cpu": cpu_m,
                "memory": mem_m,
                "disk": disk_m,
                "network": net_m,
                "processes": procs,
                "alerts": alerts,
                "timestamp": cpu_m.get("timestamp")
            }

            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, f"Error generating metrics: {e}")

    def serve_processes(self):
        try:
            procs = self.proc_monitor.get_top_processes(limit=25, sort_by="cpu")
            body = json.dumps(procs).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, f"Error generating process list: {e}")

    def serve_alerts(self):
        try:
            body = json.dumps(self.alert_engine.alert_history).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as e:
            self.send_error(500, f"Error retrieving alerts: {e}")

    def log_message(self, format, *args):
        # Suppress verbose request logs to keep terminal clean
        return

def run_web_server(port, cpu_m, mem_m, disk_m, net_m, proc_m, alert_eng):
    TelemetryHandler.cpu_monitor = cpu_m
    TelemetryHandler.mem_monitor = mem_m
    TelemetryHandler.disk_monitor = disk_m
    TelemetryHandler.net_monitor = net_m
    TelemetryHandler.proc_monitor = proc_m
    TelemetryHandler.alert_engine = alert_eng

    server = None
    candidates = [port, 5000, 5050, 8080, 8888, 9000]
    actual_port = port
    for p in candidates:
        try:
            server = HTTPServer(("127.0.0.1", p), TelemetryHandler)
            actual_port = p
            break
        except Exception:
            continue

    if not server:
        server = HTTPServer(("0.0.0.0", port), TelemetryHandler)
        actual_port = port

    print(f"\n[+] Linux Pulse Web Server actively listening at: http://localhost:{actual_port}/")
    print(f"[+] REST API available at: http://localhost:{actual_port}/api/metrics")
    print(f"[+] Press Ctrl+C to terminate.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down web server gracefully...")
        server.server_close()

