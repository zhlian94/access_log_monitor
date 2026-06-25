
## `docs/DEMO_GUIDE.md`

```markdown
# Demo Guide

This guide explains how to demonstrate the Apache Access Log Monitor project.

The demo has two main paths:

1. Manual local deployment without GitHub Actions.
2. GitHub Actions / GitOps-style deployment.

---

## Demo Goal

The goal of this demo is to show an end-to-end SRE / DevOps workflow:
```
text
Log source
    ↓
Python monitoring application
    ↓
Prometheus metrics
    ↓
Docker image
    ↓
Kubernetes deployment
    ↓
CI/CD automation
```
---

## What This Project Shows

This project demonstrates:

- Python log processing
- Prometheus metrics exposure
- Docker containerization
- Kubernetes sidecar deployment
- shared volume pattern in Kubernetes
- GitHub Actions CI
- GitHub Actions CD
- GitHub Container Registry
- manual workflow dispatch
- local workflow testing with `act`

---

## Demo Scenario 1: Manual Local Workflow

Use this scenario to show that the project works without GitHub Actions.

---

### Step 1: Run the App Locally

Install dependencies:
```
bash
pip install -r requirements.txt
```
Create a test log file:
```
bash
touch access.log
```
Start the monitor:
```
bash
LOG_FILE_PATH=./access.log python log_processor.py
```
In another terminal, append a log line:
```
bash
echo '127.0.0.1 - - [10/Oct/2026:13:55:36 -0700] "GET /api/login HTTP/1.0" 200 2326' >> access.log
```
Check metrics:
```
bash
curl http://localhost:8000/metrics
```
Expected metric:
```
text
apache_path_requests_total
```
---

### Step 2: Build Docker Image

Build the Docker image:
```
bash
docker build -t access-log-monitor:latest .
```
Verify the image:
```
bash
docker images | grep access-log-monitor
```
---

### Step 3: Deploy to Kubernetes

Deploy using the Kubernetes manifest:
```
bash
kubectl apply -f k8s/deployment.yaml
```
Check resources:
```
bash
kubectl get deployments
kubectl get pods
kubectl get svc
```
Watch rollout:
```
bash
kubectl rollout status deployment/apache-log-monitor
```
Port-forward metrics:
```
bash
kubectl port-forward svc/apache-log-monitor-service 8000:8000
```
Check metrics:
```
bash
curl http://localhost:8000/metrics
```
Clean up:
```
bash
kubectl delete -f k8s/deployment.yaml
```
---

## Demo Scenario 2: GitHub Actions / GitOps-style Workflow

Use this scenario to show repository-driven automation.

---

### Step 1: Show Workflow Files

Show the workflow files:
```
text
.github/workflows/ci.yml
.github/workflows/cd.yml
```
Explain that CI validates and builds the image, while CD deploys the image to Kubernetes.

---

### Step 2: Trigger CI from GitHub UI

1. Open the GitHub repository.
2. Go to the **Actions** tab.
3. Select **Access Log Monitor CI**.
4. Click **Run workflow**.
5. Select the branch.
6. Start the workflow.

Expected result:
```
text
CI runs dependency install, lint, security scan, tests, Docker build, and image push.
```
---

### Step 3: Trigger CD from GitHub UI

1. Open the GitHub repository.
2. Go to the **Actions** tab.
3. Select **Access Log Monitor CD**.
4. Click **Run workflow**.
5. Select the branch.
6. Start the workflow.

Expected result:
```
text
CD pulls the image from GHCR and deploys it to Kubernetes.
```
---

## Demo Scenario 3: Local GitHub Actions with act

Use this scenario to show workflow testing locally.

Run CI:
```
bash
act workflow_dispatch \
  -W .github/workflows/ci.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Run CD:
```
bash
act workflow_dispatch \
  -W .github/workflows/cd.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Expected result:
```
text
GitHub Actions workflows run locally inside Docker.
```
---

## Demo Talking Points

Use these points while presenting:

- The application follows a sidecar pattern in Kubernetes.
- The Apache container writes logs.
- The log-monitor container reads the shared log volume.
- Metrics are exposed in Prometheus format.
- Docker provides a repeatable runtime.
- Kubernetes provides orchestration.
- GitHub Actions automates build and deployment.
- GHCR stores immutable images tagged by commit SHA.
- `workflow_dispatch` allows controlled manual deployment.
- `act` allows local testing of GitHub Actions workflows.

---

## What to Show in GitHub

Show these areas:
```
text
README.md
.github/workflows/ci.yml
.github/workflows/cd.yml
Actions tab
Packages / GHCR image
```
---

## What to Show in Kubernetes

Show these commands:
```
bash
kubectl get deployments
kubectl get pods
kubectl get svc
kubectl rollout status deployment/apache-log-monitor
kubectl logs -l app=apache-log-monitor -c log-monitor
```
---

## What to Show in Metrics

Show the metrics endpoint:
```
bash
curl http://localhost:8000/metrics
```
Point out:
```
text
apache_path_requests_total
```
---

## Cleanup

Delete Kubernetes resources:
```
bash
kubectl delete -f k8s/deployment.yaml
```
Stop local port-forwarding with:
```
text
Ctrl+C
```
Remove local Docker image if needed:
```
bash
docker rmi access-log-monitor:latest
```
---

## Summary

This demo shows a complete SRE-style workflow from log ingestion to observability and deployment automation.

The project can be explained as:
```
text
A Python Apache log monitor packaged with Docker, deployed as a Kubernetes sidecar, exposing Prometheus metrics, and automated through GitHub Actions CI/CD.
```

```


---

