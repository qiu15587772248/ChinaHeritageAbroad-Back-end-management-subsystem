import request from '@/utils/request'

// 获取日志列表
export function getLogList(params) {
  return request({
    url: '/api/logs',
    method: 'get',
    params
  })
}

// 获取日志概览
export function getLogOverview() {
  return request({
    url: '/api/logs/overview',
    method: 'get'
  })
}

// 导出日志
export function exportLogs(params) {
  return request({
    url: '/api/logs/export',
    method: 'get',
    params
  })
} 