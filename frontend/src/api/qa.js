import request from '../utils/request'

export const chatWithAI = (data) => {
  return request({
    url: '/qa/chat',
    method: 'post',
    data
  })
}
