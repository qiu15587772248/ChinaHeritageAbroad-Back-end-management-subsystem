import Vue from 'vue'
import VueRouter from 'vue-router'
import Layout from '@/layout'

Vue.use(VueRouter)

// 公共路由
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },
  {
    path: '/404',
    component: () => import('@/views/error/404'),
    hidden: true
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index'),
        meta: { title: '首页', icon: 'el-icon-s-home' }
      }
    ]
  },
  
  // 用户管理
  {
    path: '/user',
    component: Layout,
    redirect: '/user/admin',
    name: 'User',
    meta: { title: '用户管理', icon: 'el-icon-user-solid' },
    children: [
      {
        path: 'admin',
        name: 'AdminUser',
        component: () => import('@/views/user/admin/index.vue'),
        meta: { title: '管理员用户', icon: 'el-icon-s-check' }
      },
      {
        path: 'mobile',
        name: 'MobileUser',
        component: () => import('@/views/user/mobile/index.vue'),
        meta: { title: '移动端用户', icon: 'el-icon-mobile-phone' }
      },
      {
        path: 'web',
        name: 'WebUser',
        component: () => import('@/views/user/web/index.vue'),
        meta: { title: '网页端用户', icon: 'el-icon-monitor' }
      }
    ]
  },
  
  // 文物管理
  {
    path: '/heritage',
    component: Layout,
    redirect: '/heritage/list',
    name: 'Heritage',
    meta: { title: '数据管理', icon: 'el-icon-s-data' },
    children: [
      {
        path: 'list',
        name: 'HeritageList',
        component: () => import('@/views/heritage/list/met-clear'),
        meta: { title: '文物列表' }
      },
      {
        path: 'edit/:id',
        name: 'HeritageEdit',
        component: () => import('@/views/heritage/edit'),
        meta: { title: '编辑文物', icon: 'el-icon-edit' },
        hidden: true
      }
    ]
  },
  
  // 信息审核模块
  {
    path: '/reviews',
    component: Layout,
    redirect: '/reviews/comments',
    name: 'Reviews',
    meta: { title: '信息审核', icon: 'el-icon-s-check' },
    children: [
      {
        path: 'comments',
        name: 'CommentReview',
        component: () => import('@/views/reviews/comments/index.vue'),
        meta: { title: '评论审核', icon: 'el-icon-chat-dot-square' }
      }
    ]
  },
  
  // 备份管理
  {
    path: '/backup',
    component: Layout,
    redirect: '/backup/list',
    name: 'Backup',
    meta: { title: '备份管理', icon: 'el-icon-folder' },
    children: [
      {
        path: 'list',
        name: 'BackupList',
        component: () => import('@/views/backup/list'),
        meta: { title: '备份列表', icon: 'el-icon-document-copy' }
      }
    ]
  },
  
  // 日志管理
  {
    path: '/log',
    component: Layout,
    redirect: '/log/list',
    name: 'Log',
    meta: { title: '日志管理', icon: 'el-icon-document' },
    children: [
      {
        path: 'list',
        name: 'LogList',
        component: () => import('@/views/log/list'),
        meta: { title: '操作日志', icon: 'el-icon-tickets' }
      }
    ]
  },
  
  // 404页必须放在最后
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new VueRouter({
  mode: 'history',
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// 重置路由
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher
}

export default router 