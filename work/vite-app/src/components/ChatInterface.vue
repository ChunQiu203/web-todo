<template>
    <div class="chat-container">
        <!-- 新增：模型和角色选择 -->
        <div class="select-bar">
            <label>选择模型：</label>
            <select v-model="selectedModel">
                <option value="qwen-plus">qwen-plus</option>
                <option value="qwen-turbo">qwen-turbo</option>
                <option value="zhipu">zhipu</option>
                <option value="ollama">ollama</option>
            </select>
            <label style="margin-left:16px;">选择角色：</label>
            <select v-model="selectedRole">
                <option value="schedule_assistant">日程助手</option>
                <option value="wiki_expert">百科专家</option>
                <option value="chat_friend">聊天伙伴</option>
            </select>
        </div>
        <!-- 历史记录栏 -->
        <div class="history-bar">
            <div v-for="(message, index) in messages" :key="'history-' + index" :class="['history-item', message.type]">
                <span v-if="message.type==='sent'">用户：</span>
                <span v-else-if="message.type==='received'">AI：</span>
                <span v-else>系统：</span>
                <span>{{ message.text }}</span>
            </div>
        </div>
        <!-- 聊天记录显示区域 -->
        <div class="chat-messages" ref="messageContainer" >
            <div v-for="(message,index) in messages" :key="index"
                :class="['message',message.type]">
                <div class="message-content">
                    {{message.text}}
                </div>
                <div class ="message-time">
                    {{ message.time }}
                </div>
            </div>
        </div>
        <!--输入区域-->
        <div class="chat-input">
            <input
            type="text"
            v-model="newMessage"
            @keyup.enter="sendMessage"
            placeholder="请输入消息..."
            >
            <button @click="sendMessage">发送</button>
        </div>
        <!-- 可选：debug信息 -->
        <div v-if="debugInfo" style="margin:10px 0;">
            <details>
                <summary>调试信息</summary>
                <pre>{{ debugInfo }}</pre>
            </details>
        </div>
    </div>
</template>

<script>
export default{
    name:'ChatInterface',
    data(){
        return{
            messages:[],
            newMessage:'',
            user_id: 1, // 假设为1，实际应从登录信息获取
            selectedModel: 'qwen-plus',
            selectedRole: 'schedule_assistant',
            debugInfo: ''
        }
    },
    methods:{
        async sendMessage(){
            if (this.newMessage.trim()){
                // 添加用户消息
                this.messages.push({
                    text:this.newMessage,
                    type:'sent',
                    time:new Date().toLocaleTimeString()
                })
                const payload = {
                    message: this.newMessage,
                    user_id: this.user_id,
                    history: this.getHistoryForSend()
                };
                try {
                    const response = await fetch(`http://localhost:8000/ai/chat/?model=${this.selectedModel}&role=${this.selectedRole}`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    const data = await response.json();
                    this.messages.push({
                        text: data.reply,
                        type: 'received',
                        time: new Date().toLocaleTimeString()
                    });
                    this.debugInfo = JSON.stringify(data.debug, null, 2);
                } catch (e) {
                    this.messages.push({
                        text: 'AI回复失败，请检查服务。',
                        type: 'received',
                        time: new Date().toLocaleTimeString()
                    });
                }
                this.newMessage='';
                this.scrollToBottom();
            }
        },
        getHistoryForSend() {
            // 只取最近10条对话，且只发role/content
            return this.messages.slice(-10).map(m => ({
                role: m.type === 'sent' ? 'user' : 'assistant',
                content: m.text
            }));
        },
        scrollToBottom(){
            this.$nextTick(()=>{
                const container = this.$refs.messageContainer
                container.scrollTop=container.scrollHeight
            })
        },
        async loadHistory() {
            try {
                const response = await fetch(`http://localhost:8000/ai/history/${this.user_id}`);
                const history = await response.json();
                this.messages = history.map(h => ({
                    text: h.content,
                    type: h.role === 'user' ? 'sent' : 'received',
                    time: h.created_at ? new Date(h.created_at).toLocaleTimeString() : ''
                }));
                this.scrollToBottom();
            } catch (e) {
                // 可选：加载历史失败处理
            }
        }
    },
    async mounted() {
        await this.loadHistory();
    }
}
</script>

<style scoped>
.chat-container{
    width:600px;
    margin:40px auto;
    height: 80vh;
    display:flex;
    flex-direction:column;
    border:1px solid #ddd;
    border-radius:8px;
}
.chat-messages{
    flex:1;
    overflow-y:auto;
    padding:10px;
    background-color:#f5f5f5;
    word-wrap:break-word;
}
.message{
    margin-bottom:10px;
    max-width:70%;
}
.message.sent{
    margin-left:auto;
    text-align: right;;
}
.message.received{
    margin-right:auto;
    text-align:left;
}
.message-content{
    padding:10px 10px;
    border-radius:15px;
    word-wrap:break-word;
}
.sent.message-content{
    background-color:#007AFF;
    color:white;
}
.received.message-content{
    background-color:white;
    border:1px solid #ddd;
}
.message.sent .message-time{
    font-size:10px;
    color:#888;
    margin-top:2px;
    text-align:right;
}
.message.received .message-time{
    font-size:10px;
    color:#888;
    margin-top:2px;
    text-align:left;
}
.chat-input{
    display:flex;
    padding:15px;
    background-color:#ffffff;
    border-top:1px solid #ddd;
}
.chat-input input{
    flex:1;
    padding:8px 12px;
    color:#000000;
    border:1px solid #ddd;
    border-radius:20px;
    margin-right:10px;
    outline:none;
    background-color: #ffffff;
    font-size:14px;
}
.chat-input button{
    padding:8px 20px;
    background-color:#007AFF;
    color:white;
    border:none;
    border-radius:20px;
    cursor:pointer;
    font-size:14px;
   
}
.chat-input button:hover{
    background-color:#0056b3;
}
.message.error {
    color: #fff;
    background-color: #d32f2f;
    border-radius: 15px;
    padding: 10px 10px;
    margin-bottom: 10px;
    max-width: 70%;
    text-align: left;
}
.history-bar {
    max-height: 120px;
    overflow-y: auto;
    background: #f0f4fa;
    border-bottom: 1px solid #e0e0e0;
    padding: 8px 12px;
    font-size: 13px;
}
.history-item {
    margin-bottom: 4px;
    color: #333;
    word-break: break-all;
}
.history-item.sent {
    color: #007AFF;
}
.history-item.received {
    color: #2e7d32;
}
.select-bar {
    padding: 10px 16px;
    background: #f8f8f8;
    border-bottom: 1px solid #e0e0e0;
    display: flex;
    align-items: center;
    font-size: 14px;
}
.select-bar label {
    margin-right: 4px;
}
.select-bar select {
    margin-right: 8px;
    padding: 2px 8px;
    border-radius: 4px;
    border: 1px solid #ccc;
}
</style>