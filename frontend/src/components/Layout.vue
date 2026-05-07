<template>
  <div class="min-h-screen flex flex-col bg-dark-950">
    <!-- Header -->
    <header class="border-b border-dark-800 bg-dark-900/80 backdrop-blur-sm sticky top-0 z-50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center space-x-2">
            <div class="w-8 h-8 bg-gradient-to-br from-accent-400 to-secondary-500 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">P</span>
            </div>
            <span class="text-xl font-bold text-white">PersonaLingo</span>
          </router-link>

          <!-- Navigation -->
          <nav class="hidden md:flex items-center space-x-6">
            <router-link
              to="/"
              class="text-dark-300 hover:text-white transition-colors duration-200"
              active-class="text-accent-400"
            >
              首页
            </router-link>
            <router-link
              to="/questionnaire"
              class="text-dark-300 hover:text-white transition-colors duration-200"
              active-class="text-accent-400"
            >
              问卷
            </router-link>
            <router-link
              to="/corpus"
              class="text-dark-300 hover:text-white transition-colors duration-200"
              active-class="text-accent-400"
            >
              语料库
            </router-link>
            <router-link
              to="/export"
              class="text-dark-300 hover:text-white transition-colors duration-200"
              active-class="text-accent-400"
            >
              导出
            </router-link>
          </nav>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="border-t border-dark-800 bg-dark-900/50 py-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <p class="text-dark-400 text-sm">
          &copy; 2026 PersonaLingo. AI-Powered Personalized IELTS Speaking Corpus Generator.
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
</script>
