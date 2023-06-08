<template>
    <div class="q-py-lg">
        <div class="text-grey-8 q-pb-md">{{ label }}</div>
        <div>
            <div v-if="typeof modalValue === 'string'" class="row q-gutter-sm q-pb-sm bg-grey-3"
                style="max-height: 200px; overflow-x: auto; border-radius: 5px;">
                <span class="q-px-sm bg-blue-2" style="border-radius: 10px; padding: 2px 4px 0px 8px;"> {{
                    options[options.findIndex((item) =>
                        item.id ==
                        modalValue)]?.name }}<q-btn dense flat icon="cancel" color="red"
                        @click="() => removeOption(modalValue)"></q-btn>
                </span>
            </div>
            <div v-else-if="modalValue.length > 0" class="row q-gutter-sm q-pb-sm bg-grey-3"
                style="max-height: 200px; overflow-x: auto; border-radius: 5px;">
                <span class="bg-blue-2 text-subtitl2" style="border-radius: 10px; padding: 2px 4px 0px 8px;"
                    v-for="option in modalValue" :key="option"> {{
                        options[options.findIndex((item) =>
                            item.id ==
                            option)]?.name }}<q-btn dense flat class="q-pa-none q-ml-sm" size="md" icon="cancel" color="red-5"
                        @click="() => removeOption(option)"></q-btn>
                </span>
            </div>
            <div v-else class="text-sm text-grey-7 q-pa-sm bg-grey-3" style="text-transform: lowercase;">no {{ label }}
                selected</div>
            <!-- selected options {{ modalValue }}--modalValue -->
        </div>
        <div>
            <q-select v-model="modalValueSelect" :label="`${label}`" option-value="id" option-label="name"
                :options="options" map-options emit-value>
                <!-- <template v-slot:append>
                                            <q-icon v-if="fields.mode !== null" class="cursor-pointer" name="clear"
                                                @click.stop.prevent="fields.mode = null" /></template> -->
            </q-select>
        </div>
        <div class="row q-gutter-sm">
            <!-- style="border-radius: 1rem; padding: 4px 12px" -->
            <!-- <q-btn @click="() => onStatusClick(statuses)" style="border-radius: 1rem; padding: 4px 12px" size="sm"
          class="text-subtitle2" v-for="(statuses, index) in options" :key="index" :class="modalValue.includes(statuses)
            ? 'bg-blue-1 text-blue-9'
            : 'bg-grey-4 text-grey-9'
            ">
          <div class="row items-center">
            <Transition>
              <q-icon style="height: 22px" v-if="modalValue.includes(statuses)" name="check" size="sm" color="blue"
                class="q-mr-xs"></q-icon>
            </Transition>
            <span style="font-size: 0.85rem; text-transform: capitalize">
              {{ statuses }}
            </span>
          </div>
        </q-btn> -->
        </div>
        <!-- {{ modalValue }} --modalValue -->
    </div>
</template>
  
<script lang="ts">
import { Ref } from 'vue'

export default {
    props: {
        options: {
            type: Array<string>,
            default: () => [],
        },
        modelValue: {
            type: Array,
            default: () => {
                return []
            },
        },
        label: {
            type: String,
            default: () => 'Statuses:',
        },
    },
    emits: ['update:modelValue'],

    setup(props, { emit }) {
        const modalValueSelect = ref(null)
        const modalValue: Ref<Array<string>> = ref(props.modelValue)
        // const onStatusClick = (status: string) => {
        //     const index: number = modalValue.value.findIndex(
        //         (item) => item === status
        //     )
        //     if (index >= 0) {
        //         modalValue.value.splice(index, 1)
        //     } else {
        //         modalValue.value.push(status)
        //     }
        // }
        const removeOption = (id) => {
            if (typeof modalValue.value === 'string') modalValue.value = []
            else {
                // debugger
                const index: number = modalValue.value.findIndex(
                    (item) => item === id
                )
                modalValue.value.splice(index, 1)
            }
        }
        watch(
            () => modalValue,
            (newValue) => {
                emit('update:modelValue', newValue)
            },
            { deep: true }
        )
        watch(
            () => modalValueSelect,
            (newValue) => {
                // console.log(newValue.value)
                if (!modalValue.value.includes(newValue.value)) {
                    // debugger
                    if (typeof modalValue.value === 'string') modalValue.value = [`${modalValue.value}`]
                    modalValue.value.push(newValue.value)
                }
            },
            { deep: true }
        )
        watch(
            () => props.modelValue,
            (newValue: Array<string>) => {
                if (typeof newValue === 'string') {
                    modalValue.value = [`${newValue}`]
                    debugger
                }
                else modalValue.value = newValue
            },
            { deep: true }
        )
        return {
            modalValue,
            modalValueSelect,
            removeOption
        }
    },
}
</script>
<style>
.v-enter-active,
.v-leave-active {
    transition: opacity 0.1s linear;
    transition: width 0.1s linear;
    overflow: hidden;
}

.v-enter-from,
.v-leave-to {
    opacity: 0;
    width: 0;
}
</style>
  