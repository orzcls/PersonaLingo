<template>
  <div class="min-h-screen flex flex-col bg-paper-50 text-ink-700">
    <!-- Header -->
    <header class="sticky top-0 z-50 bg-paper-50/85 backdrop-blur-sm hairline-b">
      <div class="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div class="flex items-center justify-between h-[72px]">
          <!-- Logo -->
          <router-link to="/" class="flex items-baseline gap-2 group select-none">
            <span
              class="font-display italic text-[2rem] leading-none text-ink-900"
              style="font-variation-settings: 'opsz' 144, 'SOFT' 60;"
            >P</span>
            <span class="font-serif text-lg text-ink-900 tracking-tight">ersonaLingo</span>
            <span class="hidden lg:inline-block ml-3 field-label pt-2">A Field Notebook</span>
          </router-link>

          <!-- Navigation (desktop) -->
          <nav class="hidden md:flex items-end gap-5">
            <router-link
              v-for="(item, idx) in navItems"
              :key="item.to"
              :to="item.to"
              class="nav-link group relative flex items-baseline gap-1.5 py-2 text-ink-700 hover:text-ink-900 transition-colors duration-200"
              :exact-active-class="item.exact ? 'nav-active' : ''"
              :active-class="item.exact ? '' : 'nav-active'"
            >
              <span class="font-mono text-[0.65rem] text-ochre-500 tracking-[0.22em] tabular-nums">
                {{ String(idx + 1).padStart(2, '0') }}
              </span>
              <span class="font-serif text-[0.98rem]">{{ t(`nav.${item.key}`) }}</span>
            </router-link>
          </nav>

          <!-- Mobile toggle -->
          <button
            class="md:hidden p-2 -mr-2 text-ink-700 hover:text-ink-900 transition-colors"
            @click="drawerOpen = !drawerOpen"
            :aria-label="drawerOpen ? 'Close menu' : 'Open menu'"
          >
            <svg class="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path v-if="!drawerOpen" stroke-linecap="round" d="M4 7h16M4 12h16M4 17h10" />
              <path v-else stroke-linecap="round" d="M6 6l12 12M6 18L18 6" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile drawer -->
      <transition name="drawer">
        <nav
          v-if="drawerOpen"
          class="md:hidden hairline-t bg-paper-50/95 backdrop-blur-sm"
        >
          <div class="max-w-7xl mx-auto px-5 py-4 flex flex-col divide-y divide-ink-200/40">
            <router-link
              v-for="(item, idx) in navItems"
              :key="item.to"
              :to="item.to"
              @click="drawerOpen = false"
              class="flex items-baseline gap-3 py-3 group"
              :exact-active-class="item.exact ? 'nav-active' : ''"
              :active-class="item.exact ? '' : 'nav-active'"
            >
              <span class="font-mono text-[0.68rem] text-ochre-500 tracking-[0.22em] w-8 tabular-nums">
                {{ String(idx + 1).padStart(2, '0') }}
              </span>
              <span class="font-serif text-lg text-ink-900">{{ t(`nav.${item.key}`) }}</span>
            </router-link>
          </div>
        </nav>
      </transition>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="hairline-t py-8 mt-16">
      <div class="max-w-7xl mx-auto px-5 sm:px-8 lg:px-12">
        <div class="flex flex-col md:flex-row md:items-baseline md:justify-between gap-3">
          <p class="font-serif italic text-ink-500 text-sm">
            {{ t('footer.copyright') }}
          </p>
          <p class="field-label">Crafted with ink, not just tokens.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from '../i18n'

const { t } = useI18n()
const drawerOpen = ref(false)

const navItems = [
  { to: '/',              key: 'home',          exact: true  },
  { to: '/questionnaire', key: 'questionnaire', exact: false },
  { to: '/topics',        key: 'topics',        exact: false },
  { to: '/corpus',        key: 'corpus',        exact: false },
  { to: '/chat',          key: 'chat',          exact: false },
  { to: '/notes',         key: 'notes',         exact: false },
  { to: '/export',        key: 'export',        exact: false },
  { to: '/settings',      key: 'settings',      exact: false }
]
</script>

<style scoped>
.nav-link::after {
  content: '';
  position: absolute;
  left: 0;
  right: 100%;
  bottom: -1px;
  height: 2px;
  background: #B8692B;
  transition: right .36s cubic-bezier(.2, .8, .2, 1);
}
.nav-link:hover::after { right: 40%; }
.nav-link.nav-active   { color: #1B1F2A; }
.nav-link.nav-active::after { right: 20%; }

.drawer-enter-active,
.drawer-leave-active {
  transition: transform .32s cubic-bezier(.2, .8, .2, 1), opacity .2s ease;
  transform-origin: top center;
}
.drawer-enter-from { opacity: 0; transform: translateY(-8px); }
.drawer-leave-to   { opacity: 0; transform: translateY(-8px); }
</style>
