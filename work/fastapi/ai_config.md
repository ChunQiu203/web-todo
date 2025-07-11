# AI 配置说明

## 功能说明

本系统支持两种AI模式：
1. **本地AI (Ollama)** - 默认模式，无需网络连接
2. **在线AI (OpenAI)** - 需要API密钥，功能更强大

## 配置在线AI

### 1. 获取OpenAI API密钥
1. 访问 https://platform.openai.com/api-keys
2. 注册账号并创建API密钥
3. 复制API密钥

### 2. 配置环境变量
在 `vue/fastapi` 目录下创建 `.env` 文件：
```env
AI_API_KEY=你的OpenAI_API密钥
```

### 3. 安装依赖
```bash
cd vue/fastapi
pip install python-dotenv requests
```

## 使用方法

1. **启动后端**：
   ```bash
   cd vue/fastapi
   uvicorn main:app --reload
   ```

2. **启动前端**：
   ```bash
   cd vue/vite-app
   npm run dev
   ```

3. **使用AI功能**：
   - 在AI助手区域输入你的需求
   - 使用开关选择本地AI或在线AI
   - 点击"AI建议"获取智能建议

## 注意事项

- 在线AI需要稳定的网络连接
- OpenAI API可能产生费用，请注意使用量
- 如果在线AI失败，系统会自动回退到本地AI
- 本地AI需要安装Ollama并下载模型 