<template>
    <div class="users-container">
        <div class="page-header">
            <h2 class="page-title">Управление пользователями</h2>
            <button class="create-button" @click="showForm = true">
                <i class="fas fa-user-plus"></i>
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
        <div class="users-container">
            <!-- Супер-администраторы -->
            <div class="user-group" v-if="superAdmins.length">
                <h3 class="group-title">Супер-администраторы</h3>
                <div class="users-grid">
                    <div v-for="user in superAdmins" :key="user.id" class="user-card">
                        <div class="user-header">
                            <div class="user-info">
                                <h3>{{ user.username }}</h3>
                                <span :class="['role-badge', user.role]">
                                    Супер-администратор
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
                            <p><i class="fas fa-clock"></i> Создан: {{ formatDate(user.date_joined) }}</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Группировка по кафе -->
            <div v-for="cafe in cafes" :key="cafe.id" class="user-group">
                <div class="group-header" @click="toggleCafeGroup(cafe.id)">
                    <h3 class="group-title">{{ cafe.name }}</h3>
                    <button class="toggle-button" :class="{ 'collapsed': !isCafeExpanded(cafe.id) }">
                        <i class="fas" :class="isCafeExpanded(cafe.id) ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
                    </button>
                </div>
                <div class="users-grid" v-show="isCafeExpanded(cafe.id)">
                    <!-- Администраторы кафе -->
                    <div v-for="user in getCafeUsers(cafe.id, 'admin')" :key="user.id" class="user-card">
                        <div class="user-header">
                            <div class="user-info">
                                <h3>{{ user.username }}</h3>
                                <span :class="['role-badge', user.role]">
                                    Администратор кафе
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
                            <p><i class="fas fa-clock"></i> Создан: {{ formatDate(user.date_joined) }}</p>
                        </div>
                    </div>

                    <!-- Ассистенты -->
                    <div v-for="user in getCafeUsers(cafe.id, 'assistant')" :key="user.id" class="user-card">
                        <div class="user-header">
                            <div class="user-info">
                                <h3>{{ user.username }}</h3>
                                <span :class="['role-badge', user.role]">
                                    Ассистент
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
                            <p><i class="fas fa-clock"></i> Создан: {{ formatDate(user.date_joined) }}</p>
                        </div>
                    </div>
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
        const expandedCafes = ref(new Set()) // Для хранения состояния развернутых групп
        const form = ref({
            id: null,
            username: '',
            email: '',
            password: '',
            role_input: 'assistant',
            cafe: ''
        })

        const toggleCafeGroup = (cafeId) => {
            if (expandedCafes.value.has(cafeId)) {
                expandedCafes.value.delete(cafeId)
            } else {
                expandedCafes.value.add(cafeId)
            }
        }

        const isCafeExpanded = (cafeId) => {
            return expandedCafes.value.has(cafeId)
        }

        const fetchUsers = async () => {
            try {
                const token = localStorage.getItem('access')
                const response = await axios.get('http://127.0.0.1:8000/api/users/', {
                    headers: { Authorization: `Bearer ${token}` }
                })
                users.value = response.data
                // Фильтруем супер-администраторов
                superAdmins.value = response.data.filter(user => user.role === 'superadmin')
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

        const getCafeUsers = (cafeId, role) => {
            return users.value.filter(user => user.cafe && user.cafe.id === cafeId && user.role === role)
        }

        const superAdmins = ref([])

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
            formatDate,
            getCafeUsers,
            superAdmins,
            toggleCafeGroup,
            isCafeExpanded
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

.user-group {
    margin-bottom: 30px;
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
}

.group-title {
    color: #333;
    font-size: 20px;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 2px solid #e9ecef;
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
    transition: transform 0.2s;
}

.user-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
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

/* Мобильные стили */
@media (max-width: 768px) {
    .users-container {
        padding: 10px;
    }

    .user-group {
        padding: 15px;
        margin-bottom: 20px;
    }

    .group-title {
        font-size: 18px;
        margin-bottom: 15px;
    }

    .users-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }

    .user-card {
        padding: 15px;
    }

    .user-header {
        flex-direction: column;
        gap: 10px;
    }

    .user-info h3 {
        font-size: 16px;
    }

    .user-actions {
        width: 100%;
        justify-content: flex-end;
    }

    .action-button {
        padding: 6px;
    }

    .user-details p {
        font-size: 14px;
    }
}

@media (max-width: 480px) {
    .user-group {
        padding: 12px;
    }

    .group-title {
        font-size: 16px;
    }

    .user-card {
        padding: 12px;
    }

    .user-info h3 {
        font-size: 15px;
    }

    .role-badge {
        font-size: 11px;
        padding: 3px 6px;
    }

    .user-details p {
        font-size: 13px;
    }

    .action-button {
        padding: 5px;
    }
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

.group-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    padding: 10px;
    border-radius: 8px;
    transition: background-color 0.2s;
}

.group-header:hover {
    background-color: #e9ecef;
}

.toggle-button {
    background: none;
    border: none;
    color: #666;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
}

.toggle-button:hover {
    background-color: #dee2e6;
    color: #333;
}

.toggle-button i {
    transition: transform 0.2s;
}

.toggle-button.collapsed i {
    transform: rotate(-90deg);
}

.users-grid {
    transition: all 0.3s ease;
    overflow: hidden;
}

/* Мобильные стили */
@media (max-width: 768px) {
    .group-header {
        padding: 8px;
    }

    .toggle-button {
        padding: 6px;
    }
}

@media (max-width: 480px) {
    .group-header {
        padding: 6px;
    }

    .toggle-button {
        padding: 5px;
    }
}
</style> 