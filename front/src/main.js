import { createApp } from 'vue'
import App from './App.vue'
import { createPinia } from 'pinia'
import router from './router'
import '@fortawesome/fontawesome-free/css/all.css'
import 'v-calendar/dist/style.css'
import axios from './plugins/axios'

const app = createApp(App)

app.config.globalProperties.$axios = axios
app.use(createPinia())
app.use(router)
app.mount('#app')
