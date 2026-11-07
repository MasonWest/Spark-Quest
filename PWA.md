# iOS 主屏幕应用

前端已接入 `public/manifest.webmanifest`、Apple 主屏幕元信息、SVG favicon、180px Apple touch PNG、192/512px PNG 和独立 maskable 图标。原始矢量图标：`frontend/public/icons/spark.svg`。

## 使用

1. 按原有方式运行前后端，或运行 `cd frontend`、`npm run build` 后部署 `dist`。
2. 正式服务使用 HTTPS，同一域名下将 `/api/` 转发到后端，其余静态资源从 `dist` 提供；前端路由不存在对应文件时回退 `index.html`。`/sw.js` 建议使用 `Cache-Control: no-cache`，manifest 使用 `application/manifest+json` 类型。
3. iPhone Safari 访问 HTTPS 地址，分享 → 添加到主屏幕，若显示「作为 Web App 打开」，保持开启。从主屏幕图标启动即为 standalone，无 Safari 地址栏；系统状态栏保留。

手机访问电脑的 HTTP 局域网 IP 不满足 Service Worker 安全上下文要求。`npm run preview` 仅用于本地构建检查，没有生产 API 代理；应使用现有开发服务器或正式反向代理服务进行真实课程验证。

## 缓存边界

生产构建注册 `sw.js`，开发模式不注册。Service Worker 只预缓存离线提示和 SVG 图标；不缓存 API、学习记录或提交请求，不支持离线课程。断网导航展示明确的离线提示。恢复连接后可点击重新连接。不要把用户数据库打包到前端。

## 验证

已通过 TypeScript / Vite 构建、CSS 命名空间检查，以及 Chromium 中 1440/768/390/320px 布局、导航、重试、通关状态、PWA 静态资源检查。界面测试使用 dashboard fixture，未写入学习数据。视觉截图位于工作区 `ux_audit/spark-refresh/`。尚未使用真实 iPhone 验证安装、启动图和系统安全区，部署后需实机确认。
