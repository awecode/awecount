<template>
    <div class="q-mx-md">
        <h6 class="q-mt-lg text-grey-9">Ratio Analysis</h6>
        <div v-for="(parentObj, index) in ratiosComputed" :key="index">
            <h6 class="text-weight-medium text-subtitle q-mb-lg text-grey-8">{{ parentObj.group_name }}</h6>
            <div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <q-card v-for="(ratioData, index) in parentObj.ratios" :key="index" class="col-6 q-pa-md">
                        <div>
                            <h6 class="q-ma-none flex justify-between q-pb-md"><span class="text-grey-8">{{
                                ratioData.card_name }}</span><span class="text-h4 text-grey-9">{{ ratioData.total }}
                                    %</span></h6>
                            <div class="flex">
                                <div class="column items-center text-grey-9" style="width: 150px; gap: 15px;">
                                    <div class="column items-center">
                                        <span>{{ ratioData.byData?.top.amount }}</span>
                                        <!-- <hr style="max-width: 100px; text-align: left; display: inline-block;"> -->
                                        <span
                                            style="display: inline-block; width: 120px; height: 2px; background-color: darkgrey;"></span>
                                        <span>{{ ratioData.byData?.bottom.amount }}</span>
                                    </div>
                                    <div class="column items-center">
                                        <span>{{ ratioData.byData?.top.label }}</span>
                                        <!-- <hr style="max-width: 100px; text-align: left; display: inline-block;"> -->
                                        <span
                                            style="display: inline-block; width: 120px; height: 2px; background-color: darkgrey;"></span>
                                        <span>{{ ratioData.byData?.bottom.label }}</span>
                                    </div>
                                </div>
                                <div style="flex-grow: 1;">
                                    <PieChart :data="ratioData.chart_data" />
                                </div>
                            </div>
                        </div>
                    </q-card>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
const data: Record<string, number> = {
    current_assets: 154658,
    current_liabilities: 65467,
    total_assets: 194956,
    total_liabilites: 89599,
    cash: 12450,
    equity: 24567,

}
const ratiosComputed = computed(() => {
    // const ratiosData = {
    //     current_ratio: {}
    // }
    const ratioData = {
        liquidity_ratios: {
            group_name: "Liquidity Ratios",
            ratios: {}
        },
        debit_ratios: {
            group_name: "Debt Ratios",
            ratios: {}
        }
    }
    ratioData.liquidity_ratios.ratios.current_ratio = {
        card_name: 'Current Ratio',
        total: parseFloat(((data.current_assets / data.current_liabilities) * 100).toFixed(2)),
        byData: {
            top: {
                label: 'Current Assets',
                amount: data.current_assets
            },
            bottom: {
                label: 'Current Liabilites',
                amount: data.current_liabilities
            }
        },
        chart_data: [
            {
                label: "Current Assets",
                amount: data.current_assets,
                color: 'rgb(54, 162, 235)',
            },
            {
                label: "Current Liabilites",
                amount: data.current_liabilities,
                color: 'rgb(255, 99, 132)',
            }
        ],
    }
    ratioData.liquidity_ratios.ratios.cash_ratio = {
        total: parseFloat(((data.cash / data.current_liabilities) * 100).toFixed(2)),
        card_name: 'Cash Ratio',
        byData: {
            top: {
                label: 'Cash',
                amount: data.cash
            },
            bottom: {
                label: 'Current Liabilites',
                amount: data.current_liabilities
            }
        },
        chart_data: [
            {
                label: "Cash",
                amount: data.cash,
                color: 'rgb(54, 162, 155)',
            },
            {
                label: "Current Liabilites",
                amount: data.current_liabilities,
                color: 'rgb(255, 99, 132)',
            }
        ],
    }
    ratioData.debit_ratios.ratios.debt_ratio = {
        total: parseFloat(((data.total_liabilites / data.total_assets) * 100).toFixed(2)),
        card_name: 'Debt Ratio',
        byData: {
            top: {
                label: 'Total Liabilites',
                amount: data.total_liabilites
            },
            bottom: {
                label: 'Total Assets',
                amount: data.total_assets
            }
        },
        chart_data: [
            {
                label: "Total Liabilites",
                amount: data.total_liabilites,
                color: 'rgb(178, 56, 136)',
            },
            {
                label: "Total Assets",
                amount: data.total_assets,
                color: 'rgb(40, 140, 185)',
            }
        ],
    }
    ratioData.debit_ratios.ratios.debt_to_equity = {
        total: parseFloat(((data.total_liabilites / data.equity) * 100).toFixed(2)),
        card_name: 'Debt to Equity Ratio',
        byData: {
            top: {
                label: 'Total Liabilites',
                amount: data.total_liabilites
            },
            bottom: {
                label: 'Shareholder Equity',
                amount: data.equity
            }
        },
        chart_data: [
            {
                label: "Total Liabilites",
                amount: data.total_liabilites,
                color: 'rgb(178, 56, 136)',
            },
            {
                label: "Shareholder Equity",
                amount: data.current_liabilities,
                color: 'rgb(255, 156, 85)',
            }
        ],
    }
    return ratioData
})
</script>
