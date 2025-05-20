<template>
    <div class="calendar-container">
        <div class="page-header">
            <h2 class="page-title">Календарь событий</h2>
        </div>

        <div v-if="loading" class="loading">
            <div class="spinner"></div>
            <p>Загрузка бронирований...</p>
        </div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else>
            <div class="calendar-header">
                <h2>Календарь бронирований</h2>
                <div class="calendar-controls">
                    <button @click="prevMonth" class="btn btn-secondary">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                    <span class="current-month">{{ currentMonth }}</span>
                    <button @click="nextMonth" class="btn btn-secondary">
                        <i class="fas fa-chevron-right"></i>
                    </button>
                </div>
            </div>

            <div class="calendar-wrapper">
                <Calendar
                    v-model="selectedDate"
                    :attributes="calendarAttributes"
                    @dayclick="onDayClick"
                    is-expanded
                    trim-weeks
                    :first-day-of-week="1"
                />
            </div>

            <!-- Модальное окно для просмотра бронирований -->
            <div v-if="showModal" class="modal">
                <div class="modal-content">
                    <h3>Бронирования на {{ selectedDateFormatted }}</h3>
                    <div v-if="selectedDateBookings.length === 0" class="no-bookings">
                        Нет бронирований на этот день
                    </div>
                    <div v-else class="bookings-list">
                        <div v-for="booking in selectedDateBookings" :key="booking.id" class="booking-item">
                            <div class="booking-header">
                                <span class="booking-time">{{ formatTime(booking.start_time) }} - {{ formatTime(booking.end_time) }}</span>
                                <span :class="['booking-status', booking.status]">{{ getStatusText(booking.status) }}</span>
                            </div>
                            <div class="booking-details">
                                <p><strong>Клиент:</strong> {{ booking.client_name }}</p>
                                <p><strong>Телефон:</strong> {{ booking.client_phone }}</p>
                                <p><strong>Количество гостей:</strong> {{ booking.number_of_people}}</p>
                                <p><strong>Название мероприятия:</strong> {{ booking.event_name}}</p>
                                <p><strong>Предоплата:</strong> {{ booking.prepayment}} ₸</p>
                                <p><strong>Цена за одного человека:</strong> {{ booking.price_per_visitor}} ₸</p>
                            </div>
                        </div>
                    </div>
                    <button @click="showModal = false" class="btn btn-primary">Закрыть</button>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { Calendar } from 'v-calendar';
import axios from '../plugins/axios';
import { format, parseISO, startOfDay, endOfDay } from 'date-fns';
import { ru } from 'date-fns/locale';

export default {
    name: 'CalendarView',
    components: {
        Calendar
    },
    data() {
        return {
            bookings: [],
            loading: true,
            error: null,
            selectedDate: new Date(),
            showModal: false,
            selectedDateBookings: []
        };
    },
    computed: {
        currentMonth() {
            return format(this.selectedDate, 'LLLL yyyy', { locale: ru });
        },
        selectedDateFormatted() {
            return format(this.selectedDate, 'd MMMM yyyy', { locale: ru });
        },
        calendarAttributes() {
            return this.bookings.map(booking => ({
                key: booking.id,
                dot: {
                    color: booking.status === 'confirmed' ? 'green' : 'orange'
                },
                dates: new Date(booking.start_time),
                popover: {
                    label: `${booking.client_name} - ${this.formatTime(booking.start_time)}`
                }
            }));
        }
    },
    methods: {
        async fetchBookings() {
            try {
                this.loading = true;
                this.error = null;
                const response = await axios.get('/api/bookings/');
                console.log('Полученные бронирования:', response.data);
                
                // Преобразуем даты в правильный формат
                this.bookings = response.data.map(booking => {
                    // Предполагаем, что дата приходит в формате "YYYY-MM-DD"
                    const [year, month, day] = booking.date.split('-').map(Number);
                    const [hours, minutes] = booking.time.split(':').map(Number);
                    
                    const startTime = new Date(year, month - 1, day, hours, minutes);
                    const endTime = new Date(startTime);
                    endTime.setHours(startTime.getHours() + booking.duration_hours);
                    
                    return {
                        ...booking,
                        start_time: startTime.toISOString(),
                        end_time: endTime.toISOString()
                    };
                });
                
                console.log('Обработанные бронирования:', this.bookings);
            } catch (error) {
                if (error.response?.status === 404) {
                    this.error = 'Сервис бронирований недоступен';
                } else if (error.response?.status === 401) {
                    this.error = 'Требуется авторизация';
                } else {
                    this.error = 'Ошибка при загрузке бронирований';
                }
                console.error('Error fetching bookings:', error);
            } finally {
                this.loading = false;
            }
        },
        formatTime(dateString) {
            if (!dateString) return '';
            try {
                const date = new Date(dateString);
                return format(date, 'HH:mm');
            } catch (error) {
                console.error('Error formatting time:', error, 'for date:', dateString);
                return '';
            }
        },
        formatDate(date) {
            if (!date) return '';
            try {
                return format(new Date(date), 'd MMMM yyyy', { locale: ru });
            } catch (error) {
                console.error('Error formatting date:', error, 'for date:', date);
                return '';
            }
        },
        getStatusText(status) {
            const statusMap = {
                'pending': 'Ожидает подтверждения',
                'confirmed': 'Подтверждено',
                'cancelled': 'Отменено'
            };
            return statusMap[status] || status;
        },
        onDayClick(day) {
            console.log('Выбран день:', day.date);
            this.selectedDate = day.date;
            this.selectedDateBookings = this.bookings.filter(booking => {
                const bookingDate = new Date(booking.start_time);
                const selectedDate = new Date(day.date);
                console.log('Сравнение дат:', {
                    bookingDate: bookingDate.toISOString(),
                    selectedDate: selectedDate.toISOString(),
                    booking: booking
                });
                return startOfDay(bookingDate).getTime() === startOfDay(selectedDate).getTime();
            });
            console.log('Найденные бронирования:', this.selectedDateBookings);
            this.showModal = true;
        },
        prevMonth() {
            const newDate = new Date(this.selectedDate);
            newDate.setMonth(newDate.getMonth() - 1);
            this.selectedDate = newDate;
            console.log('Предыдущий месяц:', this.selectedDate);
        },
        nextMonth() {
            const newDate = new Date(this.selectedDate);
            newDate.setMonth(newDate.getMonth() + 1);
            this.selectedDate = newDate;
            console.log('Следующий месяц:', this.selectedDate);
        }
    },
    mounted() {
        this.fetchBookings();
    }
};
</script>

<style>
.calendar-container {
    max-width: 1800px;
    margin: 0 auto;
    padding: 20px;
}

.calendar-wrapper {
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 20px;
}

/* Стили для v-calendar */
.vc-container {
    --vc-accent-50: #f0f9ff;
    --vc-accent-100: #e0f2fe;
    --vc-accent-200: #bae6fd;
    --vc-accent-300: #7dd3fc;
    --vc-accent-400: #38bdf8;
    --vc-accent-500: #0ea5e9;
    --vc-accent-600: #0284c7;
    --vc-accent-700: #0369a1;
    --vc-accent-800: #075985;
    --vc-accent-900: #0c4a6e;
    border: none;
    font-family: inherit;
    width: 100%;
}

.vc-header {
    padding: 20px 0;
}

.vc-weeks {
    padding: 0;
    display: flex;
    flex-direction: column;
}

.vc-week {
    display: flex;
    justify-content: center;
}

.vc-weekday {
    font-weight: 500;
    color: #4b5563;
    padding: 15px 0;
    font-size: 1.1em;
    text-align: center;
    width: 60px;
    margin: 3px;
}

.vc-day {
    padding: 12px 0;
    height: 60px;
    width: 60px;
    margin: 3px;
    position: relative;
}

.vc-day-content {
    font-weight: 500;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.2em;
}

.vc-day-content:hover {
    background-color: var(--vc-accent-100);
    border-radius: 50%;
}

.vc-day.is-today {
    background-color: var(--vc-accent-50);
    border-radius: 50%;
}

.vc-day.is-selected {
    background-color: var(--vc-accent-500);
    border-radius: 50%;
}

.vc-day.is-selected .vc-day-content {
    color: white;
}

.vc-day.has-events {
    position: relative;
}

.vc-day.has-events::after {
    content: '';
    position: absolute;
    bottom: 8px;
    left: 50%;
    transform: translateX(-50%);
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background-color: var(--vc-accent-500);
}

.calendar-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
}

.calendar-controls {
    display: flex;
    align-items: center;
    gap: 15px;
}

.current-month {
    font-size: 1.4em;
    font-weight: 500;
    min-width: 250px;
    text-align: center;
}

.loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 400px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin-bottom: 20px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error {
    color: #dc3545;
    text-align: center;
    padding: 20px;
    background-color: #f8d7da;
    border-radius: 4px;
    margin: 20px 0;
}

.modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.modal-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    max-width: 600px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
}

.bookings-list {
    margin: 20px 0;
}

.booking-item {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
}

.booking-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}

.booking-time {
    font-weight: 500;
    font-size: 1.1em;
}

.booking-status {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
}

.booking-status.confirmed {
    background-color: #d4edda;
    color: #155724;
}

.booking-status.pending {
    background-color: #fff3cd;
    color: #856404;
}

.booking-status.cancelled {
    background-color: #f8d7da;
    color: #721c24;
}

.booking-details p {
    margin: 5px 0;
}

.no-bookings {
    text-align: center;
    color: #6c757d;
    padding: 20px;
}

.btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.3s;
}

.btn-primary {
    background-color: #007bff;
    color: white;
}

.btn-primary:hover {
    background-color: #0056b3;
}

.btn-secondary {
    background-color: #6c757d;
    color: white;
}

.btn-secondary:hover {
    background-color: #545b62;
}

.page-header {
    margin-bottom: 30px;
}

.page-title {
    color: #333;
    font-size: 24px;
    margin: 0;
}
</style> 