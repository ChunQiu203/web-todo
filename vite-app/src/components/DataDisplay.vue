<template>
    <div>
        <button @click="fetchData">获取数据</button>
        <div v-if="data">
            <h2>返回的数据：</h2>
        <p>姓名：{{data.name }}</p>
        <p>年龄：{{data.age }}</p>
        <p>城市：{{data.city}}</p>
    </div>
    <div v-else>
        <p>点击按钮获取数据...</p>
    </div>
    </div>
</template>

<script>
export default{
    name: 'DataDisplay',
    data(){
        return{
            data:null
        }
    },
    methods:{
        async fetchData(){
            try{
                const repose =await fetch('/api/data');
                const result =await Response.json();
                this.data = result
            }catch(error){
                console.error('获取数据失败：',error)
                alert('获取数据失败，请稍后再试。');
            }
        }
    }
}
</script>

<style scoped>
button{
    margin-bottom:20px;
}
</style>