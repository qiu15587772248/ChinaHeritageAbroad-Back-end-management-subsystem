import Cookies from 'js-cookie'

const TokenKey = 'Admin-Token'

export function getToken() {
  return Cookies.get(TokenKey)
}

export function setToken(token) {
  return Cookies.set(TokenKey, token)
}

export function removeToken() {
  return Cookies.remove(TokenKey)
}

// 保存用户信息
export function setUserInfo(userInfo) {
  localStorage.setItem('userInfo', JSON.stringify(userInfo))
}

// 获取用户信息
export function getUserInfo() {
  const userInfo = localStorage.getItem('userInfo')
  return userInfo ? JSON.parse(userInfo) : null
}

// 移除用户信息
export function removeUserInfo() {
  localStorage.removeItem('userInfo')
}

// 检查权限
export function hasPermission(permission) {
  const userInfo = getUserInfo()
  if (!userInfo) return false
  
  // 超级管理员拥有所有权限
  if (userInfo.role === 'super_admin') {
    return true
  }
  
  // 权限映射
  const permissionMap = {
    'admin': ['user_manage', 'data_manage', 'backup_manage', 'log_view'],
    'operator': ['data_manage', 'log_view']
  }
  
  return permissionMap[userInfo.role] && permissionMap[userInfo.role].includes(permission)
} 