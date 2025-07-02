<template>
  <div class="max-w-full rounded-xl bg-white/95 shadow-lg p-4 border border-gray-200">
    <pre class="!m-0 whitespace-pre-wrap break-words">
      <code
        class="p-4 block rounded-lg text-base font-mono text-gray-800 bg-gray-50 selection:bg-yellow-200/60 whitespace-pre-wrap break-words"
        v-html="highlightedQuery"
      ></code>
    </pre>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  query: string
}

const props = defineProps<Props>()

// Simple SQL syntax highlighter (minimal)!
const keywords = [
  'SELECT',
  'FROM',
  'WHERE',
  'AND',
  'OR',
  'NOT',
  'NULL',
  'ORDER',
  'BY',
  'GROUP',
  'ASC',
  'DESC',
  'LIMIT',
  'OFFSET',
  'INNER',
  'JOIN',
  'LEFT',
  'RIGHT',
  'ON',
  'AS',
  'IN',
  'IS',
  'UPDATE',
  'DELETE',
  'INSERT',
  'INTO',
  'VALUES',
  'SET',
  'CREATE',
  'TABLE',
  'DROP',
  'ALTER',
  'ADD',
  'DISTINCT',
  'COUNT',
  'MIN',
  'MAX',
  'AVG',
  'SUM',
  'LIKE',
]

const keywordRegex = new RegExp(`\\b(${keywords.join('|')})\\b`, 'gi')

const highlightedQuery = computed(() => {
  if (!props.query) return ''
  return props.query
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(
      keywordRegex,
      (match) => `<span class="text-blue-700 font-bold">${match.toUpperCase()}</span>`,
    )
    .replace(/('[^']*')/g, `<span class="text-amber-700">$1</span>`)
    .replace(/(--.*?$)/gm, `<span class="text-gray-400 italic">$1</span>`)
})
</script>
