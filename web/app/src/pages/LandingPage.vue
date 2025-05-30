<script setup>
import { useAuthStore } from 'src/stores/auth'

const { isAuthenticated, user } = useAuthStore()

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

<template>
  <div class="bg-grey-3">
    <header class="row justify-between shadow-7 q-py-md q-px-md bg-white">
      <div class="row q-gutter-md">
        <img alt="Awecount" src="/img/awecount.png" style="width: 45px" />
        <span class="text-h4 text-weight-bold text-grey-9">AWECOUNT</span>
      </div>
      <div class="row q-gutter-md btns-con">
        <a href="https://docs.awecount.com/" style="color: inherit"><q-btn style="letter-spacing: 1px">Documentation</q-btn></a>
        <template v-if="isAuthenticated">
          <q-btn color="primary" style="letter-spacing: 1px" :to="`/${user.redirect}/dashboard`">
            Go to Dashboard
          </q-btn>
        </template>
        <template v-else>
          <q-btn style="letter-spacing: 1px" to="/login">
            Sign in
          </q-btn>
        </template>
      </div>
    </header>
    <main class="q-py-xl q-mx-lg text-grey-9">
      <div style="max-width: 1400px; margin: 0 auto">
        <div class="row-con items-end q-mb-xl">
          <div>
            <div class="text-h6 text-weight-bold text-blue-7">
              INTRODUCING
            </div>
            <div class="text-h4 text-weight-bold q-mt-sm">
              Your Awesome Accountant
            </div>
            <div class="text-body1 q-mt-xl">
              Automatic book-keeping for your business transactions.
            </div>
            <template v-if="!isAuthenticated">
              <form action="https://formspree.io/mjvwepkb" method="POST">
                <q-input
                  v-model="fields.email"
                  filled
                  required
                  class="q-mt-md"
                  label="Your Email Address?"
                  name="email"
                  style="flex-grow: 1; max-width: 450px"
                  type="email"
                  value=""
                />
                <div class="q-mt-md" style="max-width: 450px; display: flex">
                  <q-input
                    v-model="fields.phone_no"
                    filled
                    required
                    label="Your Phone Number?"
                    name="phone_no"
                    style="flex-grow: 1"
                    type="number"
                    value=""
                  />
                  <q-btn color="blue-6" style="flex-grow: 0; flex-shrink: 0" type="submit">
                    Get Started!
                  </q-btn>
                </div>
              </form>
            </template>
            <template v-else>
              <div class="q-mt-xl">
                <div class="text-h6 text-weight-medium">
                  Welcome back!
                </div>
                <div class="text-body1 q-mt-sm">
                  You're logged in as {{ user.email }}
                </div>
                <q-btn
                  class="q-mt-md"
                  color="primary"
                  :to="`/${user.redirect}/dashboard`"
                >
                  Go to Dashboard
                </q-btn>
              </div>
            </template>
          </div>
          <div>
            <img alt="" src="/img/login_bg.jpg" style="max-height: 350px; max-width: 100%" />
          </div>
        </div>
        <div class="row-con q-mb-xl">
          <div class="bg-white q-pa-lg">
            <div class="text-body1 text-weight-medium">
              FEATURES
            </div>
            <div
              v-for="(item, index) in items"
              :key="index"
              class="q-mt-lg q-pt-sm"
              style="display: flex; gap: 10px"
            >
              <div style="width: 50px">
                <q-icon
                  color="grey-8"
                  size="sm"
                  style="flex-grow: 0; flex-shrink: 0"
                  :name="item.icon"
                />
              </div>
              <div class="text-body1 text-weight-medium text-grey-8" style="flex-grow: 1">
                {{ item.text }}
              </div>
            </div>
          </div>
          <div v-if="!isAuthenticated" class="bg-white q-pa-lg">
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
          <div v-else class="bg-white q-pa-lg">
            <div class="text-body1 text-weight-medium">
              QUICK ACTIONS
            </div>
            <div class="q-mt-lg">
              <q-list>
                <q-item v-ripple clickable :to="`/${user.redirect}/dashboard`">
                  <q-item-section avatar>
                    <q-icon name="dashboard" />
                  </q-item-section>
                  <q-item-section>Dashboard</q-item-section>
                </q-item>
                <q-item v-ripple clickable :to="`/${user.redirect}/sales/vouchers`">
                  <q-item-section avatar>
                    <q-icon name="receipt" />
                  </q-item-section>
                  <q-item-section>Sales Vouchers</q-item-section>
                </q-item>
                <q-item v-ripple clickable :to="`/${user.redirect}/purchase/vouchers`">
                  <q-item-section avatar>
                    <q-icon name="shopping_cart" />
                  </q-item-section>
                  <q-item-section>Purchase Vouchers</q-item-section>
                </q-item>
                <q-item v-ripple clickable :to="`/${user.redirect}/reports/day-book`">
                  <q-item-section avatar>
                    <q-icon name="book" />
                  </q-item-section>
                  <q-item-section>Day Book</q-item-section>
                </q-item>
                <q-item v-ripple clickable :to="`/${user.redirect}/settings`">
                  <q-item-section avatar>
                    <q-icon name="settings" />
                  </q-item-section>
                  <q-item-section>Settings</q-item-section>
                </q-item>
              </q-list>
            </div>
          </div>
        </div>
        <div class="cards-con">
          <div v-for="(card, index) in cards" :key="index" class="bg-white q-pa-md">
            <div class="text-center q-mb-lg q-mt-sm">
              <q-icon color="blue-6" size="xl" :name="card.icon" />
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
      <h2 class="text-center q-mb-xl text-weight-bold text-grey-8" style="font-size: 28px">
        CLIENTS
      </h2>
      <div class="client-con grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-6">
        <img alt="Sangrila" class="object-contain w-full h-full p-8" src="/img/sangrila.png" />
        <img alt="Sampurna" class="object-contain w-full h-full p-6" src="/img/sampurna.png" />
        <a href="https://edusanjal.com/" target="_blank">
          <img alt="Edusanjal" class="object-contain w-full h-full p-4" src="/img/edusanjal.png" />
        </a>
        <a href="https://thuprai.com/" target="_blank"><img alt="Thuprai" class="object-contain w-full h-full p-4" src="/img/thuprai.svg" /></a>
        <a class="flex items-center" href="https://crayonscorp.com.np/" target="_blank"><img alt="Crayons Corp" class="object-contain w-full h-full p-4" src="/img/crayons_corp.png" /></a>
        <img alt="Self Drive Nepal" class="object-contain w-full h-full p-4" src="/img/self_drive_nepal.jpg" />
        <a href="https://sparkcar.org/" target="_blank">
          <img alt="Spark Car" class="object-contain w-full h-full p-4" src="/img/spark_car.jpg" />
        </a>
        <a href="https://khaanpin.com.np/" target="_blank">
          <img alt="Khaanpin" class="object-contain w-full h-full p-4" src="/img/khaanpin.png" />
        </a>
        <div class="text-center p-4">
          <img
            alt="Spark Link"
            class="object-contain w-full h-full"
            src="/img/spark_link.jpg"
            style="max-height: 100px"
          />
          <span class="text-center text-grey-8 text-body1">Spark Link</span>
        </div>
        <a href="https://www.codewarelab.com/" target="_blank">
          <img alt="Codeware Lab" class="object-contain w-full h-full p-4" src="/img/codeware_lab.svg" />
        </a>
        <a href="https://nepalaya.com.np/" target="_blank">
          <img alt="Nepalya" class="object-contain w-full h-full p-4" src="/img/nepalaya.svg" />
        </a>
      </div>
    </div>
    <footer class="bg-blue-6 q-py-sm">
      <div class="text-center text-white text-body1">
        Awecode © {{ new Date().getFullYear() }}
      </div>
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
}

@media (max-width: 800px) {
  .btns-con {
    display: none;
  }
}
</style>
