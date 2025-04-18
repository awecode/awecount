<script>
// import usedownloadFile from '@/composables/usedownloadFile'
// TODO: add integration
export default {
  setup() {
    const metaData = {
      title: 'Import/Export  | Awecount',
    }
    useMeta(metaData)
    const showPasswordStatus = ref(false)
    const showPasswordStatus2 = ref(false)
    const export_file = ref({
      password: null,
      passerr: '',
    })
    const import_file = ref({
      password: null,
      passerr: '',
      data: null,
      loading: false,
    })
    function downloadFile() {
      this.loading = true
      // let fileName = `awecount_export_${new Date().toLocaleString()}.zip`
      useApi()
        // .download(
        //   'export/',
        //   fileName,
        //   {
        //     email: this.$store.getters.user_email,
        //     password: this.export_file.password,
        //   },
        //   true
        // )
        .then(() => {
          this.$success('Data Exported!')
          this.loading = false
        })
        .catch(() => {
          this.$error('Export Failed!')
          this.loading = false
        })
    }
    return {
      showPasswordStatus,
      showPasswordStatus2,
      export_file,
      import_file,
      downloadFile,
    }
  },
}
</script>

<template>
  <div class="q-pa-md">
    <q-card>
      <q-card-section class="q-pa-lg">
        <h6 class="q-ma-none">
          Export
        </h6>
        <div class="q-my-lg">
          Please enter your password
        </div>
        <div>
          <q-input
            v-model="export_file.password"
            input-class="text-body1"
            label="Password"
            :type="showPasswordStatus ? 'text' : 'password'"
          >
            <template #before>
              <q-icon name="fa-solid fa-lock" />
            </template>
            <template #append>
              <q-icon class="cursor-pointer" :name="showPasswordStatus ? 'mdi-eye' : 'mdi-eye-off'" @click="showPasswordStatus = !showPasswordStatus" />
            </template>
          </q-input>
        </div>
        <q-btn
          class="q-mt-md"
          color="blue"
          icon-right="download"
          label="download"
          style="border-radius: 2rem; color: black"
          :disable="!export_file.password"
          @click="downloadFile"
        />
      </q-card-section>
    </q-card>
    <q-card class="q-mt-md">
      <q-card-section class="q-pa-lg">
        <h6 class="q-ma-none">
          Import
        </h6>
        <div class="q-my-lg bg-red text-white q-pa-md rounded-borders row items-center">
          <q-icon class="q-mr-md" name="mdi-alert" size="sm" />
          <span class="text-weight-medium text-subtitle">Proceed with caution!</span>
        </div>
        <div>
          <q-file v-model="import_file.data" class="q-mb-md" label="File input">
            <template #before>
              <q-icon name="mdi-paperclip" />
            </template>
          </q-file>
          <q-input
            v-model="import_file.password"
            input-class="text-body1"
            label="Password"
            :type="showPasswordStatus2 ? 'text' : 'password'"
          >
            <template #before>
              <q-icon name="fa-solid fa-lock" />
            </template>
            <template #append>
              <q-icon class="cursor-pointer" :name="showPasswordStatus2 ? 'mdi-eye' : 'mdi-eye-off'" @click="showPasswordStatus2 = !showPasswordStatus2" />
            </template>
          </q-input>
        </div>
        <q-btn
          class="q-mt-md"
          color="green"
          icon-right="upload"
          label="upload"
          style="border-radius: 2rem; color: black"
          :disable="!import_file.password"
        />
      </q-card-section>
    </q-card>
  </div>
</template>
