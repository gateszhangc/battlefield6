# Battlefield 6 Launch Runbook

## Deployment Mapping

- GitHub repository: `gateszhangc/battlefield6`
- Git branch: `main`
- Dokploy project: `n/a` (this site deploys through ArgoCD)
- Image repository: `registry.144.91.77.245.sslip.io/battlefield6`
- K8s manifest path: `deploy/k8s/overlays/prod`
- Argo CD application: `battlefield6`
- Primary domain: `battlefield6.lol`
- Route: `gateszhangc/battlefield6 -> main -> registry.144.91.77.245.sslip.io/battlefield6 -> deploy/k8s/overlays/prod -> ArgoCD battlefield6`

## Runtime Chain

1. Push to `main`.
2. GitHub Actions runs Playwright browser tests.
3. GitHub Actions submits a Kaniko build job into Kubernetes namespace `webapp-build`.
4. The build job pushes `registry.144.91.77.245.sslip.io/battlefield6:<git-sha>`.
5. GitHub Actions updates `deploy/k8s/overlays/prod/kustomization.yaml` `newTag`.
6. Argo CD auto-syncs `battlefield6` into namespace `battlefield6`.

## Required Platform State

- Build namespace: `webapp-build`
- Build trigger service account: `github-build-trigger`
- Build service account: `kaniko-builder`
- Registry secret: `webapp-registry-push`
- Ingress class: `nginx`
- Cluster issuer: `letsencrypt-prod`
- GitHub Actions secret: `KUBE_CONFIG_DATA` (base64-encoded kubeconfig for `webapp-build` release jobs)

## One-Time Argo CD Bootstrap

Apply the app resources from this repository after the GitHub repo exists:

```bash
kubectl apply -f deploy/argocd/appproject.yaml
kubectl apply -f deploy/argocd/application.yaml
```

## Cloudflare And GSC

- Delegate `battlefield6.lol` nameservers from Porkbun to Cloudflare.
- Create apex `A` record for `battlefield6.lol` -> `89.167.61.228`.
- Create `www` `CNAME` -> `battlefield6.lol`.
- Keep GA4 and Clarity disabled for this project.
- Verify `sc-domain:battlefield6.lol` in Google Search Console.
- Submit `https://battlefield6.lol/sitemap.xml`.

## Verification

Run locally before shipping:

```bash
npm ci
npm test
```

Validate live after Argo sync:

```bash
curl -I https://battlefield6.lol/
curl https://battlefield6.lol/healthz
curl https://battlefield6.lol/robots.txt
curl https://battlefield6.lol/sitemap.xml
argocd app get battlefield6
```
