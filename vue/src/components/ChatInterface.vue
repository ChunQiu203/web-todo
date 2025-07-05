<template>
    <div class="chat-container">
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
    </div>
</template>

<script>
export default{
    name:'ChatInterface',
    data(){
        return{
            messages:[],
            newMessage:''
        }
    },
    methods:{
        sendMessage(){
            if (this.newMessage.trim()){
                // 添加新消息
                this.messages.push({
                    text:this.newMessage,
                    type:'sent',
                    time:new Date().toLocaleTimeString()
                })

                //模拟回复
                setTimeout(()=>{
                    this.messages.push({
                        text:'这是一条自动回复消息',
                        type:'received',
                        time:new Date().toLocaleTimeString()
                    })
                    this.scrollToBottom()
                },1000)
                this.newMessage=''
                this.scrollToBottom()
            }
        },
        scrollToBottom(){
            this.$nextTick(()=>{
                const container = this.$refs.messageContainer
                container.scrollTop=container.scrollHeight
            })
        }
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
</style>