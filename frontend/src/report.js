import { createApp } from 'vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import Report from './Report.vue'

const app = createApp(Report)
app.use(Antd)
app.mount('#app')