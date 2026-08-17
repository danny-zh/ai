---
name: k8s-concepts
description: Use when explaining Kubernetes commands, resource types, architectural concepts, or when the user asks what a command does or wants to learn about K8s.
---

# Kubernetes Concepts and Commands

Use this skill when explaining Kubernetes commands, resources, or architectural concepts.

## Core Resources

### Pods
Smallest deployable unit in Kubernetes. One or more containers that share network and storage.

```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl exec -it <pod-name> -- /bin/sh
```

### Deployments
Manages replica sets and provides declarative updates for pods.

```bash
kubectl create deployment nginx --image=nginx
kubectl get deployments
kubectl rollout status deployment/nginx
kubectl rollout history deployment/nginx
kubectl rollout undo deployment/nginx
```

### Services
Exposes applications running on pods as network services.

- **ClusterIP** (default): Internal access only
- **NodePort**: Exposes on each node's IP at a static port
- **LoadBalancer**: Exposes via cloud provider load balancer
- **ExternalName**: Maps to a DNS name

```bash
kubectl expose deployment nginx --port=80 --type=LoadBalancer
kubectl get svc
```

### Namespaces
Virtual clusters within a physical cluster for resource isolation.

```bash
kubectl create namespace dev
kubectl get namespaces
kubectl config set-context --current --namespace=dev
```

### ConfigMaps and Secrets
External configuration for pods.

```bash
kubectl create configmap my-config --from-file=config.yaml
kubectl create secret generic my-secret --from-literal=password=abc123
kubectl get configmaps,secrets
```

## Architecture Components

### Control Plane
- **kube-apiserver**: Frontend for the control plane, RESTful API
- **etcd**: Distributed key-value store for cluster data
- **kube-scheduler**: Assigns pods to nodes
- **kube-controller-manager**: Runs controller loops

### Node Components
- **kubelet**: Agent ensuring containers run on nodes
- **kube-proxy**: Network proxy maintaining network rules
- **Container Runtime**: Docker, containerd, CRI-O

## Useful Commands

```bash
# Cluster info
kubectl cluster-info
kubectl version

# Resource management
kubectl top nodes
kubectl top pods

# Debugging
kubectl get events --sort-by='.lastTimestamp'
kubectl auth can-i <verb> <resource>

# Configuration
kubectl config view
kubectl config use-context <context>
```

## Concepts

### Labels and Selectors
Key-value pairs attached to resources for organization and selection.

```bash
kubectl get pods -l app=nginx
kubectl label pods <pod-name> env=dev
```

### Annotations
Non-identifying metadata for tools and libraries.

```bash
kubectl annotate pods <pod-name> description="my pod"
```

### Taints and Tolerations
Control which pods can be scheduled on which nodes.

```bash
# Taint a node
kubectl taint nodes node1 key=value:NoSchedule

# Remove taint
kubectl taint nodes node1 key=value:NoSchedule-
```

### Resource Requests and Limits
CPU and memory allocation for pods.

```yaml
resources:
  requests:
    memory: "64Mi"
    cpu: "250m"
  limits:
    memory: "128Mi"
    cpu: "500m"
```

### Init Containers
Run before main containers, used for setup tasks.

### Sidecar Containers
Run alongside main containers, providing auxiliary functionality.
