<template>
    <div class="cafes-management">
        <div class="header">
            <h1>Управление кафе</h1>
            <button class="add-button" @click="openForm">
                <i class="fas fa-plus"></i>
            </button>
        </div>

        <!-- Модальное окно для создания/редактирования -->
        <div v-if="showForm" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>{{ editingCafe ? 'Редактировать кафе' : 'Добавить кафе' }}</h2>
                    <button class="close-button" @click="closeForm">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form @submit.prevent="saveCafe" class="form">
                    <div class="form-group">
                        <label for="name">Название кафе</label>
                        <input
                            type="text"
                            id="name"
                            v-model="formData.name"
                            required
                            placeholder="Введите название кафе"
                        >
                    </div>
                    <div class="form-group">
                        <label for="address">Адрес</label>
                        <input
                            type="text"
                            id="address"
                            v-model="formData.address"
                            required
                            placeholder="Введите адрес кафе"
                        >
                    </div>
                    <div class="error-message" v-if="error">{{ error }}</div>
                    <div class="form-actions">
                        <button type="button" class="cancel-button" @click="closeForm">Отмена</button>
                        <button type="submit" class="save-button" :disabled="loading">
                            <span v-if="!loading">{{ editingCafe ? 'Сохранить' : 'Добавить' }}</span>
                            <i v-else class="fas fa-spinner fa-spin"></i>
                        </button>
                    </div>
                </form>
            </div>
        </div>

        <!-- Список кафе -->
        <div class="cafes-grid">
            <div v-for="cafe in cafes" :key="cafe.id" class="cafe-card">
                <div class="cafe-info">
                    <h3>{{ cafe.name }}</h3>
                    <p class="cafe-id">ID: {{ cafe.organization_id }}</p>
                    <p class="cafe-address">{{ cafe.address }}</p>
                </div>
                <div class="cafe-actions">
                    <button class="edit-button" @click="editCafe(cafe)">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-button" @click="confirmDelete(cafe)">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        </div>

        <!-- Модальное окно подтверждения удаления -->
        <div v-if="showDeleteConfirm" class="modal">
            <div class="modal-content delete-confirm">
                <h3>Подтверждение удаления</h3>
                <p>Вы уверены, что хотите удалить кафе "{{ cafeToDelete?.name }}"?</p>
                <div class="form-actions">
                    <button class="cancel-button" @click="showDeleteConfirm = false">Отмена</button>
                    <button class="delete-button" @click="deleteCafe" :disabled="loading">
                        <span v-if="!loading">Удалить</span>
                        <i v-else class="fas fa-spinner fa-spin"></i>
                    </button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import axios from 'axios'

export default {
    name: 'CafesManagement',
    setup() {
        const cafes = ref([])
        const showForm = ref(false)
        const showDeleteConfirm = ref(false)
        const loading = ref(false)
        const error = ref('')
        const editingCafe = ref(null)
        const cafeToDelete = ref(null)
        const formData = ref({
            name: '',
            address: ''
        })

        const fetchCafes = async () => {
            try {
                loading.value = true
                error.value = ''
                console.log('Отправка запроса на получение кафе...')
                const response = await axios.get('http://127.0.0.1:8000/api/cafes/', {
                    headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
                })
                console.log('Получен ответ:', response.data)
                cafes.value = response.data
            } catch (err) {
                console.error('Ошибка при загрузке кафе:', err)
                console.error('Детали ошибки:', {
                    status: err.response?.status,
                    data: err.response?.data,
                    headers: err.response?.headers
                })
                if (err.response?.status === 403) {
                    error.value = 'У вас нет доступа к управлению кафе'
                } else {
                    error.value = 'Не удалось загрузить список кафе'
                }
            } finally {
                loading.value = false
            }
        }

        const openForm = () => {
            editingCafe.value = null
            formData.value = {
                name: '',
                address: ''
            }
            showForm.value = true
        }

        const closeForm = () => {
            showForm.value = false
            error.value = ''
            formData.value = {
                name: '',
                address: ''
            }
        }

        const editCafe = (cafe) => {
            editingCafe.value = cafe
            formData.value = {
                name: cafe.name,
                address: cafe.address
            }
            showForm.value = true
        }

        const saveCafe = async () => {
            try {
                loading.value = true
                error.value = ''

                if (editingCafe.value) {
                    await axios.put(
                        `http://127.0.0.1:8000/api/cafes/${editingCafe.value.id}/`,
                        formData.value,
                        {
                            headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
                        }
                    )
                } else {
                    await axios.post(
                        'http://127.0.0.1:8000/api/cafes/',
                        formData.value,
                        {
                            headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
                        }
                    )
                }

                await fetchCafes()
                closeForm()
            } catch (err) {
                console.error('Ошибка при сохранении кафе:', err)
                if (err.response?.status === 403) {
                    error.value = 'У вас нет прав для создания/редактирования кафе'
                } else {
                    error.value = err.response?.data?.error || 'Не удалось сохранить кафе'
                }
            } finally {
                loading.value = false
            }
        }

        const confirmDelete = (cafe) => {
            cafeToDelete.value = cafe
            showDeleteConfirm.value = true
        }

        const deleteCafe = async () => {
            try {
                loading.value = true
                error.value = ''

                await axios.delete(
                    `http://127.0.0.1:8000/api/cafes/${cafeToDelete.value.id}/`,
                    {
                        headers: { Authorization: `Bearer ${localStorage.getItem('access')}` }
                    }
                )

                await fetchCafes()
                showDeleteConfirm.value = false
                cafeToDelete.value = null
            } catch (err) {
                console.error('Ошибка при удалении кафе:', err)
                if (err.response?.status === 403) {
                    error.value = 'У вас нет прав для удаления кафе'
                } else {
                    error.value = err.response?.data?.error || 'Не удалось удалить кафе'
                }
            } finally {
                loading.value = false
            }
        }

        onMounted(() => {
            fetchCafes()
        })

        return {
            cafes,
            showForm,
            showDeleteConfirm,
            loading,
            error,
            editingCafe,
            cafeToDelete,
            formData,
            openForm,
            closeForm,
            editCafe,
            saveCafe,
            confirmDelete,
            deleteCafe
        }
    }
}
</script>

<style scoped>
.cafes-management {
    padding: 1rem;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.header h1 {
    margin: 0;
    color: #2c3e50;
}

.add-button {
    background: #2c3e50;
    color: white;
    border: none;
    padding: 0.8rem 1.2rem;
    border-radius: 4px;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1rem;
    transition: background-color 0.2s;
}

.add-button:hover {
    background: #34495e;
}

.cafes-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 1.5rem;
}

.cafe-card {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
}

.cafe-info {
    flex: 1;
}

.cafe-info h3 {
    margin: 0 0 0.5rem 0;
    color: #2c3e50;
}

.cafe-id {
    color: #7f8c8d;
    font-size: 0.9rem;
    margin: 0 0 0.5rem 0;
}

.cafe-address {
    color: #34495e;
    margin: 0;
}

.cafe-actions {
    display: flex;
    gap: 0.5rem;
}

.edit-button,
.delete-button {
    background: none;
    border: none;
    padding: 0.5rem;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
}

.edit-button {
    color: #3498db;
}

.delete-button {
    color: #e74c3c;
}

.edit-button:hover {
    background: rgba(52, 152, 219, 0.1);
}

.delete-button:hover {
    background: rgba(231, 76, 60, 0.1);
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
}

.modal-content {
    background: white;
    border-radius: 8px;
    padding: 2rem;
    width: 100%;
    max-width: 500px;
    position: relative;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
}

.modal-header h2 {
    margin: 0;
    color: #2c3e50;
}

.close-button {
    background: none;
    border: none;
    font-size: 1.2rem;
    cursor: pointer;
    color: #7f8c8d;
    padding: 0.5rem;
}

.form {
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
}

.form-group input:focus {
    outline: none;
    border-color: #2c3e50;
}

.form-actions {
    display: flex;
    justify-content: flex-end;
    gap: 1rem;
    margin-top: 1rem;
}

.cancel-button,
.save-button {
    padding: 0.8rem 1.5rem;
    border-radius: 4px;
    font-size: 1rem;
    cursor: pointer;
    transition: background-color 0.2s;
}

.cancel-button {
    background: none;
    border: 1px solid #ddd;
    color: #7f8c8d;
}

.save-button {
    background: #2c3e50;
    border: none;
    color: white;
}

.cancel-button:hover {
    background: #f5f5f5;
}

.save-button:hover {
    background: #34495e;
}

.save-button:disabled {
    background: #95a5a6;
    cursor: not-allowed;
}

.error-message {
    color: #e74c3c;
    text-align: center;
    font-size: 0.9rem;
}

.delete-confirm {
    max-width: 400px;
    text-align: center;
}

.delete-confirm h3 {
    color: #2c3e50;
    margin: 0 0 1rem 0;
}

.delete-confirm p {
    color: #7f8c8d;
    margin: 0 0 1.5rem 0;
}

.delete-confirm .delete-button {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 0.8rem 1.5rem;
}

.delete-confirm .delete-button:hover {
    background: #c0392b;
}

.delete-confirm .delete-button:disabled {
    background: #95a5a6;
}
</style> 