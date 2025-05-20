<template>
    <div class="login-container">
        <div class="login-card">
            <div class="login-header">
                <i class="fas fa-coffee"></i>
                <h1>Вход в систему</h1>
            </div>
            <form @submit.prevent="login" class="login-form">
                <div class="form-group">
                    <label for="username">Имя пользователя</label>
                    <input
                        type="text"
                        id="username"
                        v-model="username"
                        required
                        placeholder="Введите имя пользователя"
                    >
                </div>
                <div class="form-group">
                    <label for="password">Пароль</label>
                    <input
                        type="password"
                        id="password"
                        v-model="password"
                        required
                        placeholder="Введите пароль"
                    >
                </div>
                <div v-if="error" class="error-message">
                    {{ error }}
                </div>
                <button type="submit" class="login-button" :disabled="loading">
                    <span v-if="!loading">Войти</span>
                    <i v-else class="fas fa-spinner fa-spin"></i>
                </button>
            </form>
        </div>
    </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
    name: 'Login',
    setup() {
        const router = useRouter()
        const username = ref('')
        const password = ref('')
        const error = ref('')
        const loading = ref(false)

        const login = async () => {
            try {
                loading.value = true
                error.value = ''
                
                const response = await axios.post('http://127.0.0.1:8000/api/login/', {
                    username: username.value,
                    password: password.value
                })

                localStorage.setItem('access', response.data.access)
                router.push('/bookings')
            } catch (err) {
                error.value = 'Неверное имя пользователя или пароль'
                console.error('Ошибка входа:', err)
            } finally {
                loading.value = false
            }
        }

        return {
            username,
            password,
            error,
            loading,
            login
        }
    }
}
</script>

<style scoped>
.login-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f5f5f5;
    padding: 1rem;
}

.login-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
}

.login-header {
    text-align: center;
    margin-bottom: 2rem;
}

.login-header i {
    font-size: 2.5rem;
    color: #2c3e50;
    margin-bottom: 1rem;
}

.login-header h1 {
    color: #2c3e50;
    font-size: 1.5rem;
    margin: 0;
}

.login-form {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
}

.form-group label {
    color: #2c3e50;
    font-weight: 500;
}

.form-group input {
    padding: 0.8rem;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.2s;
}

.form-group input:focus {
    outline: none;
    border-color: #2c3e50;
}

.login-button {
    background: #2c3e50;
    color: white;
    border: none;
    padding: 0.8rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
}

.login-button:hover {
    background: #34495e;
}

.login-button:disabled {
    background: #95a5a6;
    cursor: not-allowed;
}

.error-message {
    color: #e74c3c;
    text-align: center;
    font-size: 0.9rem;
}
</style>
