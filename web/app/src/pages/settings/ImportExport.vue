<template>
  <div class="q-pa-md">
    <q-card>
      <q-card-section class="q-pa-lg">
        <h6 class="q-ma-none">Export</h6>
        <div class="q-my-lg">Please enter your password</div>
        <div>
          <q-input
            v-model="export_file.password"
            :type="showPasswordStatus ? 'text' : 'password'"
            label="Passowrd"
            input-class="text-body1"
          >
            <template v-slot:before>
              <q-icon name="fa-solid fa-lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="showPasswordStatus ? 'mdi-eye' : 'mdi-eye-off'"
                @click="showPasswordStatus = !showPasswordStatus"
                class="cursor-pointer"
              />
            </template>
          </q-input>
        </div>
        <q-btn
          @click="downloadFile"
          class="q-mt-md"
          style="border-radius: 2rem; color: black"
          label="download"
          icon-right="download"
          color="blue"
        ></q-btn>
      </q-card-section>
    </q-card>
    <q-card class="q-mt-md">
      <q-card-section class="q-pa-lg">
        <h6 class="q-ma-none">Import</h6>
        <div
          class="q-my-lg bg-red text-white q-pa-md rounded-borders row items-center"
        >
          <q-icon name="mdi-alert" size="sm" class="q-mr-md"> </q-icon>
          <span class="text-weight-medium text-subtitle"
            >Proceed with caution!</span
          >
        </div>
        <div>
          <q-file v-model="import_file.data" label="File input" class="q-mb-md">
            <template v-slot:before>
              <q-icon name="mdi-paperclip" />
            </template>
          </q-file>
          <q-input
            v-model="import_file.password"
            :type="showPasswordStatus2 ? 'text' : 'password'"
            label="Passowrd"
            input-class="text-body1"
          >
            <template v-slot:before>
              <q-icon name="fa-solid fa-lock" />
            </template>
            <template v-slot:append>
              <q-icon
                :name="showPasswordStatus2 ? 'mdi-eye' : 'mdi-eye-off'"
                @click="showPasswordStatus2 = !showPasswordStatus2"
                class="cursor-pointer"
              />
            </template>
          </q-input>
        </div>
        <q-btn
          class="q-mt-md"
          style="border-radius: 2rem; color: black"
          label="upload"
          icon-right="upload"
          color="green"
          disable
        ></q-btn>
      </q-card-section>
    </q-card>
  </div>
</template>

<script>
export default {
  setup() {
    const showPasswordStatus = ref(false)
    const showPasswordStatus2 = ref(false)
    const export_file = ref({
      password: null,
      passerr: '',
    })
    const import_file = {
      password: null,
      passerr: '',
      data: null,
      loading: false,
    }
    function downloadFile() {
      console.log(import_file)
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
