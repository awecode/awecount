<script setup>
import checkPermissions from 'src/composables/checkPermissions'
import useForm from 'src/composables/useForm'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const endpoint = `/api/company/${route.params.company}/sales-voucher/`

const { fields, formDefaults, errors, isEdit, loading, submitForm, today } = useForm(endpoint, {
  getDefaults: true,
  successRoute: `/${route.params.company}/sales/vouchers`,
})

useMeta(() => ({
  title: `${isEdit.value ? 'Sales Invoice Update' : 'Sales Invoice Add'} | Awecount`,
}))

watch(() => formDefaults.value, () => {
  if (fields.value?.rows && fields.value?.tax_type === 'Tax Inclusive') {
    fields.value.rows.forEach((row) => {
      const taxObj = formDefaults.value.collections.tax_schemes.results.find(tax => tax.id === row.tax_scheme_id)
      row.rate = Number((row.rate * (1 + taxObj.rate / 100)).toFixed(6))
    })
  }
})

const router = useRouter()

const onSubmitClick = async (status, redirect) => {
  const originalStatus = fields.value.status
  fields.value.status = status

  const taxType = fields.value.tax_type
  // if fields has tax_type as Tax Inclusive then decrease the tax_amount from the total amount
  // find

  if (taxType === 'Tax Inclusive') {
    fields.value.rows.forEach((row) => {
      if (row.tax_scheme_id) {
        const taxObj = formDefaults.value.collections.tax_schemes.results.find(tax => tax.id === row.tax_scheme_id)
        row.rate = Number((row.rate / (1 + taxObj.rate / 100)).toFixed(6))
      }
    })
  }

  const data = await submitForm()
  if (data && data.hasOwnProperty('error')) {
    fields.value.status = originalStatus
  } else if (redirect) {
    router.push({
      name: 'company-sales-vouchers-id',
      params: {
        company: route.params.company,
        id: data.id,
      },
      query: {
        print: true,
      },
    })
  }
}
</script>

<template>
  <q-form v-if="fields" autofocus class="q-pa-lg">
    <q-card>
      <q-card-section class="bg-green text-white">
        <div class="text-h6" data-testid="form-title">
          <span v-if="!isEdit">New Sales Invoice | Draft</span>
          <span v-else>
            Update Sale Invoice | {{ fields.status }}
            <span v-if="fields.voucher_no">| # {{ fields.voucher_no }}</span>
          </span>
        </div>
      </q-card-section>
      <SalesVoucherFormFields
        v-model:errors="errors"
        v-model:fields="fields"
        :form-defaults="formDefaults"
        :is-edit="isEdit"
        :today="today"
      />

      <div class="q-pr-md q-pb-lg q-mt-md row justify-end q-gutter-x-md">
        <q-btn
          v-if="!isEdit && checkPermissions('sales.create')"
          color="orange-8"
          data-testid="issue-btn"
          label="Save Draft"
          type="submit"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft')"
        />

        <q-btn
          v-if="isEdit && fields.status === 'Draft' && checkPermissions('sales.update')"
          color="orange-8"
          data-testid="draft-btn"
          type="submit"
          :label="isEdit ? 'Update Draft' : 'Save Draft'"
          :loading="loading"
          @click.prevent="() => onSubmitClick('Draft')"
        />
        <!-- <q-btn
          v-if="checkPermissions('sales.create')"
          color="green"
          data-testid="create/update-btn"
          :label="
            isEdit
              ? fields?.status === 'Issued' ? 'Update'
                : fields?.status === 'Draft' ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft`
                  : 'update'
              : `Issue # ${formDefaults.options?.voucher_no || 1}`
          "
          :loading="loading"
          @click.prevent="
            () =>
              onSubmitClick(
                isEdit
                  ? fields.status === 'Draft'
                    ? 'Issued'
                    : fields.status
                  : 'Issued',
              )
          "
        /> -->

        <div v-if="checkPermissions('sales.create')">
          <q-btn-group>
            <q-btn
              color="green"
              data-testid="create/update-btn"
              :label="
                isEdit
                  ? fields?.status === 'Issued' ? 'Update'
                    : fields?.status === 'Draft' ? `Issue # ${formDefaults.options?.voucher_no || 1} from Draft`
                      : 'update'
                  : `Issue # ${formDefaults.options?.voucher_no || 1}`
              "
              :loading="loading"
              @click.prevent="
                () =>
                  onSubmitClick(
                    isEdit
                      ? fields.status === 'Draft'
                        ? 'Issued'
                        : fields.status
                      : 'Issued',
                  )
              "
            />

            <q-btn
              unelevated
              color="green"
              icon="arrow_drop_down"
            >
              <q-menu
                anchor="bottom right"
                self="top right"
              >
                <q-btn
                  color="green"
                  data-testid="create/update-btn"
                  :label="
                    isEdit
                      ? fields?.status === 'Issued and Print' ? 'Update and Print'
                        : fields?.status === 'Draft' ? `Issue from Draft and Print`
                          : 'Update and Print'
                      : `Issue and Print`
                  "
                  :loading="loading"
                  @click.prevent="
                    () =>
                      onSubmitClick(
                        isEdit
                          ? fields.status === 'Draft'
                            ? 'Issued'
                            : fields.status
                          : 'Issued',
                        true,
                      )
                  "
                />
              </q-menu>
            </q-btn>
          </q-btn-group>
        </div>
      </div>
    </q-card>
  </q-form>
</template>
