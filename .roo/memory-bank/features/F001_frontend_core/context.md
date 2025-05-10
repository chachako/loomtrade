# Feature Context: 用户界面核心 (Frontend Core & UI) (ID: F001_frontend_core)
*Initialized by Feature-Lead on 2025-05-10 02:24:17*
*Last updated by Feature-Lead on 2025-05-10 02:25:16*

## 1. Overview & Goal
实现核心的前端应用框架 (Next.js, React 19, TypeScript)，包括基础布局、导航、BFF (Backend For Frontend) 设置、WebSocket 客户端集成，以及使用 Magic UI 构建核心的仪表盘组件。
目标是创建一个响应迅速、用户友好的界面，作为整个 VibeTrade 系统的主要交互门户。
需要与后端 API (特别是 F011_api_config_service 和 F009_realtime_notification_mvp) 紧密集成。

**Refined Goal:** 主要目标是建立一个健壮、可扩展且可维护的前端基础。这包括清晰的组件结构、状态管理策略、路由机制以及为未来功能添加提供无缝的开发体验。用户界面必须在常见的桌面屏幕尺寸上具有响应性。

## 2. Detailed Requirements / User Stories
*   作为一个交易员 (Trader)，我想要一个清晰直观的导航系统，以便我可以轻松访问应用程序的不同部分 (例如，仪表盘、交易、账户设置)。
*   作为一个交易员 (Trader)，我希望在仪表盘上看到实时更新 (例如，市场数据、通知)，以便我能够及时做出决策。
*   作为一个开发者 (Developer)，我想要一个定义良好的项目结构和组件库，以便我可以高效地构建和维护 UI 功能。
*   作为一个系统管理员 (System Administrator)，我希望前端能够正确连接并使用来自 API 配置服务 (F011_api_config_service) 的配置，以便应用程序按预期运行。

## 3. Acceptance Criteria
*   鉴于应用程序已启动，当主布局呈现时，那么页眉、侧边栏 (如果适用) 和主内容区域将正确显示。
*   鉴于导航菜单可用，当用户点击导航链接时，那么应用程序将路由到正确的页面/视图，而无需完全重新加载页面。
*   鉴于 WebSocket 客户端已配置，当应用程序启动时，那么它将成功连接到 WebSocket 服务器 (F009_realtime_notification_mvp)。
*   鉴于 Magic UI 仪表盘组件已实现，当仪表盘页面加载时，那么它将显示关键指标和图表的占位符部分。
*   鉴于 BFF 已设置，当前端需要的数据需要从多个后端服务进行聚合或转换时，那么 BFF 将处理此交互。

## 4. Scope
### 4.1. In Scope:
*   基本应用程序外壳 (页眉、导航、主内容区域)。
*   核心部分的路由设置 (例如, `/dashboard`, `/settings`)。
*   状态管理设置 (例如, Zustand, Redux Toolkit, 或 React Context)。
*   具有占位符数据/小部件的初始 Magic UI 仪表盘组件。
*   WebSocket 客户端设置和连接握手。
*   至少一个聚合数据端点的基本 BFF 结构 (如果在设计期间认为必要)。
*   TypeScript 严格模式和 linter/formatter 设置。
*   标准桌面分辨率的响应式设计。
*   单元测试和集成测试框架的搭建。

### 4.2. Out of Scope:
*   实现核心仪表盘之外的所有特定交易功能。
*   用户身份验证和授权 UI (将是一个单独的功能，但可能需要占位符)。
*   移动端特定的响应式设计 (桌面优先)。
*   初始设置之外的复杂 BFF 逻辑。
*   初始仪表盘内的复杂数据可视化。
*   端到端测试套件的完整实现 (仅搭建框架)。

## 5. Technical Notes / Assumptions
*   将使用 Next.js App Router。
*   状态管理解决方案：Zustand。
*   样式解决方案：Tailwind CSS 和 Magic UI (通常与 Next.js 一起使用)。
*   单元测试：Jest/React Testing Library。
*   集成测试：Playwright 或 Cypress (仅设置)。
*   BFF 最初可能是一个简单的 Next.js API 路由，如果复杂性增加，则可能是一个单独的 Node.js 服务。
*   Magic UI 组件将用作仪表盘的主要构建块。
*   与 F011_api_config_service 的集成将用于获取例如 API 端点等配置。
*   与 F009_realtime_notification_mvp 的集成将用于实时通知。