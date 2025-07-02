<!-- <template>
  <section class="bg-core-bg-secondary flex h-screen flex-col items-start">
    <div class="flex h-14 flex-shrink-0 items-center justify-between self-stretch px-XL py-2.5">
      <div class="flex-row flex items-center gap-2">
        <slot name="title" />
      </div>
      <slot name="header-left" />
    </div>
    <slot name="main" />
  </section>
</template> -->
<template>
  <section class="bg-core-bg-secondary flex flex-col h-screen">
    <!-- Header -->
    <div class="flex h-14 flex-shrink-0 items-center justify-between px-XL py-2.5">
      <div>
        <slot name="title" />
      </div>
    </div>
    <!-- Main area, centered and 60% wide -->
    <div class="flex-1 flex justify-center">
      <div class="w-3/5 mt-6 flex flex-col">
        <slot name="main" />
      </div>
    </div>
  </section>
</template>
