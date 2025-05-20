import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
    state: () => ({
        access: localStorage.getItem('access') || '',
        refresh: localStorage.getItem('refresh') || ''
    }),
    actions: {
        async login(username, password) {
            const response = await axios.post('http://127.0.0.1:8000/api/login/', {
                username,
                password
            })

            this.access = response.data.access
            this.refresh = response.data.refresh

            localStorage.setItem('access', this.access)
            localStorage.setItem('refresh', this.refresh)
        },
        logout() {
            this.access = ''
            this.refresh = ''
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')
        }
    }
})
