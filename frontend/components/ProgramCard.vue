<template>
  <article class="program-card">
    <div class="program-card-topline">
      <span class="program-card-category">{{ program.category_meta.title }}</span>
      <span :class="planClass">{{ planLabel }}</span>
    </div>

    <div class="space-y-3">
      <div>
        <h2 class="program-card-title">{{ program.title }}</h2>
        <p class="program-card-description">{{ program.description || $t('programs.noDescription') }}</p>
      </div>

      <div class="program-card-meta">
        <span>{{ program.duration_days }} zile</span>
        <span>{{ activationLabel }}</span>
      </div>
    </div>

    <div class="program-card-actions">
      <NuxtLink :to="localePath(`/programs/${program.id}`)" class="program-card-link">
        Vezi detalii
      </NuxtLink>
      <span v-if="program.activation" class="program-card-progress">
        Ziua {{ program.activation.progress_day }}
      </span>
    </div>
  </article>
</template>

<script setup lang="ts">
const localePath = useLocalePath()

const props = defineProps<{
  program: {
    id: number
    title: string
    description: string
    category: string
    category_meta: { title: string; icon: string }
    duration_days: number
    plan_access: 'basic' | 'premium' | 'vip'
    can_activate: boolean
    activation?: { progress_day: number } | null
  }
}>()

const planLabel = computed(() => {
  if (props.program.plan_access === 'vip') return 'VIP Executive'
  if (props.program.plan_access === 'premium') return 'PREMIUM Flow'
  return 'BASIC Start'
})

const planClass = computed(() => {
  if (props.program.plan_access === 'vip') return 'program-card-plan program-card-plan-vip'
  if (props.program.plan_access === 'premium') return 'program-card-plan program-card-plan-premium'
  return 'program-card-plan program-card-plan-basic'
})

const activationLabel = computed(() => {
  if (props.program.activation) return 'Activ in acest moment'
  if (props.program.can_activate) return 'Activare disponibila'
  return 'Doar vizualizare'
})
</script>

<style scoped>
.program-card {
  display: grid;
  gap: 16px;
  border: 1px solid #d7dfd9;
  border-radius: 18px;
  padding: 20px;
  background:
    radial-gradient(circle at top right, rgba(246, 201, 119, 0.18), transparent 34%),
    linear-gradient(180deg, #fffef9 0%, #ffffff 72%);
  box-shadow: 0 18px 40px rgba(32, 48, 39, 0.06);
}

.program-card-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.program-card-category {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #6b7d72;
}

.program-card-plan {
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.program-card-plan-basic {
  background: #eef5f0;
  color: #5b7767;
}

.program-card-plan-premium {
  background: #fff2db;
  color: #9a6420;
}

.program-card-plan-vip {
  background: #e7f1eb;
  color: #2b6a4a;
}

.program-card-title {
  font-size: 22px;
  line-height: 1.15;
  font-weight: 700;
  color: #24362d;
}

.program-card-description {
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.6;
  color: #63746a;
}

.program-card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 12px;
  color: #7b8b83;
}

.program-card-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.program-card-link {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  border-radius: 999px;
  background: #1f352b;
  padding: 0 16px;
  font-size: 13px;
  font-weight: 700;
  color: white;
}

.program-card-progress {
  font-size: 12px;
  font-weight: 600;
  color: #8d5b17;
}
</style>
