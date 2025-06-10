import request from '@/utils/request'

export function getDashboardStats() {
  return request({
    url: '/api/dashboard/stats',
    method: 'get'
  })
} 