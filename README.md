# Apache Access Log Monitor (SRE Demo)

This repository contains a Python-based Apache Access Log processor, designed with SRE best practices to monitor distributed web server instances

## Architecture
- **Log Processor**: A python daemon that tails `access.log`. It saves its offset in a `state.json` file to ensure no log line is processed redundantly, even if the container restarts.
- **Metrics**: It hosts a Prometheus pull server (port 8000) that exposes native `Counter` metrics showing how many times specific target paths (e.g., `/api/login`) were hit.
- **Docker**: Containerized for lightweight distribution.
- **Kubernetes**: Deployed as a **Sidecar paradigm**. The monitor container runs in the exact same Pod as the Apache container, sharing a volume where logs are written so it cleanly reads them off the disk in real-time.

## 1. Local Testing Workflow

If you want to run it directly on your machine without Docker/Kubernetes:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Touch a dummy log file
touch access.log

# 3. Start the processor
LOG_FILE_PATH=./access.log python log_processor.py

# 4. In another terminal window, simulate apache logs writing to the file!
echo '127.0.0.1 - - [10/Oct/2026:13:55:36 -0700] "GET /api/login HTTP/1.0" 200 2326' >> access.log
```
_Wait 1 minute, or check your console, and you'll see the processor pick it up naturally. You can also view `http://localhost:8000/metrics` to see the Prometheus representation!_

## 2. GitHub Workflow

Initialize a Git repository and push your project to central source control:

```bash
cd access_log_monitor
git init
git add .
git commit -m "Initial commit of SRE Log Monitor"
# Replace with your actual repo
git remote add origin https://github.com/your-org/access_log_monitor.git
git branch -M main
git push -u origin main
```

## 3. Docker Workflow

Build the container image and test it:

```bash
# Build the image locally
docker build -t access-log-monitor:latest .

# Re-tag and push it to a registry so Kubernetes can retrieve it (Example using Docker Hub)
docker tag access-log-monitor:latest yourdockerhubusername/access-log-monitor:1.0.0
docker push yourdockerhubusername/access-log-monitor:1.0.0
```

## 4. Kubernetes Orchestration

The `k8s/deployment.yaml` file sets up a simple Pod carrying both an Apache Web Server AND our Python monitor sidecar.

```bash
# (Optional) Update the image name inside k8s/deployment.yaml to match your pushed dockerhub image above

# Deploy to your Kubernetes cluster
kubectl apply -f k8s/deployment.yaml

# Verify your pods
kubectl get pods

# Expose or curl the service metrics locally to test
kubectl port-forward svc/apache-log-monitor-service 8000:8000
curl http://localhost:8000/metrics
```

## Integrating with Grafana
Because we annotated the Pod template with `prometheus.io/scrape: "true"`, if your Kubernetes cluster is running Prometheus, it will automatically begin pulling logs periodically from port 8000.
In Grafana, you can easily query this dataset to make a time-series dashboard using simply: `apache_path_requests_total`
=======
# access_log_monitor
>>>>>>> ad6be812116a909a77dc83a81b7f48f985cb3eb5
