import request from '@/utils/request'

// 获取评论列表 (支持分页和筛选)
export function getCommentsForReview(params) {
  return request({
    url: '/api/reviews/comments',
    method: 'get',
    params
  })
}

// 更新评论审核状态
export function updateCommentStatus(commentId, passedStatus) {
  return request({
    url: `/api/reviews/comments/${commentId}/status`,
    method: 'put',
    data: { passed: passedStatus } // passedStatus should be 0 or 1
  })
}

// 更新移动用户状态
export function updateMobileUserStatusByReview(userId, status) {
  return request({
    url: `/api/reviews/users/${userId}/status`,
    method: 'put',
    data: { status } // status should be '正常' or '禁用'
  })
} 