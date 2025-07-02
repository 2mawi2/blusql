<template>
  <div class="accordion-item border-t border-b border-gray-300">
    <link
      rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200"
    />
    <!-- title bar -->
    <button
      :aria-expanded="isOpen"
      class="flex items-center flex-wrap w-full justify-between cursor-pointer py-4"
      @click="toggleContent"
    >
      <div class="flex items-center">
        <h2 class="text-xl w-full text-gray-900">{{ props.title }}</h2>
      </div>
      <div class="relative h-6 w-6">
        <Transition name="plus-icon">
          <span v-if="isOpen" class="material-symbols-outlined">keyboard_arrow_up</span>
        </Transition>
        <Transition name="minus-icon">
          <span v-if="!isOpen" class="material-symbols-outlined"> keyboard_arrow_down </span>
        </Transition>
      </div>
    </button>
    <!-- content -->
    <Transition
      name="content"
      @after-enter="contentVisible = true"
      @before-leave="contentVisible = false"
    >
      <div
        v-show="isOpen"
        :class="contentVisible ? 'overflow-visible pointer-events-auto' : 'overflow-hidden'"
      >
        <div class="overflow-y-visible pt-2 sm:pt-4 pb-6 sm:pb-8" style="max-height: inherit">
          <slot></slot>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
// Imports for unit testing
import { ref } from 'vue'

interface Props {
  title: string
  icon?: string
  isInitiallyOpen?: boolean
}

const emit = defineEmits<{
  (e: 'expand'): void
  (e: 'collapse'): void
}>()

const props = withDefaults(defineProps<Props>(), {
  isInitiallyOpen: false,
  dataTestId: undefined,
})

const isOpen = ref(props.isInitiallyOpen)
const contentVisible = ref(props.isInitiallyOpen)

function toggleContent(): void {
  isOpen.value = !isOpen.value
  if (!isOpen.value) {
    emit('collapse')
  } else {
    emit('expand')
  }
}
</script>

<style scoped>
.accordion-item {
  margin-top: -1px;
  pointer-events: none;
}

/* .accordion-item:hover:before,
.accordion-item:has(button:focus-visible):before {
  content: '';
  position: absolute;
  inset: 0;
  border-top: 1px solid var(--color-gray-900);
  border-bottom: 1px solid var(--color-gray-900);
} */

button {
  pointer-events: auto;
}

button:focus-visible .plus-minus-icon {
  border-radius: 1px;
  box-shadow:
    0 0 0 4px var(--color-white),
    0 0 0 6px var(--color-blue),
    0 0 8px 6px var(--color-blue);
}

/* .accordion-item:hover,
.accordion-item:has(button:focus-visible) {
  position: relative;
  border-top: 1px solid var(--color-gray-900);
  border-bottom: 1px solid var(--color-gray-900);
  outline: none;
} */

.content-enter-active,
.content-leave-active {
  transition: all 0.3s ease-in-out;
  max-height: 100vh;
}

.content-enter-from,
.content-leave-to {
  max-height: 0px;
}

.minus-icon-enter-active {
  transition: all 0s ease 0.3s;
}

.minus-icon-leave-active {
  transition: all 0s ease;
}

.minus-icon-enter-from,
.content-leave-to {
  opacity: 0;
}

.plus-icon-enter-active,
.plus-icon-leave-active {
  transition: all 0.3s ease-in-out;
}

.plus-icon-enter-from,
.plus-icon-leave-to {
  transform: rotate(90deg);
}
</style>
