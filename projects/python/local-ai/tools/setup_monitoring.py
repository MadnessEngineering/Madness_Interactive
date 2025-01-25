#!/usr/bin/env python3.11
"""
Setup script for model monitoring tools.
This tool helps set up monitoring for model performance, usage, and costs.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from common import setup_env  # Import the common setup_env function
from typing import List, Dict

def check_requirements():
    """Check if required packages are installed."""
    required = ['prometheus_client', 'grafana_client', 'psutil', 'python-dotenv', 'pandas']
    missing = []
    
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

def setup_env_monitoring():
    """Setup environment for monitoring."""
    env_string = """# Monitoring Settings
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
METRICS_PORT=8080
COLLECT_INTERVAL=15
RETENTION_DAYS=30
COST_PER_TOKEN=0.000001
ALERT_THRESHOLD_CPU=80
ALERT_THRESHOLD_MEMORY=85
ALERT_THRESHOLD_LATENCY=2000
"""
    setup_env(env_string)  # Call the common setup_env function

def setup_monitoring():
    """Setup the monitoring system files."""
    # Create necessary directories
    for dir_path in ["monitoring/exporters", "monitoring/dashboards", "monitoring/config"]:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    # Create metrics exporter
    with open("monitoring/exporters/model_metrics.py", "w") as f:
        f.write("""#!/usr/bin/env python3.11
import json
import os
import time
from datetime import datetime
import psutil
from prometheus_client import start_http_server, Counter, Gauge, Histogram
from dotenv import load_dotenv

load_dotenv()

# Initialize metrics
REQUEST_COUNT = Counter('model_requests_total', 'Total model requests', ['model', 'status'])
TOKEN_COUNT = Counter('model_tokens_total', 'Total tokens processed', ['model', 'type'])
RESPONSE_TIME = Histogram('model_response_seconds', 'Response time in seconds', ['model'])
MEMORY_USAGE = Gauge('model_memory_bytes', 'Memory usage in bytes', ['model'])
CPU_USAGE = Gauge('model_cpu_percent', 'CPU usage percentage', ['model'])
COST_COUNTER = Counter('model_cost_total', 'Total cost in USD', ['model'])

class ModelMetricsCollector:
    def __init__(self):
        self.collect_interval = int(os.getenv("COLLECT_INTERVAL", 15))
    
    def collect_system_metrics(self):
        \"\"\"Collect system metrics for running models.\"\"\"
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'ollama' in proc.info['name']:
                    # Get model name from command line
                    cmdline = proc.info['cmdline']
                    model_name = next((arg for arg in cmdline if arg in ['codellama', 'llama2', 'mistral']), 'unknown')
                    
                    # Collect metrics
                    process = psutil.Process(proc.info['pid'])
                    memory_info = process.memory_info()
                    
                    MEMORY_USAGE.labels(model=model_name).set(memory_info.rss)
                    CPU_USAGE.labels(model=model_name).set(process.cpu_percent())
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    
    def run(self):
        \"\"\"Start metrics collection.\"\"\"
        port = int(os.getenv("METRICS_PORT", 8080))
        start_http_server(port)
        print(f"Serving metrics on :{port}")
        
        while True:
            self.collect_system_metrics()
            time.sleep(self.collect_interval)

if __name__ == "__main__":
    collector = ModelMetricsCollector()
    collector.run()
""")
    
    # Create Prometheus config
    with open("monitoring/config/prometheus.yml", "w") as f:
        f.write("""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'model_metrics'
    static_configs:
      - targets: ['localhost:8080']
""")
    
    # Create Grafana dashboard
    with open("monitoring/dashboards/model_dashboard.json", "w") as f:
        f.write("""{
  "annotations": {
    "list": []
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 0,
  "links": [],
  "liveNow": false,
  "panels": [
    {
      "datasource": {
        "type": "prometheus",
        "uid": "prometheus"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "mode": "palette-classic"
          },
          "custom": {
            "axisCenteredZero": false,
            "axisColorMode": "text",
            "axisLabel": "",
            "axisPlacement": "auto",
            "barAlignment": 0,
            "drawStyle": "line",
            "fillOpacity": 10,
            "gradientMode": "none",
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "lineInterpolation": "linear",
            "lineWidth": 1,
            "pointSize": 5,
            "scaleDistribution": {
              "type": "linear"
            },
            "showPoints": "never",
            "spanNulls": false,
            "stacking": {
              "group": "A",
              "mode": "none"
            },
            "thresholdsStyle": {
              "mode": "off"
            }
          },
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green",
                "value": null
              }
            ]
          },
          "unit": "short"
        },
        "overrides": []
      },
      "gridPos": {
        "h": 8,
        "w": 12,
        "x": 0,
        "y": 0
      },
      "id": 1,
      "options": {
        "legend": {
          "calcs": [],
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "tooltip": {
          "mode": "single",
          "sort": "none"
        }
      },
      "targets": [
        {
          "datasource": {
            "type": "prometheus",
            "uid": "prometheus"
          },
          "expr": "rate(model_requests_total[5m])",
          "refId": "A"
        }
      ],
      "title": "Request Rate",
      "type": "timeseries"
    }
  ],
  "refresh": "5s",
  "schemaVersion": 38,
  "style": "dark",
  "tags": [],
  "templating": {
    "list": []
  },
  "time": {
    "from": "now-1h",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "",
  "title": "Model Monitoring",
  "version": 0,
  "weekStart": ""
}""")
    
    # Create Docker Compose file
    with open("docker-compose.yml", "w") as f:
        f.write("""version: '3'
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/config/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    volumes:
      - ./monitoring/dashboards:/var/lib/grafana/dashboards
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_DASHBOARDS_DEFAULT_HOME_DASHBOARD_PATH=/var/lib/grafana/dashboards/model_dashboard.json

volumes:
  prometheus_data:
  grafana_data:
""")

def main():
    parser = argparse.ArgumentParser(description="Setup model monitoring tools")
    args = parser.parse_args()
    
    print("Setting up monitoring tools...")
    
    # Check and install requirements
    check_requirements()
    
    # Setup environment
    setup_env_monitoring()
    
    # Setup monitoring
    setup_monitoring()
    
    print("""
Setup complete! To start monitoring:

1. Start monitoring stack:
   docker-compose up -d

2. Start metrics exporter:
   python monitoring/exporters/model_metrics.py

The system provides:
- Real-time metrics collection
- System resource monitoring
- Request/response tracking
- Cost tracking
- Performance metrics

Metrics Available:
- Request count by model/status
- Token usage by model
- Response times
- Memory usage
- CPU usage
- Cost tracking

Access Points:
- Metrics: http://localhost:8080
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
  * Default credentials: admin/admin
  * Pre-configured dashboard included

Features:
- Automatic metric collection
- Resource usage tracking
- Cost estimation
- Alert configuration
- Historical data retention

Tips:
- Adjust collection interval in .env
- Configure alert thresholds
- Monitor resource usage
- Check cost tracking accuracy
- Use Grafana for visualization
""")

if __name__ == "__main__":
    main() 
