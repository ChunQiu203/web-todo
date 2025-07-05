<template>
  <div id="app">
    <ScheduleManager />
  </div>
</template>

<script>
import ScheduleManager from './components/ScheduleManager.vue'
export default {
  components: { ScheduleManager }
}
</script>

<style>
html, body, #app {
  height: 100%;
  width: 100%;
  margin: 0;
  padding: 0;
  background: #f7f9fb;
  color: #222;
  font-family: "微软雅黑", "Microsoft YaHei", "PingFang SC", "Hiragino Sans GB", 
  "Arial", "sans-serif";
}

@media (prefers-color-scheme: dark) {
  html, body, #app {
    background: #f4f6fa !important; /* 浅色背景 */
    color: #111 !important;         /* 黑色字体 */
  }
}
#app {
  min-height: 100vh;
  min-width: 100vw;
  height: 100vh;
  width: 100vw;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
</style>