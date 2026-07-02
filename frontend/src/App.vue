<template>
  <div class="fixed bottom-6 right-6 z-50 font-sans">
    <Transition name="chat">
      <div v-if="store.isOpen" class="absolute bottom-16 right-0 w-[380px] h-[600px] bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col overflow-hidden">
        <div class="flex items-center justify-between px-5 py-4 border-b border-gray-200 bg-white">
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-full bg-gray-900 flex items-center justify-center text-white text-sm font-bold">
              S
            </div>
            <div>
              <div class="text-sm font-semibold text-gray-900">Vaungsophal</div>
              <div class="text-xs text-gray-500">AI twin &middot; ask me anything</div>
            </div>
          </div>
          <button @click="store.close" class="text-gray-400 hover:text-gray-600 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
          <div v-if="store.messages.length === 0" class="flex flex-col items-center justify-center h-full text-center px-6 text-gray-400">
            <div class="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center mb-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-gray-500">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
            </div>
            <p class="text-sm font-medium text-gray-500">Hi, I'm Sophal's AI twin.</p>
            <p class="text-xs mt-1">Ask me about projects, skills, or recent work.</p>
          </div>
          <ChatMessage v-for="msg in store.messages" :key="msg.id" :message="msg" />
          <div v-if="store.isLoading" class="flex gap-3">
            <div class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center text-white text-sm font-medium">S</div>
            <div class="bg-gray-100 rounded-2xl rounded-bl-md px-4 py-3">
              <div class="flex gap-1.5">
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
              </div>
            </div>
          </div>
        </div>

        <ChatInput :disabled="store.isLoading" @send="handleSend" />
      </div>
    </Transition>

    <button
      @click="store.toggle"
      class="w-14 h-14 rounded-full bg-gray-900 text-white shadow-lg flex items-center justify-center transition-transform hover:scale-105 active:scale-95"
    >
      <svg v-if="!store.isOpen" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from './stores/chat'
import ChatMessage from './components/ChatMessage.vue'
import ChatInput from './components/ChatInput.vue'

const store = useChatStore()
const messagesContainer = ref<HTMLDivElement>()

watch(() => store.messages.length, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})

watch(() => store.isLoading, () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
})

function handleSend(text: string) {
  store.sendMessage(text)
}
</script>

<style scoped>
.chat-enter-active,
.chat-leave-active {
  transition: all 0.2s ease;
}
.chat-enter-from,
.chat-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}
</style>
