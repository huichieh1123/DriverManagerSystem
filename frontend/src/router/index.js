import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/login' // Default redirect to login page
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/LoginPage.vue')
  },
  {
    path: '/company',
    name: 'Company',
    component: () => import('../views/CompanyPage.vue'),
    meta: { requiresAuth: true, roles: ['company'] }
  },
  {
    path: '/dispatcher',
    name: 'Dispatcher',
    component: () => import('../views/DispatcherPage.vue'),
    meta: { requiresAuth: true, roles: ['dispatcher'] }
  },
  {
    path: '/driver',
    name: 'Driver',
    component: () => import('../views/DriverPage.vue'),
    meta: { requiresAuth: true, roles: ['driver'] }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/ProfilePage.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard for authentication and role-based access
router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiredRoles = to.meta.roles
  const currentUser = JSON.parse(localStorage.getItem('currentUser')) // Get current user from localStorage

  if (requiresAuth && !currentUser) {
    next('/login') // Redirect to login if not authenticated
  } else if (requiredRoles && currentUser) {
    const hasRequiredRole = requiredRoles.some(role => currentUser.roles.includes(role))
    if (!hasRequiredRole) {
      alert('You do not have permission to access this page.')
      next(from.path || '/') // Redirect back or to home
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
