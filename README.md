# AI Product Image Cleaner

面向公司内部电商图片生产的本地批处理系统。上传 JPG、PNG 或 WEBP 后，FastAPI 只负责安全接收文件并将任务写入 SQLite；独立 Python Worker 加载一次真实 BiRefNet 模型，持续处理队列，生成透明 PNG、纯白 PNG、纯白 JPG、Alpha Mask 和缩略图。启发式质量分析把不确定结果分流到人工审核，目标是让员工只检查少量 `NEEDS_REVIEW` 图片，而不是逐张修整整个批次。

## 核心能力

- 批量拖拽、多选、内容级图片验证、大小限制、批次内重复检测和 UUID 磁盘文件名。
- 独立 SQLite Job Queue：`UPLOADED → QUEUED → PROCESSING → COMPLETED / NEEDS_REVIEW / FAILED`。
- 原子条件更新认领任务；多 Worker 不会处理同一张图；启动时恢复超过阈值的 stale 任务。
- `BackgroundRemovalModel` 抽象和真实 `ZhengPeng7/BiRefNet` 实现。模型在 Worker 启动时加载一次并复用。
- 保留连续 Alpha Matte，保守执行小孤岛、微孔洞、平滑、羽化、腐蚀/膨胀和边缘颜色去污染。
- 正确 Alpha compositing 输出透明 PNG、白底 PNG、白底高质量 JPG；原图永不覆盖。
- 质量分数、可解释 flags、自动 PASS/人工审核分流、批准与参数化重处理。
- 任务轮询看板、图库筛选/排序、Before/After、白/黑/棋盘格/自定义预览背景。
- 单图三种格式下载和批量 ZIP（默认不包含原图）。
- SQLite 保存任务历史，重新启动后仍然存在。

## 架构

```text
Next.js browser UI
       │ HTTP / polling
       ▼
FastAPI ── upload validation ── local storage
       │
       ▼
SQLite Job + ImageAsset records
       │ short polling / atomic claim
       ▼
Independent Worker ── BiRefNet (one load)
       │
       ├─ continuous alpha → conservative MaskRefiner
       ├─ edge-only color decontamination
       ├─ transparent / white outputs / thumbnail
       └─ heuristic QualityAnalyzer → PASS or NEEDS_REVIEW
```

HTTP 请求不执行重型推理；关掉浏览器不会停止处理。一张图片失败会记录错误并继续下一张。未来可以在不改处理管线的情况下添加 RMBG、SAM、外部 API 模型，也可把 SQLite 队列替换为 Redis/Celery。

## 技术栈

- Frontend：Next.js 16、React 19、TypeScript strict、Tailwind CSS、shadcn 风格 Radix primitives、react-dropzone、Zustand、Lucide。
- Backend：Python、FastAPI、Pydantic、SQLAlchemy 2、Alembic、SQLite。
- Vision：PyTorch、Transformers、BiRefNet、OpenCV、Pillow、NumPy。
- Storage：本地文件系统；数据库只保存相对路径和元数据，不保存 Binary/Base64。

## 项目结构

```text
backend/
  app/api/             REST API
  app/ai/models/       可替换模型接口与 BiRefNet
  app/ai/pipeline/     完整处理编排
  app/ai/processing/   Mask 与 edge 操作
  app/ai/quality/      质量启发式
  app/db/ models/      SQLAlchemy 与 SQLite
  app/workers/         独立图片 Worker
  alembic/             数据库迁移
  tests/               pytest 测试
frontend/
  app/                  /、/jobs/[id]、/images/[id]、/settings
  components/ features/ lib/ stores/ types/
data/app.db
storage/jobs/{原始文件名--job前8位}/{original,masks,transparent,white_png,white_jpg,thumbnails}
scripts/                Windows PowerShell 启动脚本
```

## Windows + VSCode 安装

### 1. 安装运行时

建议安装 64-bit Python **3.11 或 3.12** 和 Node.js 20/22 LTS，然后在 VSCode 打开仓库根目录。PyTorch 对非常新的 Python 版本支持可能滞后；本机若只有 Python 3.14，可运行 API 核心，但完整 AI 环境仍优先使用 3.11/3.12。

在 PowerShell 检查：

```powershell
python --version
node --version
npm.cmd --version
```

这里使用 `npm.cmd`，可避开某些 Windows ExecutionPolicy 对 `npm.ps1` 的限制。

### 2. 创建虚拟环境并安装依赖

在仓库根目录：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
npm.cmd install --prefix frontend
```

如果 PowerShell 禁止激活脚本，可以不激活，直接使用：

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

`backend/requirements-core.txt` 只用于快速开发 API 和运行非模型测试；正式处理图片必须安装完整 `requirements.txt`，不能用 mock 替代模型。

### 3. 环境配置

```powershell
Copy-Item .env.example .env
```

默认配置可直接运行：

```dotenv
DATABASE_URL=sqlite:///./data/app.db
STORAGE_PATH=./storage
MODEL_NAME=ZhengPeng7/BiRefNet
DEVICE=auto
MAX_UPLOAD_MB=50
QUALITY_PASS_THRESHOLD=85
WORKER_POLL_INTERVAL=1
STALE_PROCESSING_MINUTES=30
MODEL_INPUT_SIZE=1024
FRONTEND_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

数据库和目录首次启动自动创建，不要把真实 `.env` 提交到 Git。

## 启动（3 个 VSCode Terminal）

Terminal 1 — API：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-backend.ps1
```

Terminal 2 — 独立 Worker：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-worker.ps1
```

Terminal 3 — Frontend：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-frontend.ps1
```

浏览器打开 <http://localhost:3000>。API 文档在 <http://localhost:8000/docs>，健康检查在 <http://localhost:8000/api/health>。

也可以一次启动三个后台进程：

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

日常调试更推荐三个独立 Terminal，便于查看各自日志和停止进程。

## 模型、GPU 与 CPU

Worker 第一次启动时从 Hugging Face 下载 `ZhengPeng7/BiRefNet` 权重，时间取决于网络；下载后使用本机缓存。`DEVICE=auto` 会检查 `torch.cuda.is_available()`：可用时使用 CUDA 和 mixed precision，否则明确记录提示并回退 CPU。CPU 可完成同样的真实推理，只是更慢。

本机 2GB 级显存很容易无法容纳 BiRefNet。可在 `.env` 设置 `DEVICE=cpu` 保证稳定；也可降低 `MODEL_INPUT_SIZE`（例如 768），最终 Mask 仍会高质量插值回原始分辨率。发生 CUDA OOM 时仅当前图片标记 `FAILED: GPU memory insufficient`，Worker 继续处理下一张。

## 数据库与迁移

默认数据库为 `data/app.db`。应用会自动建表；正式 schema 变更使用 Alembic：

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m alembic upgrade head
```

SQLite 使用 WAL、foreign keys 和 busy timeout，并为队列与 job/status 查询建立组合索引。

## Storage

每个任务位于 `storage/jobs/{原始文件名--job前8位}/`（例如 `t1--32577466`），文件夹名在第一次上传时按该批次第一张图确定，之后不再改变，方便直接在资源管理器中辨认。文件夹内的文件同样保留原始文件名并追加图片 ID 前缀（例如 `original/微信图片_xxx--a1b2c3d4.jpg`），批次的所有输出（`masks/`、`transparent/`、`white_png/`、`white_jpg/`、`thumbnails/`）共用同一可读文件名。早期版本创建的纯 UUID 文件夹继续有效（所有路径都以相对路径存储在数据库中，与文件夹命名无关）。`original/` 永久保存上传原图且永不覆盖；数据库保留完整原始文件名。所有下载路径都在解析后检查必须位于 Storage 根目录内。

## 测试与构建

```powershell
Set-Location backend
..\.venv\Scripts\python.exe -m pytest -p no:cacheprovider

Set-Location ..\frontend
npm.cmd run typecheck
npm.cmd run build
```

测试覆盖数据库初始化、任务创建、多图上传、内容验证、损坏图片、Storage、安全队列认领、连续 Alpha compositing、Mask refinement、质量分析、失败隔离和批准流程。测试不下载模型；真实推理通过启动 Worker 和上传实际商品图验证。

## 常见问题

- **`npm.ps1 cannot be loaded`**：使用 `npm.cmd`，或调整当前用户的 PowerShell ExecutionPolicy。
- **Worker 提示模型依赖缺失**：确认使用 3.11/3.12 虚拟环境，并安装 `backend/requirements.txt` 而不是 `requirements-core.txt`。
- **首次 Worker 很久没有 ready**：模型正在下载；观察 Worker Terminal 和网络代理设置。
- **CUDA unavailable**：正常回退 CPU。确认 NVIDIA driver、CUDA 兼容的 PyTorch build 和 `torch.cuda.is_available()`。
- **GPU memory insufficient**：设置 `DEVICE=cpu`，或降低 `MODEL_INPUT_SIZE`。
- **Frontend 无法连接 Backend**：确认 8000 端口 API 已启动，`.env` 的 `FRONTEND_URL` 与 `NEXT_PUBLIC_API_URL` 匹配，然后重新启动前端。
- **图片一直 QUEUED**：独立 Worker 未启动或仍在首次下载模型。
- **图片一直 PROCESSING**：Worker 重启时会把超过 `STALE_PROCESSING_MINUTES` 的记录重新排队。
- **损坏/伪装图片被拒绝**：这是预期行为；服务端用 Pillow 解码验证真实内容，不信任扩展名和 client MIME。

## 重置与清理

先停止 API、Worker 和前端。重置数据库会清除历史元数据：

```powershell
Remove-Item -LiteralPath .\data\app.db -Force
```

清空生成任务文件（不可恢复）前，请确认路径正是本仓库的 `storage/jobs`，再手动删除其子目录。下次启动会自动重建数据库/Storage。若只需要重新处理一张图，应在 UI 使用 **Reprocess**，不要删除原图。

## 安全与当前范围

MVP 是本地公司内部工具，无登录/JWT/RBAC。不要直接暴露到公网。上传有最大大小、真实解码、格式白名单、UUID 命名与路径穿越防护；日志从不记录图片内容或 Base64。

当前专注 Clean Product Asset，不包含 LangChain、LLM、RAG、聊天、支付、微服务、Redis、Kubernetes 或详情页生成。下一阶段可加入 SAM2 点选修 Mask、处理版本历史、对象存储、Redis/Celery、用户权限和下游电商模板系统。
