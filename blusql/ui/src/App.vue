<template>
  <!-- <div class="font-bold text-4xl">
    <span class="text-blue">Blu</span>
    <span>sql</span>
  </div> -->
  <div>
    <AaAppLayout
      :header-props="{ title: 'BlueSQL' }"
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
              @clear-input="usecaseQaInputStore.getUsecaseState(usecaseId).question = ''"
            />
            <div class="px-1">
              <!-- Explanation -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" class="h-30 mb-4 mt-4" />
              <AccordionItem
                v-else-if="currentChatSession?.explanation"
                is-initially-open
                class="b-none"
                :title="'Explanation'"
              >
                {{ currentChatSession.explanation }}
              </AccordionItem>

              <!-- Markdown -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" class="h-70" />
              <AccordionItem
                v-else-if="currentChatSession?.markdown"
                is-initially-open
                :title="'SQL Query Output'"
              >
                <vue-markdown :source="currentChatSession.markdown" />
              </AccordionItem>

              <!-- Query SQL -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" class="h-30 mb-4 mt-4" />
              <AccordionItem
                v-else-if="currentChatSession?.query"
                :is-initially-open="false"
                :title="'SQL Query'"
              >
                <SqlPreview :query="currentChatSession.query" />
              </AccordionItem>

              <!-- Buttons for managing session state -->
              <BaseSkeleton v-if="isProcessingRequest[usecaseId]" />
              <div v-else-if="currentChatSession">
                <AaButton
                  class="shrink-0 mt-4"
                  size="small"
                  variant="danger"
                  @click="chatHistory = []"
                  >{{ 'Delete Session' }}</AaButton
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
import SqlPreview from './components/SqlPreview.vue'
import { useUsecaseQaInputStore } from './stores/usecaseQaInput'

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
    label: 'Query Checker',
    icon: 'i-material-symbols-radio-button-unchecked',
    active: true,
  },
]

const usecaseQaInputStore = useUsecaseQaInputStore()

const usecaseIdCounter = ref(1)
const usecaseId = computed(() => `usecase-${usecaseIdCounter.value}`)

const usecaseQaStore = useUsecaseQaStore()
const { isProcessingRequest } = storeToRefs(usecaseQaStore)

const usecaseHistoryStore = useUsecaseHistoryStore()
const { chatHistory } = storeToRefs(usecaseHistoryStore)

const currentChatSession = computed(() =>
  chatHistory.value.find((entry) => entry.usecaseId === 'usecase-1'),
)

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

table {
  width: 100%;
  border-radius: 1rem;
  box-shadow: 0 4px 24px 0 rgba(0, 0, 0, 0.06);
  border-collapse: separate;
  border-spacing: 0;
  overflow: hidden;
}

caption {
  text-align: left;
  font-weight: 700;
  font-size: 24px;
  line-height: 32px;
  margin-bottom: 24px;
}

th {
  padding: 1.25rem 2rem;
  font-weight: 700;
  font-size: 1rem;
  line-height: 1.5rem;
  color: black;
  background-color: #fbfbfd;
  border-width: 1px 1px 1px 0;
  border-color: #f2f2f9;
  border-style: solid;
  overflow-wrap: break-word;
  vertical-align: top;
}

th:first-child {
  border-left-width: 1px;
}

th:last-child {
  border-right-width: 1px;
}

td {
  width: 50%;
  overflow-wrap: break-word;
  vertical-align: top;
  color: black;
  padding: 1rem 1.5rem;
  font-size: 1rem;
  line-height: 1.5rem;
  font-weight: normal;
  border-width: 1px 1px 1px 0;
  border-color: #f2f2f9;
  border-style: solid;
  background-color: #fbfbfd;
}

td:first-child {
  border-left-width: 1px;
}

td:not(:only-child):first-child {
  font-weight: 700;
  background-color: #fbfbfd;
}

tr:nth-child(even) td,
tr:nth-child(even) th {
  background-color: #f2f2f9;
}

tr:last-child td,
tr:last-child th {
  border-bottom-width: 1px;
}

h3 {
  font-size: 1.5rem;
  line-height: 2rem;
}
</style>
