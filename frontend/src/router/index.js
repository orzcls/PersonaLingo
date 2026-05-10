import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Questionnaire from '../views/Questionnaire.vue'
import Generating from '../views/Generating.vue'
import Corpus from '../views/Corpus.vue'
import Export from '../views/Export.vue'
import Topics from '../views/Topics.vue'
import Chat from '../views/Chat.vue'
import Notes from '../views/Notes.vue'
import Settings from '../views/Settings.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/questionnaire', name: 'Questionnaire', component: Questionnaire },
  { path: '/generating', name: 'Generating', component: Generating },
  { path: '/corpus', name: 'Corpus', component: Corpus },
  { path: '/topics', name: 'Topics', component: Topics },
  { path: '/chat', name: 'Chat', component: Chat },
  { path: '/notes', name: 'Notes', component: Notes },
  { path: '/settings', name: 'Settings', component: Settings },
  { path: '/export', name: 'Export', component: Export }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
