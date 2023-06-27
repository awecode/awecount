<template>
    <div class="text-red-6 text-white text-center q-pa-md flex flex-center">
        <div class="q-pt-xl">
            <div class="text-h3" style="opacity:.4">
                You Don't Have Permission.
            </div>
            <q-btn class="q-mt-xl" text-color="blue" outline to="/" label="Go Back" no-caps @click="router.go(-1)" />
        </div>
    </div>
</template>  