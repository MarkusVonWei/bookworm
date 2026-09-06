import { createRouter, createWebHistory } from 'vue-router'
import Bookshelf from '../views/Bookshelf.vue'
import BookDetail from '../views/BookDetail.vue'
import Records from '../views/Records.vue'
import My from '../views/My.vue'

const routes = [
  {
    path: '/',
    name: 'Bookshelf',
    component: Bookshelf
  },
  {
    path: '/book/:id',
    name: 'BookDetail',
    component: BookDetail
  },
  {
    path: '/records',
    name: 'Records',
    component: Records
  },
  {
    path: '/my',
    name: 'My',
    component: My
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
