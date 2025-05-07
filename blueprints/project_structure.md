# Vibetrade 项目目录结构

本文档详细描述了 Vibetrade 项目的整体目录结构，旨在为所有开发人员提供一个清晰、一致的项目组织规范。

## 1. 顶级目录结构概览

```
vibetrade/
├── .github/                    # GitHub 特定配置，如 CI/CD 工作流
│   └── workflows/
│       └── main.yml            # 主 CI/CD 工作流示例
├── .gitignore                  # 指定 Git 应忽略的文件和目录
├── .vscode/                    # VSCode 编辑器特定配置 (可选)
│   └── settings.json           # 编辑器设置示例
├── backend/                    # FastAPI 后端服务
├── blueprints/                 # 项目的设计蓝图、规格和核心架构文档
├── database/                   # 数据库相关的脚本和文档 (除迁移外)
├── docs/                       # 项目的各类文档 (用户手册、API文档等)
├── frontend/                   # Next.js 前端应用
├── packages/                   # 共享的 TypeScript/JavaScript 包或模块
├── scripts/                    # 项目辅助脚本 (开发、构建、部署等)
├── tests/                      # 集成测试、端到端测试等
├── .env.example                # 环境变量示例文件
├── docker-compose.yml          # Docker Compose 配置文件，用于本地开发环境
├── Dockerfile                  # 项目主 Dockerfile (或前后端分离的 Dockerfiles)
├── README.md                   # 项目主 README
└── project_structure.md        # (本文档) 项目目录结构说明
```

## 2. 各主要目录详解

### 2.1 `.github/`

存放与 GitHub 相关联的配置文件。

*   **`workflows/`**: 包含 GitHub Actions 的 CI/CD 工作流配置文件。
    *   `main.yml`: 主要的持续集成和持续部署流程定义。

### 2.2 `backend/`

FastAPI 后端服务的根目录。

*   **`app/`**: FastAPI 应用的核心代码。
    *   **`api/`**: API 路由模块。
        *   `v1/`: API 版本1的路由。
            *   `endpoints/`: 各个资源或功能的路由定义 (例如 `users.py`, `agents.py`, `strategies.py`)。
            *   `deps.py`: API 依赖项 (例如，获取当前用户、数据库会话)。
    *   **`core/`**: 核心配置、安全、中间件等。
        *   `config.py`: 应用配置加载。
        *   `security.py`:密码哈希、JWT令牌处理等。
        *   `dependencies.py`: 项目级的通用依赖项。
    *   **`db/`**: 数据库交互逻辑。
        *   `session.py`: 数据库会话管理 (SQLAlchemy)。
        *   `base_class.py`: SQLAlchemy 声明式基类。
        *   `init_db.py`: 初始化数据库的脚本 (可选，用于开发)。
    *   **`models/`**: SQLAlchemy 数据库模型定义。
        *   `user.py`, `agent.py`, `strategy.py`, `trade_order.py` 等。
    *   **`schemas/`**: Pydantic 数据校验模型 (用于API请求/响应和内部数据结构)。
        *   `user.py`, `agent.py`, `strategy.py`, `token.py` 等。
    *   **`services/`**: 业务逻辑服务层，封装了更复杂的操作。
        *   `user_service.py`, `agent_service.py` 等。
    *   **`crud/`**: 基本的数据库 CRUD (Create, Read, Update, Delete) 操作。
        *   `crud_user.py`, `crud_item.py` 等 (遵循 FastAPI 项目生成器的模式)。
    *   **`main.py`**: FastAPI 应用实例的创建和主配置入口。
    *   **`initial_data.py`**: (可选) 用于在应用启动时或通过特定命令创建初始数据的脚本。
*   **`alembic/`**: Alembic 数据库迁移脚本和配置。
    *   `versions/`: 存放自动生成的迁移脚本。
    *   `env.py`: Alembic 运行环境配置。
    *   `script.py.mako`: 迁移脚本模板。
*   **`tests/`**: 后端单元测试和集成测试。
    *   `api/`, `services/`, `crud/` 等子目录对应测试目标。
    *   `conftest.py`: Pytest 配置文件和 fixtures。
*   `.env`: 后端特定的环境变量 (通常在 `.gitignore` 中)。
*   `requirements.txt`: Python 依赖列表。
*   `pytest.ini`: Pytest 配置文件。

### 2.3 `blueprints/`

存放项目的设计蓝图、技术规格、核心架构决策记录等高级文档。

*   **`technical_specs.md`**: 项目的详细技术规格说明书。
*   **`project_structure.md`**: 本文档，描述项目目录结构。
*   **`development_roadmap.md`**: 项目的开发路线图。
*   `(其他架构图、ADRs等)`

### 2.4 `database/`

存放与数据库直接相关，但非迁移脚本的文件。

*   **`seeds/`**: 数据填充脚本，用于在开发或测试环境中填充初始数据。
    *   `users.py`, `strategies.py` 等。
*   **`schemas/`**: (可选) 如果有复杂的数据库 schema 图或文档，可以放这里。
*   **`backups/`**: (可选, 本地开发) 数据库备份文件目录 (通常在 `.gitignore` 中)。

### 2.5 `docs/`

存放项目的各类用户和开发者文档。

*   **`user_manual/`**: 用户手册，指导用户如何使用平台。
*   **`api/`**: API 文档。
    *   可以由 FastAPI 自动生成 (Swagger UI / ReDoc)，这里可存放导出的静态版本或自定义的 API 文档。
*   **`architecture/`**: 更详细的架构文档、设计决策记录 (ADRs - Architecture Decision Records)。
*   **`guides/`**: 开发者指南，例如如何设置开发环境、编码规范等。

### 2.6 `frontend/`

Next.js 前端应用的根目录。参考 [`blueprints/technical_specs.md:282`](blueprints/technical_specs.md:282) 并补充。

*   **`app/`**: (如果采用 Next.js App Router) 核心应用路由和组件。
    *   `layout.tsx`: 根布局。
    *   `page.tsx`: 根页面。
    *   `(dashboard)/`: 仪表盘相关的路由组。
        *   `layout.tsx`
        *   `page.tsx`
        *   `settings/page.tsx`
    *   `api/`: API Routes (BFF)。
        *   `auth/[...nextauth]/route.ts`: NextAuth.js 认证路由。
*   **`pages/`**: (如果采用 Pages Router 或混合模式) 页面级路由。
    *   `api/`: API Routes (BFF)。
*   **`components/`**: 可复用的 React UI 组件。
    *   `ui/`: 基础 UI 元素 (Button, Input, Modal 等，可能来自 Shadcn/UI 或类似库)。
    *   `layout/`: 布局组件 (Navbar, Sidebar, Footer)。
    *   `features/`: 特定功能的组件 (e.g., `AgentChat/`, `StrategyEditor/`)。
*   **`contexts/`**: React Context API 的定义。
    *   `AuthContext.tsx`, `SettingsContext.tsx` 等。
*   **`hooks/`**: 自定义 React Hooks。
    *   `useAuth.ts`, `useLocalStorage.ts` 等。
*   **`lib/`** 或 **`utils/`**: 辅助函数、工具类、客户端服务。
    *   `api.ts`: 封装的 API 请求函数。
    *   `helpers.ts`: 通用辅助函数。
    *   `constants.ts`: 应用常量。
*   **`public/`**: 存放静态资源 (图片, favicons, fonts 等)。
*   **`store/`**: 全局状态管理 (例如 Zustand, Redux Toolkit)。
    *   `index.ts`
    *   `slices/` 或 `features/` (根据状态管理库的组织方式)。
*   **`styles/`**: 全局样式文件。
    *   `globals.css` (TailwindCSS 基础样式或全局 CSS)。
*   **`types/`**: TypeScript 类型定义。
    *   `index.ts`, `next-auth.d.ts` 等。
*   `.env.local`: 前端本地环境变量 (在 `.gitignore` 中)。
*   `next.config.js` 或 `next.config.mjs`: Next.js 配置文件。
*   `postcss.config.js`: PostCSS 配置文件 (例如，与 TailwindCSS 一起使用)。
*   `tailwind.config.ts`: TailwindCSS 配置文件。
*   `tsconfig.json`: TypeScript 配置文件。
*   `package.json`: 项目依赖和脚本。

### 2.7 `packages/`

用于存放未来可能出现的本地共享包或模块 (monorepo 风格，即使当前不是完整的 monorepo)。

*   **`shared-types/`**: (示例) 如果前后端需要共享 TypeScript 类型定义。
    *   `src/`
    *   `package.json`
    *   `tsconfig.json`
*   **`common-utils/`**: (示例) 通用的工具函数库。
    *   `src/`
    *   `package.json`
    *   `tsconfig.json`

### 2.8 `scripts/`

存放用于辅助开发、构建、部署等的脚本。

*   `setup_dev.sh`: (示例) 设置本地开发环境的脚本。
*   `build.sh`: (示例) 执行构建流程的脚本。
*   `deploy.sh`: (示例) 执行部署流程的脚本。
*   `lint.sh`: (示例) 执行代码检查和格式化的脚本。

### 2.9 `tests/`

存放非特定于前端或后端的测试，主要是集成测试和端到端 (E2E) 测试。
单元测试通常位于其对应的模块内 (例如 `backend/tests/`, `frontend/tests/` - 如果有)。

*   **`e2e/`**: 端到端测试 (例如使用 Playwright, Cypress)。
    *   `specs/`: 测试用例。
    *   `fixtures/`: 测试数据。
    *   `config/`: E2E 测试框架配置文件。
*   **`integration/`**: 跨组件或服务的集成测试。

## 3. 根目录下的其他关键文件

*   **`.env.example`**: 环境变量的示例文件，指导开发者如何配置本地环境。实际的 `.env` 文件应被 `.gitignore` 忽略。
*   **`docker-compose.yml`**: 用于在本地环境中编排和运行多个 Docker 容器（例如前端、后端、数据库）。
*   **`Dockerfile`**: (可以有一个根 Dockerfile 用于构建整个应用，或者在 `frontend/` 和 `backend/` 分别有各自的 Dockerfile)。用于构建应用的 Docker 镜像。
*   **`README.md`**: 项目的主要说明文件，包含项目简介、如何开始、如何运行测试、贡献指南等。

---

本文档将作为 Vibetrade 项目目录组织的权威参考。随着项目的发展，本文档可能会进行更新。