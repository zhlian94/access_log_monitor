## `Apache Access Log Monitor(demo)`



A Python-based SRE / DevOps demo project for monitoring Apache access logs, exposing Prometheus metrics, containerizing the application with Docker, deploying it to Kubernetes, and demonstrating CI/CD automation with GitHub Actions.

This project demonstrates a practical end-to-end workflow:
```
text
Apache access logs
        ↓
Python log monitor
        ↓
Prometheus metrics
        ↓
Docker image
        ↓
Kubernetes sidecar deployment
        ↓
GitHub Actions CI/CD
```
---

## Overview

The application monitors Apache-style access logs and counts requests for selected target paths such as:
```
text
/api/login
/checkout
/home
```
It exposes the request counts as Prometheus metrics on port `8000`.

The project supports two main operating modes:

1. **Manual local workflow**
   - Run the Python log monitor locally.
   - Build the Docker image locally.
   - Deploy manually to local Kubernetes.
   - Verify metrics through the Prometheus endpoint.

2. **GitHub Actions / GitOps-style workflow**
   - Run CI through GitHub Actions.
   - Install dependencies, run checks, and execute tests.
   - Build and push a Docker image to GitHub Container Registry.
   - Deploy to Kubernetes through the CD workflow.
   - Trigger workflows manually from the GitHub Actions UI or locally with `act`.

---

## Key Features

- Python-based Apache access log monitor
- Prometheus metrics endpoint
- Dockerized runtime
- Kubernetes deployment
- Sidecar-style container pattern
- Shared volume between Apache and log-monitor containers
- GitHub Actions CI workflow
- GitHub Actions CD workflow
- Manual workflow trigger with `workflow_dispatch`
- Local GitHub Actions testing with `act`
- Basic pytest test integration
- Local Kubernetes demo support with Docker Desktop Kubernetes

---

## Architecture

The Kubernetes deployment uses a sidecar-style pattern.
```
text
Kubernetes Pod
├── apache-server container
│   └── writes Apache access logs
│
├── log-monitor container
│   ├── reads shared Apache log volume
│   ├── tracks processed file offset
│   └── exposes Prometheus metrics on port 8000
│
└── shared emptyDir volume
```
The log-monitor container reads new Apache log entries from the shared volume, tracks progress using a state file, and increments Prometheus counters for configured target paths.

---

## Repository Structure
```
text
access_log_monitor/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── README.md
├── k8s/
│   └── deployment.yaml
├── tests/
│   └── test_dummy.py
├── Dockerfile
├── log_processor.py
├── requirements.txt
├── README.md
├── SETUP_GUIDE.md
├── workflow_dispatch.json
└── act-secrets.env
```
---

## Quick Start: Run Locally with Python

Install dependencies:
```
bash
pip install -r requirements.txt
```
Create a local Apache-style access log file:
```
bash
touch access.log
```
Start the monitor:
```
bash
LOG_FILE_PATH=./access.log python log_processor.py
```
In another terminal, simulate an Apache access log entry:
```
bash
echo '127.0.0.1 - - [10/Oct/2026:13:55:36 -0700] "GET /api/login HTTP/1.0" 200 2326' >> access.log
```
Check the Prometheus metrics endpoint:
```
bash
curl http://localhost:8000/metrics
```
Expected metric name:
```
text
apache_path_requests_total
```
---

## Run Tests

Run the test suite locally:
```
bash
python -m pip install pytest
pytest
```
The GitHub Actions CI workflow also runs tests automatically.

---

## Docker Workflow

Build the Docker image locally:
```
bash
docker build -t access-log-monitor:latest .
```
Optional registry push example:
```
bash
docker tag access-log-monitor:latest yourdockerhubusername/access-log-monitor:1.0.0
docker push yourdockerhubusername/access-log-monitor:1.0.0
```
When using the GitHub Actions CI workflow, the image is pushed to GitHub Container Registry using the commit SHA as the tag:
```
text
ghcr.io/<owner>/<repo>:<commit-sha>
```
---

## Kubernetes Workflow

The Kubernetes manifest is located at:
```
text
k8s/deployment.yaml
```
Deploy manually:
```
bash
kubectl apply -f k8s/deployment.yaml
```
Check the deployment:
```
bash
kubectl get deployments
kubectl get pods
kubectl get svc
```
Watch rollout status:
```
bash
kubectl rollout status deployment/apache-log-monitor
```
Port-forward the metrics service:
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

## GitHub Actions CI/CD

This project includes two GitHub Actions workflows.

### CI Workflow

Workflow file:
```
text
.github/workflows/ci.yml
```
Workflow name:
```
text
Access Log Monitor CI
```
The CI workflow performs:

- repository checkout
- Python setup
- dependency installation
- flake8 linting
- Bandit security scanning
- pytest execution
- Docker image build
- Docker image push to GitHub Container Registry

The CI workflow runs on:

- push to `main`
- pull request to `main`
- manual `workflow_dispatch`

### CD Workflow

Workflow file:
```
text
.github/workflows/cd.yml
```
Workflow name:
```
text
Access Log Monitor CD
```
The CD workflow performs:

- repository checkout
- GitHub Container Registry login
- Docker image pull
- kubectl setup
- Kubernetes context setup
- Kubernetes manifest image patching
- Kubernetes deployment apply
- rollout verification

The CD workflow runs on:

- CI workflow completion
- manual `workflow_dispatch`

---

## GitOps-style Demo

This project supports a simple GitOps-style demo using GitHub Actions.

The demo can be run from the GitHub Actions UI or locally with `act`.

### Option 1: Trigger from GitHub UI

1. Open the GitHub repository.
2. Go to the **Actions** tab.
3. Select **Access Log Monitor CI**.
4. Click **Run workflow**.
5. Select the target branch.
6. Run the workflow.
7. After CI completes, select **Access Log Monitor CD**.
8. Click **Run workflow** to deploy.

This demonstrates a repository-driven deployment flow where the build and deployment are controlled by GitHub Actions.

### Option 2: Run Locally with act

Run the CI workflow locally:
```
bash
act workflow_dispatch \
  -W .github/workflows/ci.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Run the CD workflow locally:
```
bash
act workflow_dispatch \
  -W .github/workflows/cd.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Docker must be running before using `act`.

---

## Required Secrets

For GitHub Actions deployment, configure repository secrets under:
```
text
Settings -> Secrets and variables -> Actions
```
Required or recommended secrets:
```
text
KUBE_CONFIG
```
`GITHUB_TOKEN` is automatically provided by GitHub Actions and is used for GitHub Container Registry authentication.

For local `act` testing, use:
```
text
act-secrets.env
```
Example:
```
bash
GITHUB_TOKEN=your_github_token
KUBE_CONFIG=your_kubeconfig_content
```
---

## Expected CI/CD Flow
```
text
Developer pushes code
        ↓
GitHub Actions CI starts
        ↓
Install dependencies
        ↓
Run lint, security scan, and tests
        ↓
Build Docker image
        ↓
Push image to GitHub Container Registry
        ↓
GitHub Actions CD starts
        ↓
Pull image from registry
        ↓
Patch Kubernetes manifest image tag
        ↓
Apply Kubernetes deployment
        ↓
Verify rollout
        ↓
Metrics available on port 8000
```
---

## Observability

The application exposes Prometheus metrics at:
```
text
http://localhost:8000/metrics
```
Primary metric:
```
text
apache_path_requests_total
```
If Prometheus is running in the Kubernetes cluster, the Pod annotations allow Prometheus to discover and scrape the metrics endpoint.

The metric can be used in Grafana to visualize traffic volume by monitored path.

---

## Documentation

Additional documentation:

- [Setup Guide](SETUP_GUIDE.md) — detailed local setup, Docker, Kubernetes, and troubleshooting.
- [Workflow Guide](.github/workflows/README.md) — GitHub Actions CI/CD and GitOps demo details.

---

## Skills Demonstrated

This project demonstrates practical experience with:

- Python application development
- Apache access log processing
- Prometheus metrics
- Docker image creation
- Kubernetes deployment
- Kubernetes sidecar pattern
- GitHub Actions CI/CD
- [Demo Guide](docs/DEMO_GUIDE.md)
- [GitHub Actions GitOps Guide](docs/GITHUB_ACTIONS_GITOPS.md)
- GitHub Container Registry
- Manual workflow dispatch
- Local GitHub Actions testing with `act`
- SRE-style observability workflow

---

## Production Considerations

This repository is intended as a local demo and learning project.

For production usage, recommended improvements include:

- stronger application test coverage
- stricter CI quality gates
- non-root container user
- pinned GitHub Action versions
- pinned Kubernetes tooling versions
- externalized runtime configuration
- dedicated secret management
- image vulnerability scanning
- production-grade Prometheus and Grafana setup
- deployment promotion across environments
- rollback strategy
- resource requests and limits review
```


---


