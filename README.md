# WDP Debug Tool - 基于WebSocket的Chrome扩展调试工具

这是一个功能强大的Chrome扩展调试工具，基于WebSocket通信协议，提供实时的页面调试和脚本执行功能。

## 🚀 项目特性

- **WebSocket实时通信**: 基于WebSocket协议的双向通信
- **Chrome扩展集成**: 完整的Chrome扩展开发框架
- **Vue 3 + TypeScript**: 现代化的前端技术栈
- **代码高亮**: 支持JSON格式化和语法高亮
- **预设命令**: 内置常用调试命令模板
- **Markdown文档**: 集成Markdown文档查看器
- **实时日志**: 完整的消息发送和接收日志

## 📁 项目结构

```
crxjs-wdpdebugtool/
├── src/
│   ├── popup/                    # 扩展弹窗界面
│   │   ├── App.vue              # 主应用组件
│   │   ├── components/
│   │   │   ├── Dock.vue         # 预设命令面板
│   │   │   └── Sidebar.vue      # 文档侧边栏
│   │   ├── index.html           # 弹窗HTML模板
│   │   ├── main.ts              # 弹窗入口文件
│   │   └── style.css            # 样式文件
│   ├── background/               # 后台脚本
│   │   └── main.ts              # 扩展后台逻辑
│   ├── content/                  # 内容脚本
│   │   ├── main.ts              # 内容脚本入口
│   │   └── views/
│   │       └── App.vue          # 内容脚本UI组件
│   └── assets/                   # 静态资源
├── server/
│   └── websocket_server.py      # WebSocket服务器
├── public/
│   ├── dock-config.json         # 预设命令配置
│   └── markdown/
│       └── sample.md            # 示例文档
├── manifest.config.ts           # 扩展清单配置
├── vite.config.ts              # Vite构建配置
└── package.json                # 项目依赖配置
```

## 🔧 核心技术架构

### 1. WebSocket通信层

**服务端** (<mcfile name="websocket_server.py" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\server\websocket_server.py"></mcfile>):
```python
import asyncio
import websockets

async def echo(websocket):
    async for message in websocket:
        await websocket.send(message)

async def main():
    async with websockets.serve(echo, "localhost", 5151):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
```

**客户端** (<mcfile name="App.vue" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\src\popup\App.vue"></mcfile>):
- 支持WebSocket连接管理
- 实时消息发送和接收
- JSON格式验证和格式化
- 消息日志记录和高亮显示

### 2. Chrome扩展架构

**Manifest配置** (<mcfile name="manifest.config.ts" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\manifest.config.ts"></mcfile>):
```typescript
export default defineManifest({
  manifest_version: 3,
  name: pkg.name,
  version: pkg.version,
  background: {
    service_worker: 'src/background/main.ts',
    type: 'module',
  },
  content_scripts: [{
    js: ['src/content/main.ts'],
    matches: ['https://*/*'],
  }],
  permissions: [
    'activeTab',
    'storage'
  ]
})
```

**后台脚本** (<mcfile name="main.ts" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\src\background\main.ts"></mcfile>):
```typescript
chrome.action.onClicked.addListener(() => {
  chrome.tabs.create({
    url: chrome.runtime.getURL('src/popup/index.html')
  });
});
```

### 3. 预设命令系统

**配置文件** (<mcfile name="dock-config.json" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\public\dock-config.json"></mcfile>):
```json
{
  "categories": [
    { "id": "default", "name": "默认" },
    { "id": "page", "name": "页面操作" },
    { "id": "element", "name": "元素操作" },
    { "id": "script", "name": "脚本执行" }
  ],
  "presets": [
    {
      "id": 1,
      "categoryId": "page",
      "label": "获取页面信息",
      "icon": "📄",
      "content": "{\n  \"action\": \"getPageInfo\",\n  \"params\": {}\n}",
      "description": "获取当前页面的基本信息"
    }
  ]
}
```

**预设命令类型**:
- **页面操作**: 获取页面信息、Cookie、标题等
- **元素操作**: 获取元素、点击元素等
- **脚本执行**: 执行JavaScript代码
- **连接测试**: WebSocket连接状态检测

### 4. 文档系统

**Sidebar组件** (<mcfile name="Sidebar.vue" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\src\popup\components\Sidebar.vue"></mcfile>):
- 支持Markdown文件加载和渲染
- 多标签页文档管理
- 代码块一键复制到输入框
- 可调整宽度的侧边栏

## 🛠️ 开发和构建

### 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 启动WebSocket服务器（另开终端）
cd server
python websocket_server.py
```

### 生产构建

```bash
# 构建扩展（包含类型检查）
npm run build

# 构建完成后会生成：
# - dist/ 目录：包含构建后的扩展文件
# - release/ 目录：包含打包好的zip文件
```

### Chrome扩展加载

1. 构建项目：`npm run build`
2. 打开Chrome浏览器
3. 访问 `chrome://extensions/`
4. 启用"开发者模式"
5. 点击"加载已解压的扩展程序"
6. 选择项目的 `dist` 目录

### 发布打包

构建完成后，在 `release/` 目录下会自动生成 `crx-crxjs-wdpdebugtool-1.0.0.zip` 文件，可直接用于发布。

## 📖 使用指南

### 1. 基本连接

1. 点击Chrome扩展图标打开调试工具
2. 在WebSocket URL输入框中输入服务器地址（默认: `ws://localhost:5151`）
3. 点击"Connect"按钮建立连接
4. 连接成功后状态显示为"Connected"

### 2. 发送消息

1. 在消息输入框中输入JSON格式的调试命令
2. 系统会自动验证JSON格式
3. 点击"Send"按钮发送消息
4. 可使用"格式化"按钮美化JSON格式

### 3. 使用预设命令

1. 点击右侧Dock面板中的预设命令
2. 命令会自动填入输入框并发送
3. 可以自定义添加新的预设命令
4. 支持导入/导出预设配置

### 4. 查看文档

1. 左侧Sidebar显示Markdown文档
2. 可以加载本地Markdown文件
3. 支持多标签页文档管理
4. 点击代码块可直接复制到输入框

## 🔍 核心功能实现

### WebSocket连接管理

```typescript:src/popup/App.vue
const connectWebSocket = () => {
  websocket = new WebSocket(wsUrl.value.trim());
  
  websocket.onopen = () => {
    updateStatus(`Connected to ${wsUrl.value}`);
    // 更新UI状态
  };
  
  websocket.onmessage = (event) => {
    // 处理接收到的消息
    logReceivedMessage(messageData);
  };
  
  websocket.onerror = (error) => {
    updateStatus(`WebSocket Error: ${error.message}`, true);
  };
};
```

### JSON验证和格式化

```typescript:src/popup/App.vue
const validateJson = (jsonString: string) => {
  try {
    JSON.parse(jsonString);
    return { valid: true, message: '格式正确' };
  } catch (e) {
    return { valid: false, message: e.message };
  }
};

const formatJson = () => {
  try {
    const parsedJson = JSON.parse(messageToSend.value);
    messageToSend.value = JSON.stringify(parsedJson, null, 4);
  } catch (e) {
    updateStatus(`无法格式化: ${e.message}`, true);
  }
};
```

### 代码高亮显示

```typescript:src/popup/App.vue
const highlightedMessages = computed(() => {
  return receivedMessages.value
    .split('\n\n')
    .map(line => {
      try {
        JSON.parse(content);
        const highlighted = hljs.highlight(content, { language: 'json' }).value;
        return `<pre class="code-block"><code class="language-json">${highlighted}</code></pre>`;
      } catch (e) {
        return `<pre class="code-block"><code>${escapeHtml(content)}</code></pre>`;
      }
    })
    .join('');
});
```

## 🎯 应用场景

1. **Web应用调试**: 实时调试网页应用的WebSocket通信
2. **API测试**: 测试WebSocket API接口
3. **页面自动化**: 通过WebSocket控制页面元素和脚本执行
4. **开发工具集成**: 作为开发工具链的一部分
5. **教学演示**: 用于WebSocket技术的教学和演示

## 📝 扩展开发

### 添加新的预设命令

1. 编辑 <mcfile name="dock-config.json" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\public\dock-config.json"></mcfile>
2. 在 `presets` 数组中添加新命令
3. 指定分类、图标、内容和描述

### 自定义WebSocket服务器

1. 修改 <mcfile name="websocket_server.py" path="g:\CodeSpace\CRX_Dev\crxjs-wdpdebugtool\server\websocket_server.py"></mcfile>
2. 实现自定义的消息处理逻辑
3. 添加业务相关的调试功能

### 扩展UI组件

1. 在 `src/popup/components/` 目录下添加新组件
2. 在主应用中引入和使用
3. 添加相应的样式和交互逻辑

## 🔗 相关技术文档

- [Vue 3 Documentation](https://vuejs.org/)
- [Vite Documentation](https://vitejs.dev/)
- [CRXJS Documentation](https://crxjs.dev/vite-plugin)
- [Chrome Extensions API](https://developer.chrome.com/docs/extensions/)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)

## 📄 许可证

本项目采用 MIT 许可证。详见 LICENSE 文件。

---

**注意**: 这是一个开发工具，请在安全的环境中使用，避免在生产环境中暴露敏感信息。

## 🔧 构建和打包配置

### Vite配置 (vite.config.ts)

项目使用Vite作为构建工具，配置了以下特性：

```typescript
export default defineConfig({
  resolve: {
    alias: {
      '@': `${path.resolve(__dirname, 'src')}`,
    },
  },
  build: {
    rollupOptions: {
      input: {
        popup: 'src/popup/index.html',
      },
    },
  },
  base: './',
  plugins: [
    vue(),                    // Vue 3支持
    crx({ manifest }),        // Chrome扩展构建
    zip({                     // 自动打包为zip文件
      outDir: 'release', 
      outFileName: `crx-${name}-${version}.zip` 
    }),
  ],
  server: {
    cors: {
      origin: [/chrome-extension:\/\//],  // 支持扩展开发
    },
  },
})
```

## 📦 项目依赖

### 核心依赖
- **Vue 3** (^3.5.13): 现代化前端框架
- **TypeScript** (~5.7.2): 类型安全的JavaScript
- **highlight.js** (^11.11.1): 代码语法高亮
- **markdown-it** (^14.1.0): Markdown解析和渲染

### 开发依赖
- **@crxjs/vite-plugin** (^2.0.0): Chrome扩展开发插件
- **@vitejs/plugin-vue** (^5.2.1): Vue单文件组件支持
- **vite** (^6.2.0): 现代化构建工具
- **vite-plugin-zip-pack** (^1.2.4): 自动打包插件
- **vue-tsc** (^2.2.4): Vue TypeScript编译器
- 现代化的前端技术栈
- 支持JSON格式化和语法高亮
- 内置常用调试命令模板
- 集成Markdown文档查看器
- 完整的消息发送和接收日志

## 🎠 组件架构

### 主要组件

1. **App.vue** - 主应用容器
   - 管理三个主要组件的布局和通信
   - 处理组件间的消息传递

2. **MainPanel.vue** - 核心功能面板
   - WebSocket连接管理
   - 消息发送和接收
   - JSON验证和格式化
   - 代码高亮显示

3. **Sidebar.vue** - 文档侧边栏
   - Markdown文档加载和渲染
   - 多标签页管理
   - 代码块复制功能

4. **Dock.vue** - 预设命令面板
   - 预设命令管理
   - 分类系统
   - 快速发送功能

### 组件通信

```typescript
// App.vue中的组件通信
const handleInsertCode = (code: string) => {
  // Sidebar -> MainPanel: 插入代码
  mainPanel.value?.setMessage(code);
};

const handleDockMessage = (message: string) => {
  // Dock -> MainPanel: 发送预设消息
  mainPanel.value?.setMessageAndSend(message);
};
```
        