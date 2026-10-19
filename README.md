# SupportPilot

**面向电商场景的智能客服 Agent，集成知识库问答、业务工具调用和多轮任务处理。**

SupportPilot 使用 FastAPI 提供 Web 与 API 服务，通过 LangGraph 编排对话、检索和业务流程。用户可以查询商品与售后政策、查询订单物流，并在确认后进入退款或工单流程；管理端提供知识库维护、检索评估、知识审核和运行分析入口。

## 核心功能

|模块|功能|
|-|-|
|智能对话|流式回复、意图识别、指代消解、多轮上下文管理与会话摘要|
|知识库问答|文档切块、向量化、向量与 BM25 混合检索、RRF 融合、重排及引用展示|
|业务处理|订单与物流查询、商品查询、退款确认、售后工单，以及中断后恢复流程|
|工具系统|内置工具与 MCP 服务接入、工具注册、超时与重试、调用审计|
|知识维护|从历史会话提取候选问答、去重、人工审核及知识入库|
|评估与观测|检索策略评估、置信度分析、调用成本统计与可选 Langfuse 链路追踪|
|主题分类|语料处理、分类模型微调、评测、ONNX 导出与独立推理服务|

订单、物流等业务数据使用项目内置的模拟实现。接入真实业务时，需要替换对应的业务数据源和工具实现。Langfuse 与主题分类服务为可选模块，需要单独部署或训练后使用。

## 技术栈

* **后端与编排**：Python 3.12+、FastAPI、LangGraph、LangChain。
* **数据与检索**：SQLAlchemy、MySQL、Milvus、MinIO、etcd；SQLite 用于保存流程检查点。
* **模型服务**：分别配置聊天、嵌入和重排服务，聊天与嵌入使用 OpenAI 兼容接口。
* **工具与运维**：MCP、Docker Compose、uv、Make、pytest；可选 Langfuse。
* **分类训练**：PyTorch、Transformers、ONNX Runtime，按需安装 `ml` 依赖组。

## 快速开始

以下命令在 Linux、macOS 或 Windows 的 WSL2 Ubuntu 终端中执行。需要安装 uv、Docker 和 Make；Windows 使用 Docker Desktop 时，应开启对应 Ubuntu 发行版的 WSL 集成。

### 1\. 获取项目并安装依赖

```bash
git clone https://github.com/11Kou/SupportPilot.git
cd SupportPilot
uv sync
cp .env.example .env
```

### 2\. 配置模型服务

编辑 `.env`，按 `.env.example` 填写配置：

|配置|说明|
|-|-|
|`CHAT\\\_BASE\\\_URL`|聊天模型的接口地址|
|`CHAT\\\_MODEL`|服务商支持的真实模型名称|
|`CHAT\\\_API\\\_KEY`|聊天服务密钥|
|`EMBED\\\_API\\\_KEY`|嵌入服务密钥|
|`RERANK\\\_API\\\_KEY`|重排服务密钥|
|`EMBED\\\_BASE\\\_URL` / `EMBED\\\_MODEL`|更换嵌入服务时调整，默认值见 `app/config.py`|
|`RERANK\\\_BASE\\\_URL` / `RERANK\\\_MODEL`|更换重排服务时调整，默认值见 `app/config.py`|

三组服务分别连接各自上游；仅在服务商与权限允许时共用同一密钥。`.env` 已加入忽略规则，仓库保留 `.env.example` 作为配置模板。

### 3\. 启动基础服务

```bash
docker compose build minio
docker compose up -d
docker compose ps
```

基础服务包含 MySQL、Milvus、MinIO 和 etcd。首次启动会自动执行 `sql/` 中的数据库初始化脚本；等待容器健康后继续下一步。

仓库通过 `docker-compose.override.yml` 使用本地构建的 MinIO 镜像。对应官方版本的源码包、Dockerfile 和来源记录位于 `.deploy/minio/`；首次构建需要联网下载构建依赖。

### 4\. 初始化示例数据与知识库

```bash
make seed
make seed-conv
make kb-build
make kb-vectorize
```

`kb-vectorize` 会调用配置的嵌入服务，生成向量并写入 Milvus，因此需要有效的模型服务配置。

### 5\. 启动应用

```bash
make dev
```

该命令启动依赖容器、等待 Milvus 就绪，再启动物流与售后 MCP 服务和主应用。浏览器打开 [**客服页面**](http://127.0.0.1:8000/) 即可使用。

完成首次初始化后，也可以在项目目录执行 `python3 .deploy/start.py` 将应用启动到后台。

可以尝试提问：

* “支持几天无理由退货？”
* “订单 1001 的物流到哪了？”
* “智能猫砂盆 Pro 适合多重的猫？”

停止应用与业务工具服务使用 `make dev-down`；停止基础容器使用 `docker compose stop`，数据库与向量数据保留在 Docker 数据卷中。

## 页面入口

|页面|地址|用途|
|-|-|-|
|客服首页|`/`|多轮对话与业务咨询|
|管理后台|`/admin`|管理功能导航|
|知识库|`/kb`|文档录入、索引构建与检索测试|
|RAG 评估|`/rag-eval`|查看和运行检索评估|
|知识审核|`/review`|审核候选知识|
|观测与成本|`/observability`|查看成本、评估趋势和置信度分析|
|主题分布|`/topics`|查看问题分类统计|
|分类器验收|`/acceptance`|查看分类数据、评测和模型产物|

以上路径均相对于 `http://127.0.0.1:8000`。评估、知识审核及分类页面需要先运行对应流程才会产生数据；页面入口本身不会自动完成模型训练或启动独立服务。

## 项目结构

```text
app/
  api/          HTTP 接口
  core/         模型调用、检索、意图、上下文与评估能力
  graph/        LangGraph 状态、节点与流程路由
  kb/           文档处理、知识入库与向量索引
  tools/        内置工具、MCP 客户端与执行引擎
  db/           数据模型与访问层
  schemas/      请求与响应模型
  static/       客服和后台页面
mcp\\\_servers/    物流、售后 MCP 服务
data/kb/        示例知识文档
sql/            数据库初始化及迁移脚本
scripts/        建库、评估、知识处理与训练脚本
tests/          测试及评估样本
.deploy/        本地部署辅助文件
```

## 常用命令

|命令|用途|
|-|-|
|`make help`|查看带说明的任务|
|`make test`|运行测试，不调用真实模型|
|`make kb-preview`|预览知识库文档切块|
|`make smoke-rag`|验证 Milvus 检索与重排，需要基础服务和模型配置|
|`make eval-rag`|对比检索策略，需要知识库和模型服务|
|`make flywheel`|处理问题池并生成待审知识|
|`make langfuse-up`|启动可选 Langfuse 观测栈，Web 端口为 3000|
|`make classifier-up`|启动分类器推理服务，需先准备 ONNX 模型产物，端口为 8110|

主应用端口为 **8000**，物流与售后 MCP 服务分别使用 **8101 / 8102**，MySQL 使用 **3306**，Milvus 使用 **19530**，其健康检查端口为 **9091**。

## 项目说明

本项目基于《AI Agent 智能客服实战》配套源码整理，保留原有源码中的来源标注与课程设计文档。部分内部包名、容器名称及 Compose 项目标识沿用 `mewhelp`，用于兼容现有部署和数据卷。
