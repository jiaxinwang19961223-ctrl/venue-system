import { defineStore } from 'pinia'
import { ref } from 'vue'
import { getVenues } from '../api'

export const useVenueStore = defineStore('venue', () => {
  const venues = ref([])
  const currentId = ref(parseInt(localStorage.getItem('venue_id') || '0'))
  const currentName = ref(localStorage.getItem('venue_name') || '')

  async function load() {
    try {
      const res = await getVenues()
      venues.value = res.venues || []
      // 如果还没选，默认第一个
      if (!currentId.value && venues.value.length) {
        setCurrent(venues.value[0].id, venues.value[0].name)
      }
    } catch { /* */ }
  }

  function setCurrent(id, name) {
    currentId.value = id
    currentName.value = name
    localStorage.setItem('venue_id', id)
    localStorage.setItem('venue_name', name || '')
  }

  return { venues, currentId, currentName, load, setCurrent }
})
