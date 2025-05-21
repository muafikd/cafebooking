<template>
    <div class="bookings-container">
        <div class="page-header">
            <!-- <h2 class="page-title">Заявки</h2> -->
            <div class="header-actions">
                <button class="create-button" @click="showForm = true">
                    <i class="fas fa-plus"></i>
                </button>
            </div>
        </div>
        <!-- Модальное окно формы -->
        <div v-if="showForm" class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h3>{{ isEditing ? 'Редактирование заявки' : 'Создание заявки' }}</h3>
                    <button class="close-button" @click="closeForm">&times;</button>
                </div>
                <form @submit.prevent="createBooking" class="booking-form">
                    <label for="cafe">Выберите кафе:</label>
                    <select v-model="form.cafe" required>
                        <option disabled value="">Пожалуйста, выберите кафе</option>
                        <option v-for="cafe in cafes" :key="cafe.id" :value="cafe.id">
                            {{ cafe.name }}
                        </option>
                    </select>
                    <label>
                        Имя клиента:
                        <input v-model="form.client_name" type="text" required />
                    </label>

                    <label>
                        Название мероприятия:
                        <input v-model="form.event_name" type="text" required />
                    </label>


                    <label>
                        Телефон клиента:
                        <input v-model="form.client_phone" type="tel" required pattern="^\+?\d{10,15}$"
                            placeholder="+77081234567" />
                    </label>

                    <label>
                        Дата бронирования:
                        <input v-model="form.date" type="date" required />
                    </label>

                    <label>
                        Время:
                        <input v-model="form.time" type="time" required />
                    </label>

                    <label>
                        Email клиента:
                        <input v-model="form.client_email" type="email" />
                    </label>

                    <label>
                        Комментарий:
                        <textarea v-model="form.client_comment"></textarea>
                    </label>

                    <label>
                        Длительность (часы):
                        <input v-model.number="form.duration_hours" type="number" required min="1" />
                    </label>

                    <label>
                        Кол-во людей:
                        <input v-model.number="form.number_of_people" type="number" required min="1" />
                    </label>

                    <label>
                        Цена за посетителя:
                        <input v-model.number="form.price_per_visitor" type="number" required min="0"
                            @input="calculateTotals" />
                    </label>

                    <label>
                        Предоплата:
                        <input v-model.number="form.prepayment" type="number" required min="0"
                            @input="calculateTotals" />
                    </label>

                    <div class="form-totals">
                        <div class="total-row">
                            <span>Общая сумма:</span>
                            <span>{{ form.total_price }} ₸</span>
                        </div>
                        <div class="total-row">
                            <span>К оплате:</span>
                            <span>{{ form.final_price }} ₸</span>
                        </div>
                    </div>

                    <button type="submit" :disabled="loadingCreate">
                        {{ loadingCreate ? 'Создание...' : 'Создать' }}
                    </button>
                </form>
                <div v-if="createError" class="error">{{ createError }}</div>
            </div>
        </div>

        <h2 class="page-title">Созданные заявки</h2>

        <div v-if="loading" class="loading">Загрузка...</div>
        <div v-if="error" class="error">{{ error }}</div>

        <div class="bookings-grid" v-if="bookings.length">
            <div v-for="booking in bookings" :key="booking.id" class="booking-card">
                <div class="booking-header">
                    <div class="booking-title">
                        <h3>Заявка #{{ booking.id }}</h3>
                    </div>
                    <span :class="['status-badge', booking.event_status]">
                        {{ booking.event_status === 'confirmed' ? 'Подтверждено' : 'Ожидает' }}
                    </span>
                </div>

                <div class="booking-main-info">
                    <p><i class="fas fa-newspaper"></i> {{ booking.event_name }}</p>
                    <p><i class="fas fa-calendar"></i> {{ booking.date }}</p>
                    <p><i class="fas fa-clock"></i> {{ booking.time }}</p>
                    <p><i class="fas fa-user"></i> {{ booking.client_name }}</p>
                    <p><i class="fas fa-phone"></i> {{ booking.client_phone }}</p>
                </div>
                <div class="booking-details" v-if="booking.isExpanded">
                    <div class="details-section">
                        <p><strong>Email:</strong> {{ booking.client_email }}</p>
                        <p><strong>Комментарий:</strong> {{ booking.client_comment }}</p>
                        <p><strong>Количество гостей:</strong> {{ booking.number_of_people }}</p>
                        <p><strong>Длительность:</strong> {{ booking.duration_hours }} ч.</p>
                    </div>
                    <div class="price-section">
                        <p><strong>Цена за гостя:</strong> {{ booking.price_per_visitor }} ₸</p>
                        <p><strong>Общая сумма:</strong> {{ booking.total_price }} ₸</p>
                        <p><strong>Предоплата:</strong> {{ booking.prepayment }} ₸</p>
                        <p><strong>К оплате:</strong> {{ (booking.price_per_visitor * booking.number_of_people) -
                            booking.prepayment }} ₸</p>
                    </div>
                </div>

                <div class="booking-actions">
                    <button class="action-button expand" @click="toggleBookingDetails(booking)">
                        {{ booking.isExpanded ? 'Свернуть' : 'Подробнее' }}
                    </button>
                    <template v-if="isAdmin">
                        <button class="action-button edit" @click="editBooking(booking)">
                            <i class="fas fa-edit"></i>
                        </button>
                        <button class="action-button delete" @click="deleteBooking(booking.id)">
                            <i class="fas fa-trash"></i>
                        </button>
                    </template>
                    <button v-if="booking.event_status === 'not_confirmed'" class="action-button confirm"
                        @click="showConfirmationForm(booking)">
                        Подтвердить
                    </button>
                </div>
            </div>
        </div>
        <div v-else class="no-bookings">Заявок нет.</div>

        <!-- Модальное окно подтверждения -->
        <div v-if="confirmationBooking" class="modal-overlay">
            <div class="modal-content confirmation-modal">
                <div class="modal-header">
                    <h3>Подтверждение заявки #{{ confirmationBooking.id }}</h3>
                    <button class="close-button" @click="closeConfirmationForm">&times;</button>
                </div>

                <div class="confirmation-content">
                    <div v-if="!confirmationCodeSent" class="confirmation-step">
                        <p class="confirmation-description">Выберите метод подтверждения:</p>
                        <div class="confirmation-methods">
                            <label class="method-option">
                                <input type="radio" value="email" v-model="confirmationMethod" />
                                <span class="method-label">
                                    <i class="fas fa-envelope"></i>
                                    Email
                                </span>
                            </label>
                            <label class="method-option">
                                <input type="radio" value="sms" v-model="confirmationMethod" />
                                <span class="method-label">
                                    <i class="fas fa-sms"></i>
                                    SMS
                                </span>
                            </label>
                        </div>
                        <div class="confirmation-actions">
                            <button class="action-button confirm" @click="sendConfirmationCode"
                                :disabled="loadingConfirm">
                                <i class="fas fa-paper-plane"></i>
                                {{ loadingConfirm ? 'Отправка...' : 'Отправить код' }}
                            </button>
                            <button class="action-button cancel" @click="closeConfirmationForm">
                                <i class="fas fa-times"></i>
                                Отмена
                            </button>
                        </div>
                    </div>

                    <div v-if="confirmationCodeSent" class="confirmation-step">
                        <p class="confirmation-description">Введите код подтверждения, отправленный на {{
                            confirmationMethod ===
                            'email' ? 'email' : 'телефон' }}:</p>
                        <div class="code-input-container">
                            <input v-model="confirmationCode" type="text" class="code-input" placeholder="Введите код"
                                maxlength="6" />
                        </div>
                        <div class="confirmation-actions">
                            <button class="action-button confirm" @click="confirmBookingCode" :disabled="loadingVerify">
                                <i class="fas fa-check"></i>
                                {{ loadingVerify ? 'Проверка...' : 'Подтвердить' }}
                            </button>
                            <button class="action-button cancel" @click="closeConfirmationForm">
                                <i class="fas fa-times"></i>
                                Отмена
                            </button>
                        </div>
                    </div>

                    <div v-if="confirmationError" class="error">{{ confirmationError }}</div>
                    <div v-if="confirmationErrorFinal" class="error">{{ confirmationErrorFinal }}</div>
                </div>
            </div>
        </div>

        <!-- Модальное окно подтверждения удаления -->
        <div v-if="showDeleteModal" class="modal-overlay">
            <div class="modal-content confirmation-modal">
                <div class="modal-header">
                    <h3>Подтверждение удаления заявки #{{ bookingToDelete }}</h3>
                    <button class="close-button" @click="cancelDelete">&times;</button>
                </div>

                <div class="confirmation-content">
                    <p class="confirmation-description">Вы уверены, что хотите удалить эту заявку?</p>
                    <div class="confirmation-actions">
                        <button class="action-button confirm" @click="confirmDelete">
                            <i class="fas fa-check"></i>
                            Подтвердить
                        </button>
                        <button class="action-button cancel" @click="cancelDelete">
                            <i class="fas fa-times"></i>
                            Отмена
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios'
import { useRouter } from 'vue-router'

export default {
    name: 'BookingsList',
    setup() {
        const router = useRouter()
        return { router }
    },
    data() {
        return {
            bookings: [],
            loading: false,
            error: null,
            showForm: false,
            cafes: [],
            form: {
                cafe: '',
                client_name: '',
                client_phone: '',
                client_email: '',
                client_comment: '',
                date: '',
                time: '',
                duration_hours: 1,
                number_of_people: 1,
                price_per_visitor: 0,
                prepayment: 0,
                total_price: 0,
                final_price: 0,
                event_name: ''
            },
            loadingCreate: false,
            createError: null,
            isAdmin: false,
            confirmationBooking: null,
            confirmationMethod: 'email',
            loadingConfirm: false,
            confirmationError: null,
            isEditing: false,
            confirmationError: '',
            confirmationErrorFinal: '',
            confirmationCode: '',
            confirmationCodeSent: false,
            loadingVerify: false,
            isSuperAdmin: false,
            showDeleteModal: false,
            bookingToDelete: null,
        }
    },
    async created() {
        await this.fetchUserRole();
        await this.fetchBookings()
        await this.fetchCafes()
    },
    methods: {
        async fetchBookings() {
            this.loading = true
            this.error = null
            try {
                const token = localStorage.getItem('access')
                if (!token) throw new Error('Не авторизован')

                const response = await axios.get('http://127.0.0.1:8000/api/bookings/', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                })
                // Сортируем заявки: сначала неподтвержденные, затем подтвержденные
                this.bookings = response.data.sort((a, b) => {
                    if (a.event_status === 'not_confirmed' && b.event_status === 'confirmed') {
                        return -1;
                    }
                    if (a.event_status === 'confirmed' && b.event_status === 'not_confirmed') {
                        return 1;
                    }
                    return 0;
                });
            } catch (err) {
                this.error = err.response?.data?.detail || err.message || 'Ошибка загрузки'
            } finally {
                this.loading = false
            }
        },
        async fetchCafes() {
            try {
                const response = await axios.get('http://127.0.0.1:8000/api/cafes/', {
                    headers: {
                        Authorization: `Bearer ${localStorage.getItem('access')}`,
                    },
                })
                this.cafes = response.data
            } catch (error) {
                console.error('Ошибка загрузки кафе:', error)
            }
        },
        async fetchUserRole() {
            try {
                const token = localStorage.getItem('access');
                const response = await axios.get('http://127.0.0.1:8000/api/user/', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                console.log(response.data.role)
                this.isAdmin = response.data.role === 'admin'; // предполагается, что в ответе есть поле role
            } catch (error) {
                console.error('Ошибка при получении роли пользователя', error);
            }
        },
        async deleteBooking(bookingId) {
            this.bookingToDelete = bookingId;
            this.showDeleteModal = true;
        },
        async confirmDelete() {
            try {
                const token = localStorage.getItem('access');
                await axios.delete(`http://127.0.0.1:8000/api/delete/${this.bookingToDelete}/`, {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                });
                this.bookings = this.bookings.filter(b => b.id !== this.bookingToDelete);
                this.showDeleteModal = false;
                this.bookingToDelete = null;
            } catch (error) {
                this.error = 'Ошибка при удалении заявки.';
                console.error(error);
            }
        },
        cancelDelete() {
            this.showDeleteModal = false;
            this.bookingToDelete = null;
        },
        async confirmBookingCode() {
            this.loadingVerify = true;
            this.confirmationErrorFinal = '';
            const token = localStorage.getItem('access');

            try {
                await axios.post(
                    `http://127.0.0.1:8000/api/bookings/${this.confirmationBooking.id}/confirm/`,
                    { code: this.confirmationCode },
                    { headers: { Authorization: `Bearer ${token}` } }
                );

                this.confirmationBooking.event_status = 'confirmed';
                this.confirmationBooking = null;
                this.confirmationCodeSent = false;
            } catch (error) {
                this.confirmationErrorFinal = 'Неверный код подтверждения';
                console.error(error);
            } finally {
                this.loadingVerify = false;
            }
        },

        openForm() {
            this.isEditing = false;
            this.form = {
                cafe: '',
                client_name: '',
                client_phone: '',
                client_email: '',
                client_comment: '',
                date: '',
                time: '',
                duration_hours: 1,
                number_of_people: 1,
                price_per_visitor: 0,
                prepayment: 0,
                total_price: 0,
                final_price: 0,
            };
            this.showForm = true;
        },

        closeForm() {
            this.showForm = false;
            this.isEditing = false;
            this.form = {
                cafe: '',
                client_name: '',
                client_phone: '',
                client_email: '',
                client_comment: '',
                date: '',
                time: '',
                duration_hours: 1,
                number_of_people: 1,
                price_per_visitor: 0,
                prepayment: 0,
                total_price: 0,
                final_price: 0,
            };
        },

        editBooking(booking) {
            this.isEditing = true;
            this.form = { ...booking };
            this.calculateTotals(); // Рассчитываем суммы при редактировании
            this.showForm = true;
        },

        async createBooking() {
            this.loadingCreate = true;
            this.createError = null;
            const token = localStorage.getItem('access');

            try {
                if (this.isEditing && this.form.id) {
                    // Редактирование
                    await axios.put(
                        `http://127.0.0.1:8000/api/update/${this.form.id}/`,
                        this.form,
                        {
                            headers: {
                                Authorization: `Bearer ${token}`,
                            },
                        }
                    );
                    const index = this.bookings.findIndex(b => b.id === this.form.id);
                    if (index !== -1) {
                        this.bookings[index] = { ...this.form };
                    }
                } else {
                    // Создание
                    const response = await axios.post(
                        'http://127.0.0.1:8000/api/create/',
                        this.form,
                        {
                            headers: {
                                Authorization: `Bearer ${token}`,
                            },
                        }
                    );
                    this.bookings.push(response.data.booking);
                }

                // Сброс
                this.form = {
                    cafe: '',
                    client_name: '',
                    client_phone: '',
                    date: '',
                    time: '',
                    duration_hours: 1,
                    number_of_people: 1,
                    price_per_visitor: 0,
                    prepayment: 0,
                    total_price: 0,
                    final_price: 0,
                };
                this.showForm = false;
                this.isEditing = false;
            } catch (err) {
                this.createError = err.response?.data?.error || err.message || 'Ошибка создания/редактирования';
            } finally {
                this.loadingCreate = false;
            }
        },
        showConfirmationForm(booking) {
            this.confirmationBooking = booking
            this.confirmationMethod = 'email' // по умолчанию
            this.confirmationError = null
        },
        closeConfirmationForm() {
            this.confirmationBooking = null;
            this.confirmationMethod = 'email';
            this.confirmationError = null;
            this.confirmationErrorFinal = null;
            this.confirmationCode = '';
            this.confirmationCodeSent = false;
        },
        async sendConfirmationCode() {
            if (!this.confirmationBooking || !this.confirmationMethod) return;

            this.loadingConfirm = true;
            this.confirmationError = null;

            try {
                const token = localStorage.getItem('access');
                await axios.post(
                    `http://127.0.0.1:8000/api/bookings/${this.confirmationBooking.id}/send-code/`,
                    { method: this.confirmationMethod },
                    {
                        headers: {
                            Authorization: `Bearer ${token}`,
                        },
                    }
                );
                this.confirmationCodeSent = true;
            } catch (err) {
                this.confirmationError = err.response?.data?.detail || err.message || 'Ошибка при отправке';
            } finally {
                this.loadingConfirm = false;
            }
        },
        getCafeName(cafeId) {
            const cafe = this.cafes.find(c => c.id === cafeId);
            return cafe ? cafe.name : 'Неизвестное кафе';
        },
        toggleBookingDetails(booking) {
            // Закрываем все остальные карточки
            this.bookings.forEach(b => {
                if (b.id !== booking.id) {
                    b.isExpanded = false;
                }
            });
            // Переключаем состояние текущей карточки
            booking.isExpanded = !booking.isExpanded;
        },
        calculateTotals() {
            // Рассчитываем общую сумму
            this.form.total_price = this.form.price_per_visitor * this.form.number_of_people;
            // Рассчитываем сумму к оплате
            this.form.final_price = this.form.total_price - this.form.prepayment;
        },
        async logout() {
            try {
                const token = localStorage.getItem('access')
                if (token) {
                    await axios.post('http://127.0.0.1:8000/api/logout/', {}, {
                        headers: {
                            Authorization: `Bearer ${token}`
                        }
                    })
                }
                // Очищаем токен независимо от результата запроса
                localStorage.removeItem('access')
                // Принудительно перенаправляем на страницу логина
                this.router.push('/login')
            } catch (error) {
                console.error('Ошибка при выходе:', error)
                // Даже если запрос не удался, очищаем токен и перенаправляем
                localStorage.removeItem('access')
                this.router.push('/login')
            }
        },
    }
}
</script>

<style scoped>
.bookings-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    position: relative;
}

.create-button {
    position: fixed;
    bottom: 30px;
    right: 30px;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: #4CAF50;
    color: white;
    border: none;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    transition: transform 0.2s;
}

.create-button:hover {
    transform: scale(1.1);
}

.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
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
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.close-button {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
}

.bookings-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.booking-card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s;
}

.booking-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.booking-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
}

.booking-title {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.booking-title h3 {
    margin: 0;
    font-size: 24px;
    color: #333;
    font-weight: bold;
}

.booking-id {
    display: none;
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.status-badge.confirmed {
    background-color: #4CAF50;
    color: white;
}

.status-badge.not_confirmed {
    background-color: #FFC107;
    color: black;
}

.booking-main-info {
    margin-bottom: 15px;
}

.booking-main-info p {
    margin: 5px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.booking-main-info p i {
    width: 20px;
    text-align: center;
}

.booking-details {
    border-top: 1px solid #eee;
    padding-top: 15px;
    margin-top: 15px;
}

.details-section,
.price-section {
    margin-bottom: 15px;
}

.booking-actions {
    display: flex;
    gap: 10px;
    margin-top: 15px;
    flex-wrap: wrap;
}

.action-button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    transition: background-color 0.2s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    flex: 1;
    min-width: 100px;
}

.action-button.expand {
    background-color: #2196F3;
    color: white;
}

.action-button.edit {
    background-color: #FFC107;
    color: black;
}

.action-button.delete {
    background-color: #F44336;
    color: white;
}

.action-button.confirm {
    background-color: #4CAF50;
    color: white;
}

.error {
    color: #F44336;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
    background-color: #ffebee;
}

.loading {
    text-align: center;
    padding: 20px;
    color: #666;
}

.no-bookings {
    text-align: center;
    padding: 40px;
    color: #666;
    background: #f5f5f5;
    border-radius: 8px;
}

.page-title {
    color: #333;
    margin-bottom: 30px;
    font-size: 24px;
}

/* Стили для формы */
.booking-form {
    display: grid;
    gap: 15px;
}

.booking-form label {
    display: flex;
    flex-direction: column;
    gap: 5px;
}

.booking-form input,
.booking-form select,
.booking-form textarea {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.booking-form input:focus,
.booking-form select:focus,
.booking-form textarea:focus {
    border-color: #2196F3;
    outline: none;
}

.confirmation-modal {
    max-width: 400px;
    text-align: center;
}

.confirmation-content {
    padding: 20px 0;
}

.confirmation-step {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.confirmation-description {
    font-size: 16px;
    color: #333;
    margin: 20px 0;
}

.confirmation-methods {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
}

.method-option {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.method-label {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
}

.method-label i {
    font-size: 18px;
    color: #666;
}

.code-input-container {
    margin: 20px 0;
}

.code-input {
    width: 100%;
    padding: 12px;
    font-size: 18px;
    text-align: center;
    letter-spacing: 4px;
    border: 2px solid #ddd;
    border-radius: 8px;
    transition: border-color 0.2s;
}

.code-input:focus {
    border-color: #2196F3;
    outline: none;
}

.confirmation-actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-top: 20px;
}

.action-button.cancel {
    background-color: #9e9e9e;
    color: white;
}

.action-button.cancel:hover {
    background-color: #757575;
}

.action-button.confirm {
    background-color: #4CAF50;
    color: white;
}

.action-button.confirm:hover {
    background-color: #388E3C;
}

.action-button i {
    margin-right: 8px;
}

.form-totals {
    margin-top: 20px;
    padding: 15px;
    background-color: #f5f5f5;
    border-radius: 8px;
}

.total-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    font-size: 16px;
    font-weight: 500;
}

.total-row:first-child {
    border-bottom: 1px solid #ddd;
    margin-bottom: 8px;
    padding-bottom: 12px;
}

.total-row:last-child {
    color: #4CAF50;
    font-size: 18px;
}

.page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.logout-button {
    background-color: #f44336;
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

.logout-button:hover {
    background-color: #d32f2f;
}

.logout-button i {
    font-size: 18px;
}

.header-actions {
    display: flex;
    gap: 10px;
    align-items: center;
}

.admin-button {
    background-color: #2196F3;
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

.admin-button:hover {
    background-color: #1976D2;
}

.admin-button i {
    font-size: 18px;
}

/* Мобильные стили */
@media (max-width: 768px) {
    .bookings-container {
        padding: 10px;
    }

    .bookings-grid {
        grid-template-columns: 1fr;
        gap: 15px;
    }

    .booking-card {
        padding: 15px;
    }

    .booking-header {
        flex-direction: column;
        gap: 10px;
    }

    .booking-title h3 {
        font-size: 20px;
    }

    .status-badge {
        align-self: flex-start;
    }

    .booking-main-info p {
        font-size: 14px;
    }

    .booking-main-info p i {
        width: 16px;
    }

    .booking-details {
        padding-top: 10px;
        margin-top: 10px;
    }

    .details-section p,
    .price-section p {
        font-size: 14px;
        margin: 5px 0;
    }

    .booking-actions {
        flex-direction: column;
        gap: 8px;
    }

    .action-button {
        width: 100%;
        padding: 10px;
    }

    .create-button {
        width: 50px;
        height: 50px;
        bottom: 20px;
        right: 20px;
        font-size: 20px;
    }

    .modal-content {
        width: 95%;
        padding: 15px;
        margin: 10px;
    }

    .booking-form {
        gap: 10px;
    }

    .booking-form label {
        font-size: 14px;
    }

    .booking-form input,
    .booking-form select,
    .booking-form textarea {
        padding: 10px;
        font-size: 14px;
    }

    .confirmation-methods {
        flex-direction: column;
        gap: 10px;
    }

    .method-option {
        padding: 10px;
        border: 1px solid #ddd;
        border-radius: 4px;
    }

    .confirmation-actions {
        flex-direction: column;
    }

    .confirmation-actions .action-button {
        width: 100%;
    }

    .confirmation-modal {
        width: 90%;
        max-width: 350px;
    }

    .confirmation-description {
        font-size: 15px;
        margin: 15px 0;
    }
}

@media (max-width: 480px) {
    .booking-card {
        padding: 12px;
    }

    .booking-title h3 {
        font-size: 18px;
    }

    .booking-main-info p {
        font-size: 13px;
    }

    .action-button {
        font-size: 13px;
    }

    .create-button {
        width: 45px;
        height: 45px;
        font-size: 18px;
    }
}
</style>
