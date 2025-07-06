'
<template>
  <div class="schedule-app">
    <!-- 侧边栏 -->
    <aside class="sidebar">
      <el-button type="primary" size="small" @click="registerDialogVisible=true" round>注册用户</el-button>
      <div class="logo">🗓️</div>
      <nav>
        <ul>
          <li :class="{active: activeMenu==='today'}" @click="activeMenu='today'">
            <i class="el-icon-date"></i>
            <span>今天</span>
          </li>
          <li :class="{active: activeMenu==='week'}" @click="activeMenu='week'">
            <i class="el-icon-timer"></i>
            <span>未来7天</span>
          </li>
          <li :class="{active: activeMenu==='inbox'}" @click="activeMenu='inbox'">
            <i class="el-icon-message"></i>
            <span>收件箱</span>
          </li>
        </ul>
      </nav>
      <div class="sidebar-bottom">
        <i class="el-icon-setting"></i>
        <i class="el-icon-bell"></i>
      </div>
    </aside>

    <!-- 任务列表 -->
    <section class="task-list">
      <div class="task-list-header">
        <h2>{{ menuTitle }}</h2>
        <el-button type="primary" size="small" @click="dialogVisible=true" round>+ 添加任务</el-button>
      </div>
      <div class="task-group" v-for="(group, gidx) in groupedTasks" :key="gidx">
        <div class="group-title">{{ group.title }}</div>
        <ul>
          <li v-for="task in sortTasks(group.tasks)" :key="task.id" :class="{selected: selectedTask && selectedTask.id===task.id, completed: task.completed}" @click="selectTask(task)">
            <el-checkbox v-model="task.completed" @change.stop="toggleComplete(task)" />
            <span class="task-title">{{ task.title }}</span>
            <span class="task-time" v-if="task.start_time">{{ formatTime(task.start_time) }}</span>
            <el-button type="text" icon="el-icon-delete" @click.stop="deleteSchedule(task.id)" />
          </li>
        </ul>
      </div>
    </section>

    <!-- 任务详情/日历 -->
    <section class="task-detail">
      <div v-if="selectedTask" class="detail-card">
        <h3>{{ selectedTask.title }}</h3>
        <div class="detail-time">
          <i class="el-icon-time"></i>
          {{ formatDate(selectedTask.start_time) }} ~ {{ formatDate(selectedTask.end_time) }}
        </div>
        <div class="detail-desc">{{ selectedTask.description }}</div>
      </div>
      <div v-else class="empty-detail">
        <i class="el-icon-notebook-2"></i>
        <p>请选择一个任务查看详情</p>
      </div>
      <div class="ai-assistant-area">
        <div class="ai-simple-list">
          <div v-for="(item, idx) in aiHistory" :key="idx" class="ai-simple-item">
            <div v-if="item.role === 'user'">用户：{{ item.content }}</div>
            <div v-else>AI：{{ item.content }}</div>
          </div>
        </div>
        <div class="ai-helper">
          <div class="ai-header">
            <h4>🤖 AI 智能助手</h4>
            <el-switch
              v-model="useOnlineAI"
              active-text="在线AI"
              inactive-text="本地AI"
              size="small"
            />
          </div>
          <el-input
            v-model="aiPrompt"
            placeholder="如：帮我安排明天下午三点开会"
            clearable
            @keyup.enter="getAISuggestion"
          />
          <el-button type="success" @click="getAISuggestion" :loading="aiLoading" round>
            {{ aiLoading ? '思考中...' : 'AI建议' }}
          </el-button>
        </div>
      </div>
    </section>

    <!-- 添加任务弹窗 -->
    <el-dialog title="添加任务" v-model="dialogVisible" width="400px" :close-on-click-modal="false" center>
      <el-form :model="form" label-width="70px">
        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="20" show-word-limit />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" maxlength="50" show-word-limit />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker v-model="form.start_time" type="datetime" style="width:100%;" />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker v-model="form.end_time" type="datetime" style="width:100%;" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="addSchedule">确定</el-button>
      </template>
    </el-dialog>
  </div>

  <!-- 注册用户弹窗 -->
   <el-dialog
    title="注册/登录用户"
    v-model="registerDialogVisible"
    width="400px"
    :close-on-click-modal="false"
  >
    <el-form>
      <el-form-item label="用户">
        <el-input v-model="username" />
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="registerDialogVisible = false">取消</el-button>
      <el-button type="primary"@click="createUser">注册/登录</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted, registerRuntimeCompiler } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const userId = 1
const allTasks = ref([])      // 收件箱
const todayTasks = ref([])    // 今天
const weekTasks = ref([])     // 未来7天
const dialogVisible = ref(false)
const form = ref({
  title: '',
  description: '',
  start_time: '',
  end_time: ''
})
const aiPrompt = ref('')
const aiSuggestion = ref('')
const useOnlineAI = ref(false)
const aiLoading = ref(false)
const selectedTask = ref(null)
const activeMenu = ref('inbox')
const aiHistory = ref([])


// 加载所有任务
const fetchAllTasks = async () => {
  const res = await axios.get(`http://localhost:8000/users/${userId}/schedules/`)
  allTasks.value = res.data.map(item => ({ ...item, completed: false }))
}
// 加载今天任务
const fetchTodayTasks = async () => {
  const res = await axios.get(`http://localhost:8000/users/${userId}/schedules/today/`)
  todayTasks.value = res.data.map(item => ({ ...item, completed: false }))
}
// 加载未来7天任务
const fetchWeekTasks = async () => {
  const res = await axios.get(`http://localhost:8000/users/${userId}/schedules/week/`)
  weekTasks.value = res.data.map(item => ({ ...item, completed: false }))
}

// 页面加载时拉取所有数据
onMounted(async () => {
  await fetchAllTasks()
  await fetchTodayTasks()
  await fetchWeekTasks()
})

// 根据菜单切换显示不同任务
const groupedTasks = computed(() => {
  if (activeMenu.value === 'today') {
    return [{ title: '今天', tasks: todayTasks.value }]
  }
  if (activeMenu.value === 'week') {
    return [{ title: '未来7天', tasks: weekTasks.value }]
  }
  // 收件箱显示所有任务
  return [{ title: '收件箱', tasks: allTasks.value }]
})

const registerDialogVisible = ref(false)
const username = ref('')
const password = ref('')


// 新建用户逻辑
async function createUser() {
  try {
    if (!username.value || !password.value) {
      ElMessage.warning('用户名和密码不能为空');
      return;
    }
    const response = await fetch("http://localhost:8000/users/", {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || '创建用户失败');
    }
    const data = await response.json();
    ElMessage.success('用户操作成功');
    registerDialogVisible.value = false;
    console.log('用户操作成功：', data);
    username.value = '';
    password.value = '';
  } catch (error) {
    console.error('用户操作失败：', error);
    ElMessage.error('用户操作失败：' + error.message);
  }
}    


// 其它逻辑（如添加、删除、AI建议等）保持不变
const addSchedule = async () => {
  if (!form.value.title || !form.value.start_time || !form.value.end_time) {
    ElMessage.warning('请填写完整信息')
    return
  }
  try {
    await axios.post(`http://localhost:8000/users/${userId}/schedules/`, form.value)
    ElMessage.success('添加成功')
    dialogVisible.value = false
    form.value = { title: '', description: '', start_time: '', end_time: '' }
    await fetchAllTasks()
    await fetchTodayTasks()
    await fetchWeekTasks()
  } catch {
    ElMessage.error('添加失败')
  }
}

const deleteSchedule = async (id) => {
  try {
    await axios.delete(`http://localhost:8000/schedules/${id}`)
    ElMessage.success('删除成功')
    if (selectedTask.value && selectedTask.value.id === id) selectedTask.value = null
    await fetchAllTasks()
    await fetchTodayTasks()
    await fetchWeekTasks()
  } catch {
    ElMessage.error('删除失败')
  }
}

const selectTask = (task) => {
  selectedTask.value = task
}

const toggleComplete = async (task) => {
  // 切换本地状态
  task.completed = !task.completed
  // 同步到后端
  try {
    await axios.patch(`http://localhost:8000/schedules/${task.id}/completed/`, { completed: task.completed })
  } catch {
    ElMessage.error('更新任务完成状态失败')
    // 回滚本地状态
    task.completed = !task.completed
  }
}

const getAISuggestion = async () => {
  if (!aiPrompt.value) {
    ElMessage.warning('请输入需求')
    return
  }
  aiLoading.value = true
  try {
    // 先记录用户输入
    aiHistory.value.push({ role: 'user', content: aiPrompt.value })
    const res = await axios.post('http://localhost:8000/ai/schedule_suggestion/', {
      message: aiPrompt.value,
      use_online: useOnlineAI.value
    })
    aiHistory.value.push({ role: 'ai', content: res.data.response.replace(/<think>|<\/think>/g, '').trim() })
    ElMessage.success(`AI建议 (${res.data.source})`)
    aiPrompt.value = ''
  } catch (error) {
    aiHistory.value.push({ role: 'ai', content: 'AI建议获取失败，请检查网络连接或API配置' })
    ElMessage.error('AI建议获取失败')
  } finally {
    aiLoading.value = false
  }
}

const menuTitle = computed(() => {
  if (activeMenu.value === 'today') return '今天'
  if (activeMenu.value === 'week') return '未来7天'
  if (activeMenu.value === 'inbox') return '收件箱'
  return ''
})

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.getHours().toString().padStart(2, '0') + ':' + d.getMinutes().toString().padStart(2, '0')
}
function formatDate(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString()
}

function sortTasks(tasks) {
  // 未完成的在前，已完成的在后
  return [...tasks].sort((a, b) => Number(a.completed) - Number(b.completed));
}

</script>

<style scoped>
.schedule-app {
  display: flex;
  min-height: 100vh;
  height: 100vh;
  width: 100vw;
  max-width: none;        /* 取消最大宽度限制 */
  margin: 0;              /* 去除外边距 */
  background: #f7f9fb;
  border-radius: 0;       /* 去除圆角 */
  box-shadow: none;       /* 去除阴影 */
  overflow: hidden;
  font-size: 1.15rem;
}
.sidebar {
  width: 100px;           /* 侧边栏更宽 */
  background: #fff;
  border-right: 1px solid #f0f0f0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0 12px 0;
  box-shadow: 2px 0 8px 0 rgba(60,120,200,0.03);
}
.logo {
  font-size: 2rem;
  margin-bottom: 30px;
}
.sidebar nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  width: 100%;
}
.sidebar nav li {
  width: 100%;
  text-align: center;
  padding: 18px 0;
  cursor: pointer;
  color: #8a98b3;
  transition: background 0.2s, color 0.2s;
  border-radius: 12px;
  margin-bottom: 6px;
  font-size: 1.1rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}
.sidebar nav li.active, .sidebar nav li:hover {
  background: #eaf3ff;
  color: #409eff;
}
.sidebar-bottom {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
  color: #bfc8d7;
  font-size: 1.3rem;
}
.task-list {
  flex: 1.5;              /* 更宽 */
  background: #f7f9fb;
  padding: 48px 36px 36px 36px; /* 增大内边距 */
  border-right: 1px solid #f0f0f0;
  min-width: 420px;       /* 增大最小宽度 */
}
.task-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}
.task-group {
  margin-bottom: 18px;
}
.group-title {
  font-size: 1rem;
  color: #8a98b3;
  margin: 12px 0 6px 0;
  font-weight: bold;
}
.task-group ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.task-group li {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 10px;
  margin-bottom: 8px;
  padding: 10px 14px;
  box-shadow: 0 1px 4px 0 rgba(60,120,200,0.03);
  cursor: pointer;
  transition: box-shadow 0.2s, background 0.2s;
}
.task-group li.selected, .task-group li:hover {
  background: #eaf3ff;
  box-shadow: 0 2px 8px 0 rgba(60,120,200,0.06);
}
.task-title {
  flex: 1;
  margin-left: 10px;
  font-size: 1.05rem;
  color: #3a3a3a;
}
.task-time {
  color: #8a98b3;
  font-size: 0.95rem;
  margin-right: 10px;
}
.task-group li .el-button {
  margin-left: 8px;
}
.task-detail {
  flex: 1.3;              /* 更宽 */
  background: #f7f9fb;
  padding: 48px 36px 36px 36px; /* 增大内边距 */
  min-width: 420px;       /* 增大最小宽度 */
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.detail-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 8px 0 rgba(60,120,200,0.06);
  padding: 24px;
  margin-bottom: 24px;
}
.detail-card h3 {
  margin: 0 0 10px 0;
  font-size: 1.3rem;
  color: #409eff;
}
.detail-time {
  color: #8a98b3;
  font-size: 1rem;
  margin-bottom: 10px;
}
.detail-desc {
  color: #3a3a3a;
  font-size: 1.05rem;
}
.empty-detail {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #bfc8d7;
  font-size: 1.2rem;
  margin-bottom: 24px;
}
.empty-detail i {
  font-size: 2.5rem;
  margin-bottom: 10px;
}
.ai-assistant-area {
  margin-top: auto;
  /* 保证AI助手区域始终在底部 */
  display: flex;
  flex-direction: column;
}
.ai-simple-list {
  margin-top: 24px;
  margin-bottom: 12px;
  max-height: 220px; /* 可根据需要调整高度 */
  overflow-y: auto;
  background: #fafbfc;
  border-radius: 6px;
  padding: 8px 12px;
}
.ai-simple-item {
  padding: 4px 0;
  color: #333;
  font-size: 1rem;
}
.ai-helper {
  margin-top: auto;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 1px 4px 0 rgba(60,120,200,0.03);
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.ai-header h4 {
  margin: 0;
  color: #409eff;
  font-size: 1.1rem;
}

@media (max-width: 900px) {
  .schedule-app {
    flex-direction: column;
    border-radius: 0;
  }
  .sidebar {
    flex-direction: row;
    width: 100%;
    height: 60px;
    border-right: none;
    border-bottom: 1px solid #f0f0f0;
    padding: 0 12px;
  }
  .sidebar nav ul {
    flex-direction: row;
    display: flex;
    width: auto;
  }
  .sidebar nav li {
    flex-direction: row;
    margin-bottom: 0;
    margin-right: 12px;
    padding: 0 10px;
  }
  .sidebar-bottom {
    flex-direction: row;
    gap: 12px;
    margin-top: 0;
  }
  .task-list, .task-detail {
    min-width: 0;
    padding: 18px 8px;
  }
}

.completed .task-title {
  text-decoration: line-through;
  color: #b0b0b0;
}
</style>