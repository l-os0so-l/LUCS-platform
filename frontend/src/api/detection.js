import request from '../utils/request'

// 单图分类接口
export const detectSingleImage = (data) => {
  return request({
    url: '/detection/single',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

// 获取分类历史列表（分页+搜索）
export const getDetectionHistory = (params) => {
  return request({
    url: '/detection/history',
    method: 'get',
    params
  })
}

// 获取单条分类详情
export const getDetectionDetail = (id) => {
  return request({
    url: `/detection/history/${id}`,
    method: 'get'
  })
}

// 删除分类历史记录
export const deleteDetectionHistory = (id) => {
  return request({
    url: `/detection/history/${id}`,
    method: 'delete'
  })
}

// 视频实时帧分类接口
export const detectVideoFrame = (data) => {
  return request({
    url: '/detection/video-frame',
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 15000
  })
}

// 获取土地类型列表
export const getTargetList = () => {
  return request({
    url: '/targets/list',
    method: 'get'
  })
}
