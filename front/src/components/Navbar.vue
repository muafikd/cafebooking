<template>
  <nav class="navbar">
    <div class="nav-brand">
      <i class="fas fa-coffee"></i>
      <span>Система управления кафе</span>
    </div>
    
    <!-- Бургер меню для мобильной версии -->
    <button class="burger-menu" @click="toggleMenu" :class="{ 'active': isMenuOpen }">
      <span></span>
      <span></span>
      <span></span>
    </button>

    <div class="nav-links" :class="{ 'active': isMenuOpen }">
      <router-link to="/bookings" class="nav-link" @click="closeMenu">
        <i class="fas fa-list"></i>
        <span>Заявки</span>
      </router-link>
      <router-link to="/calendar" class="nav-link" @click="closeMenu">
        <i class="fas fa-calendar"></i>
        <span>Календарь</span>
      </router-link>
      <router-link v-if="isSuperAdmin" to="/cafes" class="nav-link" @click="closeMenu">
        <i class="fas fa-store"></i>
        <span>Кафе</span>
      </router-link>
      <router-link v-if="isSuperAdmin" to="/users" class="nav-link" @click="closeMenu">
        <i class="fas fa-users"></i>
        <span>Пользователи</span>
      </router-link>
      <button @click="logout" class="nav-link logout">
        <i class="fas fa-sign-out-alt"></i>
        <span>Выход</span>
      </button>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'Navbar',
  setup() {
    const router = useRouter()
    const isSuperAdmin = ref(false)
    const isMenuOpen = ref(false)

    const toggleMenu = () => {
      isMenuOpen.value = !isMenuOpen.value
    }

    const closeMenu = () => {
      isMenuOpen.value = false
    }

    const checkUserRole = async () => {
      try {
        const token = localStorage.getItem('access')
        if (!token) return

        const response = await axios.get('http://127.0.0.1:8000/api/user/', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        isSuperAdmin.value = response.data.is_superuser
      } catch (error) {
        console.error('Ошибка при проверке роли пользователя:', error)
      }
    }

    const logout = async () => {
      try {
        const token = localStorage.getItem('access')
        await axios.post('http://127.0.0.1:8000/api/logout/', {}, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        })
        localStorage.removeItem('access')
        router.push('/login')
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      }
    }

    onMounted(() => {
      checkUserRole()
    })

    return {
      isSuperAdmin,
      logout,
      isMenuOpen,
      toggleMenu,
      closeMenu
    }
  }
}
</script>

<style scoped>
.navbar {
  background: #2c3e50;
  padding: 0.8rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: relative;
}

.nav-brand {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
}

.nav-brand i {
  font-size: 1.4rem;
}

.nav-links {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  font-weight: 500;
  font-size: 0.95rem;
}

.nav-link i {
  font-size: 1rem;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: white;
}

.nav-link.router-link-active {
  background-color: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-link.logout {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.95rem;
  color: rgba(255, 255, 255, 0.9);
}

.nav-link.logout:hover {
  color: #ff6b6b;
  background-color: rgba(255, 107, 107, 0.1);
}

.burger-menu {
  display: none;
  flex-direction: column;
  justify-content: space-between;
  width: 30px;
  height: 21px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  z-index: 1000;
}

.burger-menu span {
  width: 100%;
  height: 3px;
  background-color: white;
  border-radius: 3px;
  transition: all 0.3s ease;
}

.burger-menu.active span:nth-child(1) {
  transform: translateY(9px) rotate(45deg);
}

.burger-menu.active span:nth-child(2) {
  opacity: 0;
}

.burger-menu.active span:nth-child(3) {
  transform: translateY(-9px) rotate(-45deg);
}

@media (max-width: 768px) {
  .burger-menu {
    display: flex;
  }

  .nav-links {
    position: fixed;
    top: 0;
    right: -100%;
    width: 80%;
    max-width: 300px;
    height: 100vh;
    background: #2c3e50;
    flex-direction: column;
    padding: 80px 20px 20px;
    transition: right 0.3s ease;
    z-index: 999;
  }

  .nav-links.active {
    right: 0;
  }

  .nav-link {
    width: 100%;
    padding: 1rem;
    justify-content: flex-start;
  }

  .nav-link i {
    width: 24px;
  }

  .nav-brand span {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0.8rem 1rem;
  }
}
</style> 