import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

export const useChatStore = defineStore('chat', () => {
  const messages = ref<Message[]>([])
  const isOpen = ref(false)
  const isLoading = ref(false)
  const sessionId = ref<string | null>(null)
  const error = ref<string | null>(null)

  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

  function toggle() {
    isOpen.value = !isOpen.value
  }

  function open() {
    isOpen.value = true
  }

  function close() {
    isOpen.value = false
  }

  function addMessage(role: 'user' | 'assistant', content: string) {
    messages.value.push({
      id: crypto.randomUUID(),
      role,
      content,
      timestamp: Date.now(),
    })
  }

  async function sendMessage(text: string) {
    if (!text.trim() || isLoading.value) return

    addMessage('user', text.trim())
    isLoading.value = true
    error.value = null

    try {
      const resp = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text.trim(),
          session_id: sessionId.value,
        }),
      })

      if (!resp.ok) throw new Error(`HTTP ${resp.status}`)

      const data = await resp.json()
      sessionId.value = data.session_id
      addMessage('assistant', data.reply)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to send message'
      addMessage('assistant', 'Sorry, I hit an error. Please try again.')
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    messages.value = []
    sessionId.value = null
    error.value = null
  }

  return {
    messages,
    isOpen,
    isLoading,
    sessionId,
    error,
    toggle,
    open,
    close,
    sendMessage,
    addMessage,
    reset,
  }
})
