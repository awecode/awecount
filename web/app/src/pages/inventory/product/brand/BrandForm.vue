<template>
  <div>
    <h1 class="form-title">
      <span v-if="fields.id">Update {{ fields.name }}</span>
      <span v-else>New Brand</span>
    </h1>
    <q-form @submit.prevent="submitForm">
      <div>
        <q-input />
      </div>
    </q-form>
    <!-- <vue-form
      :action="endpoint()"
      :collection-name="$options.collection_name"
      :create-permission="$hasPerm('BrandCreate')"
      :fields="fields"
      :submit-as-modal="submitAsModal"
      :update-permission="$hasPerm('BrandModify')"
    >
      <template ref="formTemplate" slot-scope="form">
        <div ref="setDisable">
          <v-row>
            <v-col cols="12" sm="6">
              <v-text-field
                v-model="fields.name"
                :error-messages="form.errors.get('name')"
                :label="'Name *'"
                name="name"
              ></v-text-field>
            </v-col>
          </v-row>
          <v-row>
            <v-col>
              <v-textarea
                v-model="fields.description"
                :error-messages="form.errors.get('description')"
                :label="'Description'"
                name="description"
              ></v-textarea>
            </v-col>
          </v-row>
        </div>
      </template>
    </vue-form> -->
  </div>
</template>
<script>
// import Form from "@/mixins/Form";
// import VueForm from "@/components/form/VueForm";
import useForm from '/src/composables/useForm'
export default {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  setup(props, context) {
    const endpoint = '/v1/brands/'
    return {
      ...useForm(endpoint, {
        getDefaults: true,
        successRoute: '/items/',
        // TODO: Add succes route
      }),
      // LedgerForm,
    }
  },
}
// export default {
//   components: { VueForm },
//   mixins: [Form],
//   endpoint: "brands/",
//   modifyModule: "BrandModify",
//   success_url: "/brand/",
//   collection_name: "brands",
//   data() {
//     return {
//       fields: {
//         id: null,
//         name: null,
//         description: null
//       }
//     };
//   }
// };
</script>
