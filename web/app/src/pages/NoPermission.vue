<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <div class="text-red-6 text-white text-center q-pa-md flex flex-center">
    <div class="q-pt-xl">
      <div class="text-h3" style="opacity: 0.4">
        You Don't Have Permission.
      </div>
      <q-btn
        no-caps
        outline
        class="q-mt-xl"
        label="Go Back"
        text-color="blue"
        @click="router.go(-1)"
      />
    </div>
  </div>
</template>
