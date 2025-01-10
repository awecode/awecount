<template>
  <q-field :label="label" stack-label :error="!!props.error" :error-message="props.error">
    <div class="relative flex flex-wrap items-center p-3 w-full" @click="onFieldClick">
      <div v-for="(file, index) in fileList" :key="index" class="relative w-32 h-32 m-2 flex items-center">
        <q-img v-if="file.isImage" :src="file.preview" class="w-full h-full object-cover rounded overflow-hidden"
          alt="Preview" />
        <div v-else class="grid place-content-center w-full h-full">
          <q-icon name="mdi-file" class="mx-auto" size="lg" color="grey" />
        </div>

        <div class="absolute top-0 right-0">
          <q-icon name="close" class="cursor-pointer" @click.stop="deleteFile(index)" />
        </div>
      </div>
    </div>
    <input :accept="[...allowedImageExtensions, ...allowedFileExtensions].join(',')" :multiple="multiple" ref="imageRef"
      type="file" class="hidden" @change="handleFileChange" />
  </q-field>
</template>

<script setup>
import { ref, watch } from 'vue'
import { QImg, QIcon, QField } from 'quasar'

const props = defineProps({
  label: {
    type: String,
    default: '',
  },
  modelValue: {
    type: [String, Array, File, Array],
    default: undefined,
  },
  error: {
    type: String,
    default: '',
  },
  multiple: {
    type: Boolean,
    default: false,
  },
  maxFileSize: {
    type: Number,
    default: process.env.MAX_FILE_UPLOAD_SIZE,
  },
})

const $q = useQuasar()

const emit = defineEmits(['update:modelValue'])

const allowedImageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']

const allowedFileExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt']

const fileList = ref([])

const imageRef = ref(null)

watch(
  () => props.modelValue,
  () => {
    processFiles(props.modelValue)
  },
  { immediate: true }
)

function handleFileChange(event) {
  const target = event.target
  if (target.files) {
    const files = Array.from(target.files)
    if (files.some(file => file.size > props.maxFileSize)) {
      $q.notify({
        type: 'negative',
        message: `Please upload files with size less than ${(props.maxFileSize / (1024 * 1024)).toFixed(2)}MB`,
        icon: 'report_problem',
      })
      return
    }
    emit('update:modelValue', props.multiple ? [...props.modelValue, ...files] : files[0])
  }
}

function deleteFile(index) {
  const files = Array.isArray(props.modelValue) ? [...props.modelValue] : [props.modelValue]
  files.splice(index, 1)
  emit('update:modelValue', files)
}

function processFiles(value) {
  const files = Array.isArray(value) ? value : [value]
  fileList.value = files.map((file) => {
    if (file instanceof File) {
      const isImage = file.type.startsWith('image/')
      const preview = isImage ? URL.createObjectURL(file) : ''
      return {
        name: file.name,
        preview,
        isImage,
      }
    }
    return {
      name: file,
      preview: file,
      isImage: allowedImageExtensions.some((ext) => file.endsWith(ext)),
    }
  })
}

function onFieldClick() {
  imageRef.value?.click()
}
</script>
