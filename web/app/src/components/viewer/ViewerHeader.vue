<template>
  <q-card class="q-mx-lg q-pa-lg row text-grey-8 text-body2">
    <div class="col-12 col-md-6 q-gutter-y-lg">
      <div class="col-12 col-md-6 row">
        <div class="col-6">Party</div>
        <div class="col-6">{{ fields?.party_name }}</div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">Address</div>
        <div class="col-6">{{ fields?.address }}</div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">Status</div>
        <div class="col-6">{{ fields?.status }}</div>
      </div>
      <div class="col-12 col-md-6 row" v-if="discountComputed">
        <div class="col-6">Discount</div>
        <div class="col-6">
          {{ discountComputed }}
        </div>
      </div>
    </div>
    <div class="col-12 col-md-6 q-gutter-y-lg">
      <div class="col-12 col-md-6 row">
        <div class="col-6">Date</div>
        <div class="col-6">{{ fields?.date }}</div>
      </div>
      <div class="col-12 col-md-6 row">
        <div class="col-6">Mode</div>
        <div class="col-6">{{ fields?.mode }}</div>
      </div>
      <!-- <div class="col-12 col-md-6 row">
        <div class="col-6">Party</div>
        <div class="col-6">{{ fields?.status }}</div>
      </div> -->
    </div>
  </q-card>
</template>

<script>
export default {
  props: {
    fields: {
      type: Object,
      default: () => {
        return {}
      },
    },
  },
  setup(props, { emit }) {
    const discountComputed = computed(() => {
      console.log(props.fields)
      if (props.fields?.discount_obj) {
        return (
          `${props.fields.discount_obj.value}` +
          ' ' +
          `${props.fields.discount_obj.type === 'Amount' ? '-/' : '%'}`
        )
      } else if (props.fields?.discount) {
        ;`${props.fields.discount}` +
          ' ' +
          `${props.fields.discount_type === 'Amount' ? '-/' : '%'}`
      } else return false
    })
    return {
      props,
      discountComputed,
    }
  },
}
</script>
