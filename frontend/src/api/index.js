import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// Request interceptor
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export default {
  // Get system status
  getStatus() {
    return api.get('/status')
  },

  // Get chats with flexible filtering (unified endpoint)
  getChats(params = {}) {
    return api.get('/chats', { params })
  },

  // Create chats
  createChats(chats) {
    return api.post('/chats', chats)
  },

  // Delete single chat
  deleteChat(id) {
    return api.delete('/chats', { params: { id } })
  },

  // Batch delete chats
  batchDeleteChats(ids) {
    return api.delete('/chats', { params: { ids: ids.join(',') } })
  }
}