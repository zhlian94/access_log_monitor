# Local Development & Deployment Guide



## Step 1: Create Private GitHub Repository

1. **Go to GitHub** → Click **New** (in Repositories section)
2. **Name:** `access-log-monitor`
3. **Privacy:** Select **Private**
4. **Do NOT initialize** with README, .gitignore, or license (we have these locally)
5. Click **Create repository**

Copy the HTTPS URL (e.g., `https://github.com/YOUR_USERNAME/access-log-monitor.git`)

---

## Step 2: Initialize Git & Push to GitHub

Run these commands in PowerShell from `C:\docker\access_log_monitor`:

```powershell
# Initialize git repo
git init

# Configure git (use your GitHub email/username)
git config user.email "your-email@example.com"
git config user.name "Your Name"

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: SRE Log Monitor with Docker & K8s support"

# Add remote (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/access-log-monitor.git

# Rename branch to main (GitHub default)
git branch -M main

# Push to GitHub
git push -u origin main
```

If you see a login prompt, use:
- **Username:** Your GitHub username
- **Password:** A [Personal Access Token](https://github.com/settings/tokens) (not your password)
  - Generate token with `repo` scope at GitHub → Settings → Developer Settings → Personal Access Tokens

---

## Step 3: Set Up Local Development Environment

### 3a. Install Dependencies Locally (Optional)

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Test locally (creates dummy log file)
$null = New-Item -Name "access.log" -ItemType File -Force
$env:LOG_FILE_PATH = ".\access.log"
python log_processor.py
```

Leave this running, then in another PowerShell terminal:
```powershell
# Simulate Apache log entries
$logEntry = '127.0.0.1 - - [10/Oct/2026:13:55:36 -0700] "GET /api/login HTTP/1.0" 200 2326'
Add-Content -Path "access.log" -Value $logEntry

# Check metrics
Start-Process "http://localhost:8000/metrics"
```

---

## Step 4: Build & Run Docker Image Locally

### 4a. Build the Docker Image

```powershell
cd C:\docker\access_log_monitor

# Build image locally (tag it for later Docker Hub push)
docker build -t access-log-monitor:latest .

# Verify it built successfully
docker images | Select-String "access-log-monitor"
```

### 4b. Run the Container Locally

```powershell
# Create a persistent volume for state/logs
docker volume create log-monitor-data

# Run the container
docker run `
  --name log-monitor-local `
  -p 8000:8000 `
  -v log-monitor-data:/app/data `
  -e LOG_FILE_PATH=/var/log/apache2/access.log `
  access-log-monitor:latest

# Check metrics in browser
Start-Process "http://localhost:8000/metrics"

# Stop when done
docker stop log-monitor-local
docker rm log-monitor-local
```

---

## Step 5: Push to Docker Hub (Optional - for K8s)

### 5a. Create Docker Hub Account & Repository

1. Go to [Docker Hub](https://hub.docker.com/)
2. Sign up or log in
3. Create a repository: **access-log-monitor** (can be private)

### 5b. Push Your Image

```powershell
# Log in to Docker Hub
docker login

# Tag image with your Docker Hub username
$dockerUsername = "your-dockerhub-username"
docker tag access-log-monitor:latest $dockerUsername/access-log-monitor:latest

# Push to Docker Hub
docker push $dockerUsername/access-log-monitor:latest

# Verify on Docker Hub website
```

---

## Step 6: Set Up Kubernetes Locally (Docker Desktop)

### 6a. Enable Kubernetes in Docker Desktop

1. Open **Docker Desktop** → Settings
2. Go to **Kubernetes** tab
3. Check **Enable Kubernetes**
4. Click **Apply & Restart** (wait 2-3 minutes)
5. Verify: `kubectl cluster-info`

### 6b. Update Deployment YAML

Edit `k8s/deployment.yaml` and replace the image reference:

```yaml
# Change this line:
image: access-log-monitor:latest  
imagePullPolicy: IfNotPresent

# To:
image: YOUR_DOCKERHUB_USERNAME/access-log-monitor:latest
imagePullPolicy: IfNotPresent  # for local, or Always for Docker Hub
```

Or if testing locally without Docker Hub:
```yaml
imagePullPolicy: IfNotPresent  # Use locally built image
```

### 6c. Deploy to Local Kubernetes

```powershell
# Navigate to project root
cd C:\docker\access_log_monitor

# Apply the deployment
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get svc

# View logs from the log-monitor sidecar
kubectl logs -l app=apache-log-monitor -c log-monitor -f

# Port-forward to access metrics locally
kubectl port-forward pod/apache-log-monitor-xxxxx 8000:8000

# Open metrics
Start-Process "http://localhost:8000/metrics"

# Clean up when done
kubectl delete -f k8s/deployment.yaml
```

---

## Step 7: GitHub CI/CD Setup (Optional)

Create `.github/workflows/docker-build.yml` to auto-build on push:

```yaml
name: Build & Push Docker Image

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          push: true
          tags: ${{ secrets.DOCKER_USERNAME }}/access-log-monitor:latest
```

Then add secrets to GitHub:
- Go to **Settings** → **Secrets** → **New repository secret**
- Add `DOCKER_USERNAME` and `DOCKER_PASSWORD`

---

## Workflow Summary

```
Local Development
    ↓
    Commit & Push to GitHub (Private Repo)
    ↓
    Build Docker Image Locally
    ↓
    Push to Docker Hub (or keep private)
    ↓
    Deploy to Local Kubernetes (Docker Desktop)
    ↓
    Verify Metrics & Logs
```

---

## Troubleshooting

### Git authentication fails
- Use a Personal Access Token instead of password
- Generate at: https://github.com/settings/tokens
- Scope: `repo` (full control of private repositories)

### Docker build fails
```powershell
docker build -t access-log-monitor:latest --no-cache .
```

### Kubernetes pod won't start
```powershell
kubectl describe pod apache-log-monitor-xxxxx
kubectl logs apache-log-monitor-xxxxx -c log-monitor
```

### Metrics not showing
- Wait 1 minute for first log entry to be processed
- Check: `kubectl port-forward ... 8000:8000` and visit `http://localhost:8000/metrics`

---

## Next Steps

1. ✅ Initialize GitHub repo
2. ✅ Push code to GitHub
3. ✅ Test locally with Docker
4. ✅ Test with local Kubernetes
5. 📊 Set up Prometheus to scrape metrics
6. 📈 Add Grafana dashboard
7. 🚀 Deploy to production K8s cluster
