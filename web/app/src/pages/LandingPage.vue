<template>
  <div class="bg-grey-3">
    <header class="row justify-between shadow-7 q-py-md q-px-md bg-white">
      <div class="row q-gutter-md">
        <img src="/img/awecount.png" alt="Awecount" style="width: 45px;">
        <span class="text-h4 text-weight-bold text-grey-9">AWECOUNT</span>
      </div>
      <div class="row q-gutter-md btns-con">
        <a href="https://docs.awecount.com/" style="color: inherit;"><q-btn style="letter-spacing: 1px;">Documentation</q-btn></a>
        <q-btn style="letter-spacing: 1px;" to="/login">Sign in</q-btn>
      </div>
    </header>
    <main class="q-py-xl q-mx-lg text-grey-9">
      <div class="row-con items-end q-mb-xl">
        <div>
          <div class="text-h6 text-weight-bold text-blue-7">INTRODUCING</div>
          <div class="text-h4 text-weight-bold q-mt-sm">Your Awesome Accountant</div>
          <div class="text-body1 q-mt-xl">Automatic book-keeping for your business transactions.</div>
          <div style="max-width: 450px; display: flex;" class="q-mt-md ">
            <q-input v-model="text" label="Your Email Address?" filled style="flex-grow: 1;" />
            <q-btn style="flex-grow: 0; flex-shrink: 0;" color="blue-6">Get Started!</q-btn>
          </div>
        </div>
        <div>
          <img src="/img/login_bg.jpg" alt="" style="max-height: 350px; max-width: 100%;">
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
        <div class="bg-white q-pa-lg">
          <div class="q-my-lg">
            <div class="text-center text-h6 font-weight-medium text-grey-8">Already have an account?</div>
            <div class="text-center text-body2 text-weight-bold text-grey-8 q-mt-md">Login to Company Portal</div>
          </div>
          <LoginCard />
        </div>
      </div>
      <div class="cards-con">
        <div v-for="(card, index) in cards" :key="index" class="bg-white q-pa-md">
          <div class="text-center q-mb-lg q-mt-sm">
            <q-icon :name="card.icon" size="xl" color="blue-6"></q-icon>
          </div>
          <div class="text-center q-mb-lg text-h5 text-grey-8 font-weight-medium">{{ card.title }}</div>
          <div class="text-center q-mb-lg text-body1 text-grey-7 font-weight-medium">{{ card.text }}</div>
        </div>
      </div>
    </main>
    <div class="bg-white q-px-lg q-pt-md q-pb-xl">
      <h2 style="font-size: 28px;" class="text-center q-mb-xl text-weight-bold text-grey-8">CLIENTS</h2>
      <div class="client-con">
        <img src="/img/sangrila.png" alt="Sangrila">
        <img src="/img/sampurna.png" alt="Sampurna">
        <a href="https://edusanjal.com/" target="_blank">
          <img src="/img/edusanjal.png" alt="Edusanjal">
        </a>
        <a href="https://thuprai.com/" target="_blank"><img src="/img/thuprai.svg" alt="Thuprai"></a>
      </div>
    </div>
    <footer class="bg-blue-6 q-py-sm">
      <div class="text-center text-white text-body1">© Awecode, 2020</div>
    </footer>
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

.cards-con {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 15px;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr 1fr;
  }
  @media (max-width: 800px) {
    grid-template-columns: 1fr;
  }
}

.client-con {
  max-width: 1300px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;

  @media (max-width: 800px) {
    flex-flow: column;
    /* justify-content: center; */
    align-items: center;
    gap: 15px;
  }

  @media (max-width: 800px) {
    flex-flow: column;
    /* justify-content: center; */
    align-items: center;
    gap: 15px;
  }
}

@media (max-width: 800px) {
  .client-con img {
    max-width: 180px;
    max-height: 40px;
  }
  .btns-con {
    display: none;
  }
}

.client-con img {
  height: 50px;
  width: auto;
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
const cards = [
  {
    title: 'User Friendly',
    text: 'An accounting system made for non-accountants as well - handles double entry book keeping in the background.',
    icon: 'mdi-emoticon-happy'
  },
  {
    title: 'Automated Reports',
    text: 'Automatic generation of Sales Book, Purchase Book, Tax Reports, Trial Balance and other reports',
    icon: 'mdi-chart-pie'
  },
  {
    title: 'Highly Configurable',
    text: 'Localized Calendar, Settings for invoices and vouchers, and many customization options.',
    icon: 'mdi-cogs'
  },
  {
    title: 'Advanced Accounting',
    text: 'Has advanced features for seasoned accountants.',
    icon: 'mdi-book-plus'
  },
  {
    title: 'Secure and Compliant',
    text: 'Provides secure accounting with role based access control and is compliant with taxation laws.',
    icon: 'mdi-book-lock'
  },
  {
    title: 'Same-day Support',
    text: 'Our support team is available for support in all working days.',
    icon: 'mdi-face-agent'
  },
]
</script>