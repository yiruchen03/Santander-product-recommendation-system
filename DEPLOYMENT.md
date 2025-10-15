# Santander 推荐系统部署指南

本文档提供完整的部署说明，帮助你将 Santander 产品推荐系统部署到生产环境。

## 目录

- [前置要求](#前置要求)
- [快速部署](#快速部署)
- [本地开发部署](#本地开发部署)
- [Docker 容器部署](#docker-容器部署)
- [云平台部署](#云平台部署)
  - [AWS 部署](#aws-部署)
  - [Google Cloud 部署](#google-cloud-部署)
  - [Azure 部署](#azure-部署)
- [性能调优](#性能调优)
- [监控和日志](#监控和日志)
- [故障排查](#故障排查)

---

## 前置要求

### 系统要求
- **操作系统**: Linux, macOS, 或 Windows (with WSL2)
- **Python**: 3.9+
- **内存**: 最少 4GB RAM (推荐 8GB+)
- **存储**: 最少 2GB 可用空间

### 软件依赖
- Docker (可选，用于容器化部署)
- Git
- curl (用于 API 测试)

### 模型文件
在部署前，必须先训练并保存模型：

1. 运行 `Santander_Recommendation_System4.ipynb`
2. 执行最后一个 cell 保存模型
3. 确认 `models/` 目录包含以下文件：
   - 24 个 `*_model.txt` 文件（每个产品一个）
   - `feature_cols.json`
   - `products.json`
   - `config.json`
   - `metrics.json`

---

## 快速部署

使用我们提供的部署脚本，一键完成部署：

```bash
# 1. 确保已训练并保存模型
# 2. 运行部署脚本
./deploy.sh
```

脚本会自动：
- ✅ 检查模型文件
- ✅ 构建 Docker 镜像
- ✅ 停止旧容器
- ✅ 启动新容器
- ✅ 执行健康检查

部署成功后，访问：
- API: http://localhost:8000
- 文档: http://localhost:8000/docs

---

## 本地开发部署

适合开发和测试环境。

### 步骤 1: 安装依赖

```bash
# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 步骤 2: 启动服务

```bash
# 开发模式（支持热重载）
uvicorn app:app --host 0.0.0.0 --port 8000 --reload

# 或使用部署脚本
./deploy.sh --local
```

### 步骤 3: 测试 API

```bash
# 打开新终端
python predict_client.py
```

---

## Docker 容器部署

适合生产环境，提供更好的隔离性和可移植性。

### 方式 A: 使用部署脚本（推荐）

```bash
./deploy.sh
```

### 方式 B: 手动部署

```bash
# 1. 构建镜像
docker build -t santander-api:latest .

# 2. 运行容器
docker run -d \
  --name santander-api \
  -p 8000:8000 \
  --restart unless-stopped \
  santander-api:latest

# 3. 查看日志
docker logs -f santander-api

# 4. 健康检查
curl http://localhost:8000/health
```

### Docker Compose 部署

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    container_name: santander-api
    ports:
      - "8000:8000"
    restart: unless-stopped
    environment:
      - MODELS_DIR=/app/models
    volumes:
      - ./models:/app/models:ro
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

启动：

```bash
docker-compose up -d
```

---

## 云平台部署

### AWS 部署

#### 选项 1: AWS ECS Fargate (推荐)

```bash
# 1. 登录 ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 2. 创建 ECR 仓库
aws ecr create-repository --repository-name santander-api

# 3. 标记并推送镜像
docker tag santander-api:latest \
  <account-id>.dkr.ecr.us-east-1.amazonaws.com/santander-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/santander-api:latest

# 4. 创建 ECS 任务定义和服务（通过 AWS Console 或 CLI）
```

**ECS 任务定义示例** (`task-definition.json`):

```json
{
  "family": "santander-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "santander-api",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/santander-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

#### 选项 2: AWS EC2

```bash
# 1. 启动 EC2 实例（Amazon Linux 2）
# 2. SSH 连接到实例
ssh -i your-key.pem ec2-user@<instance-ip>

# 3. 安装 Docker
sudo yum update -y
sudo yum install docker -y
sudo service docker start
sudo usermod -a -G docker ec2-user

# 4. 拉取代码并部署
git clone <your-repo>
cd santander-product-recommendation
./deploy.sh
```

#### 选项 3: AWS Lambda + API Gateway

对于无服务器部署，可以使用 Mangum 适配器：

```bash
pip install mangum

# 修改 app.py 添加 Lambda 处理器
from mangum import Mangum
handler = Mangum(app)
```

---

### Google Cloud 部署

#### Cloud Run (推荐)

```bash
# 1. 设置项目
gcloud config set project <project-id>

# 2. 构建并推送镜像
gcloud builds submit --tag gcr.io/<project-id>/santander-api

# 3. 部署到 Cloud Run
gcloud run deploy santander-api \
  --image gcr.io/<project-id>/santander-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --port 8000

# 4. 获取服务 URL
gcloud run services describe santander-api --region us-central1 --format 'value(status.url)'
```

#### GKE (Kubernetes)

```bash
# 1. 创建集群
gcloud container clusters create santander-cluster \
  --num-nodes=2 \
  --machine-type=n1-standard-2

# 2. 部署应用
kubectl create deployment santander-api --image=gcr.io/<project-id>/santander-api
kubectl expose deployment santander-api --type=LoadBalancer --port=80 --target-port=8000

# 3. 获取外部 IP
kubectl get service santander-api
```

---

### Azure 部署

#### Azure Container Instances

```bash
# 1. 创建资源组
az group create --name santander-rg --location eastus

# 2. 创建容器注册表
az acr create --resource-group santander-rg \
  --name santanderregistry --sku Basic

# 3. 构建并推送镜像
az acr build --registry santanderregistry \
  --image santander-api:latest .

# 4. 部署容器实例
az container create \
  --resource-group santander-rg \
  --name santander-api \
  --image santanderregistry.azurecr.io/santander-api:latest \
  --dns-name-label santander-api \
  --ports 8000 \
  --cpu 2 \
  --memory 4

# 5. 获取 FQDN
az container show \
  --resource-group santander-rg \
  --name santander-api \
  --query ipAddress.fqdn
```

---

## 性能调优

### 1. 增加 Workers

**本地部署**:
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docker**:
修改 `Dockerfile` 的 CMD:
```dockerfile
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### 2. 使用 Gunicorn + Uvicorn Workers

```bash
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### 3. 模型预加载和缓存

在 `app.py` 中已实现模型预加载。对于大规模部署，考虑：
- Redis 缓存特征计算结果
- 模型版本管理（MLflow, DVC）

### 4. 负载均衡

使用 Nginx 或云平台的负载均衡器：

**Nginx 配置示例**:
```nginx
upstream santander_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://santander_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 监控和日志

### 基础监控

```bash
# Docker 日志
docker logs -f santander-api

# 实时监控资源使用
docker stats santander-api
```

### Prometheus + Grafana

添加 `prometheus-fastapi-instrumentator`:

```bash
pip install prometheus-fastapi-instrumentator
```

在 `app.py` 中添加：

```python
from prometheus_fastapi_instrumentator import Instrumentator

@app.on_event("startup")
async def startup():
    Instrumentator().instrument(app).expose(app)
```

### 日志聚合

推荐使用：
- **AWS**: CloudWatch Logs
- **GCP**: Cloud Logging
- **Azure**: Application Insights
- **自建**: ELK Stack (Elasticsearch + Logstash + Kibana)

---

## 故障排查

### 问题 1: 模型文件未找到

**错误**: `FileNotFoundError: Feature columns file not found`

**解决**:
```bash
# 检查 models/ 目录
ls -la models/

# 重新运行 notebook 保存模型
jupyter notebook Santander_Recommendation_System4.ipynb
```

### 问题 2: 内存不足

**错误**: Container killed (OOM)

**解决**:
```bash
# 增加 Docker 内存限制
docker run -m 4g -d --name santander-api -p 8000:8000 santander-api:latest

# 或减少 workers 数量
```

### 问题 3: API 响应慢

**诊断**:
```bash
# 测试推理时间
time curl -X POST http://localhost:8000/recommend \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

**解决**:
- 增加 workers/并发数
- 使用 GPU 加速（需要重新编译 LightGBM）
- 实现特征缓存

### 问题 4: 端口被占用

**错误**: `Address already in use`

**解决**:
```bash
# 找到占用端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 或使用不同端口
uvicorn app:app --port 8001
```

---

## 安全建议

1. **API 认证**: 添加 JWT 或 API Key 认证
2. **HTTPS**: 使用 SSL/TLS 证书（Let's Encrypt）
3. **速率限制**: 防止 API 滥用
4. **输入验证**: 严格验证用户输入
5. **敏感数据**: 不要在日志中记录客户敏感信息

---

## 联系支持

如有问题，请：
- 查看 [README.md](README.md)
- 提交 Issue 到 GitHub
- 联系作者: [your-email@example.com]

---

**祝部署顺利！** 🚀



