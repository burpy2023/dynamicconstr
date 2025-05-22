<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center px-4">
    <!-- Card Container -->
    <div class="w-full max-w-md bg-white rounded-3xl shadow-xl p-10">
      
      <!-- Big Centered Heading -->
      <h1 class="text-6xl font-extrabold text-gray-900 mb-8 text-center">
        Dynamic Construction Form
      </h1>

      <!-- Reset Button (top-right) -->
  <div class="flex justify-end mb-6">
    <button
      @click="resetForm"
      class="flex items-center space-x-2 p-3 bg-red-500 hover:bg-red-600 text-white rounded-full shadow-lg transition"
      aria-label="Reset form"
    >
      <svg xmlns="http://www.w3.org/2000/svg"
          class="w-6 h-6"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          stroke-width="2"
      >
        <path d="M4 4v5h5M20 20v-5h-5M5 13a7 7 0 0112-4.9L20 8m-1 8a7 7 0 01-12 4.9L4 16"/>
      </svg>
      <span class="font-medium">Reset</span>
    </button>
  </div>

      <!-- Step Indicator -->
      <p class="text-xl text-gray-700 mb-4 text-center">
        Step {{ displayStep }} of {{ estimatedTotal }}
      </p>
      <div class="w-full bg-gray-200 h-2 rounded-full mb-8 overflow-hidden">
        <div
          class="h-full bg-blue-500 transition-all"
          :style="{ width: ((displayStep - 1) / (estimatedTotal - 1)) * 100 + '%' }"
        />
      </div>

      <!-- Breadcrumbs (one per line) -->
      <transition-group
        name="slide"
        tag="div"
        class="mb-8 space-y-3 text-lg text-gray-700"
      >
        <div v-for="(value, key) in selections" :key="key" class="pl-2">
          {{ key }}: <strong>{{ value }}</strong>
        </div>
      </transition-group>

      <!-- Question Card -->
      <transition name="fade" mode="out-in">
        <div
          v-if="constructionNumber"
          key="result"
          class="text-center"
        >
          <svg class="mx-auto mb-4 w-16 h-16 text-green-600" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd"
                  d="M16.707 5.293a1 1 0 00-1.414 0L8 12.586  4.707 9.293a1 1 0 10-1.414 1.414l4 4a1 1 0  001.414 0l8-8a1 1 0 000-1.414z"
                  clip-rule="evenodd"/>
          </svg>
          <p class="text-2xl font-semibold text-gray-800">
            Final Construction Number: <span class="text-green-600">{{ constructionNumber }}</span>
          </p>
        </div>

        <div
          v-else-if="nextField && options.length"
          key="question"
          class="space-y-6"
        >
          <p class="text-2xl font-medium text-gray-800">{{ nextField }}</p>
          <div class="flex items-center space-x-4">
            <select
              v-model="selectedOption"
              class="flex-grow border border-gray-300 rounded-lg px-6 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            >
              <option disabled value="">Select an option</option>
              <option v-for="opt in options" :key="opt" :value="opt">
                {{ opt }}
              </option>
            </select>
            <button
              @click="onNext"
              :disabled="!selectedOption"
              class="px-6 py-3 bg-blue-600 text-white rounded-lg text-lg shadow disabled:opacity-50 hover:bg-blue-700 transition"
            >
              Next
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-else key="loading" class="text-center text-gray-500 text-lg">
          Loading...
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from 'vue'

const selections = reactive({})
const nextField = ref(null)
const options = ref([])
const constructionNumber = ref(null)
const selectedOption = ref('')
const estimatedTotal = 5  // adjust to your total steps

// never let the step count exceed estimatedTotal
const displayStep = computed(() => {
  const s = Object.keys(selections).length + 1
  return s > estimatedTotal ? estimatedTotal : s
})

async function fetchNext(params = {}) {
  const query = new URLSearchParams(params).toString()
  const res = await fetch(`http://localhost:8000/api/next/?${query}`)
  const data = await res.json()
  if (data.construction_number) {
    constructionNumber.value = data.construction_number
    nextField.value = null
    options.value = []
  } else {
    nextField.value = data.next
    options.value = data.options
    selectedOption.value = ''
  }
}

function onNext() {
  selections[nextField.value] = selectedOption.value
  fetchNext(selections)
}

function resetForm() {
  Object.keys(selections).forEach((k) => delete selections[k])
  nextField.value = null
  options.value = []
  constructionNumber.value = null
  selectedOption.value = ''
  fetchNext()
}

onMounted(() => fetchNext())
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.4s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

/* slide transition for breadcrumbs */
.slide-enter-active, .slide-leave-active {
  transition: all 0.3s ease;
}
.slide-enter-from, .slide-leave-to {
  transform: translateY(-10px);
  opacity: 0;
}
</style>
