import os

bind = f"0.0.0.0:{os.environ.get('PORT', 8000)}"
workers = 1  # Model memory usage için tek worker
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5 minute timeout for image processing
keepalive = 5
max_requests = 100
max_requests_jitter = 10
preload_app = True
