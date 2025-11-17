# 0. Setup infra

## 0.1. Install Jenkins

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update
kubectl create namespace jenkins
helm install jenkins jenkins/jenkins -n jenkins
```

Run the following cmd to get password

```bash
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
```

Example:
```
user: admin
password: <password-jenkins>
```
## 0.2. Install Jenkins plugin

- Go to Manage Jenkins → Plugins → Available plugins
- Install: GitHub Integration Plugin and Docker and Docker pipeline and Kubernetes CLI

### 0.3. Init repo and add remote repo

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <REMOTE_URL>
git branch --set-upstream-to=origin/main main
git push -u origin main
```

### 0.4. Download and run ngrok to expose domain of Jenkins

```bash
kubectl --namespace jenkins port-forward svc/jenkins 8080:8080
```

```bash
ngrok http 8080
```
### 0.5. Add jenkins ngrok url to Github
Access `your Github repo` => choose `Settings` => choose `Webhook` and paste above url of Jenkisn to it.

Example: `https://<id>.ngrok-free.app/github-webhook/`

Then, choose more Actions to allow push/pull code.

## 0.6. Configure Jenkins Credentials for GitHub and Docker

In Jenkins: Go to `Manage Jenkins` → `Credentials` → `Global` → `Add Credentials`
- Type: Username and Password or Personal Access Token
- Scope: Global

For Github, add username/password with id `github-token`.

For Docker, add username/password with id `dockerhub`.

## 0.7. Create a Jenkins pipeline

Choose `New item` => fill pipeline name => Choose multiple branch

Go to `Configure` => `Branch Sources` => Choose above Github credentials. => Choose `Scan Multibranch Pipeline Triggers` with 1 mins => Choose above Docker credentials.

## 0.8. Apply permissions for default Service Account of Jenkins

```bash
cd deployment
kubectl apply -f jenkins-role.yaml
```

# 1. Try to commit in folder `src`

```bash
git add <path-to-files>
git commit -m 'feat: add something'
git push
```

# 2. Test model `sentiment`

## 2.1. Install local env

```bash
uv venv
uv sync
source .venv/bin/activate
```

## 2.2. Test

```python
python tests/test_kserve.py
```
