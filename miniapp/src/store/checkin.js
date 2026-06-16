import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCheckinStore = defineStore('checkin', () => {
  const todayTasks = ref([])
  const isCheckedIn = ref(false)
  const stats = ref({ continuous_days: 0, total_days: 0 })

  function setTasks(tasks) { todayTasks.value = tasks }
  function setChecked(v) { isCheckedIn.value = v }
  function setStats(s) { stats.value = s }

  return { todayTasks, isCheckedIn, stats, setTasks, setChecked, setStats }
})
