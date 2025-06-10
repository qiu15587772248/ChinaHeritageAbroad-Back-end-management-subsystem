<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 数据概览卡片 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
        <div class="card-panel-col">
          <div class="card-panel">
            <div class="card-panel-description">
              <div class="card-panel-text">海外藏中国文物平台后台管理系统</div>
              <div class="welcome-text">欢迎，{{ username }}</div>
            </div>
          </div>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="data-overview">
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <el-card class="data-card" shadow="hover">
          <div slot="header" class="clearfix">
            <span>文物总数</span>
          </div>
          <div class="card-content">
            <div class="card-icon">
              <i class="el-icon-collection" />
            </div>
            <div class="card-count">{{ stats.heritage_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <el-card class="data-card" shadow="hover">
          <div slot="header" class="clearfix">
            <span>用户总数</span>
          </div>
          <div class="card-content">
            <div class="card-icon">
              <i class="el-icon-user" />
            </div>
            <div class="card-count">{{ stats.total_user_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <el-card class="data-card" shadow="hover">
          <div slot="header" class="clearfix">
            <span>备份数量</span>
          </div>
          <div class="card-content">
            <div class="card-icon">
              <i class="el-icon-folder" />
            </div>
            <div class="card-count">{{ stats.backup_count || 0 }}</div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="12" :lg="6" :xl="6">
        <el-card class="data-card" shadow="hover">
          <div slot="header" class="clearfix">
            <span>今日访问量</span>
          </div>
          <div class="card-content">
            <div class="card-icon">
              <i class="el-icon-view" />
            </div>
            <div class="card-count">{{ stats.today_visits || 0 }}</div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20">
      <!-- 最近操作日志 -->
      <el-col :xs="24" :sm="24" :md="24" :lg="24" :xl="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>最近操作记录</span>
            <el-button style="float: right; padding: 3px 0" type="text" @click="viewMoreLogs">查看更多</el-button>
          </div>
          <el-table :data="recentLogs" style="width: 100%" v-loading="loading" element-loading-text="加载中...">
            <el-table-column prop="admin_username" label="操作人" width="120" />
            <el-table-column prop="operation_type" label="操作类型" width="120">
              <template slot-scope="{row}">
                <el-tag :type="getOperationTypeColor(row.operation_type)">
                  {{ getOperationTypeName(row.operation_type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="operation_content" label="操作内容" show-overflow-tooltip />
            <el-table-column prop="operation_time" label="操作时间" width="180" />
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'
import { getDashboardStats } from '@/api/dashboard'

export default {
  name: 'Dashboard',
  data() {
    return {
      stats: {
        heritage_count: 0,
        total_user_count: 0,
        backup_count: 0,
        today_visits: 0
      },
      recentLogs: [],
      loading: false
    }
  },
  computed: {
    ...mapGetters([
      'name',
      'avatar',
    ]),
    username() {
      return this.name
    }
  },
  created() {
    this.fetchDashboardData()
  },
  methods: {
    fetchDashboardData() {
      this.loading = true
      getDashboardStats().then(response => {
        if (response && response.data && response.data.data) {
          this.stats = {
            heritage_count: response.data.data.heritage_count,
            total_user_count: response.data.data.total_user_count,
            backup_count: response.data.data.backup_count,
            today_visits: response.data.data.today_visits
          }
          this.recentLogs = response.data.data.recent_logs || []
        } else {
          this.$message.error('获取仪表盘数据失败，数据格式不正确或数据为空。')
        }
        this.loading = false
      }).catch((err) => {
        this.loading = false
        this.$message.error('获取仪表盘数据失败。')
      })
    },
    viewMoreLogs() {
      this.$router.push('/log/list')
    },
    getOperationTypeName(type) {
      const typeMap = {
        '用户管理': '用户管理',
        '数据管理': '数据管理',
        '备份管理': '备份管理',
        '登录': '登录',
        '登出': '登出',
        'admin_create': '管理员创建',
        'admin_update': '管理员更新',
        'admin_delete': '管理员删除',
        'mobile_user_create': '移动用户创建',
        'mobile_user_update': '移动用户更新',
        'mobile_user_delete': '移动用户删除',
        'web_user_create': '网页用户创建',
        'web_user_update': '网页用户更新',
        'web_user_delete': '网页用户删除',
        'heritage_add': '文物添加',
        'heritage_update': '文物更新',
        'heritage_delete': '文物删除'
      }
      return typeMap[type] || type
    },
    getOperationTypeColor(type) {
      const colorMap = {
        '用户管理': 'primary',
        '数据管理': 'success',
        '备份管理': 'warning',
        '登录': 'info',
        '登出': 'info',
        'admin_create': 'primary',
        'admin_update': 'primary',
        'admin_delete': 'danger',
        'mobile_user_create': 'primary',
        'mobile_user_update': 'primary',
        'mobile_user_delete': 'danger',
        'web_user_create': 'primary',
        'web_user_update': 'primary',
        'web_user_delete': 'danger',
        'heritage_add': 'success',
        'heritage_update': 'success',
        'heritage_delete': 'danger'
      }
      return colorMap[type] || 'default'
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px;
  
  .card-panel-col {
    margin-bottom: 20px;
  }
  
  .card-panel {
    height: 108px;
    background: linear-gradient(135deg, #b8860b 0%, #cd853f 100%);
    color: #fff;
    border-radius: 8px;
    position: relative;
    overflow: hidden;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    
    .card-panel-description {
      font-weight: bold;
      
      .card-panel-text {
        font-size: 22px;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
      }
      
      .welcome-text {
        font-size: 16px;
        opacity: 0.9;
      }
    }
  }
  
  .data-overview {
    margin-bottom: 20px;
    
    .data-card {
      border: none;
      background-color: #fff;
      border-radius: 8px;
      transition: all 0.3s cubic-bezier(.25,.8,.25,1);
      box-shadow: 0 2px 12px 0 rgba(0,0,0,0.06);

      &:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.1);
      }

      ::v-deep .el-card__header {
        border-bottom: 1px solid #EBEEF5;
        padding: 15px 20px;
      }
      
      .clearfix span {
        font-weight: 600;
        color: #303133;
        font-size: 15px;
      }
      
      .card-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 20px;
        
        .card-icon {
          font-size: 38px;
          color: #AF8F6D;
          margin-right: 15px;
        }
        
        .card-count {
          font-size: 28px;
          font-weight: bold;
          color: #303133;
        }
      }
    }
  }
}

.box-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0,0,0,0.06);
  ::v-deep .el-card__header {
      border-bottom: 1px solid #EBEEF5;
      padding: 15px 20px;
      .clearfix span {
          font-weight: 600;
          color: #303133;
          font-size: 16px;
      }
  }
}
</style> 