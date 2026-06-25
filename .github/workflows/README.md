## `.github/workflows/README.md`

```markdown
# GitHub Actions Workflow Guide

This folder contains the GitHub Actions workflows for the Apache Access Log Monitor project.

The workflows demonstrate a simple CI/CD and GitOps-style deployment flow.

---

## Workflow Files
```
text
.github/workflows/
├── ci.yml
├── cd.yml
└── README.md
```
---

## CI Workflow

Workflow file:
```
text
ci.yml
```
Workflow name:
```
text
Access Log Monitor CI
```
---

## CI Purpose

The CI workflow validates the application and builds the container image.

It performs:

- repository checkout
- Python setup
- dependency installation
- flake8 linting
- Bandit security scanning
- pytest test execution
- Docker image build
- Docker image push to GitHub Container Registry

---

## CI Triggers

The CI workflow runs on:
```
text
push to main
pull request to main
manual workflow_dispatch
```
This allows the workflow to run automatically on code changes and manually from the GitHub Actions UI.

---

## CI Image Output

The Docker image is pushed to GitHub Container Registry using this tag format:
```
text
ghcr.io/<owner>/<repo>:<commit-sha>
```
Using the commit SHA creates a traceable image version for each build.

---

## CD Workflow

Workflow file:
```
text
cd.yml
```
Workflow name:
```
text
Access Log Monitor CD
```
---

## CD Purpose

The CD workflow deploys the built image to Kubernetes.

It performs:

- repository checkout
- GitHub Container Registry login
- Docker image pull
- kubectl setup
- Kubernetes context setup
- Kubernetes manifest image patching
- Kubernetes deployment apply
- rollout status verification

---

## CD Triggers

The CD workflow runs on:
```
text
CI workflow completion
manual workflow_dispatch
```
The manual trigger is useful for controlled demo deployment.

---

## GitOps-style Demo Flow
```
text
Code pushed to GitHub
        ↓
CI workflow starts
        ↓
Dependencies installed
        ↓
Lint, security scan, and tests run
        ↓
Docker image built
        ↓
Image pushed to GHCR
        ↓
CD workflow starts
        ↓
Image pulled from GHCR
        ↓
Kubernetes manifest patched
        ↓
Deployment applied
        ↓
Rollout verified
```
---

## Running from GitHub UI

To manually trigger the CI workflow:

1. Open the repository on GitHub.
2. Go to the **Actions** tab.
3. Select **Access Log Monitor CI**.
4. Click **Run workflow**.
5. Select the branch.
6. Click **Run workflow**.

To manually trigger the CD workflow:

1. Open the repository on GitHub.
2. Go to the **Actions** tab.
3. Select **Access Log Monitor CD**.
4. Click **Run workflow**.
5. Select the branch.
6. Click **Run workflow**.

---

## Running Locally with act

The workflows can also be tested locally with `act`.

Run CI locally:
```
bash
act workflow_dispatch \
  -W .github/workflows/ci.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Run CD locally:
```
bash
act workflow_dispatch \
  -W .github/workflows/cd.yml \
  -e workflow_dispatch.json \
  --secret-file act-secrets.env
```
Docker must be running before executing `act`.

---

## Required Files for act

The local `act` demo uses:
```
text
workflow_dispatch.json
act-secrets.env
```
Example event payload file:
```
text
workflow_dispatch.json
```
Example secrets file:
```
text
act-secrets.env
```
---

## Required Secrets

For GitHub-hosted Actions:
```
text
KUBE_CONFIG
```
`GITHUB_TOKEN` is automatically provided by GitHub Actions.

For local `act` usage:
```
text
GITHUB_TOKEN=your_github_token
KUBE_CONFIG=your_kubeconfig_content
```
---

## Demo Scenarios

### Scenario 1: CI Only

Use this to demonstrate validation and image build.

Expected result:
```
text
CI completes successfully
Docker image is pushed to GHCR
```
### Scenario 2: CI + CD

Use this to demonstrate full deployment.

Expected result:
```
text
CI completes successfully
CD pulls image
Kubernetes deployment is updated
Rollout completes
```
### Scenario 3: Local act Run

Use this to demonstrate that GitHub Actions workflows can be tested locally before pushing.

Expected result:
```
text
act runs the workflow locally using Docker
```
---

## Notes

This workflow setup is intended for a local demo environment.

For production usage, recommended improvements include:

- fail CI on lint errors
- fail CI on test failures
- fail CI on high-severity security findings
- add image vulnerability scanning
- use environment-specific approvals
- separate dev, staging, and production deployments
- use deployment protection rules
- avoid deploying directly from local kubeconfig where possible
```


---
