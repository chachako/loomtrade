# 项目结构设计：AI 自动化交易 Agent

## 1. 引言

本文档定义了 AI 自动化交易 Agent 项目的目录结构和模块组织方式。一个清晰、一致的项目结构对于团队协作、代码可维护性以及未来扩展至关重要。此结构基于 `blueprints/technical_specs.md` 中描述的系统架构。

## 2. 顶层目录结构

项目的顶层目录结构建议如下：

```plain
vibetrade/
├── .git/                     # Git 版本控制元数据
├── .github/                  # GitHub 相关配置 (如 workflows for CI/CD)
├── .roo/                     # Roo AI Agent 配置及 Memory Bank
│   ├── memory-bank/
│   └── ...
├── .vscode/                  # VS Code 编辑器配置
├── blueprints/               # 项目核心设计文档 (本文档及其他)
│   ├── development_roadmap.md
│   ├── project_bible.md
│   ├── project_structure.md  <-- 本文档
│   └── technical_specs.md
├── frontend/                 # Next.js 前端应用 (Web UI & BFF)
├── backend/                  # Python FastAPI 后端服务 (Agent核心、API等)
├── shared/                   # (可选) 前后端共享的类型定义、常量等 (如果使用 TypeScript/Python 兼容方式)
├── tests/                    # 集成测试、端到端测试
├── scripts/                  # 项目辅助脚本 (如部署、数据迁移)
├── .dockerignore             # Docker 构建时忽略的文件
├── .env.example              # 环境变量示例文件
├── .gitignore                # Git 忽略文件配置
├── docker-compose.yml        # Docker Compose 配置 (用于本地开发环境)
├── LICENSE                   # 项目许可证
└── README.md                 # 项目主 README
```

## 3. 前端应用 (Next.js) 目录结构 (`frontend/`)

基于 Next.js (React 19) 的标准实践，并考虑模块化和可维护性：

```
frontend/
├── .env.local                # 本地环境变量 (不提交到 Git)
├── .eslintrc.json            # ESLint 配置
├── .gitignore
├── next.config.js            # Next.js 配置文件
├── package.json
├── tsconfig.json             # TypeScript 配置文件
├── public/                   # 静态资源 (图片, favicons)
│   └── ...
├── src/
│   ├── app/                  # Next.js App Router (推荐)
│   │   ├── (auth)/           # 认证相关页面路由组 (如登录、注册)
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/        # 用户主仪表盘路由组
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx      # 仪表盘主页
│   │   │   ├── positions/page.tsx
│   │   │   └── strategies/page.tsx
│   │   ├── settings/         # 用户设置页面路由组
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── api-keys/page.tsx
│   │   │   └── llm-config/page.tsx
│   │   ├── api/              # API Routes (BFF - Backend For Frontend)
│   │   │   ├── auth/[...nextauth].ts # NextAuth.js 或类似认证路由
│   │   │   ├── configs/      # 调用后端配置服务的BFF接口
│   │   │   │   ├── exchanges/route.ts
│   │   │   │   └── llm/route.ts
│   │   │   ├── data/         # 调用后端数据服务的BFF接口
│   │   │   │   ├── positions/route.ts
│   │   │   │   └── orders/route.ts
│   │   │   └── agent/        # 调用后端Agent服务的BFF接口
│   │   │       └── chat/route.ts # 例如处理Agent聊天或命令
│   │   ├── favicon.ico
│   │   ├── globals.css
│   │   ├── layout.tsx        # 根布局
│   │   └── page.tsx          # 应用首页 (可能是欢迎页或重定向到登录/仪表盘)
│   ├── components/           # 可复用UI组件 (遵循原子设计或类似模式)
│   │   ├── ui/               # 基础UI元素 (Button, Input, Card - 可来自Magic UI或自定义)
│   │   ├── layout/           # 布局相关组件 (Navbar, Sidebar, Footer)
│   │   ├── dashboard/        # 仪表盘专用组件 (Charts, PositionList, OrderForm)
│   │   ├── settings/         # 设置页面组件
│   │   └── common/           # 通用业务组件
│   ├── contexts/             # React Context API (如 AuthContext, ThemeContext)
│   ├── hooks/                # 自定义 React Hooks
│   ├── lib/                  # 辅助函数、工具库、客户端API服务封装
│   │   ├── auth.ts           # 认证相关辅助函数
│   │   ├── api-client.ts     # 封装调用BFF或后端API的客户端
│   │   ├── utils.ts          # 通用工具函数
│   │   └── validators.ts     # 前端表单校验逻辑 (可配合Zod等)
│   ├── services/             # (可选) 更具体的客户端服务逻辑 (如WebSocket服务封装)
│   │   └── websocketService.ts
│   ├── store/                # 全局状态管理 (Zustand / Redux Toolkit)
│   │   ├── userStore.ts
│   │   └── agentStore.ts
│   ├── styles/               # 全局样式或主题相关 (如果 globals.css 不够)
│   └── types/                # TypeScript 类型定义 (也可考虑 `shared/` 目录)
│       ├── api.d.ts
│       └── index.d.ts
└── yarn.lock or package-lock.json
```

* **App Router (`src/app/`)**: 推荐使用 Next.js 的 App Router 以获得更好的组件化路由、布局和数据获取能力。
* **API Routes (`src/app/api/`)**: 作为 BFF 层，处理前端到主后端的请求转发、数据转换和部分业务逻辑，有助于解耦。
* **Components (`src/components/`)**: 组织良好、可复用的组件是高效开发的关键。
* **State Management (`src/store/`)**: 根据复杂度选择 Zustand 或 Redux Toolkit。
* **Internationalization (i18n)**: 相关文件 (如 `locales/` 目录) 将根据选型 (如 `next-i18next`) 添加在 `src/` 或项目根目录。

## 4. 后端服务 (FastAPI) 目录结构 (`backend/`)

基于 Python (FastAPI) 的模块化设计，确保服务清晰、易于维护和测试：

```
backend/
├── .env                    # 后端环境变量 (不提交到 Git)
├── .gitignore
├── alembic/                # Alembic 数据库迁移脚本
│   ├── versions/
│   └── env.py
├── app/                    # FastAPI 应用核心代码
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用实例创建和根路由
│   ├── core/               # 核心逻辑与配置
│   │   ├── __init__.py
│   │   ├── config.py       # 应用配置加载 (环境变量等)
│   │   └── security.py     # 安全相关 (密码哈希, JWT, API Key加密)
│   ├── api/                # API 路由模块 (版本化, 如 v1)
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/    # 各资源API端点
│   │       │   ├── __init__.py
│   │       │   ├── auth.py         # 认证
│   │       │   ├── users.py        # 用户管理
│   │       │   ├── exchange_configs.py
│   │       │   ├── llm_configs.py
│   │       │   ├── strategies.py
│   │       │   ├── agents.py       # Agent实例管理与交互
│   │       │   ├── positions.py
│   │       │   └── orders.py
│   │       └── deps.py       # API依赖项 (如获取当前用户)
│   ├── crud/               # CRU(D) 操作 (数据库交互逻辑)
│   │   ├── __init__.py
│   │   ├── base.py         # 基础CRU(D)类
│   │   ├── crud_user.py
│   │   ├── crud_exchange_config.py
│   │   └── ...             # 其他模型的CRUD操作
│   ├── db/                 # 数据库相关
│   │   ├── __init__.py
│   │   ├── base_class.py   # SQLAlchemy Base
│   │   ├── session.py      # SQLAlchemy Session/Engine设置
│   │   └── init_db.py      # (可选) 初始化数据库脚本
│   ├── models/             # SQLAlchemy 数据模型 (对应数据库表)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── exchange_config.py
│   │   └── ...             # 其他数据模型
│   ├── schemas/            # Pydantic 数据校验模型 (API请求/响应, 内部数据传输)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── token.py
│   │   ├── exchange_config.py
│   │   └── ...             # 其他Pydantic模型
│   ├── services/           # 业务服务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── agent_service/  # Agent核心逻辑与Agentic Loop实现
│   │   │   ├── __init__.py
│   │   │   ├── agent_instance_manager.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── llm_client.py
│   │   │   ├── response_parser.py
│   │   │   └── agent_loop.py
│   │   ├── tool_executor/  # 工具执行器与各市场处理器
│   │   │   ├── __init__.py
│   │   │   ├── base_tool_handler.py
│   │   │   ├── crypto_handler.py # 加密货币市场工具实现
│   │   │   ├── stock_handler.py  # 股票市场工具实现 (V1.x+)
│   │   │   └── tool_registry.py
│   │   ├── market_data_service.py # (可选) 统一的市场数据获取接口
│   │   ├── order_management_service.py
│   │   ├── notification_service.py (V1.x+)
│   │   └── websocket_manager.py  # WebSocket连接管理与消息推送
│   └── utils/              # 通用工具函数
│       └── __init__.py
├── tests/                  # 后端单元测试和集成测试
│   ├── __init__.py
│   ├── conftest.py         # Pytest配置文件和fixtures
│   ├── api/
│   │   └── v1/
│   ├── crud/
│   ├── services/
│   └── utils/
├── alembic.ini             # Alembic 配置
├── poetry.lock or requirements.txt
├── pyproject.toml or setup.py
└── README.md               # 后端特定README
```

* **Modular Design (`app/`)**: 将应用按功能（API, CRUD, DB, Models, Schemas, Services）组织。
* **Services Layer (`app/services/`)**: 包含核心业务逻辑，如 `agent_service` (Agentic Loop, LLM 交互) 和 `tool_executor` (多市场工具实现)。这是实现多市场适配的关键。
* **Schemas (`app/schemas/`)**: Pydantic 模型用于数据校验和序列化，确保 API 接口的健壮性。
* **Database (`app/db/`, `app/models/`, `alembic/`)**: SQLAlchemy 用于 ORM，Alembic 用于数据库迁移。
* **Internationalization (i18n)**: API 错误消息和状态文本的 i18n 支持将通过中间件或特定库集成，相关翻译文件可能位于 `app/locales/`。

## 5. 共享代码 (`shared/`) (可选)

如果项目采用 Monorepo 结构或有机制在前后端共享 TypeScript 类型（例如，通过编译 Python Pydantic 模型到 TypeScript 类型），可以在此目录下管理。

```plain
shared/
└── types/                  # 例如, 共享的Pydantic模型生成的TypeScript接口
    └── index.ts
```

这有助于确保前后端数据结构的一致性。

## 6. 数据库 Schema

数据库的详细表结构和关系定义在 `blueprints/technical_specs.md` 的第 7 节 (数据模型) 中。项目结构中的 `backend/app/models/` 目录将包含这些模型的 SQLAlchemy 实现。

## 7. 总结

此项目结构旨在提供一个可扩展、可维护的基础。随着项目的进展，可能需要根据实际需求进行调整和细化。关键在于保持模块化和关注点分离。
