<template>
  <div :class="[
    'flex gap-3',
    message.role === 'user' ? 'justify-end' : 'justify-start'
  ]">
    <div v-if="message.role === 'assistant'" class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-900 flex items-center justify-center text-white text-sm font-medium">
      S
    </div>
    <div :class="[
      'max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed',
      message.role === 'user'
        ? 'bg-gray-900 text-white rounded-br-md'
        : 'bg-gray-100 text-gray-900 rounded-bl-md'
    ]">
      <div class="whitespace-pre-wrap">{{ message.content }}</div>
      <div :class="[
        'text-[10px] mt-1',
        message.role === 'user' ? 'text-gray-400 text-right' : 'text-gray-400'
      ]">
        {{ time }}
      </div>
    </div>
    <div v-if="message.role === 'user'" class="flex-shrink-0 w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 text-sm font-medium">
      U
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Message } from '../stores/chat'

const props = defineProps<{ message: Message }>()

const time = new Date(props.message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
</script>
