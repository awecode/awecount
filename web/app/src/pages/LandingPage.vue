<template>
  <div class="bg-grey-3">
    <header class="row justify-between shadow-7 q-py-md q-px-md bg-white">
      <div class="row q-gutter-md">
        <img src="/img/awecount.png" alt="Awecount" style="width: 45px" />
        <span class="text-h4 text-weight-bold text-grey-9">AWECOUNT</span>
      </div>
      <div class="row q-gutter-md btns-con">
        <a href="https://docs.awecount.com/" style="color: inherit"><q-btn
            style="letter-spacing: 1px">Documentation</q-btn></a>
        <span><q-btn style="letter-spacing: 1px" to="/login">Sign in</q-btn></span>
      </div>
    </header>
    <main class="q-py-xl q-mx-lg text-grey-9">
      <div style="max-width: 1400px; margin: 0 auto">
        <div class="row-con items-end q-mb-xl">
          <div>
            <div class="text-h6 text-weight-bold text-blue-7">INTRODUCING</div>
            <div class="text-h4 text-weight-bold q-mt-sm">
              Your Awesome Accountant
            </div>
            <div class="text-body1 q-mt-xl">
              Automatic book-keeping for your business transactions.
            </div>
            <form action="https://formspree.io/mjvwepkb" method="POST">
              <q-input v-model="fields.email" class="q-mt-md" label="Your Email Address?" filled
                style="flex-grow: 1; max-width: 450px" type="email" required value="" name="email" />
              <div style="max-width: 450px; display: flex" class="q-mt-md">
                <q-input v-model="fields.phone_no" label="Your Phone Number?" filled style="flex-grow: 1" type="number"
                  required value="" name="phone_no" />
                <q-btn style="flex-grow: 0; flex-shrink: 0" color="blue-6" type="submit">Get Started!</q-btn>
              </div>
            </form>
          </div>
          <div>
            <img src="/img/login_bg.jpg" alt="" style="max-height: 350px; max-width: 100%" />
          </div>
        </div>
        <div class="row-con q-mb-xl">
          <div class="bg-white q-pa-lg">
            <div class="text-body1 text-weight-medium">FEATURES</div>
            <div class="q-mt-lg q-pt-sm" style="display: flex; gap: 10px" v-for="(item, index) in items" :key="index">
              <div style="width: 50px">
                <q-icon :name="item.icon" size="sm" color="grey-8" style="flex-grow: 0; flex-shrink: 0"></q-icon>
              </div>
              <div style="flex-grow: 1" class="text-body1 text-weight-medium text-grey-8">
                {{ item.text }}
              </div>
            </div>
          </div>
          <div class="bg-white q-pa-lg">
            <div class="q-my-lg">
              <div class="text-center text-h6 font-weight-medium text-grey-8">
                Already have an account?
              </div>
              <div class="text-center text-body2 text-weight-bold text-grey-8 q-mt-md">
                Login to Company Portal
              </div>
            </div>
            <LoginCard />
          </div>
        </div>
        <div class="cards-con">
          <div v-for="(card, index) in cards" :key="index" class="bg-white q-pa-md">
            <div class="text-center q-mb-lg q-mt-sm">
              <q-icon :name="card.icon" size="xl" color="blue-6"></q-icon>
            </div>
            <div class="text-center q-mb-lg text-h5 text-grey-8 font-weight-medium">
              {{ card.title }}
            </div>
            <div class="text-center q-mb-lg text-body1 text-grey-7 font-weight-medium">
              {{ card.text }}
            </div>
          </div>
        </div>
      </div>
    </main>
    <div class="bg-white q-px-lg q-pt-md q-pb-xl">
      <h2 style="font-size: 28px" class="text-center q-mb-xl text-weight-bold text-grey-8">
        CLIENTS
      </h2>
      <div class="client-con grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        <img src="/img/sangrila.png" alt="Sangrila" class="object-contain w-full h-full p-8" />
        <img src="/img/sampurna.png" alt="Sampurna" class="object-contain w-full h-full p-6" />
        <a href="https://edusanjal.com/" target="_blank">
          <img src="/img/edusanjal.png" alt="Edusanjal" class="object-contain w-full h-full p-4" />
        </a>
        <a href="https://thuprai.com/" target="_blank"><img src="/img/thuprai.svg" alt="Thuprai"
            class="object-contain w-full h-full p-4" /></a>
        <a href="https://crayonscorp.com.np/" target="_blank" class="flex items-center"><img src="/img/crayons_corp.png"
            alt="Crayons Corp" class="object-contain w-full h-full p-4" /></a>
        <img src="/img/self_drive_nepal.jpg" alt="Self Drive Nepal" class="object-contain w-full h-full p-4" />
        <a href="https://sparkcar.org/" target="_blank">
          <img src="/img/spark_car.jpg" alt="Spark Car" class="object-contain w-full h-full p-4" />
        </a>
        <a href="https://khaanpin.com.np/" target="_blank">
          <img src="/img/khaanpin.png" alt="Khaanpin" class="object-contain w-full h-full p-4" />
        </a>
        <div class="text-center p-4">
          <img src="/img/spark_link.jpg" alt="Spark Link" class="object-contain w-full h-full"
          style="max-height: 100px;" />
          <span class="text-center text-grey-8 text-body1">Spark Link</span>
        </div>
        <a href="https://www.codewarelab.com/" target="_blank">
          <img src="/img/codeware_lab.svg" alt="Codeware Lab" class="object-contain w-full h-full p-4" />
        </a>
        <a href="https://nepalaya.com.np/" target="_blank">
          <img src="/img/nepalaya.svg" alt="Nepalya" class="object-contain w-full h-full p-4" />
        </a>
      </div>
    </div>
    <footer class="bg-blue-6 q-py-sm">
      <div class="text-center text-white text-body1">Awecode © {{ new Date().getFullYear() }}</div>
    </footer>
  </div>
</template>

<script setup>
const items = [
  {
    text: 'IRD Approved Billing and POS System',
    icon: 'mdi-check-decagram',
  },
  {
    text: 'Automatic Sales and Purchase Books',
    icon: 'mdi-notebook-multiple',
  },
  { text: 'Graphical Reports', icon: 'mdi-chart-bar' },
  { text: 'Tax Reports', icon: 'mdi-cash-multiple' },
  { text: 'Advanced Accounting Suite', icon: 'mdi-calculator-variant' },
]
const cards = [
  {
    title: 'User Friendly',
    text: 'An accounting system made for non-accountants as well - handles double entry book keeping in the background.',
    icon: 'mdi-emoticon-happy',
  },
  {
    title: 'Automated Reports',
    text: 'Automatic generation of Sales Book, Purchase Book, Tax Reports, Trial Balance and other reports',
    icon: 'mdi-chart-pie',
  },
  {
    title: 'Highly Configurable',
    text: 'Localized Calendar, Settings for invoices and vouchers, and many customization options.',
    icon: 'mdi-cogs',
  },
  {
    title: 'Advanced Accounting',
    text: 'Has advanced features for seasoned accountants.',
    icon: 'mdi-book-plus',
  },
  {
    title: 'Secure and Compliant',
    text: 'Provides secure accounting with role based access control and is compliant with taxation laws.',
    icon: 'mdi-book-lock',
  },
  {
    title: 'Same-day Support',
    text: 'Our support team is available for support in all working days.',
    icon: 'mdi-face-agent',
  },
]
const fields = ref({
  email: '',
  phone_no: '',
})
useMeta({
  title: 'Awecount',
})
</script>

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
}

@media (max-width: 800px) {

  .btns-con {
    display: none;
  }
}
</style>
