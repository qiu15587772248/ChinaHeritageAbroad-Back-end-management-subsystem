import request from '@/utils/request'

// 获取备份列表
export function getBackupList(params) {
  return request({
    url: '/api/backup',
    method: 'get',
    params
  })
}

// 创建备份
export function createBackup(data) {
  return request({
    url: '/api/backup',
    method: 'post',
    data
  })
}

// 恢复备份
export function restoreBackup(id) {
  return request({
    url: `/api/backup/${id}/restore`,
    method: 'post'
  })
}

// 删除备份
export function deleteBackup(id) {
  return request({
    url: `/api/backup/${id}`,
    method: 'delete'
  })
}

// 下载备份
export function downloadBackup(id) {
  return request({
    url: `/api/backup/${id}`,
    method: 'get',
    responseType: 'blob'
  })
} 