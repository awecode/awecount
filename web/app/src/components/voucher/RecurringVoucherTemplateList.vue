<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { capitalize } from 'vue'
import { useRoute } from 'vue-router'

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
})

const route = useRoute()

const capitalizedType = capitalize(props.type)

const metaData = {
  title: `Recurring ${capitalizedType} Invoice Templates | Awecount`,
}
useMeta(metaData)

const endpoint = `/api/company/${route.params.company}/recurring-voucher-template/?type=${capitalizedType} Voucher`
const { rows, loading, searchQuery, pagination, onRequest } = useList(endpoint)

const newColumn = [
  {
    name: 'title',
    label: 'Title',
    align: 'left',
    field: 'title',
  },
  {
    name: 'repeat_interval',
    label: 'Repeat Interval',
    align: 'left',
    field: 'repeat_interval',
  },
  {
    name: 'start_date',
    label: 'Start Date',
    align: 'left',
    field: 'start_date',
    sortable: true,
  },
  {
    name: 'end_date',
    label: 'End Date/After',
    align: 'left',
    field: 'end_date',
  },
  {
    name: 'due_date_after',
    label: 'Due Date',
    align: 'left',
    field: 'due_date_after',
  },
  {
    name: 'is_active',
    label: 'Is Active?',
    align: 'center',
    field: 'is_active',
  },
  {
    name: 'send_email',
    label: 'Send Email',
    align: 'center',
    field: 'send_email',
  },
  {
    name: 'actions',
    label: 'Actions',
    align: 'center',
    field: 'actions',
  },
]
</script>

<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('recurringvouchertemplate.create')"
        class="add-btn"
        color="green"
        icon-right="add"
        :label="`New Recurring ${capitalizedType} Invoice Template`"
        :to="`/${type}-voucher/recurring-template/add/`"
      />
    </div>
    <q-table
      v-model:pagination="pagination"
      class="q-mt-md"
      row-key="id"
      :columns="newColumn"
      :filter="searchQuery"
      :loading="loading"
      :rows="rows"
      :rows-per-page-options="[20]"
      @request="onRequest"
    >
      <template #top>
        <div class="search-bar">
          <q-input
            v-model="searchQuery"
            dense
            class="full-width search-input"
            debounce="500"
            placeholder="Search"
          >
            <template #append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>
      </template>

      <template #body-cell-repeat_interval="props">
        <q-td :props="props">
          <span>Every {{ props.row.repeat_interval }} {{ props.row.repeat_interval_time_unit }}</span>
        </q-td>
      </template>

      <template #body-cell-due_date_after="props">
        <q-td :props="props">
          <span>{{ props.row.due_date_after }} {{ props.row.due_date_after_time_unit }} after invoice date</span>
        </q-td>
      </template>

      <template #body-cell-end_date="props">
        <q-td :props="props">
          <span v-if="props.row.end_date && props.row.end_after">At {{ props.row.end_date }} or after creating {{ props.row.end_after }} invoice(s)</span>
          <span v-else-if="props.row.end_date">
            {{ props.row.end_date }}
          </span>
          <span v-else-if="props.row.end_after">{{ props.row.end_after }} invoices created</span>
          <span v-else>Never</span>
        </q-td>
      </template>

      <template #body-cell-is_active="props">
        <q-td :props="props">
          <q-icon :color="props.row.is_active ? 'green' : 'red'" :name="props.row.is_active ? 'check_circle' : 'cancel'" />
        </q-td>
      </template>

      <template #body-cell-send_email="props">
        <q-td :props="props">
          <q-icon :color="props.row.send_email ? 'green' : 'red'" :name="props.row.send_email ? 'check_circle' : 'cancel'" />
        </q-td>
      </template>

      <template #body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('recurringvouchertemplate.modify')"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            color="orange-6"
            label="edit"
            style="font-size: 12px"
            :to="`/${type}-voucher/recurring-template/${props.row.id}/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>
