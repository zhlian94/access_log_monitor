## `GITHUB_ACTIONS_GITOPS.md`

```markdown
# GitHub Actions and GitOps Demo

This document explains the GitHub Actions and GitOps-style automation used by the Apache Access Log Monitor project.

---

## Purpose

The purpose of this setup is to demonstrate a repository-driven deployment workflow.

Instead of manually building and deploying every change, the repository contains automation that can:

1. validate the application
2. run tests
3. build a Docker image
4. push the image to GitHub Container Registry
5. deploy the image to Kubernetes

---

## Workflow Overview
```
text
Developer commits code
        ↓
Push or manual workflow trigger
        ↓
CI workflow runs
        ↓
Docker image is built
        ↓
Image is pushed to GHCR
        ↓
CD workflow runs
        ↓
Kubernetes deployment is updated
```
---

## CI Workflow

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
---

## CI Responsibilities

The CI workflow is responsible for validation and image publishing.

It performs:

- checkout repository
- set up Python
- install dependencies
- run flake8 linting
- run Bandit security scan
- run pytest tests
- login to GitHub Container Registry
- build Docker image
- push Docker image

---

## CI Triggers

The CI workflow runs on:
```
text
push to main
pull request to main
workflow_dispatch
```
The `workflow_dispatch` trigger allows the workflow to be started manually from the GitHub Actions UI.

---

## Docker Image Tagging

The CI workflow publishes the Docker image using the Git commit SHA.

Image format:
```
text
ghcr.io/<owner>/<repo>:<commit-sha>
```
This makes each image traceable to a specific commit.

---

## CD Workflow

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
---

## CD Responsibilities

The CD workflow is responsible for deployment.

It performs:

- checkout repository
- login to GitHub Container Registry
- pull the Docker image
- set up kubectl
- configure Kubernetes context
- update the Kubernetes manifest with the image tag
- apply the Kubernetes manifest
- wait for rollout completion

---

## CD Triggers

The CD workflow runs on:
```
text
workflow_run
workflow_dispatch
```
The `workflow_run` trigger allows CD to run after CI completes.

The `workflow_dispatch` trigger allows manual deployment from GitHub UI.

---

## Required Secret

The CD workflow requires Kubernetes access.

Add this repository secret:
```
text
KUBE_CONFIG
```
Location:
```
text
Repository Settings
    ↓
Secrets and variables
    ↓
Actions
    ↓
New repository secret
```
---

## GitHub Token

GitHub Actions automatically provides:
```
text
GITHUB_TOKEN
```
This token is used for GitHub Container Registry authentication.

---

## Manual GitOps-style Operation

To manually run CI:

1. Open the repository.
2. Go to **Actions**.
3. Select **Access Log Monitor CI**.
4. Click **Run workflow**.
5. Select the branch.
6. Run it.

To manually run CD:

1. Open the repository.
2. Go to **Actions**.
3. Select **Access Log Monitor CD**.
4. Click **Run workflow**.
5. Select the branch.
6. Run it.

---

## Local Testing with act

The workflows can be tested locally with `act`.

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
---

## Required Local Files

Local `act` execution uses:
```
text
workflow_dispatch.json
act-secrets.env
```
---

## Example act Secrets

Example:
```
bash
GITHUB_TOKEN=your_github_token
KUBE_CONFIG=your_kubeconfig_content
```
Do not commit real secrets to a public repository.

---

## Security Notes

Before making the repository public:

- remove real tokens
- remove real kubeconfig values
- remove sensitive registry credentials
- confirm `.gitignore` excludes secret files
- rotate any secrets that were previously committed
- use GitHub repository secrets instead of plain files

---

## Demo Explanation

This setup is not a full enterprise GitOps platform, but it demonstrates the same core idea:
```
text
Git repository controls build and deployment behavior.
```
The workflow files define how the application is built and deployed.

The Kubernetes manifest defines the desired runtime state.

GitHub Actions acts as the automation engine.

---

## Production Improvements

For production usage, consider:

- environment approvals
- separate dev/stage/prod workflows
- branch protection rules
- required CI checks
- stricter test gates
- image vulnerability scanning
- signed container images
- deployment rollback strategy
- Argo CD or Flux for continuous reconciliation
- dedicated secret management
```

