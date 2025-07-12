日程管理与 AI 聊天系统项目 README
一、项目概述
本项目是一个集日程管理与 AI 聊天功能于一体的系统，前端采用 Vue + Vite 构建用户界面，后端使用 FastAPI 处理业务逻辑并与数据库交互。系统支持用户注册登录、日程的创建、查看、更新和删除，同时集成了 AI 智能助手，用户可以与 AI 进行自然语言交互，获取日程安排建议等。
二、项目结构
前端部分
ChatInterface.vue：聊天界面组件，实现与 AI 助手的交互，包括消息的发送和接收、历史记录的展示，支持选择不同的 AI 模型和角色。
ScheduleManager.vue：日程管理主界面，包含日程列表展示、任务详情查看、用户注册登录、AI 助手区域，可加载不同时间段的日程信息。
后端部分
main.py：FastAPI 应用的主文件，定义了各种 API 接口，如用户操作、日程操作、AI 聊天等，处理业务逻辑和与数据库的交互。
crud.py：数据访问层，负责与数据库进行交互，提供了用户、日程和 AI 聊天历史等数据的增删改查操作。
schemas.py：数据模型定义，使用 Pydantic 进行数据验证和序列化，确保数据的准确性和一致性。
models.py：数据库模型定义，使用 SQLAlchemy 定义数据库表结构，包括用户、日程和 AI 聊天历史等表。
三、功能特性
用户管理
用户可以进行注册和登录操作，系统会验证用户名和密码的有效性。
通过用户名可以获取用户的详细信息。
日程管理
创建日程：用户可以为自己创建日程，包括日程的标题、描述、开始时间和结束时间，系统会自动处理时间的时区信息，确保为北京时间。
查看日程：支持查看用户的所有日程、今天的日程和未来 7 天的日程。
更新日程：用户可以标记日程为已完成或未完成。
删除日程：用户可以删除指定的日程。
AI 聊天功能
用户可以选择不同的 AI 模型（如 qwen-plus、qwen-turbo 等）和角色（如日程助手、百科专家等）与 AI 进行交互。
系统会记录用户与 AI 的聊天历史，方便用户查看。
可以根据用户的输入，AI 助手会根据历史记录和当前选择的角色进行回复，提供日程安排建议等信息。
四、安装与运行
前端部分
确保你已经安装了 Node.js 和 npm。
进入前端项目目录，安装依赖：

bash
npm install

启动开发服务器：

bash
npm run dev
后端部分
确保你已经安装了 Python 和 pip。
创建虚拟环境并激活：

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate  # Windows

安装依赖：

bash
pip install -r requirements.txt

启动 FastAPI 应用：

bash
uvicorn main:app --reload
五、API 接口文档
用户相关接口
接口路径	方法	功能
/users/	POST	创建或登录用户
/users/{username}	GET	获取用户信息
日程相关接口
接口路径	方法	功能
/users/{user_id}/schedules/	POST	为用户创建日程
/users/{user_id}/schedules/	GET	获取用户所有日程
/users/{user_id}/schedules/today/	GET	获取用户今天的日程
/users/{user_id}/schedules/week/	GET	获取用户未来 7 天的日程
/schedules/{schedule_id}/completed/	PATCH	更新日程完成状态
/schedules/{schedule_id}	DELETE	删除日程
AI 相关接口
接口路径	方法	功能
/ai/history/{user_id}	GET	获取用户 AI 历史对话，支持按角色过滤
/ai/history/	POST	创建 AI 历史记录
/ai/chat/	POST	与 AI 聊天
六、注意事项
时间处理
在创建日程时，系统会对开始时间和结束时间进行时区处理，确保其为北京时间。如果传入的时间没有时区信息，会假设为北京时间；如果是其他时区，会将其转换为北京时间。
数据验证
在使用 API 接口时，确保传入的数据符合schemas.py中定义的数据验证模式，以避免数据错误。
数据库配置
确保数据库连接配置正确，在main.py中可以修改数据库连接信息。
AI 模型配置
部分 AI 模型需要相应的 API 密钥，请根据实际情况进行配置。
