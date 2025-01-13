<template>
  <div class="w-full">
    <div class="bg-white q-pa-lg -mt-2 transition-all">
      <q-card class="mt-2">
        <q-skeleton height="64px" square class="bg-green" />
        <q-card class="q-mx-lg q-pt-md pb-8 px-3">
          <div class="grid lg:grid-cols-2 grid-cols-1 gap-y-12 gap-x-6 py-6">
            <div class="flex gap-4">
              <div class="flex grow gap-1">
                <q-skeleton height="45px" type="rect" class="grow"></q-skeleton>
                <q-skeleton height="45px" width="45px" type="QBtn" square></q-skeleton>
              </div>
              <q-skeleton height="45px" width="65px" type="QBtn" square></q-skeleton>
            </div>
            <q-skeleton height="45px" type="QInput"></q-skeleton>
            <q-skeleton height="45px" type="QInput"></q-skeleton>
            <q-skeleton height="45px" type="QInput"></q-skeleton>
            <div class="flex gap-4">
              <q-skeleton height="45px" type="rect" class="grow"></q-skeleton>
              <q-skeleton height="45px" width="65px" type="QBtn" square></q-skeleton>
            </div>
            <div></div>
            <q-skeleton height="45px" type="QInput"></q-skeleton>
            <div></div>
          </div>
          <!-- <div class="pb-10">
            <q-card>
              <q-card-section class="q-pa-lg">
                <div class="pt-8 pb-6">
                  <hr class="h-[2px] bg-gray-300 b-0">
                </div>
                <div class="grid grid-cols-12 gap-6">
                  <div class="flex grow gap-1 col-span-5">
                    <q-skeleton height="45px" type="rect" class="grow">
                    </q-skeleton>
                    <q-skeleton height="45px" width="45px" type="QBtn" square>
                    </q-skeleton>
                  </div>
                  <div class="col-span-2">
                    <q-skeleton height="45px" type="rect">
                    </q-skeleton>
                  </div>
                  <div class="col-span-2">
                    <q-skeleton height="45px" type="rect">
                    </q-skeleton>
                  </div>
                  <div class="col-span-2">
                    <q-skeleton height="45px" type="rect">
                    </q-skeleton>
                  </div>
                  <div class="col-span-1 grid grid-cols-2 gap-2">
                    <q-skeleton type="rect">
                    </q-skeleton>
                    <q-skeleton type="rect">
                    </q-skeleton>
                  </div>
                </div>
                <div class="sm:grid grid-cols-8 py-8">
                  <div class="col-span-5"></div>
                  <div class="col-span-3 grid grid-cols-2 gap-x-4">
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                    <q-skeleton type="text" height="30px" class="w-">
                    </q-skeleton>
                  </div>

                </div>
              </q-card-section>
            </q-card>
          </div> -->
          <div class="flex justify-right">
            <q-skeleton type="QBtn" class="bg-green" height="36px"></q-skeleton>
          </div>
        </q-card>
      </q-card>
    </div>
  </div>
</template>
