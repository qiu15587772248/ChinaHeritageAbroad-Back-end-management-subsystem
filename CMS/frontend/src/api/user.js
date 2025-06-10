import request from '@/utils/request'

// 用户登录
export function login(data) {
  return request({
    url: '/api/auth/login',
    method: 'post',
    data
  })
}

// 获取用户信息
export function getInfo() {
  return request({
    url: '/api/auth/profile',
    method: 'get'
  })
}

// 修改密码
export function changePassword(data) {
  return request({
    url: '/api/auth/change-password',
    method: 'post',
    data
  })
}

// 获取管理员用户列表
export function getAdminUsers(params) {
  return request({
    url: '/api/users/admin',
    method: 'get',
    params
  })
}

// 创建管理员用户
export function createAdminUser(data) {
  return request({
    url: '/api/users/admin',
    method: 'post',
    data
  })
}

// 更新管理员用户
export function updateAdminUser(id, data) {
  return request({
    url: `/api/users/admin/${id}`,
    method: 'put',
    data
  })
}

// 删除管理员用户
export function deleteAdminUser(id) {
  return request({
    url: `/api/users/admin/${id}`,
    method: 'delete'
  })
}

// 获取移动端用户列表
export function getMobileUsers(params) {
  return request({
    url: '/api/users/mobile',
    method: 'get',
    params
  })
}

// 创建移动端用户
export function createMobileUser(data) {
  return request({
    url: '/api/users/mobile',
    method: 'post',
    data
  })
}

// 更新移动端用户
export function updateMobileUser(id, data) {
  return request({
    url: `/api/users/mobile/${id}`,
    method: 'put',
    data
  })
}

// 删除移动端用户
export function deleteMobileUser(id) {
  return request({
    url: `/api/users/mobile/${id}`,
    method: 'delete'
  })
}

// 获取Web端用户列表
export function getWebUsers(params) {
  return request({
    url: '/api/users/web',
    method: 'get',
    params
  })
}

// 创建Web端用户
export function createWebUser(data) {
  return request({
    url: '/api/users/web',
    method: 'post',
    data
  })
}

// 更新Web端用户
export function updateWebUser(id, data) {
  return request({
    url: `/api/users/web/${id}`,
    method: 'put',
    data
  })
}

// 删除Web端用户
export function deleteWebUser(id) {
  return request({
    url: `/api/users/web/${id}`,
    method: 'delete'
  })
}

// 获取云端用户列表（兼容旧代码）
export function getCloudUsers(params) {
  console.warn("getCloudUsers is a compatibility function and might be deprecated.")
  if (params && params.type === 'knowledge') {
    return getWebUsers(params);
  } else if (params && params.type === 'mobile') {
    return getMobileUsers(params);
  } else {
    return Promise.all([getMobileUsers(params), getWebUsers(params)])
      .then(([mobileResponse, webResponse]) => {
        const mobileData = (mobileResponse.data && mobileResponse.data.users) ? mobileResponse.data.users : [];
        const webData = (webResponse.data && webResponse.data.users) ? webResponse.data.users : [];

        const mobileUsers = mobileData.map(user => ({...user, user_type: 'mobile'}));
        const webUsers = webData.map(user => ({
          id: user.id,
          username: user.username,
          email: user.email,
          status: user.status,
          registration_time: user.registration_time,
          last_login: user.last_login,
          user_type: 'knowledge'
        }));
        
        return {
          data: {
            users: [...mobileUsers, ...webUsers],
            total: (mobileResponse.data.total || 0) + (webResponse.data.total || 0)
          }
        };
      }).catch(error => {
        console.error("Error in getCloudUsers compatibility function:", error);
        return Promise.reject(error);
      });
  }
}

// 更新云端用户（兼容旧代码）
export function updateCloudUser(userType, id, data) {
  console.warn("updateCloudUser is a compatibility function and might be deprecated.")
  if (userType === 'knowledge') {
    return updateWebUser(id, data);
  } else if (userType === 'mobile') {
    return updateMobileUser(id, data);
  } else {
    console.error('Unsupported userType for updateCloudUser:', userType)
    return Promise.reject(new Error('Unsupported userType for updateCloudUser'))
  }
}

// 删除云端用户（兼容旧代码）
export function deleteCloudUser(userType, id) {
  console.warn("deleteCloudUser is a compatibility function and might be deprecated.")
  if (userType === 'knowledge') {
    return deleteWebUser(id);
  } else if (userType === 'mobile') {
    return deleteMobileUser(id);
  } else {
    console.error('Unsupported userType for deleteCloudUser:', userType)
    return Promise.reject(new Error('Unsupported userType for deleteCloudUser'))
  }
} 