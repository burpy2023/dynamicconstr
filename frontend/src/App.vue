<template>
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white">

    <!-- HEADER -->
    <div class="w-full py-8 px-6">
      <h1 class="text-4xl font-light tracking-wide text-white/90">
        Dynamic Construction Form
      </h1>
    </div>

    <!-- TWO-COLUMN LAYOUT -->
    <div class="flex w-full h-full">

      <!-- LEFT COLUMN: FORM -->
      <div class="w-1/2 p-6 space-y-8">

        <!-- Reset -->
        <div class="flex justify-end">
          <button
            @click="resetForm"
            class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 text-red-300 rounded-lg transition"
          >
            Reset
          </button>
        </div>

        <!-- Progress -->
        <div class="space-y-6">
          <div class="space-y-2">
            <div class="text-sm text-white/60">
              Progress Step {{ displayStep }} of {{ estimatedTotal }}
            </div>
            <div class="w-full bg-white/10 h-1 rounded overflow-hidden">
              <div
                class="h-full bg-gradient-to-r from-blue-400 to-purple-400 transition-all"
                :style="{ width: ((displayStep - 1)/(estimatedTotal - 1))*100 + '%' }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Question / Result -->
        <div class="space-y-6">
          <transition name="fade" mode="out-in">
            <!-- Final Result -->
            <div v-if="constructionNumber" key="result" class="space-y-4">
              <h2 class="text-2xl font-light text-green-400">Construction Complete</h2>
              <div class="bg-white/5 border border-white/10 rounded-lg p-6">
                <p class="text-white/60 text-sm">Construction Number</p>
                <p class="text-3xl font-mono text-green-400">{{ constructionNumber }}</p>
              </div>
            </div>

            <!-- Next Question -->
            <div v-else-if="nextField && options.length" key="question" class="space-y-4">
              <h2 class="text-2xl font-light text-white/90">{{ nextField }}</h2>
              <p class="text-white/60 text-sm">Select your preferred option</p>
              <select
                v-model="selectedOption"
                class="w-full bg-white/5 border border-white/20 rounded px-4 py-2 text-white"
              >
                <option disabled value="">Choose an option…</option>
                <option v-for="opt in options" :key="opt" :value="opt">{{ opt }}</option>
              </select>
              <button
                @click="onNext"
                :disabled="!selectedOption"
                class="w-full px-4 py-2 bg-blue-500/20 hover:bg-blue-500/30 disabled:bg-white/5 border border-blue-500/30 text-blue-300 rounded transition disabled:cursor-not-allowed"
              >
                {{ selectedOption ? 'Continue' : 'Please select an option' }}
              </button>
            </div>

            <!-- Loading -->
            <div v-else key="loading" class="text-center py-12">
              <div class="animate-spin w-8 h-8 border-2 border-white/20 border-t-blue-400 rounded-full mx-auto mb-4"></div>
              <p class="text-white/60">Loading options…</p>
            </div>
          </transition>
        </div>
      </div>

      <!-- RIGHT COLUMN: EXCEL-STYLE PRICING TABLE -->
      <div class="w-1/2 p-6">
        <h3 class="text-xl font-light text-white/80 mb-4">Pricing Table</h3>
        <div v-if="Object.keys(selections).length" class="bg-white/5 border border-white/10 rounded-lg overflow-auto">
          <table class="w-full table-auto border-separate border-spacing-0 text-white">
            <thead>
              <tr class="bg-white/10">
                <th class="px-2 py-1 text-left">Property</th>
                <th class="px-2 py-1 text-left">Selection</th>
                <th class="px-2 py-1 text-left">Price</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(v,k) in selections" :key="k + '-price'" class="hover:bg-white/10">
                <td class="px-2 py-1">{{ k }}</td>
                <td class="px-2 py-1">{{ v }}</td>
                <td class="px-2 py-1">&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, onMounted } from 'vue'

const selections        = reactive({})
const nextField         = ref(null)
const options           = ref([])
const constructionNumber= ref(null)
const selectedOption    = ref('')
const estimatedTotal    = 5

const displayStep = computed(() => {
  const s = Object.keys(selections).length + 1
  return s > estimatedTotal ? estimatedTotal : s
})

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function fetchNext(params = {}) {
  const query = new URLSearchParams(params).toString()
  const data  = await fetch(`${API_BASE}/api/next?${query}`).then(r => r.json())

  if (data.construction_number) {
    constructionNumber.value = data.construction_number
    nextField.value          = null
    options.value            = []
  } else {
    nextField.value          = data.next
    options.value            = data.options
    selectedOption.value     = ''
  }
}

function onNext() {
  selections[nextField.value] = selectedOption.value
  fetchNext(selections)
}

function resetForm() {
  Object.keys(selections).forEach(k => delete selections[k])
  nextField.value          = null
  options.value            = []
  constructionNumber.value = null
  selectedOption.value     = ''
  fetchNext()
}

onMounted(() => fetchNext())
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all .3s ease }
.fade-enter-from, .fade-leave-to   { opacity: 0; transform: translateY(10px) }
.slide-enter-active, .slide-leave-active { transition: all .3s ease }
.slide-enter-from, .slide-leave-to       { opacity: 0; transform: translateX(-10px) }

/* Override borders to ensure 6px white lines */
table th,
table td {
  border: 6px solid white !important;
}
</style>
