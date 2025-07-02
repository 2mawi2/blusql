import { useUsecaseHistoryStore } from '@/stores/usecaseHistory'
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { CUSTOM_RAG_SERVICE } from '@/utils/http.ts'

export const useUsecaseQaStore = defineStore('usecase-qa', () => {
  const usecaseHistoryStore = useUsecaseHistoryStore()
  const isProcessingRequest = ref<{ [key: string]: boolean }>({})

  async function executeUsecase(usecaseId: string, question: string) {
    isProcessingRequest.value[usecaseId] = true

    try {
      const response = await CUSTOM_RAG_SERVICE.customQa({ natural_query: question })
      console.log('SQLQUERY:' + response.sql_query)
      usecaseHistoryStore.addEntry(usecaseId, question, {
        query: response.sql_query,
        markdown: response.markdown_result,
        explanation: response.explanation ?? '',
      })
      isProcessingRequest.value[usecaseId] = false
    } catch (error) {
      isProcessingRequest.value[usecaseId] = false

      throw error
    }
  }

  /**
   * executes http request and updates usecaseHistoryStore
   */
  const submitQuestion = async (usecaseId: string, question: string) => {
    if (!question) return
    await executeUsecase(usecaseId, question)
  }

  return {
    isProcessingRequest,
    submitQuestion,
  }
})
