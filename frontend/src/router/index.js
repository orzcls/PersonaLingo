import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Questionnaire from '../views/Questionnaire.vue'
import Generating from '../views/Generating.vue'
import Corpus from '../views/Corpus.vue'
import Export from '../views/Export.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/questionnaire',
    name: 'Questionnaire',
    component: Questionnaire
  },
  {
    path: '/generating',
    name: 'Generating',
    component: Generating
  },
  {
    path: '/corpus',
    name: 'Corpus',
    component: Corpus
  },
  {
    path: '/export',
    name: 'Export',
    component: Export
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
