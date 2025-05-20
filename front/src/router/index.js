import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import BookingsList from '../views/BookingsList.vue'
import CafesManagement from '../views/CafesManagement.vue'
import UsersManagement from '../views/UsersManagement.vue'
import CalendarView from '../views/CalendarView.vue'

const router = createRouter({
    history: createWebHistory(),
    routes: [
        {
            path: '/login',
            name: 'login',
            component: Login
        },
        {
            path: '/bookings',
            name: 'bookings',
            component: BookingsList,
            meta: { requiresAuth: true }
        },
        {
            path: '/calendar',
            name: 'calendar',
            component: CalendarView,
            meta: { requiresAuth: true }
        },
        {
            path: '/cafes',
            name: 'cafes',
            component: CafesManagement,
            meta: { requiresAuth: true }
        },
        {
            path: '/users',
            name: 'users',
            component: UsersManagement,
            meta: { requiresAuth: true }
        },
        {
            path: '/',
            redirect: '/bookings'
        }
    ]
})

router.beforeEach((to, from, next) => {
    const isAuthenticated = !!localStorage.getItem('access')
    
    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/login')
    } else if (to.path === '/login' && isAuthenticated) {
        next('/bookings')
    } else {
        next()
    }
})

export default router
