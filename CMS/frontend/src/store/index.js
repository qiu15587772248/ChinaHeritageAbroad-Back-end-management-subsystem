import Vue from 'vue'
import Vuex from 'vuex'
import getters from './getters'

// 导入模块
import user from './modules/user'
import app from './modules/app'

Vue.use(Vuex)

const store = new Vuex.Store({
  modules: {
    user,
    app
  },
  getters
})

export default store 