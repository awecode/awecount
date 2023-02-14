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
          :error="true"
          :error-message="() => 'elol'"
        />
      </div>
      {{ isErrorComputed }}--computed -- props errr
    </div>
    <!-- {{ errors[0]?.email[0] }}--err -->
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
        return {};
      },
    },
  },
  emits: ['update:modelValue'],

  setup(props, { emit }) {
    const modalValue = ref(props.modelValueProp);
    const endpoint = '/v1/sales-voucher/';
    const isErrorComputed = computed(() => {
      const error = props.errors;
      debugger;
      if (error) {
        return error;
      }
    });
    watch(
      () => props.modelValueProp,
      (newValue) => {
        modalValue.value = newValue;
      }
    );
    watch(
      modalValue,
      (newValue) => {
        emit('update:modelValue', newValue);
      },
      { deep: true }
    );

    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/account/',
      }),
      modalValue,
      isErrorComputed,
    };
  },
};
</script>
