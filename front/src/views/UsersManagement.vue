<template>
    <div class="users-container">
        <div class="page-header">
            <h2 class="page-title">Управление пользователями</h2>
            <button class="create-button" @click="showForm = true">
                <i class="fas fa-user-plus"></i>
                Добавить пользователя
            </button>
        </div>

        <!-- Форма создания пользователя -->
        <div v-if="showForm" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>Создание нового пользователя</h3>
                    <button class="close-button" @click="closeForm">&times;</button>
                </div>
                <form @submit.prevent="createUser" class="user-form">
                    <div class="form-group">
                        <label>
                            <i class="fas fa-user"></i>
                            Имя пользователя
                        </label>
                        <input v-model="form.username" type="text" required />
                    </div>

                    <div class="form-group">
                        <label>
                            <i class="fas fa-envelope"></i>
                            Email
                        </label>
                        <input v-model="form.email" type="email" required />
                    </div>

                    <div class="form-group">
                        <label>
                            <i class="fas fa-lock"></i>
                            Пароль
                        </label>
                        <input v-model="form.password" type="password" :required="!form.id" />
                        <small v-if="form.id" class="form-text">Оставьте пустым, если не хотите менять пароль</small>
                    </div>

                    <div class="form-group">
                        <label>
                            <i class="fas fa-user-tag"></i>
                            Роль
                        </label>
                        <select v-model="form.role_input" required>
                            <option value="superadmin">Супер-администратор</option>
                            <option value="admin">Администратор кафе</option>
                            <option value="assistant">Ассистент</option>
                        </select>
                    </div>

                    <div class="form-group" v-if="form.role_input !== 'superadmin'">
                        <label>
                            <i class="fas fa-store"></i>
                            Кафе
                        </label>
                        <select v-model="form.cafe" required>
                            <option v-for="cafe in cafes" :key="cafe.id" :value="cafe.id">
                                {{ cafe.name }}
                            </option>
                        </select>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="submit-button" :disabled="loading">
                            <i class="fas fa-save"></i>
                            {{ loading ? 'Создание...' : 'Создать' }}
                        </button>
                        <button type="button" class="cancel-button" @click="closeForm">
                            <i class="fas fa-times"></i>
                            Отмена
                        </button>
                    </div>
                </form>
                <div v-if="error" class="error">{{ error }}</div>
            </div>
        </div>

        <!-- Список пользователей -->
        <div class="users-grid">
            <div v-for="user in users" :key="user.id" class="user-card">
                <div class="user-header">
                    <div class="user-info">
                        <h3>{{ user.username }}</h3>
                        <span :class="['role-badge', user.role]">
                            {{ user.role === 'superadmin' ? 'Супер-администратор' : 
                               user.role === 'admin' ? 'Администратор кафе' : 'Ассистент' }}
                        </span>
                    </div>
                    <div class="user-actions">
                        <button class="action-button edit" @click="editUser(user)">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-button delete" @click="deleteUser(user.id)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
                <div class="user-details">
                    <p><i class="fas fa-envelope"></i> {{ user.email }}</p>
                    <p v-if="user.cafe && user.role !== 'superadmin'">
                        <i class="fas fa-store"></i> {{ user.cafe.name }}
                    </p>
                    <p><i class="fas fa-clock"></i> Создан: {{ formatDate(user.date_joined) }}</p>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { ref, onMounted } from 'vue'

export default {
    name: 'UsersManagement',
    setup() {
        const users = ref([])
        const cafes = ref([])
        const showForm = ref(false)
        const loading = ref(false)
        const error = ref(null)
        const form = ref({
            id: null,
            username: '',
            email: '',
            password: '',
            role_input: 'assistant',
            cafe: ''
        })

        const fetchUsers = async () => {
            try {
                const token = localStorage.getItem('access')
                const response = await axios.get('http://127.0.0.1:8000/api/users/', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                users.value = response.data
            } catch (err) {
                error.value = 'Ошибка загрузки пользователей'
                console.error(err)
            }
        }

        const fetchCafes = async () => {
            try {
                const token = localStorage.getItem('access')
                const response = await axios.get('http://127.0.0.1:8000/api/cafes/', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                cafes.value = response.data
            } catch (err) {
                error.value = 'Ошибка загрузки кафе'
                console.error(err)
            }
        }

        const createUser = async () => {
            loading.value = true
            error.value = null
            try {
                const token = localStorage.getItem('access')
                const data = { ...form.value }
                
                // Удаляем id при создании нового пользователя
                delete data.id

                // Если это создание нового пользователя, пароль обязателен
                if (!form.value.id && !data.password) {
                    error.value = 'Пароль обязателен для нового пользователя'
                    loading.value = false
                    return
                }

                // Если это обновление и пароль пустой, удаляем его из запроса
                if (form.value.id && !data.password) {
                    delete data.password
                }

                if (form.value.id) {
                    // Обновление существующего пользователя
                    await axios.put(`http://127.0.0.1:8000/api/users/${form.value.id}/update/`, data, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                } else {
                    // Создание нового пользователя
                    await axios.post('http://127.0.0.1:8000/api/users/create/', data, {
                        headers: { Authorization: `Bearer ${token}` }
                    })
                }
                await fetchUsers()
                closeForm()
            } catch (err) {
                if (err.response?.data) {
                    // Обработка ошибок валидации
                    const errors = err.response.data
                    const errorMessages = []
                    for (const field in errors) {
                        if (Array.isArray(errors[field])) {
                            errorMessages.push(...errors[field])
                        } else {
                            errorMessages.push(errors[field])
                        }
                    }
                    error.value = errorMessages.join(', ')
                } else {
                    error.value = 'Ошибка при сохранении пользователя'
                }
                console.error(err.response?.data)
            } finally {
                loading.value = false
            }
        }

        const deleteUser = async (userId) => {
            if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) return
            try {
                const token = localStorage.getItem('access')
                await axios.delete(`http://127.0.0.1:8000/api/users/${userId}/`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
                await fetchUsers()
            } catch (err) {
                error.value = 'Ошибка удаления пользователя'
                console.error(err)
            }
        }

        const editUser = (user) => {
            console.log('Editing user:', user) // Для отладки
            form.value = {
                id: user.id,
                username: user.username,
                email: user.email,
                password: '', // Пустой пароль при редактировании
                role_input: user.role, // Используем role_input вместо role
                cafe: user.cafe ? user.cafe.id : null // Сохраняем ID кафе
            }
            showForm.value = true
        }

        const closeForm = () => {
            showForm.value = false
            form.value = {
                id: null,
                username: '',
                email: '',
                password: '',
                role_input: 'assistant', // Используем role_input вместо role
                cafe: ''
            }
            error.value = null
        }

        const getCafeName = (cafeId) => {
            const cafe = cafes.value.find(c => c.id === cafeId)
            return cafe ? cafe.name : 'Неизвестное кафе'
        }

        const formatDate = (date) => {
            return new Date(date).toLocaleDateString('ru-RU')
        }

        onMounted(() => {
            fetchUsers()
            fetchCafes()
        })

        return {
            users,
            cafes,
            showForm,
            loading,
            error,
            form,
            createUser,
            deleteUser,
            editUser,
            closeForm,
            getCafeName,
            formatDate
        }
    }
}
</script>

<style scoped>
.users-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.create-button {
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    transition: background-color 0.2s;
}

.create-button:hover {
    background-color: #388E3C;
}

.users-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
}

.user-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.user-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
}

.user-info {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.user-info h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
}

.role-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
    display: inline-block;
}

.role-badge.superadmin {
    background-color: #9C27B0;
    color: white;
}

.role-badge.admin {
    background-color: #2196F3;
    color: white;
}

.role-badge.assistant {
    background-color: #FFC107;
    color: black;
}

.user-actions {
    display: flex;
    gap: 8px;
}

.action-button {
    padding: 8px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.action-button.edit {
    background-color: #2196F3;
    color: white;
}

.action-button.delete {
    background-color: #F44336;
    color: white;
}

.user-details {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.user-details p {
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 0;
    color: #666;
}

.user-details i {
    color: #4CAF50;
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    padding: 20px;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
}

.user-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.form-group label {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #666;
}

.form-group input,
.form-group select {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 16px;
}

.form-actions {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
}

.submit-button,
.cancel-button {
    padding: 10px 20px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
}

.submit-button {
    background-color: #4CAF50;
    color: white;
}

.cancel-button {
    background-color: #9e9e9e;
    color: white;
}

.error {
    color: #F44336;
    padding: 10px;
    margin-top: 10px;
    background-color: #ffebee;
    border-radius: 4px;
}
</style> 