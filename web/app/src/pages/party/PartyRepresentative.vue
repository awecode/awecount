<template>
  <h6>Contact Person</h6>
  <q-card class="q-pa-md">
    <div v-for="(representative, index) in modalValue" :key="index">
      <div class="row q-col-gutter-md q-gutter-y-md">
        <q-input
          v-model="representative.name"
          label="Name"
          class="col-12 col-md-6"
        />
        <q-input
          v-model="representative.position"
          label="Positions"
          class="col-12 col-md-6"
        />
      </div>
      <div class="row q-col-gutter-md q-gutter-y-md">
        <q-input
          v-model="representative.phone"
          label="Phone Number"
          class="col-12 col-md-6"
        />
        <q-input
          v-model="representative.email"
          label="Email"
          class="col-12 col-md-6"
          type="email"
          :error="!!errors.representative"
          :error-message="errors.representative"
        />
      </div>
    </div>
  </q-card>
</template>
<script>
export default {
  props: {
    modelValueProp: {
      type: Array,
      default: () => [
        {
          name: '',
          position: '',
          phone: '',
          email: '',
        },
      ],
    },
    form: Object,
    errors: {
      type: [Object, String],
      default: () => {
        return {
          representative: null,
        };
      },
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalValue = ref(props.modelValueProp);
    const endpoint = '/v1/sales-voucher/';
    // const isErrorComputed = computed(() => {
    //   // const error = errors;
    //   debugger;
    //   if (errors) {
    //     return errors;
    //   }
    // });
    watch(
      () => props.modelValueProp,
      (newValue) => {
        modalValue.value = newValue;
      }
    );
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/account/',
      }),
      modalValue,
    };
  },
};
</script>
