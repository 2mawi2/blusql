import { useModal } from '@/@core/composables/useModal'
import { type UsecaseHistoryEntry } from '@/models/UsecaseQaChatEntry'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { z } from 'zod'

export const SUCCESSFUL_QA_ANSWER_SCHEMA = z.object({
  query: z.string(),
  markdown: z.string(),
  explanation: z.string(),
})
export type SuccessfulQaAnswer = z.infer<typeof SUCCESSFUL_QA_ANSWER_SCHEMA>

// const QA_CHAT_HISTORY_LIMIT = 1_000

export const useUsecaseHistoryStore = defineStore('usecase-qa-chat', () => {
  const chatHistory = ref<UsecaseHistoryEntry[]>([])
  const deleteChatHistory = useModal()

  const addEntry = (usecaseId: string, question: string, answer: SuccessfulQaAnswer) => {
    const entry: UsecaseHistoryEntry = {
      question,
      usecaseId,
      query: answer.query,
      markdown: answer.markdown,
      explanation: answer.explanation,
    }
    console.log('entry: ', entry)
    chatHistory.value.push(entry)
    console.log('chatHistory.value: ', chatHistory.value)
  }

  const deleteEntry = (usecaseId: string) =>
    (chatHistory.value = chatHistory.value.filter((entry) => entry.usecaseId !== usecaseId))

  return {
    chatHistory,
    addEntry,
    deleteEntry,
    deleteChatHistory,
    // exporting so this information is persisted
    deleteChatHistoryShouldBeHidden: deleteChatHistory.shouldBeHidden,
  }
})
