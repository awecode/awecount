<template>
  <div class="q-pa-md">
    <div class="row q-gutter-x-md justify-end">
      <q-btn
        v-if="checkPermissions('RecurringVoucherTemplateCreate')"
        color="green"
        :to="`/${type}-voucher/recurring-template/add/`"
        :label="`New Recurring ${capitalizedType} Invoice Template`"
        icon-right="add"
        class="add-btn"
      />
    </div>
    <q-table
      :rows="rows"
      :columns="newColumn"
      :loading="loading"
      :filter="searchQuery"
      v-model:pagination="pagination"
      row-key="id"
      @request="onRequest"
      class="q-mt-md"
      :rows-per-page-options="[20]"
    >
      <template v-slot:top>
        <div class="search-bar">
          <q-input
            dense
            debounce="500"
            v-model="searchQuery"
            placeholder="Search"
            class="full-width search-input"
          >
            <template v-slot:append>
              <q-icon name="search" />
            </template>
          </q-input>
        </div>
      </template>

      <template v-slot:body-cell-title="props">
        <q-td :props="props">
          <span
            v-if="checkPermissions('RecurringVoucherTemplateView')"
            data-testid="voucher-no"
          >
            <router-link
              v-if="
                checkPermissions('RecurringVoucherTemplateView') &&
                props.row.title
              "
              :to="`/${type}-voucher/recurring-template/${props.row.id}/view/`"
              style="font-weight: 500; text-decoration: none"
              class="text-blue"
            >
              {{ props.row.title }}
            </router-link>
          </span>
          <span v-else data-testid="voucher-no">
            {{ props.row.title }}
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-repeat_interval="props">
        <q-td :props="props">
          <span
            >Every {{ props.row.repeat_interval }}
            {{ props.row.repeat_interval_time_unit }}</span
          >
        </q-td>
      </template>

      <template v-slot:body-cell-due_date_after="props">
        <q-td :props="props">
          <span
            >{{ props.row.due_date_after }}
            {{ props.row.due_date_after_time_unit }} after invoice date
          </span>
        </q-td>
      </template>

      <template v-slot:body-cell-end_date="props">
        <q-td :props="props">
          <span v-if="props.row.end_date && props.row.end_after">
            At {{ props.row.end_date }} or after creating
            {{ props.row.end_after }} invoice(s)
          </span>
          <span v-else-if="props.row.end_date">
            {{ props.row.end_date }}
          </span>
          <span v-else-if="props.row.end_after">
            {{ props.row.end_after }} invoices created
          </span>
          <span v-else>Never</span>
        </q-td>
      </template>

      <template v-slot:body-cell-is_active="props">
        <q-td :props="props">
          <q-icon
            :name="props.row.is_active ? 'check_circle' : 'cancel'"
            :color="props.row.is_active ? 'green' : 'red'"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-send_email="props">
        <q-td :props="props">
          <q-icon
            :name="props.row.send_email ? 'check_circle' : 'cancel'"
            :color="props.row.send_email ? 'green' : 'red'"
          />
        </q-td>
      </template>

      <template v-slot:body-cell-actions="props">
        <q-td :props="props">
          <q-btn
            v-if="checkPermissions('RecurringVoucherTemplateModify')"
            color="orange-6"
            class="q-py-none q-px-md font-size-sm q-mr-sm l-edit-btn"
            style="font-size: 12px"
            label="edit"
            :to="`/${type}-voucher/recurring-template/${props.row.id}/`"
          />
        </q-td>
      </template>
    </q-table>
  </div>
</template>

<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import { capitalize } from 'vue'

const props = defineProps({
  type: {
    type: String,
    required: true,
  },
})

const capitalizedType = capitalize(props.type)

const metaData = {
  title: `Recurring ${capitalizedType} Invoice Templates | Awecount`,
}
useMeta(metaData)

const endpoint = `/v1/recurring-voucher-template/?type=${capitalizedType} Voucher`
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
    label: 'Due Date After',
    align: 'left',
    field: 'due_date_after',
  },
  {
    name: 'is_active',
    label: 'Active',
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
