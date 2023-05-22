<template>
    <template v-if="!(props.config.hide_zero_transactions && !checkZeroTrans()) &&
        !props.config.hide_categories
        ">
        <template v-for="(newobj, index) in newTotalObjArray" :key="index">
            {{ itemProps.name }}
            <hr>
            {{ newobj }}
            <hr>
            {{ itemProps }}
        </template>
        <!-- <template v-for="(newTotalObj, index) in newTotalObjArray" :key="index">
            <tr v-if="newTotalObj" :class="expandAccountsProps ? '' : 'hidden'">
                <td class="text-blue-6" :class="props.root ? 'text-weight-bold' : ''">
                    <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                    <span style="display: inline-block; width: 40px; margin-left: -5px;">
                        <q-btn class="expand-btn" dense flat round :class="expandStatus ? 'expanded' : ''"
                            @click="changeExpandStatus(item.id)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                                class="text-grey-7">
                                <path fill="currentColor" d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" />
                            </svg>
                        </q-btn>
                    </span>
                    <RouterLink style="text-decoration: none" target="_blank"
                        :to="`/account/?has_balance=true&category=${item.id}`" class="text-blue-6">{{ item.name }}
                    </RouterLink>
                </td>
                <td>
                    {{ calculateNet(newTotalObj) }}
                </td>
            </tr>
        </template> -->
        <template v-for="(showTotalObjPeriod, index) in showTotalObject" :key="index">
            <tr v-if="!!(
                showTotalObjPeriod.opening_cr ||
                showTotalObjPeriod.opening_dr ||
                showTotalObjPeriod.closing_cr ||
                showTotalObjPeriod.closing_dr
            )
                " :class="expandAccountsProps ? '' : 'hidden'">
                <td class="text-blue-6">
                    <span v-for="num in level" :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span>
                    <span style="display: inline-block; width: 40px; margin-left: -5px;">
                        <q-btn class="expand-btn" dense flat round :class="expandStatus ? 'expanded' : ''"
                            @click="changeExpandStatus(item.id)">
                            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                                class="text-grey-7">
                                <path fill="currentColor" d="m12 15.4l-6-6L7.4 8l4.6 4.6L16.6 8L18 9.4l-6 6Z" />
                            </svg>
                        </q-btn>
                    </span>
                    <RouterLink style="text-decoration: none" target="_blank"
                        :to="`/account/?has_balance=true&category=${item.id}`" class="text-blue-6">{{ item.name }}
                    </RouterLink>
                </td>
                <td>{{ calculateNet(showTotalObjPeriod) }}</td>
            </tr>
        </template>
    </template>
    <!-- {{ activeObjectArray }}--active -->
    <template v-for="(periodArray, index) in activeObjectArray" :key="index">
        <template v-if="periodArray &&
            periodArray.length &&
            !props.config.hide_accounts
            ">
            <template v-for="activeObject in periodArray" :key="activeObject.id">
                <tr v-if="!(
                    props.config.hide_zero_transactions &&
                    !(activeObject.transaction_dr || activeObject.transaction_cr)
                )
                    " :class="expandAccountsProps && expandStatus ? '' : 'hidden'">
                    <td class="text-blue-6 text-italic">
                        <span v-if="!props.config.hide_categories">
                            <span style="display: inline-block; width: 40px; margin-left: -5px;"></span>
                            <span v-for="num in props.level + 1"
                                :key="num">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;</span></span>
                        <RouterLink target="_blank" style="text-decoration: none"
                            :to="`/account/${activeObject.account_id}/view/`"
                            class="text-blue-7 text-italic text-weight-regular">{{ activeObject.name }}</RouterLink>
                    </td>
                    <td>{{ calculateNet(activeObject) }}</td>
                </tr>
            </template>
        </template>
    </template>
    <template v-if="item.children && item.children.length">
        <BalanceSheetTableNode v-for="(child, index) in item.children" :key="child.id" :item="child" :index="index"
            :level="props.level + 1" :accounts="props.accounts" :category_accounts="props.category_accounts"
            @updateTotal="onUpdateTotal" :config="props.config" :expandAccountsProps="expandAccountsProps && expandStatus"
            :isAsset="props.isAsset">
        </BalanceSheetTableNode>
    </template>
</template>
  
<script>
import { useLoginStore } from 'src/stores/login-info'
export default {
    props: {
        item: {
            type: Object,
            default: () => {
                return {}
            },
        },
        root: {
            type: Boolean,
            default: () => false,
        },
        level: {
            type: Number,
            default: () => 0,
        },
        accounts: {
            type: Object,
            default: () => {
                return {}
            },
        },
        category_accounts: {
            type: Object,
            default: () => {
                return {}
            },
        },
        index: {
            type: [Number, null],
            default: null,
        },
        config: {
            type: Object,
            default: () => {
                return {}
            },
        },
        expandAccountsProps: {
            type: Boolean,
            default: () => true
        },
        isAsset: {
            type: Boolean,
            default: () => false
        }
    },
    emits: ['updateTotal'],

    setup(props, { emit }) {
        const loginStore = useLoginStore()
        // const expandStatus = ref(true)
        const itemProps = ref({ ...props.item })
        const fieldsArray = [
            'closing_cr',
            'closing_dr',
            'opening_cr',
            'opening_dr',
            'transaction_cr',
            'transaction_dr',
        ]
        const totalObjectFormat = {
            closing_cr: 0,
            closing_dr: 0,
            opening_cr: 0,
            opening_dr: 0,
            transaction_cr: 0,
            transaction_dr: 0,
        }
        const showTotalObject = ref([])
        const newTotalObjArray = ref([])
        const activeObjectArray = computed(() => {
            const activeArray = []
            props.accounts.forEach((item, index) => {
                const currentActiveArray = []
                showTotalObject.value[index] = totalObjectFormat
                const accountArray = props.category_accounts[index][props.item.id]
                if (accountArray) {
                    accountArray.forEach((item) => {
                        const currentObj = props.accounts[index][item]
                        currentActiveArray.push(currentObj)
                        fieldsArray.forEach((item) => {
                            showTotalObject.value[index][item] += currentObj[item]
                        })
                        activeArray[index] = currentActiveArray
                    })
                    emit('updateTotal', showTotalObject.value, props.index)
                }
                // debugger
            })
            return activeArray
        })
        const activeObject = null
        const onUpdateTotal = (total, index) => {
            itemProps.value.children[index].total = total
        }
        const calculateNet = (obj) => {
            let netAmount = 0
            if (props.isAsset) {
                netAmount = obj.closing_dr - obj.closing_cr
            }
            else {
                netAmount = obj.closing_cr - obj.closing_dr
            }
            if (netAmount > 0) return netAmount
            return `(${netAmount * -1})`
            // const net = parseFloat(
            //     (obj[`${type}` + '_cr'] - obj[`${type}` + '_dr']).toFixed(2)
            // )
            // if (net === 0) {
            //     return 0
            // } else if (net > 0) {
            //     return `${net}` + ' cr'
            // } else {
            //     return `${net * -1}` + ' dr'
            // }
        }
        // check zero trans status
        // const checkZeroTrans = () => {
        //     if (newTotalObj.value) {
        //         return !!(
        //             newTotalObj.value.transaction_cr || newTotalObj.value.transaction_dr
        //         )
        //     } else if (showTotalObject.value) {
        //         return !!(
        //             showTotalObject.value.transaction_cr ||
        //             showTotalObject.value.transaction_dr
        //         )
        //     } else return true
        // }
        watch(
            itemProps,
            (newValue) => {
                let computedTotal = []
                newValue.children.forEach((child, childIndex) => {
                    if (child.total && child.total.length > 0) {
                        child.total.forEach((totalObj, totalIndex) => {
                            if (totalObj) {
                                // console.log(computedTotal)
                                computedTotal = [totalObjectFormat]
                                fieldsArray.forEach((field) => {
                                    computedTotal[totalIndex][field] = computedTotal[totalIndex][field] + totalObj[field]
                                })
                            }
                        })
                    }
                    else computedTotal = []
                })
                // if (itemProps.value.name === 'Liabilities') debugger
                newTotalObjArray.value = computedTotal
                emit('updateTotal', computedTotal, props.index)
            },
            { deep: true }
        )
        const changeExpandStatus = (id) => {
            const index = loginStore.trialBalanceCollapseId.indexOf(id)
            if (index >= 0) loginStore.trialBalanceCollapseId.splice(index, 1)
            else loginStore.trialBalanceCollapseId.push(id)
        }
        const expandStatus = computed(() => {
            const newTotalObjStatus = props.item.id && loginStore.trialBalanceCollapseId.includes(props.item.id)
            return !newTotalObjStatus
        })
        // watch([newTotalObj, showTotalObject], () => {
        // })
        return {
            props,
            itemProps,
            activeObject,
            activeObjectArray,
            onUpdateTotal,
            showTotalObject,
            newTotalObjArray,
            calculateNet,
            // checkZeroTrans,
            expandStatus,
            changeExpandStatus,
            loginStore
        }
    },
}
</script>
  
  
<style lang="scss">
.expand-btn {
    width: 20px;

    svg {
        padding: 5px;
        // width: 20px;
        // width: 100%;
        translate: 0.5px 1px;
        transition: all 0.2s ease-in;
    }

    &.expanded {
        svg {
            translate: 1px 1px;
            transform: rotate(-90deg);
        }
    }

}
</style>