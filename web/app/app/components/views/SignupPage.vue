<script setup>
useMeta({ title: 'Sign Up | Awecount' })
</script>

<template>
  <div class="window-height background row justify-center items-center">
    <div class="q-pa-md rounded-borders bg-white signupContainer">
      <div class="column items-center">
        <img alt="Awecount" class="logo" src="/img/awecount.png" />
        <div class="text-md text-h6 q-mt-sm">
          Awecount
        </div>
        <span class="q-mt-md">Create Your Account</span>
      </div>
      <SignupCard />
    </div>
  </div>
</template>

<style scoped>
.background {
  background-image: url('/img/login_bg.jpg');
  background-position: center center;
  background-repeat: no-repeat;
  background-size: cover;
}

@media (max-width: 800px) {
  div.signupContainer {
    width: 90%;
    margin: 0 40px;
    padding: 20px 0;
  }
}

.signupContainer {
  width: 600px;
  padding: 50px 0;
}

.logo {
  width: 50%;
  max-width: 100px;
}
</style>
