<template>
  <div class="fullscreen bg-login-gradient text-center q-pa-md flex flex-center">
    <div class="glass-card q-pa-xl text-center" style="max-width: 480px; width: 92vw; border-radius: 28px;">
      <q-avatar size="72px" class="bg-lavender-gradient text-white shadow-md q-mb-md">
        <q-icon name="explore_off" size="36px" />
      </q-avatar>

      <div class="text-h2 text-weight-bolder" style="color: #C50337; letter-spacing: -0.04em;">
        404
      </div>

      <div class="text-h6 text-weight-bold q-mt-sm" style="color: #FFFFFF;">
        Page Not Found
      </div>

      <div class="text-caption text-grey-7 q-mt-xs q-mb-xl">
        The financial page or destination you are attempting to visit does not exist or may have been relocated.
      </div>

      <q-btn
        unelevated
        color="primary"
        to="/"
        icon="home"
        label="Return to Dashboard"
        no-caps
        class="text-weight-bold q-py-sm q-px-lg full-width"
        style="border-radius: 14px;"
      />
    </div>
  </div>
</template>
