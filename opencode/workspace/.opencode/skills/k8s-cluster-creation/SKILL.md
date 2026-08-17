---
name: k8s-cluster-creation
description: Use when creating or setting up Kubernetes clusters with kubeadm, minikube, kind, k3s, EKS, GKE, AKS, or other tools.
---

# Kubernetes Cluster Creation

Use this skill when setting up new Kubernetes clusters or managing existing cluster infrastructure.

## Local Development Clusters

### minikube
```bash
# Start a cluster
minikube start

# Start with specific driver
minikube start --driver=docker

# Start with specific K8s version
minikube start --kubernetes-version=v1.28.0

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Stop/delete cluster
minikube stop
minikube delete
```

### kind (Kubernetes IN Docker)
```bash
# Create cluster
kind create cluster

# Create with specific name
kind create cluster --name my-cluster

# Create with config file
kind create cluster --config kind-config.yaml

# List clusters
kind get clusters

# Delete cluster
kind delete cluster --name my-cluster
```

### k3s (Lightweight)
```bash
# Install k3s
curl -sfL https://get.k3s.io | sh -

# Install without agent (server only)
curl -sfL https://get.k3s.io | sh -s - --disable-agent

# Check installation
sudo k3s kubectl get nodes

# Uninstall k3s
/usr/local/bin/k3s-uninstall.sh
```

## Production Clusters

### kubeadm
```bash
# Initialize cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Set up kubeconfig for user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install CNI (e.g., Calico)
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/calico.yaml

# Join worker nodes
sudo kubeadm join <master-ip>:6443 --token <token> --discovery-token-ca-cert-hash <hash>

# Generate new join token
sudo kubeadm token create --print-join-command
```

### Managed Kubernetes Services

#### AWS EKS
```bash
# Create cluster with eksctl
eksctl create cluster --name my-cluster --region us-west-2

# Delete cluster
eksctl delete cluster --name my-cluster --region us-west-2
```

#### Google GKE
```bash
# Create cluster
gcloud container clusters create my-cluster --zone us-central1-a

# Get credentials
gcloud container clusters get-credentials my-cluster --zone us-central1-a

# Delete cluster
gcloud container clusters delete my-cluster --zone us-central1-a
```

#### Azure AKS
```bash
# Create cluster
az aks create --resource-group myResourceGroup --name myAKSCluster --node-count 2 --enable-addons monitoring

# Get credentials
az aks get-credentials --resource-group myResourceGroup --name myAKSCluster

# Delete cluster
az aks delete --resource-group myResourceGroup --name myAKSCluster
```

## Post-Installation Tasks

1. Verify cluster is running: `kubectl get nodes`
2. Install a CNI plugin (Calico, Flannel, Cilium)
3. Deploy metrics-server for resource monitoring
4. Set up RBAC and network policies
5. Configure storage classes
6. Install ingress controller
