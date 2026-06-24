import { createRouter, createWebHashHistory } from 'vue-router'
import CardNewsPage from '@/pages/CardNewsPage.vue'
import PodcastPage from '@/pages/PodcastPage.vue'
import AskPage from '@/pages/AskPage.vue'
import MePage from '@/pages/MePage.vue'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', redirect: '/news' },
    { path: '/news', name: 'news', component: CardNewsPage },
    { path: '/podcast', name: 'podcast', component: PodcastPage },
    { path: '/ask', name: 'ask', component: AskPage },
    { path: '/me', name: 'me', component: MePage },
  ],
})

export default router
