<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 py-12 sm:py-16">
    <!-- Page Header -->
    <header class="mb-12 text-center space-y-3">
      <p class="num-chapter">§ 08 · Instrument panel</p>
      <h1 class="font-display text-5xl text-ink-900" style="font-variation-settings:'opsz' 144, 'SOFT' 50;">
        {{ t('settings.title') }}
      </h1>
      <p class="text-ink-500 font-serif italic">{{ t('settings.subtitle') }}</p>
    </header>

    <!-- Status Indicator -->
    <div class="mb-10 px-5 py-4 hairline flex items-center gap-3"
         :class="isConfigured ? 'bg-sage-500/10' : 'bg-paper-100'">
      <span class="relative flex w-2.5 h-2.5">
        <span v-if="isConfigured" class="absolute inset-0 rounded-full bg-sage-500 animate-ping opacity-60"></span>
        <span class="relative w-2.5 h-2.5 rounded-full" :class="isConfigured ? 'bg-sage-500' : 'bg-ink-300'"></span>
      </span>
      <span class="font-mono text-xs tracking-[0.22em]" :class="isConfigured ? 'text-sage-500' : 'text-ink-500'">
        {{ isConfigured ? t('settings.connected') : t('settings.notConfigured') }}
      </span>
    </div>

    <!-- LLM Provider Section -->
    <section class="paper-card p-8 mb-8">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-3">
        <span class="px-4">{{ t('settings.provider') }}</span>
      </h2>
      <p class="text-ink-500 text-sm font-serif italic text-center mb-6">{{ t('settings.providerDesc') }}</p>

      <div class="grid grid-cols-2 gap-4 mb-8">
        <!-- OpenAI Card -->
        <button
          @click="settings.provider = 'openai'"
          class="p-5 transition-colors duration-300 text-left"
          :class="settings.provider === 'openai' ? 'bg-paper-100 hairline-strong' : 'hairline hover:bg-paper-100/50'"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-11 h-11 hairline flex items-center justify-center bg-paper-50">
              <span class="font-display italic text-2xl text-ink-900">O</span>
            </div>
            <div>
              <p class="font-display italic text-ink-900">OpenAI</p>
              <p class="font-mono text-[10px] tracking-[0.22em] text-ink-500">OPENAI · COMPATIBLE</p>
            </div>
          </div>
          <div v-if="settings.provider === 'openai'" class="mt-3 pt-3 border-t border-ink-900/10">
            <span class="font-mono text-[10px] tracking-[0.22em] text-ochre-500">✓ SELECTED</span>
          </div>
        </button>

        <!-- Anthropic Card -->
        <button
          @click="settings.provider = 'anthropic'"
          class="p-5 transition-colors duration-300 text-left"
          :class="settings.provider === 'anthropic' ? 'bg-paper-100 hairline-strong' : 'hairline hover:bg-paper-100/50'"
        >
          <div class="flex items-center gap-3 mb-2">
            <div class="w-11 h-11 hairline flex items-center justify-center bg-paper-50">
              <span class="font-display italic text-2xl text-ink-900">A</span>
            </div>
            <div>
              <p class="font-display italic text-ink-900">Anthropic</p>
              <p class="font-mono text-[10px] tracking-[0.22em] text-ink-500">CLAUDE · SERIES</p>
            </div>
          </div>
          <div v-if="settings.provider === 'anthropic'" class="mt-3 pt-3 border-t border-ink-900/10">
            <span class="font-mono text-[10px] tracking-[0.22em] text-ochre-500">✓ SELECTED</span>
          </div>
        </button>
      </div>

      <!-- OpenAI Configuration -->
      <div v-if="settings.provider === 'openai'" class="space-y-5">
        <div>
          <label class="field-label mb-2 block">{{ t('settings.baseUrl') }}</label>
          <input v-model="settings.openaiBaseUrl" type="text" placeholder="https://api.openai.com/v1" class="input-hairline" />
          <p class="text-xs text-ink-500 font-serif italic mt-1">{{ t('settings.baseUrlHint') }}</p>
        </div>

        <div>
          <label class="field-label mb-2 block">{{ t('settings.apiKey') }}</label>
          <div class="relative">
            <input v-model="settings.openaiApiKey" :type="showOpenaiKey ? 'text' : 'password'"
                   @input="keyDirty.openai = true"
                   :placeholder="openaiKeySet ? '••••••••（已配置，输入新值可替换）' : 'sk-...'"
                   class="input-hairline pr-12 font-mono text-xs" />
            <button @click="showOpenaiKey = !showOpenaiKey"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-500 hover:text-ink-900 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path v-if="!showOpenaiKey" stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path v-if="!showOpenaiKey" stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                <path v-if="showOpenaiKey" stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.584 10.587a2 2 0 102.828 2.83M9.363 5.365A9.466 9.466 0 0112 5c4.478 0 8.268 2.943 9.542 7a9.956 9.956 0 01-4.132 5.411M6.228 6.228A9.956 9.956 0 002.458 12C3.732 16.057 7.522 19 12 19c1.61 0 3.131-.38 4.48-1.056" />
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="field-label mb-2 block">{{ t('settings.model') }}</label>
          <div class="flex gap-2">
            <select v-model="settings.openaiModel" class="flex-1 input-hairline appearance-none">
              <option value="" disabled>{{ openaiModels.length ? t('settings.model') + '...' : t('settings.noModels') }}</option>
              <option v-for="model in openaiModels" :key="model" :value="model">{{ model }}</option>
            </select>
            <button @click="fetchModels" :disabled="loadingModels"
                    class="px-4 py-2.5 hairline text-ink-700 hover:text-ink-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              <svg v-if="!loadingModels" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <div v-else class="w-3 h-3 rounded-full bg-ochre-500 animate-ink-breath"></div>
              <span class="font-serif italic text-sm">{{ t('settings.refreshModels') }}</span>
            </button>
          </div>
          <p v-if="modelError" class="font-serif italic text-xs text-rouge-600 mt-2">{{ modelError }}</p>
        </div>
      </div>

      <!-- Anthropic Configuration -->
      <div v-if="settings.provider === 'anthropic'" class="space-y-5">
        <div>
          <label class="field-label mb-2 block">{{ t('settings.baseUrl') }}</label>
          <input v-model="settings.anthropicBaseUrl" type="text" placeholder="https://api.anthropic.com" class="input-hairline" />
          <p class="text-xs text-ink-500 font-serif italic mt-1">{{ t('settings.baseUrlHintAnthropic') }}</p>
        </div>

        <div>
          <label class="field-label mb-2 block">{{ t('settings.apiKey') }}</label>
          <div class="relative">
            <input v-model="settings.anthropicApiKey" :type="showAnthropicKey ? 'text' : 'password'"
                   @input="keyDirty.anthropic = true"
                   :placeholder="anthropicKeySet ? '••••••••（已配置，输入新值可替换）' : 'sk-ant-...'"
                   class="input-hairline pr-12 font-mono text-xs" />
            <button @click="showAnthropicKey = !showAnthropicKey"
                    class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-500 hover:text-ink-900 transition-colors">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path v-if="!showAnthropicKey" stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path v-if="!showAnthropicKey" stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                <path v-if="showAnthropicKey" stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.584 10.587a2 2 0 102.828 2.83M9.363 5.365A9.466 9.466 0 0112 5c4.478 0 8.268 2.943 9.542 7a9.956 9.956 0 01-4.132 5.411M6.228 6.228A9.956 9.956 0 002.458 12C3.732 16.057 7.522 19 12 19c1.61 0 3.131-.38 4.48-1.056" />
              </svg>
            </button>
          </div>
        </div>

        <div>
          <label class="field-label mb-2 block">{{ t('settings.model') }}</label>
          <div class="flex gap-2">
            <select v-model="settings.anthropicModel" class="flex-1 input-hairline appearance-none">
              <option value="" disabled>{{ anthropicModels.length ? t('settings.model') + '...' : t('settings.noModels') }}</option>
              <option v-for="model in anthropicModels" :key="model" :value="model">{{ model }}</option>
            </select>
            <button @click="fetchModels" :disabled="loadingModels"
                    class="px-4 py-2.5 hairline text-ink-700 hover:text-ink-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2">
              <svg v-if="!loadingModels" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              <div v-else class="w-3 h-3 rounded-full bg-ochre-500 animate-ink-breath"></div>
              <span class="font-serif italic text-sm">{{ t('settings.refreshModels') }}</span>
            </button>
          </div>
          <p v-if="modelError" class="font-serif italic text-xs text-rouge-600 mt-2">{{ modelError }}</p>
        </div>
      </div>
    </section>

    <!-- Test Connection -->
    <section class="paper-card p-6 mb-8">
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h2 class="font-display italic text-ink-900 text-lg">{{ t('settings.testConnectionTitle') }}</h2>
          <p class="text-ink-500 text-sm font-serif italic">{{ t('settings.testConnectionDesc') }}</p>
        </div>
        <button @click="testApiConnection" :disabled="testingConnection"
                class="px-5 py-2.5 hairline text-ink-700 hover:text-ink-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-serif italic text-sm">
          <div v-if="testingConnection" class="w-3 h-3 rounded-full bg-ochre-500 animate-ink-breath"></div>
          <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
          <span>{{ t('settings.testConnection') }}</span>
        </button>
      </div>
      <div v-if="connectionResult" class="mt-4 px-4 py-3 hairline text-sm font-serif"
           :class="connectionResult.status === 'ok' ? 'bg-sage-500/10 text-sage-500' : 'bg-rouge-600/10 text-rouge-600'">
        {{ connectionResult.message }}
      </div>
    </section>

    <!-- Target Score Section -->
    <section class="paper-card p-8 mb-8">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-3">
        <span class="px-4">{{ t('settings.targetScore') }}</span>
      </h2>
      <p class="text-ink-500 text-sm font-serif italic text-center mb-6">{{ t('settings.targetScoreDesc') }}</p>

      <div class="grid grid-cols-4 gap-3">
        <button v-for="score in scoreOptions" :key="score" @click="settings.targetScore = score"
                class="py-4 text-center transition-colors duration-300"
                :class="settings.targetScore === score ? 'chip-ink-selected' : 'hairline text-ink-700 hover:text-ink-900'">
          <span class="font-display text-xl" style="font-variation-settings:'opsz' 144, 'SOFT' 40;">{{ score }}</span>
        </button>
      </div>
    </section>

    <!-- Language Section -->
    <section class="paper-card p-8 mb-10">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-6">
        <span class="px-4">{{ t('settings.language') }}</span>
      </h2>
      <div class="flex gap-3 justify-center">
        <button @click="setLocale('zh')"
                class="px-7 py-2.5 font-serif italic transition-colors duration-300"
                :class="locale === 'zh' ? 'chip-ink-selected' : 'hairline text-ink-500 hover:text-ink-900'">
          中文
        </button>
        <button @click="setLocale('en')"
                class="px-7 py-2.5 font-serif italic transition-colors duration-300"
                :class="locale === 'en' ? 'chip-ink-selected' : 'hairline text-ink-500 hover:text-ink-900'">
          English
        </button>
      </div>
    </section>

    <!-- Web Search Section -->
    <section class="paper-card p-8 mb-10">
      <h2 class="rule-heading font-display italic text-ink-900 text-xl mb-3">
        <span class="px-4">{{ t('settings.webSearch.title') }}</span>
      </h2>
      <p class="text-ink-500 text-sm font-serif italic text-center mb-6">{{ t('settings.webSearch.subtitle') }}</p>

      <!-- 1) 服务商选择（API + Local 分组） -->
      <div class="space-y-5 mb-6">
        <div>
          <p class="field-label mb-3">{{ t('settings.webSearch.apiProviders') }}</p>
          <div v-if="apiProviders.length === 0" class="text-xs font-serif italic text-ink-500 px-1">
            {{ t('settings.webSearch.loadingProviders') }}
          </div>
          <div v-else class="grid grid-cols-3 sm:grid-cols-4 gap-2">
            <button
              v-for="p in apiProviders"
              :key="p.id"
              @click="settings.searchProvider = p.id"
              :title="p.description || ''"
              class="px-3 py-2 text-left transition-colors duration-200"
              :class="settings.searchProvider === p.id ? 'chip-ink-selected' : 'hairline hover:bg-paper-100/50'"
            >
              <p class="font-display italic text-sm" :class="settings.searchProvider === p.id ? 'text-paper-50' : 'text-ink-900'">{{ p.name }}</p>
              <p class="font-mono text-[9px] tracking-widest" :class="settings.searchProvider === p.id ? 'text-paper-100/80' : (p.key_required ? 'text-ink-500' : 'text-sage-500')">{{ p.key_required ? 'KEY' : 'FREE' }}</p>
            </button>
          </div>
        </div>

        <div>
          <p class="field-label mb-3">{{ t('settings.webSearch.localProviders') }}</p>
          <div v-if="localProviders.length === 0" class="text-xs font-serif italic text-ink-500 px-1">
            {{ t('settings.webSearch.loadingProviders') }}
          </div>
          <div v-else class="grid grid-cols-3 gap-2">
            <button
              v-for="p in localProviders"
              :key="p.id"
              @click="settings.searchProvider = p.id"
              :title="p.description || ''"
              class="px-3 py-2 text-left transition-colors duration-200"
              :class="settings.searchProvider === p.id ? 'chip-ink-selected' : 'hairline hover:bg-paper-100/50'"
            >
              <p class="font-display italic text-sm" :class="settings.searchProvider === p.id ? 'text-paper-50' : 'text-ink-900'">{{ p.name }}</p>
              <p class="font-mono text-[9px] tracking-widest" :class="settings.searchProvider === p.id ? 'text-paper-100/80' : 'text-sage-500'">FREE</p>
            </button>
          </div>
        </div>

        <!-- API Key / Base URL（按 provider 元信息条件显示） -->
        <div v-if="selectedProvider && (selectedProvider.key_required || selectedProvider.base_url_required)" class="space-y-4">
          <div v-if="selectedProvider.key_required">
            <label class="field-label mb-2 block">{{ t('settings.webSearch.apiKey') }}</label>
            <div class="relative">
              <input v-model="settings.searchApiKey" :type="showSearchKey ? 'text' : 'password'"
                     @input="keyDirty.search = true"
                     :placeholder="searchKeySet ? '••••••••（已配置，输入新值可替换）' : 'key-...'"
                     class="input-hairline pr-12 font-mono text-xs" />
              <button @click="showSearchKey = !showSearchKey"
                      class="absolute right-3 top-1/2 -translate-y-1/2 text-ink-500 hover:text-ink-900 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="1.5" viewBox="0 0 24 24">
                  <path v-if="!showSearchKey" stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path v-if="!showSearchKey" stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  <path v-if="showSearchKey" stroke-linecap="round" stroke-linejoin="round" d="M3 3l18 18M10.584 10.587a2 2 0 102.828 2.83M9.363 5.365A9.466 9.466 0 0112 5c4.478 0 8.268 2.943 9.542 7a9.956 9.956 0 01-4.132 5.411M6.228 6.228A9.956 9.956 0 002.458 12C3.732 16.057 7.522 19 12 19c1.61 0 3.131-.38 4.48-1.056" />
                </svg>
              </button>
            </div>
            <p v-if="selectedProvider.api_key_url" class="text-xs font-serif italic text-ink-500 mt-1">
              <a :href="selectedProvider.api_key_url" target="_blank" rel="noopener" class="hover:text-ink-900 underline decoration-dotted underline-offset-2">{{ selectedProvider.api_key_url }} ↗</a>
            </p>
          </div>
          <div v-if="selectedProvider.base_url_required">
            <label class="field-label mb-2 block">{{ t('settings.webSearch.baseUrl') }}</label>
            <input v-model="settings.searchBaseUrl" type="text" placeholder="https://" class="input-hairline" />
          </div>
        </div>
      </div>

      <!-- 2) 常规设置 -->
      <div class="border-t border-ink-900/10 pt-6 mb-6">
        <p class="field-label mb-4">{{ t('settings.webSearch.general') }}</p>
        <div class="space-y-4">
          <label class="flex items-center justify-between gap-3 text-sm font-serif italic text-ink-700">
            <span>{{ t('settings.webSearch.includeDate') }}</span>
            <input type="checkbox" v-model="settings.searchIncludeDate" class="w-4 h-4 accent-ink-900" />
          </label>
          <div>
            <p class="text-sm font-serif italic text-ink-700 mb-2">{{ t('settings.webSearch.maxResults') }}</p>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="n in [1, 5, 20, 50, 100]"
                :key="n"
                @click="settings.searchMaxResults = n"
                class="px-3 py-1.5 text-sm font-serif italic transition-colors"
                :class="settings.searchMaxResults === n ? 'chip-ink-selected' : 'hairline text-ink-500 hover:text-ink-900'"
              >{{ n }}</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 3) 搜索结果压缩 -->
      <div class="border-t border-ink-900/10 pt-6 mb-6">
        <p class="field-label mb-4">{{ t('settings.webSearch.compression') }}</p>
        <div class="space-y-4">
          <div>
            <p class="text-sm font-serif italic text-ink-700 mb-2">{{ t('settings.webSearch.compressMethod') }}</p>
            <div class="flex gap-2 flex-wrap">
              <button
                v-for="opt in ['rag', 'truncate', 'none']"
                :key="opt"
                @click="settings.searchCompression = opt"
                class="px-3 py-1.5 text-sm font-serif italic transition-colors"
                :class="settings.searchCompression === opt ? 'chip-ink-selected' : 'hairline text-ink-500 hover:text-ink-900'"
              >{{ t(`settings.webSearch.compressOptions.${opt}`) }}</button>
            </div>
          </div>
          <div v-if="settings.searchCompression === 'rag'" class="space-y-4">
            <div>
              <p class="text-sm font-serif italic text-ink-700 mb-2">{{ t('settings.webSearch.chunkCount') }}</p>
              <input v-model.number="settings.searchChunkCount" type="number" min="1" max="20" class="input-hairline w-32" />
            </div>
            <div>
              <label class="field-label mb-2 block">{{ t('settings.webSearch.embeddingModel') }}</label>
              <select v-model="embeddingPresetId" @change="onEmbeddingPresetChange" class="input-hairline" :disabled="ragModelsLoading">
                <option v-if="ragModelsLoading" value="__loading">{{ t('settings.webSearch.ragPresetAuto') }}</option>
                <option v-for="p in embeddingPresets" :key="p.id || 'local'" :value="p.id">
                  {{ locale === 'zh' ? p.label_cn : p.label }}{{ p.dim ? ` (${p.dim}D)` : '' }}
                </option>
              </select>
              <input v-if="embeddingPresetId === 'custom'" v-model="settings.searchEmbeddingModel" type="text"
                     :placeholder="t('settings.webSearch.ragPresetCustom')" class="input-hairline mt-2" />
              <p class="text-xs font-serif italic text-ink-500 mt-1">
                {{ ragModelsError || currentEmbeddingNote || t('settings.webSearch.embeddingModelHint') }}
              </p>
            </div>
            <div>
              <label class="field-label mb-2 block">{{ t('settings.webSearch.embeddingDim') }}</label>
              <input v-model.number="settings.searchEmbeddingDim" type="number" min="0" max="8192"
                     :disabled="embeddingPresetId !== 'custom' && embeddingPresetId !== ''"
                     class="input-hairline w-32" />
              <p class="text-xs font-serif italic text-ink-500 mt-1">{{ t('settings.webSearch.embeddingDimHint') }}</p>
            </div>
            <div>
              <label class="field-label mb-2 block">{{ t('settings.webSearch.rerankerModel') }}</label>
              <select v-model="rerankerPresetId" @change="onRerankerPresetChange" class="input-hairline" :disabled="ragModelsLoading">
                <option v-if="ragModelsLoading" value="__loading">{{ t('settings.webSearch.ragPresetAuto') }}</option>
                <option v-for="p in rerankerPresets" :key="p.id || 'local'" :value="p.id">
                  {{ locale === 'zh' ? p.label_cn : p.label }}
                </option>
              </select>
              <input v-if="rerankerPresetId === 'custom'" v-model="settings.searchRerankerModel" type="text"
                     :placeholder="t('settings.webSearch.ragPresetCustom')" class="input-hairline mt-2" />
              <p class="text-xs font-serif italic text-ink-500 mt-1">
                {{ currentRerankerNote || t('settings.webSearch.rerankerModelHint') }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- 测试按钮 -->
      <div class="flex items-center justify-between gap-4 flex-wrap">
        <div v-if="searchTestResult" class="text-sm font-serif italic flex-1"
             :class="searchTestResult.status === 'ok' ? 'text-sage-500' : 'text-rouge-600'">
          {{ searchTestResult.message }}
        </div>
        <div v-else class="text-xs font-mono tracking-[0.22em] text-ink-500">—</div>
        <button @click="runSearchTest" :disabled="testingSearch"
                class="px-5 py-2.5 hairline text-ink-700 hover:text-ink-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-serif italic text-sm">
          <div v-if="testingSearch" class="w-3 h-3 rounded-full bg-ochre-500 animate-ink-breath"></div>
          <span>{{ testingSearch ? t('settings.webSearch.testing') : t('settings.webSearch.test') }}</span>
        </button>
      </div>
    </section>

    <!-- Save Button -->
    <div class="flex items-center justify-between gap-4 flex-wrap">
      <p v-if="saveMessage" class="text-sm font-serif italic" :class="saveSuccess ? 'text-sage-500' : 'text-rouge-600'">
        {{ saveMessage }}
      </p>
      <div v-else class="text-xs font-mono tracking-[0.22em] text-ink-500">— UNSAVED CHANGES WILL BE DISCARDED —</div>
      <button @click="saveSettings" :disabled="saving" class="btn-ink disabled:opacity-50 disabled:cursor-not-allowed">
        <span v-if="saving" class="flex items-center gap-2">
          <div class="w-3 h-3 rounded-full bg-paper-50 animate-ink-breath"></div>
          {{ t('settings.saving') }}
        </span>
        <span v-else class="flex items-center gap-2">{{ t('settings.save') }} <span class="text-ochre-300">→</span></span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getSettings, updateSettings, getAvailableModels, testConnection, getSearchProviders, getSearchRagModels, testSearch } from '../api/index.js'
import { useI18n } from '../i18n'

const { t, locale, setLocale } = useI18n()

const settings = ref({
  provider: 'openai',
  openaiBaseUrl: 'https://api.openai.com/v1',
  openaiApiKey: '',
  openaiModel: '',
  anthropicBaseUrl: 'https://api.anthropic.com',
  anthropicApiKey: '',
  anthropicModel: '',
  targetScore: '7.0',
  // Web Search
  searchProvider: 'tavily',
  searchApiKey: '',
  searchBaseUrl: '',
  searchIncludeDate: true,
  searchMaxResults: 20,
  searchCompression: 'rag',
  searchChunkCount: 3,
  searchEmbeddingModel: '',
  searchEmbeddingDim: 0,
  searchRerankerModel: ''
})

const showOpenaiKey = ref(false)
const showAnthropicKey = ref(false)
const saving = ref(false)

// 追踪密钥是否被用户实际修改
const keyDirty = ref({ openai: false, anthropic: false, search: false })
// 后端返回的密钥是否已配置标志
const openaiKeySet = ref(false)
const anthropicKeySet = ref(false)
const searchKeySet = ref(false)
const saveMessage = ref('')
const saveSuccess = ref(false)

const openaiModels = ref([])
const anthropicModels = ref([])
const loadingModels = ref(false)
const modelError = ref('')

const testingConnection = ref(false)
const connectionResult = ref(null)

// web search state
const searchProvidersList = ref([])
const showSearchKey = ref(false)
const testingSearch = ref(false)
const searchTestResult = ref(null)

// QMD RAG 模型预设（后端自动检测，前端下拉选择）
const embeddingPresets = ref([])
const rerankerPresets = ref([])
const embeddingPresetId = ref('')
const rerankerPresetId = ref('')
const ragModelsLoading = ref(false)
const ragModelsError = ref('')

const currentEmbeddingNote = computed(() => {
  const p = embeddingPresets.value.find(x => x.id === embeddingPresetId.value)
  return p ? p.note : ''
})
const currentRerankerNote = computed(() => {
  const p = rerankerPresets.value.find(x => x.id === rerankerPresetId.value)
  return p ? p.note : ''
})

function onEmbeddingPresetChange() {
  const pid = embeddingPresetId.value
  if (pid === 'custom') {
    // 保留现有字段让用户输入
    return
  }
  const preset = embeddingPresets.value.find(p => p.id === pid)
  if (preset) {
    settings.value.searchEmbeddingModel = preset.id  // 空字符串 = 内置 BM25
    settings.value.searchEmbeddingDim = preset.dim || 0
  }
}

function onRerankerPresetChange() {
  const pid = rerankerPresetId.value
  if (pid === 'custom') return
  const preset = rerankerPresets.value.find(p => p.id === pid)
  if (preset) {
    settings.value.searchRerankerModel = preset.id
  }
}

// 根据后端返回的当前值，反向匹配预设。匹配不到 → custom
function syncPresetFromValues() {
  const em = settings.value.searchEmbeddingModel || ''
  const rm = settings.value.searchRerankerModel || ''
  const embMatched = embeddingPresets.value.find(p => p.id === em)
  embeddingPresetId.value = embMatched ? embMatched.id : (em ? 'custom' : '')
  const rrMatched = rerankerPresets.value.find(p => p.id === rm)
  rerankerPresetId.value = rrMatched ? rrMatched.id : (rm ? 'custom' : '')
}

const apiProviders = computed(() => searchProvidersList.value.filter(p => p.group === 'api'))
const localProviders = computed(() => searchProvidersList.value.filter(p => p.group === 'local'))
const selectedProvider = computed(() => searchProvidersList.value.find(p => p.id === settings.value.searchProvider) || null)

const scoreOptions = ['6.0', '6.5', '7.0', '7.5+']

const isConfigured = computed(() => {
  if (settings.value.provider === 'openai') return openaiKeySet.value || (keyDirty.value.openai && settings.value.openaiApiKey.length > 5)
  return anthropicKeySet.value || (keyDirty.value.anthropic && settings.value.anthropicApiKey.length > 5)
})

onMounted(async () => {
  try {
    const data = await getSettings()
    if (data) {
      settings.value.provider = data.llm_provider || 'openai'
      settings.value.openaiBaseUrl = data.openai_base_url || 'https://api.openai.com/v1'
      // 密钥字段：不加载脱敏值到输入框，仅记录是否已配置
      settings.value.openaiApiKey = ''
      settings.value.openaiModel = data.openai_model || ''
      settings.value.anthropicBaseUrl = data.anthropic_base_url || 'https://api.anthropic.com'
      settings.value.anthropicApiKey = ''
      settings.value.anthropicModel = data.anthropic_model || ''
      settings.value.targetScore = data.target_score || '7.0'
      settings.value.searchProvider = data.search_provider || 'tavily'
      settings.value.searchApiKey = ''
      settings.value.searchBaseUrl = data.search_base_url || ''
      // 记录密钥是否已配置
      openaiKeySet.value = !!data.openai_api_key_set
      anthropicKeySet.value = !!data.anthropic_api_key_set
      searchKeySet.value = !!data.search_api_key_set
      // 重置 dirty 标记
      keyDirty.value = { openai: false, anthropic: false, search: false }
      if (typeof data.search_include_date === 'boolean') settings.value.searchIncludeDate = data.search_include_date
      if (typeof data.search_max_results === 'number') settings.value.searchMaxResults = data.search_max_results
      if (data.search_compression) settings.value.searchCompression = data.search_compression
      if (typeof data.search_chunk_count === 'number') settings.value.searchChunkCount = data.search_chunk_count
      if (typeof data.search_embedding_model === 'string') settings.value.searchEmbeddingModel = data.search_embedding_model
      if (typeof data.search_embedding_dim === 'number') settings.value.searchEmbeddingDim = data.search_embedding_dim
      if (typeof data.search_reranker_model === 'string') settings.value.searchRerankerModel = data.search_reranker_model
    }
  } catch (e) {
    console.error('Failed to load settings:', e)
  }
  fetchModels()
  fetchSearchProviders()
  fetchRagModels()
})

async function fetchRagModels() {
  ragModelsLoading.value = true
  ragModelsError.value = ''
  try {
    const res = await getSearchRagModels()
    const payload = (res && res.data) || {}
    embeddingPresets.value = payload.embedding_presets || []
    rerankerPresets.value = payload.reranker_presets || []
    // 预设拉回后，把当前 settings 值反向映射到下拉
    syncPresetFromValues()
  } catch (e) {
    console.warn('Failed to load RAG model presets:', e)
    ragModelsError.value = t('settings.webSearch.ragPresetLoadFail')
    // 降级：没有预设时允许 custom 输入
    embeddingPresets.value = [{ id: '', label: 'Built-in BM25+TF-IDF', label_cn: '内置 BM25+TF-IDF', dim: 0, note: '' }, { id: 'custom', label: 'Custom', label_cn: '自定义', dim: 0, note: '' }]
    rerankerPresets.value = [{ id: '', label: 'No rerank', label_cn: '不重排', note: '' }, { id: 'custom', label: 'Custom', label_cn: '自定义', note: '' }]
    syncPresetFromValues()
  } finally {
    ragModelsLoading.value = false
  }
}

async function fetchSearchProviders() {
  try {
    const res = await getSearchProviders()
    searchProvidersList.value = (res && (res.data || res)) || []
  } catch (e) {
    console.warn('Failed to load search providers:', e)
  }
}

async function runSearchTest() {
  testingSearch.value = true
  searchTestResult.value = null
  try {
    const res = await testSearch({
      provider: settings.value.searchProvider,
      api_key: settings.value.searchApiKey,
      base_url: settings.value.searchBaseUrl
    })
    if (res && res.status === 'ok') {
      searchTestResult.value = {
        status: 'ok',
        message: t('settings.webSearch.testOk').replace('{ms}', res.elapsed_ms || 0).replace('{n}', res.result_count || 0)
      }
    } else {
      searchTestResult.value = { status: 'error', message: `${t('settings.webSearch.testFail')}${(res && res.message) || 'unknown error'}` }
    }
  } catch (e) {
    searchTestResult.value = { status: 'error', message: `${t('settings.webSearch.testFail')}${e.message || 'network error'}` }
  } finally {
    testingSearch.value = false
  }
}

async function fetchModels() {
  loadingModels.value = true
  modelError.value = ''
  try {
    const data = await getAvailableModels()
    if (data) {
      openaiModels.value = data.openai?.models || []
      anthropicModels.value = data.anthropic?.models || []
      if (openaiModels.value.length === 0 && settings.value.provider === 'openai') {
        modelError.value = '未获取到模型列表，请检查 Base URL 和 API Key'
      }
    }
  } catch (e) {
    modelError.value = '获取模型列表失败: ' + (e.message || 'Network error')
  } finally {
    loadingModels.value = false
  }
}

async function testApiConnection() {
  testingConnection.value = true
  connectionResult.value = null
  try {
    const result = await testConnection({
      provider: settings.value.provider,
      base_url: settings.value.provider === 'openai' ? settings.value.openaiBaseUrl : settings.value.anthropicBaseUrl,
      api_key: settings.value.provider === 'openai' ? settings.value.openaiApiKey : settings.value.anthropicApiKey
    })
    connectionResult.value = result
  } catch (e) {
    connectionResult.value = { status: 'error', message: 'Request failed: ' + (e.message || 'Network error') }
  } finally {
    testingConnection.value = false
  }
}

async function saveSettings() {
  saving.value = true
  saveMessage.value = ''
  try {
    const payload = {
      llm_provider: settings.value.provider,
      openai_base_url: settings.value.openaiBaseUrl,
      anthropic_base_url: settings.value.anthropicBaseUrl,
      openai_model: settings.value.openaiModel,
      anthropic_model: settings.value.anthropicModel,
      target_score: settings.value.targetScore,
      search_provider: settings.value.searchProvider,
      search_base_url: settings.value.searchBaseUrl,
      search_include_date: settings.value.searchIncludeDate,
      search_max_results: settings.value.searchMaxResults,
      search_compression: settings.value.searchCompression,
      search_chunk_count: settings.value.searchChunkCount,
      search_embedding_model: settings.value.searchEmbeddingModel,
      search_embedding_dim: settings.value.searchEmbeddingDim,
      search_reranker_model: settings.value.searchRerankerModel
    }
    // 只有用户实际修改了密钥才发送，避免回传脱敏值
    if (keyDirty.value.openai && settings.value.openaiApiKey) {
      payload.openai_api_key = settings.value.openaiApiKey
    }
    if (keyDirty.value.anthropic && settings.value.anthropicApiKey) {
      payload.anthropic_api_key = settings.value.anthropicApiKey
    }
    if (keyDirty.value.search && settings.value.searchApiKey) {
      payload.search_api_key = settings.value.searchApiKey
    }
    await updateSettings(payload)
    saveMessage.value = t('settings.saveSuccess')
    saveSuccess.value = true
    // 保存成功后更新 key_set 状态
    if (keyDirty.value.openai && settings.value.openaiApiKey) openaiKeySet.value = true
    if (keyDirty.value.anthropic && settings.value.anthropicApiKey) anthropicKeySet.value = true
    if (keyDirty.value.search && settings.value.searchApiKey) searchKeySet.value = true
    // 保存后清空输入框中的明文密钥并重置 dirty
    settings.value.openaiApiKey = ''
    settings.value.anthropicApiKey = ''
    settings.value.searchApiKey = ''
    keyDirty.value = { openai: false, anthropic: false, search: false }
  } catch (e) {
    saveMessage.value = t('settings.saveFail')
    saveSuccess.value = false
  } finally {
    saving.value = false
    setTimeout(() => { saveMessage.value = '' }, 3000)
  }
}
</script>
