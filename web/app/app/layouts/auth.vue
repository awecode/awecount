<template>
  <div class="row justify-center items-center" style="min-height: 100vh">
    <div class="col-xs-12 col-sm-8 col-md-6 col-lg-4">
      <div class="text-center q-mb-xl">
        <img alt="Logo" src="/img/awecount.png" style="height: 48px" />
      </div>

      <q-card class="q-pa-md">
        <slot></slot>
      </q-card>
    </div>
  </div>
</template>
