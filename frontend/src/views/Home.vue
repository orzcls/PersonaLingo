<template>
  <div class="min-h-[calc(100vh-8rem)]">
    <!-- Hero Section -->
    <section class="relative overflow-hidden py-20 lg:py-32">
      <!-- Background gradient effects -->
      <div class="absolute inset-0 bg-gradient-to-b from-accent-500/5 to-transparent"></div>
      <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-accent-500/10 rounded-full blur-3xl"></div>
      <div class="absolute bottom-1/4 right-1/4 w-96 h-96 bg-secondary-500/10 rounded-full blur-3xl"></div>

      <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <!-- Title -->
        <h1 class="text-5xl lg:text-7xl font-bold mb-6">
          <span class="bg-gradient-to-r from-accent-400 via-secondary-400 to-primary-400 bg-clip-text text-transparent">
            PersonaLingo
          </span>
        </h1>

        <!-- Subtitle -->
        <p class="text-xl lg:text-2xl text-dark-300 mb-12 max-w-3xl mx-auto leading-relaxed">
          AI-Powered Personalized IELTS Speaking Corpus Generator
        </p>

        <!-- CTA Button -->
        <router-link
          to="/questionnaire"
          class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-accent-500 to-secondary-500 text-white font-semibold rounded-xl shadow-lg shadow-accent-500/25 hover:shadow-accent-500/40 hover:scale-105 transition-all duration-300"
        >
          开始生成你的专属语料库
          <svg class="ml-2 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </router-link>
      </div>
    </section>

    <!-- Features Section -->
    <section class="py-20 bg-dark-900/50">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 class="text-3xl font-bold text-center text-white mb-16">核心功能</h2>

        <div class="grid md:grid-cols-3 gap-8">
          <!-- Feature 1: MBTI -->
          <div class="group p-8 bg-dark-800/50 border border-dark-700 rounded-2xl hover:border-accent-500/50 transition-all duration-300">
            <div class="w-14 h-14 bg-accent-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-accent-500/20 transition-colors">
              <svg class="w-7 h-7 text-accent-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">MBTI 性格分析</h3>
            <p class="text-dark-400 leading-relaxed">
              通过专业 MBTI 测评了解你的性格特征，为语料库生成提供个性化基础。
            </p>
          </div>

          <!-- Feature 2: Personalized Corpus -->
          <div class="group p-8 bg-dark-800/50 border border-dark-700 rounded-2xl hover:border-secondary-500/50 transition-all duration-300">
            <div class="w-14 h-14 bg-secondary-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-secondary-500/20 transition-colors">
              <svg class="w-7 h-7 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">个性化语料库</h3>
            <p class="text-dark-400 leading-relaxed">
              结合你的兴趣爱好与性格特点，AI 生成专属于你的 IELTS Speaking 语料。
            </p>
          </div>

          <!-- Feature 3: Agent Skill Export -->
          <div class="group p-8 bg-dark-800/50 border border-dark-700 rounded-2xl hover:border-primary-500/50 transition-all duration-300">
            <div class="w-14 h-14 bg-primary-500/10 rounded-xl flex items-center justify-center mb-6 group-hover:bg-primary-500/20 transition-colors">
              <svg class="w-7 h-7 text-primary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
            <h3 class="text-xl font-semibold text-white mb-3">Agent Skill 导出</h3>
            <p class="text-dark-400 leading-relaxed">
              将语料库导出为 Agent Skill 格式，可直接导入 AI 助手使用。
            </p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
</script>
