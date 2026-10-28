<template>
  <div class="brand-logo-wrap row items-center no-wrap flex-shrink-0" :style="{ gap: gap + 'px' }">
    <!-- $100k Luxury Fintech Emblem Jewel -->
    <div
      class="brand-logo-jewel-frame row items-center justify-center flex-shrink-0"
      :style="{
        width: size + 'px',
        height: size + 'px',
        borderRadius: badgeRadius + 'px'
      }"
    >
      <img
        v-if="!imgError"
        :src="logoUrl"
        :width="size"
        :height="size"
        alt="MyBank Logo"
        class="brand-logo-img"
        :style="{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          borderRadius: Math.max(badgeRadius - 2, 4) + 'px',
          display: 'block'
        }"
        @error="imgError = true"
      />
      <q-icon
        v-else
        name="account_balance"
        :size="Math.round(size * 0.6) + 'px'"
        color="primary"
      />
    </div>

    <!-- $100k Precision Typography Lockup -->
    <div v-if="withText" class="column justify-center leading-tight flex-shrink-0" style="min-width: max-content;">
      <div class="row items-center no-wrap">
        <span
          class="brand-title"
          :style="{
            fontSize: titleSize,
            letterSpacing: '-0.035em'
          }"
        >
          <span class="brand-title-text">
            <span style="color: var(--text-primary) !important;">My</span><span style="color: var(--gold-primary) !important;">Bank</span>
          </span>
        </span>
        <span
          v-if="withYear"
          class="q-ml-xs luxury-pill-badge"
        >
          <span class="beacon-wrap">
            <span class="beacon-wave"></span>
            <span class="beacon-core"></span>
          </span>
          <span class="pill-label">LIVE</span>
        </span>
      </div>
      <span
        v-if="subtitle"
        class="text-caption brand-subtitle gt-xs"
        :style="{ fontSize: subtitleSize }"
      >
        {{ subtitle }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import logoUrl from '@/assets/logo.png'

const imgError = ref(false)

const props = defineProps({
  size: { type: [Number, String], default: 36 },
  gap: { type: [Number, String], default: 11 },
  withText: { type: Boolean, default: false },
  withYear: { type: Boolean, default: false },
  subtitle: { type: String, default: '' },
  theme: { type: String, default: 'dark' },
  withBadge: { type: Boolean, default: true },
})

const badgeRadius = computed(() => {
  return Math.round(Number(props.size) * 0.28)
})

const titleSize = computed(() => {
  const s = Number(props.size)
  if (s >= 64) return '1.55rem'
  if (s >= 48) return '1.38rem'
  if (s >= 36) return '1.22rem'
  return '1.08rem'
})

const subtitleSize = computed(() => {
  const s = Number(props.size)
  if (s >= 48) return '0.74rem'
  return '0.68rem'
})
</script>

<style scoped>
.brand-logo-wrap {
  user-select: none;
  cursor: pointer;
  flex-shrink: 0;
  white-space: nowrap;
}

.brand-logo-jewel-frame {
  position: relative;
  background: linear-gradient(145deg, rgba(255, 244, 217, 0.9) 0%, rgba(255, 255, 255, 1) 100%);
  border: 1px solid rgba(212, 175, 55, 0.4);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.8),
              0 7px 18px -8px rgba(29, 36, 48, 0.18);
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  padding: 1px;
}

.brand-logo-wrap:hover .brand-logo-jewel-frame {
  transform: scale(1.08) rotate(1deg);
  border-color: rgba(212, 175, 55, 0.6);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.9),
              0 12px 22px -10px rgba(29, 36, 48, 0.22);
}

.brand-title {
  font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Inter', sans-serif;
  font-weight: 800;
  line-height: 1.1;
  white-space: nowrap;
  flex-shrink: 0;
  color: var(--text-primary) !important;
}

.brand-title-text {
  color: var(--text-primary) !important;
  display: inline-block;
  white-space: nowrap;
  padding-right: 2px;
  text-shadow: none;
}

.luxury-pill-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(52, 199, 89, 0.1);
  border: 1px solid rgba(52, 199, 89, 0.28);
  color: #34C759;
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 0.62rem;
  font-weight: 800;
  letter-spacing: 0.08em;
  line-height: 1;
  white-space: nowrap;
  flex-shrink: 0;
}

.beacon-wrap {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 8px;
  height: 8px;
  margin-right: 5px;
}

.beacon-core {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #34C759;
  box-shadow: 0 0 6px #34C759;
}

.beacon-wave {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: rgba(52, 199, 89, 0.5);
  animation: radarWave 2s infinite ease-out;
}

@keyframes radarWave {
  0% {
    transform: scale(0.9);
    opacity: 0.9;
  }
  70% {
    transform: scale(2.2);
    opacity: 0;
  }
  100% {
    transform: scale(2.2);
    opacity: 0;
  }
}

.brand-subtitle {
  color: var(--text-secondary) !important;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  line-height: 1.1;
  margin-top: 2px;
}
</style>
