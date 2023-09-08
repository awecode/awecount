<template>
  <div class="window-height background row justify-center items-center">
    <div class="q-pa-md rounded-borders bg-white loginContainer">
      <div class="column items-center">
        <img class="logo" src="/img/awecount.png" alt="Awecount">
        <div class="text-md text-h6 q-mt-sm">Awecount</div>
        <span class="q-mt-md">Login to Company Portal</span>
      </div>
      <LoginCard />
    </div>
  </div>
</template>

<script setup>
useMeta({
  title: 'Login | Awecount',
})
</script>

<style scoped>
.background {
  background-image: url('/img/login_bg.jpg');
  background-position: center center;
  background-repeat: no-repeat;
  background-size: cover;
}

@media (max-width: 800px) {
  div.loginContainer {
    width: 90%;
    margin: 0 40px;
    padding: 20px 0;
  }
}

.loginContainer {
  width: 600px;
  padding: 50px 0;
}

.logo {
  width: 50%;
  max-width: 100px;
}
</style>
