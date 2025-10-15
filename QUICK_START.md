# 快速开始指南

## 🚀 首次部署（5 步搞定）

### 1️⃣ 训练并保存模型（首次必须，约 30-60 分钟）

```bash
# 启动 Jupyter
jupyter notebook

# 在浏览器中：
# 1. 打开 Santander_Recommendation_System4.ipynb
# 2. 点击菜单：Cell -> Run All
# 3. 等待所有 cells 运行完成
# 4. 确认最后输出显示模型保存成功
```

### 2️⃣ 验证模型文件

```bash
# 检查模型文件（应该看到 24 个 .txt 文件）
ls -lh models/*.txt | wc -l

# 应该输出: 24

# 检查配置文件
ls models/*.json
# 应该看到: config.json, feature_cols.json, metrics.json, products.json
```

### 3️⃣ 本地测试部署

```bash
# 安装依赖（首次）
pip install -r requirements.txt

# 启动 API（开发模式）
./deploy.sh --local

# 或手动启动
# uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4️⃣ 测试 API

**打开新终端窗口**，运行：

```bash
# 测试健康检查
curl http://localhost:8000/health

# 运行完整测试
python predict_client.py
```

### 5️⃣ Docker 生产部署（可选）

```bash
# 停止开发模式（按 Ctrl+C）

# Docker 部署
./deploy.sh

# 查看运行状态
docker ps

# 查看日志
docker logs -f santander-api
```

---

## ✅ 后续部署（模型已存在，3 步搞定）

**不需要重新训练模型！**

### 1️⃣ 确认模型文件存在

```bash
ls models/*.txt | wc -l
# 应该输出: 24
```

### 2️⃣ 直接部署

```bash
# Docker 部署
./deploy.sh

# 或本地开发
./deploy.sh --local
```

### 3️⃣ 测试

```bash
python predict_client.py
```

---

## 📍 所有命令都在这个目录运行

```bash
cd /Users/chenyiru/Downloads/santander-product-recommendation
# 所有命令在这里执行
```

---

## ❓ 常见问题

### Q1: 我需要每次部署都运行 notebook 吗？
**答**: **不需要**！只有首次部署或需要重新训练模型时才运行。模型文件保存后可以反复使用。

### Q2: 模型文件保存在哪里？
**答**: `models/` 目录。包含 24 个 `.txt` 模型文件和几个 `.json` 配置文件。

### Q3: 如何知道模型已经保存成功？
**答**: 运行以下命令检查：
```bash
ls -lh models/
# 应该看到约 24 个文件，总大小约 500MB
```

### Q4: 部署失败怎么办？
**答**: 按顺序检查：
```bash
# 1. 检查模型文件
ls models/*.txt

# 2. 检查依赖
pip install -r requirements.txt

# 3. 查看详细错误
./deploy.sh --local
# 或
docker logs santander-api
```

### Q5: 端口 8000 被占用怎么办？
**答**:
```bash
# 查找占用进程
lsof -i :8000

# 停止旧容器
docker stop santander-api
docker rm santander-api

# 或使用不同端口
uvicorn app:app --port 8001
```

### Q6: 如何更新模型？
**答**: 重新运行 notebook，新的模型文件会覆盖旧的。然后重启 API 服务。

### Q7: 能在其他服务器上部署吗？
**答**: 可以！只需要：
1. 复制整个项目目录（包括 models/）
2. 在新服务器上运行 `./deploy.sh`

---

## 🎯 一键部署命令（模型已存在）

```bash
# 快速部署
cd /Users/chenyiru/Downloads/santander-product-recommendation && ./deploy.sh
```

---

## 📊 部署检查清单

**首次部署前**：
- [ ] 已运行 Notebook 所有 cells
- [ ] models/ 目录包含 24 个 .txt 文件
- [ ] models/ 目录包含 4 个 .json 文件
- [ ] 已安装 Python 依赖（requirements.txt）

**后续部署前**：
- [ ] models/ 目录存在且完整
- [ ] Docker 已安装（如果使用 Docker）
- [ ] 端口 8000 未被占用

---

## 🔗 相关文档

- **README.md** - 项目详细说明
- **DEPLOYMENT.md** - 完整部署指南（包括云平台）
- **PROJECT_SUMMARY.md** - 项目总结
- **DEPLOYMENT_CHECKLIST.md** - 详细检查清单

---

## 💡 提示

1. **首次部署最重要的是运行 notebook 保存模型**
2. **模型保存后，可以无限次部署，不需要重新训练**
3. **建议先用 `./deploy.sh --local` 测试，确认无误后再用 Docker**
4. **访问 http://localhost:8000/docs 查看自动生成的 API 文档**

---

**祝部署顺利！** 🚀



