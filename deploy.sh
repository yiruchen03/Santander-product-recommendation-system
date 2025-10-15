#!/bin/bash
# Santander Product Recommendation API 部署脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "Santander 推荐系统部署脚本"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 models/ 目录是否存在且包含模型文件
check_models() {
    echo -e "\n${YELLOW}[1/5] 检查模型文件...${NC}"
    
    if [ ! -d "models" ]; then
        echo -e "${RED}❌ models/ 目录不存在${NC}"
        echo "请先运行 Santander_Recommendation_System4.ipynb 训练并保存模型"
        exit 1
    fi
    
    if [ ! -f "models/feature_cols.json" ]; then
        echo -e "${RED}❌ models/feature_cols.json 不存在${NC}"
        echo "请运行 notebook 的最后一个 cell 保存模型"
        exit 1
    fi
    
    model_count=$(ls -1 models/*_model.txt 2>/dev/null | wc -l | tr -d ' ')
    if [ "$model_count" -eq "0" ]; then
        echo -e "${RED}❌ 未找到模型文件${NC}"
        echo "请运行 notebook 的最后一个 cell 保存模型"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 找到 $model_count 个模型文件${NC}"
}

# 构建 Docker 镜像
build_docker() {
    echo -e "\n${YELLOW}[2/5] 构建 Docker 镜像...${NC}"
    docker build -t santander-api:latest .
    echo -e "${GREEN}✓ Docker 镜像构建完成${NC}"
}

# 停止并删除旧容器（如果存在）
stop_old_container() {
    echo -e "\n${YELLOW}[3/5] 检查并停止旧容器...${NC}"
    
    if [ "$(docker ps -q -f name=santander-api)" ]; then
        echo "停止运行中的容器..."
        docker stop santander-api
    fi
    
    if [ "$(docker ps -aq -f name=santander-api)" ]; then
        echo "删除旧容器..."
        docker rm santander-api
    fi
    
    echo -e "${GREEN}✓ 清理完成${NC}"
}

# 启动新容器
start_container() {
    echo -e "\n${YELLOW}[4/5] 启动 API 容器...${NC}"
    docker run -d \
        --name santander-api \
        -p 8000:8000 \
        --restart unless-stopped \
        santander-api:latest
    
    echo -e "${GREEN}✓ 容器启动成功${NC}"
}

# 健康检查
health_check() {
    echo -e "\n${YELLOW}[5/5] 执行健康检查...${NC}"
    
    # 等待服务启动
    echo "等待 API 启动..."
    sleep 5
    
    # 检查健康状态
    max_attempts=10
    attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "${GREEN}✓ API 健康检查通过${NC}"
            
            # 显示服务信息
            echo -e "\n=========================================="
            echo -e "${GREEN}部署成功！${NC}"
            echo "=========================================="
            echo "API 地址: http://localhost:8000"
            echo "API 文档: http://localhost:8000/docs"
            echo "健康检查: http://localhost:8000/health"
            echo ""
            echo "查看日志: docker logs -f santander-api"
            echo "停止服务: docker stop santander-api"
            echo "=========================================="
            
            return 0
        fi
        
        attempt=$((attempt + 1))
        echo "等待中... ($attempt/$max_attempts)"
        sleep 2
    done
    
    echo -e "${RED}❌ 健康检查失败${NC}"
    echo "查看日志: docker logs santander-api"
    exit 1
}

# 主函数
main() {
    check_models
    build_docker
    stop_old_container
    start_container
    health_check
}

# 显示帮助信息
show_help() {
    echo "用法: ./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --help, -h     显示帮助信息"
    echo "  --local        本地运行（不使用 Docker）"
    echo ""
    echo "示例:"
    echo "  ./deploy.sh              # Docker 部署"
    echo "  ./deploy.sh --local      # 本地运行"
}

# 本地运行模式
local_run() {
    echo -e "${YELLOW}启动本地开发服务器...${NC}"
    check_models
    echo -e "${GREEN}✓ 模型检查通过${NC}"
    echo ""
    echo "启动 FastAPI 服务..."
    uvicorn app:app --host 0.0.0.0 --port 8000 --reload
}

# 解析命令行参数
case "${1}" in
    --help|-h)
        show_help
        exit 0
        ;;
    --local)
        local_run
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "未知选项: ${1}"
        show_help
        exit 1
        ;;
esac



