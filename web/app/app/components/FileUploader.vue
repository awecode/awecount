<script setup>
import { QField, QIcon, QImg } from 'quasar'
import { ref, watch } from 'vue'

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

const emit = defineEmits(['update:modelValue'])

const $q = useQuasar()

const allowedImageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.svg']

const allowedFileExtensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.csv', '.txt']

const fileList = ref([])

const imageRef = ref(null)

watch(
  () => props.modelValue,
  () => {
    processFiles(props.modelValue)
  },
  { immediate: true },
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
      isImage: allowedImageExtensions.some(ext => file.endsWith(ext)),
    }
  })
}

function onFieldClick() {
  imageRef.value?.click()
}
</script>

<template>
  <QField
    stack-label
    :error="!!props.error"
    :error-message="props.error"
    :label="label"
  >
    <div class="relative flex flex-wrap items-center p-3 w-full" @click="onFieldClick">
      <div v-for="(file, index) in fileList" :key="index" class="relative w-32 h-32 m-2 flex items-center">
        <QImg
          v-if="file.isImage"
          alt="Preview"
          class="w-full h-full object-cover rounded overflow-hidden"
          :src="file.preview"
        />
        <div v-else class="grid place-content-center w-full h-full">
          <QIcon
            class="mx-auto"
            color="grey"
            name="mdi-file"
            size="lg"
          />
        </div>

        <div class="absolute top-0 right-0">
          <QIcon class="cursor-pointer" name="close" @click.stop="deleteFile(index)" />
        </div>
      </div>
    </div>
    <input
      ref="imageRef"
      class="hidden"
      type="file"
      :accept="[...allowedImageExtensions, ...allowedFileExtensions].join(',')"
      :multiple="multiple"
      @change="handleFileChange"
    />
  </QField>
</template>
