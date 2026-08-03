import { defineStore } from 'pinia'
import { getVenues } from '../api'

export const useVenueStore = defineStore('venue', {
  state: () => ({
    venues: [],
    currentId: uni.getStorageSync('customer_venue_id') || null,
    currentName: uni.getStorageSync('customer_venue_name') || '',
  }),
  actions: {
    async load() {
      try {
        const res = await getVenues()
        this.venues = res.venues || []
        if (!this.currentId && this.venues.length > 0) {
          this.setCurrent(this.venues[0].id, this.venues[0].name)
        }
      } catch { /* */ }
    },
    setCurrent(id, name) {
      this.currentId = id
      this.currentName = name
      uni.setStorageSync('customer_venue_id', id)
      uni.setStorageSync('customer_venue_name', name)
    },
  },
})
