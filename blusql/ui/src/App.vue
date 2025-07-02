<template>
  <!-- <div class="font-bold text-4xl">
    <span class="text-blue">Blu</span>
    <span>sql</span>
  </div> -->
  <div>
    <AaAppLayout
      :header-props="{ title: 'BluSQL' }"
      :user-avatar-props="{ userName: 'Test User', parent: parentEl }"
      :sidebar-props="{ items: items }"
      :accesibility-labels="{ helpButton: '' }"
    >
      <template #app-content>
        <BaseLayout>
          <template #title>
            <span>Query the database by describing what you want to see</span>
          </template>
          <template #main>
            <!-- User Input -->
            <UsecaseQaInput
              :usecase-id="usecaseId"
              :request-processing="isProcessingRequest[usecaseId]"
              @on-submit="onSubmit"
            />
            <div class="px-1">
              <!-- Explanation -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" class="h-20 mb-4 mt-4" />
              <AccordionItem
                v-else-if="currentChatSession?.explanation"
                is-initially-open
                class="b-none"
                :title="'Explanation'"
              >
                {{ currentChatSession.explanation }}
              </AccordionItem>

              <!-- Markdown -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" />
              <AccordionItem
                v-else-if="currentChatSession?.markdown"
                is-initially-open
                :title="'Your Output'"
              >
                <vue-markdown :source="currentChatSession.markdown" />
              </AccordionItem>

              <!-- Query SQL -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" class="h-20 mb-4 mt-4" />
              <AccordionItem
                v-else-if="currentChatSession?.query"
                :is-initially-open="false"
                :title="'Generated SQL Query'"
              >
                {{ currentChatSession.query }}
              </AccordionItem>

              <!-- Buttons for managing session state -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" />
              <div v-else-if="currentChatSession?.markdown" class="">
                <AaButton
                  class="shrink-0 mt-4"
                  size="small"
                  variant="danger"
                  @click="console.log('delete')"
                  >{{ 'Delete Entry' }}</AaButton
                >
              </div>
            </div>
          </template>
        </BaseLayout>
      </template>
    </AaAppLayout>
  </div>
</template>

<script lang="ts" setup>
import VueMarkdown from 'vue-markdown-render'
import { AaAppLayout, AaButton, type SidebarOption } from '@aleph-alpha/ds-components-vue'
import { computed, ref } from 'vue'
import BaseLayout from '@/@core/layouts/BaseLayout.vue'
import { HTTP_CLIENT } from '@/utils/http.ts'
import { onMounted } from 'vue'
import { useUsecaseQaStore } from '@/stores/usecaseQa.ts'
import { useUsecaseHistoryStore } from '@/stores/usecaseHistory'
import UsecaseQaInput from '@/components/UsecaseQaInput.vue'
import BaseSkeleton from '@/components/loading/BaseSkeleton.vue'
import { storeToRefs } from 'pinia'
import AccordionItem from './components/AccordionItem.vue'

const props = withDefaults(
  defineProps<{
    userToken: string
    serviceBaseUrl?: string
  }>(),
  {
    userToken: import.meta.env.VITE_USER_TOKEN || '',
    serviceBaseUrl: import.meta.env.VITE_SERVICE_BASE_URL || '',
  },
)

const parentEl = ref<HTMLElement | null>(null)

const items: SidebarOption[] = [
  {
    id: '1',
    link: {
      name: 'test',
    },
    label: 'Summarize',
    icon: 'i-material-symbols-radio-button-checked',
    active: true,
  },
  {
    id: '2',
    link: {
      name: '/test',
    },
    label: 'Summarize',
    icon: 'i-material-symbols-radio-button-unchecked',
    active: false,
  },
]

const usecaseIdCounter = ref(1)
const usecaseId = computed(() => `usecase-${usecaseIdCounter.value}`)

const usecaseQaStore = useUsecaseQaStore()
const { isProcessingRequest } = storeToRefs(usecaseQaStore)

const usecaseHistoryStore = useUsecaseHistoryStore()
const { chatHistory } = storeToRefs(usecaseHistoryStore)

const currentChatSession = computed(() =>
  chatHistory.value.find((entry) => entry.usecaseId === 'usecase-1'),
)

// function onDeleteChatHistory() {
//   usecaseHistoryStore.deleteChatHistory.callActionOrOpenModal(deleteChatHistory)
// }

// function onConfirmDeleteQueryItem(checkboxChecked: boolean) {
//   usecaseHistoryStore.deleteChatHistory.getConfirmActionCallback(deleteChatHistory)(checkboxChecked)
// }

// async function deleteChatHistory() {
//   usecaseHistoryStore.clearChat(usecaseId.value)
// }

// async function onDeleteChatHistoryItem(idToDelete: string) {
//   usecaseHistoryStore.deleteEntry(usecaseId.value, idToDelete)
// }

const onSubmit = async (usecaseId: string, question: string) => {
  await usecaseQaStore.submitQuestion(usecaseId, question)
  usecaseIdCounter.value++
}

onMounted(() => {
  HTTP_CLIENT.updateConfig({ baseURL: props.serviceBaseUrl })
  HTTP_CLIENT.setBearerToken(props.userToken)
  console.log(props.userToken)
})
</script>

<style lang="scss">
:root {
  font-family: Raleway, sans-serif, ui-sans-serif;
}
</style>
