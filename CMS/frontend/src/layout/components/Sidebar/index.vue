<template>
  <div class="sidebar-wrapper">
    <el-scrollbar wrap-class="scrollbar-wrapper">
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :background-color="variables.menuBg"
        :text-color="variables.menuText"
        :active-text-color="variables.menuActiveText"
        :collapse-transition="false"
        mode="vertical"
        @select="handleMenuSelect"
      >
        <sidebar-item
          v-for="route in routes"
          :key="route.path"
          :item="route"
          :base-path="route.path"
        />
      </el-menu>
    </el-scrollbar>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import SidebarItem from './SidebarItem'

export default {
  name: 'Sidebar',
  components: { SidebarItem },
  computed: {
    ...mapGetters(['sidebar']),
    routes() {
      return this.$router.options.routes
    },
    activeMenu() {
      const route = this.$route
      const { meta, path } = route
      // 如果设置了activeMenu属性，则使用它
      if (meta.activeMenu) {
        return meta.activeMenu
      }
      return path
    },
    isCollapse() {
      return !this.sidebar.opened
    },
    variables() {
      return {
        menuBg: '#5D4037',
        menuText: '#EAE0D5',
        menuActiveText: '#FFD700'
      }
    }
  },
  methods: {
    handleMenuSelect(index, indexPath) {
      // index 是 el-menu-item 的 index，它应该是我们要导航的路径
      // indexPath 是包含父级路径的完整路径数组，但我们通常用 index
      console.log(`[Sidebar] Menu selected, index: ${index}, indexPath: ${indexPath.join(', ')}`);
      if (this.$route.path !== index) { // 避免重复导航到当前页
        this.$router.push(index).catch(err => {
          if (err.name === 'NavigationDuplicated') {
            // 已在目标页，忽略
          } else if (err.name === 'NavigationCancelled') {
            console.warn(`[Sidebar] Navigation to ${index} was cancelled. This is often due to a redirect or another navigation occurring. Current error being caught and ignored.`);
            // 不做任何处理
          } else {
            console.error('[Sidebar] Unknown navigation error:', err);
          }
        });
      }
    }
  }
}
</script>

<style scoped>
.sidebar-wrapper {
  height: 100%;
  background-color: #304156;
}

.scrollbar-wrapper {
  overflow-x: hidden !important;
}
</style> 