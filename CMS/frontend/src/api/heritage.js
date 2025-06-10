import request from '@/utils/request'

// 获取元数据清洗表项目列表 (新的文物列表将使用这个)
export function getMetClearItems(query) {
  return request({
    url: '/api/heritage/met-clear',
    method: 'get',
    params: query
  })
}

// 获取特定元数据清洗表项目 (新的文物详情可能需要这个)
export function getMetClearItem(id) {
  return request({
    url: `/api/heritage/met-clear/${id}`,
    method: 'get'
  })
}

// 创建元数据清洗表项目 (新的添加文物功能可能需要这个)
export function createMetClearItem(data) {
  return request({
    url: '/api/heritage/met-clear',
    method: 'post',
    data
  })
}

// 更新元数据清洗表项目 (新的编辑文物功能可能需要这个)
export function updateMetClearItem(id, data) {
  return request({
    url: `/api/heritage/met-clear/${id}`,
    method: 'put',
    data
  })
}

// 删除元数据清洗表项目 (新的删除文物功能可能需要这个)
export function deleteMetClearItem(id) {
  return request({
    url: `/api/heritage/met-clear/${id}`,
    method: 'delete'
  })
}

// 批量删除元数据清洗表项目
export function batchDeleteMetClearItems(ids) {
  return request({
    url: '/api/heritage/met-clear/batch-delete',
    method: 'delete',
    data: { ids } // 将ids数组作为请求体发送，通常DELETE请求体通过data参数
  })
} 