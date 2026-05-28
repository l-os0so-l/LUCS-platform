import request from '../utils/request'

export const getUserProfile = () => {
  return request({
    url: '/users/profile',
    method: 'get'
  })
}

export const updateUserProfile = (data) => {
  return request({
    url: '/users/profile',
    method: 'put',
    data
  })
}

export const getUserStats = () => {
  return request({
    url: '/users/stats',
    method: 'get'
  })
}
