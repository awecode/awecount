<template>
  <div class="bg-grey-2">
    <header class="row justify-between shadow-7 q-py-md q-px-md bg-white">
      <div class="row q-gutter-md">
        <img src="/img/awecount.png" alt="Awecount" style="width: 45px;">
        <span class="text-h4 text-weight-bold text-grey-9">AWECOUNT</span>
      </div>
      <div class="row q-gutter-md">
        <q-btn style="letter-spacing: 1px;">Documentation</q-btn>
        <q-btn style="letter-spacing: 1px;">Sign in</q-btn>
      </div>
    </header>
    <main class="q-pt-xl q-mx-lg text-grey-9">
      <div class="row-con items-end q-mb-xl">
        <div>
          <div class="text-h6 text-weight-bold text-blue-7">INTRODUCING</div>
          <div class="text-h4 text-weight-bold q-mt-sm">Your Awesome Accountant</div>
          <div class="text-body1 q-mt-xl">Automatic book-keeping for your business transactions.</div>
          <div style="max-width: 450px; display: flex;" class="q-mt-md">
            <q-input v-model="text" label="Your Email Address?" filled style="flex-grow: 1;" />
            <q-btn style="flex-grow: 0; flex-shrink: 0;" color="blue-6">Get Started!</q-btn>
          </div>
        </div>
        <div>
          <img src="/img/login_bg.jpg" alt="" style="max-height: 350px;">
        </div>
      </div>
      <div class="row-con q-mb-xl">
        <div class="bg-white q-pa-lg">
          <div class="text-body1 text-weight-medium">FEATURES</div>
          <div class="q-mt-lg" style="display: flex; gap: 10px;" v-for="(item, index) in items" :key="index">
            <div style="width: 50px;">
              <q-icon :name="item.icon" size="sm" color="grey-8" style="flex-grow: 0; flex-shrink: 0;"></q-icon>
            </div>
            <div style="flex-grow: 1;" class="text-body1 text-weight-medium text-grey-8">{{ item.text }}</div>
          </div>
        </div>
        <div>
          <img src="/img/login_bg.jpg" alt="" style="max-height: 350px;">
        </div>
      </div>
    </main>
  </div>
</template>
<style scoped>
/* .row-con {
    display: grid;
    grid-template-rows: auto auto;
  } */
.row-con {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}
</style>

<script setup>
const items = [
  {
    text: 'IRD Approved Billing and POS System',
    icon: 'mdi-check-decagram'
  },
  {
    text: 'Automatic Sales and Purchase Books',
    icon: 'mdi-notebook-multiple'
  },
  { text: 'Graphical Reports', icon: 'mdi-chart-bar' },
  { text: 'Tax Reports', icon: 'mdi-cash-multiple' },
  { text: 'Advanced Accounting Suite', icon: 'mdi-calculator-variant' }
]
</script>