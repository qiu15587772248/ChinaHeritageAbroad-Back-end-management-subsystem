<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.username" placeholder="管理员用户名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      
      <el-select v-model="listQuery.operation_type" placeholder="操作类型" clearable style="width: 150px" class="filter-item">
        <el-option v-for="item in operationTypeOptions" :key="item.key" :label="item.display_name" :value="item.key" />
      </el-select>
      
      <el-date-picker
        v-model="dateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="结束日期"
        value-format="yyyy-MM-dd"
        style="width: 300px;"
        class="filter-item"
      />
      
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      
      <el-button v-waves :loading="downloadLoading" class="filter-item" type="primary" icon="el-icon-download" @click="handleDownload">
        导出
      </el-button>
    </div>
    
    <!-- 日志概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>今日日志数</span>
          </div>
          <div class="overview-count">{{ overview.today || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>本周日志数</span>
          </div>
          <div class="overview-count">{{ overview.week || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>本月日志数</span>
          </div>
          <div class="overview-count">{{ overview.month || 0 }}</div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <div slot="header" class="clearfix">
            <span>总日志数</span>
          </div>
          <div class="overview-count">{{ overview.total || 0 }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
    >
      <el-table-column align="center" label="ID" width="80">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="管理员" width="120">
        <template slot-scope="{row}">
          <span>{{ row.admin_username }}</span>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="操作类型" width="120">
        <template slot-scope="{row}">
          <el-tag :type="getOperationTypeColor(row.operation_type)">
            {{ getOperationTypeName(row.operation_type) }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="操作内容">
        <template slot-scope="{row}">
          <el-tooltip
            class="item"
            effect="dark"
            :content="row.operation_content"
            placement="top"
            :disabled="row.operation_content.length < 50"
          >
            <span>{{ row.operation_content | ellipsis }}</span>
          </el-tooltip>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="IP地址" width="140">
        <template slot-scope="{row}">
          <span>{{ row.ip_address }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作时间" width="180">
        <template slot-scope="{row}">
          <span>{{ row.operation_time }}</span>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="操作" width="100" fixed="right">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleDetail(row)">
            详情
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <pagination
      v-show="total > 0"
      :total="total"
      :page.sync="listQuery.page"
      :limit.sync="listQuery.limit"
      @pagination="getList"
    />
    
    <!-- 日志详情对话框 -->
    <el-dialog title="日志详情" :visible.sync="dialogVisible" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="ID">{{ currentLog.id }}</el-descriptions-item>
        <el-descriptions-item label="管理员">{{ currentLog.admin_username }}</el-descriptions-item>
        <el-descriptions-item label="操作类型">
          <el-tag :type="getOperationTypeColor(currentLog.operation_type)">
            {{ getOperationTypeName(currentLog.operation_type) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="操作内容">{{ currentLog.operation_content }}</el-descriptions-item>
        <el-descriptions-item label="IP地址">{{ currentLog.ip_address }}</el-descriptions-item>
        <el-descriptions-item label="操作时间">{{ currentLog.operation_time }}</el-descriptions-item>
      </el-descriptions>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </div>
</template>

<script>
import { getLogList, getLogOverview, exportLogs } from '@/api/log'
import Pagination from '@/components/Pagination'

export default {
  name: 'LogList',
  components: { Pagination },
  filters: {
    ellipsis(value) {
      if (!value) return ''
      if (value.length > 50) {
        return value.slice(0, 50) + '...'
      }
      return value
    }
  },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      downloadLoading: false,
      dialogVisible: false,
      currentLog: {},
      overview: {},
      dateRange: [],
      listQuery: {
        page: 1,
        limit: 10,
        username: '',
        operation_type: '',
        start_date: '',
        end_date: ''
      },
      operationTypeOptions: [
        { key: 'login', display_name: '登录' },
        { key: 'user_manage', display_name: '用户管理' },
        { key: 'create_heritage', display_name: '创建文物' },
        { key: 'update_heritage', display_name: '更新文物' },
        { key: 'delete_heritage', display_name: '删除文物' },
        { key: 'backup', display_name: '备份管理' }
      ]
    }
  },
  watch: {
    dateRange(val) {
      if (val) {
        this.listQuery.start_date = val[0]
        this.listQuery.end_date = val[1]
      } else {
        this.listQuery.start_date = ''
        this.listQuery.end_date = ''
      }
    }
  },
  created() {
    this.getList()
    this.getOverview()
  },
  methods: {
    getList() {
      this.listLoading = true
      getLogList(this.listQuery).then(response => {
        this.list = response.data.logs
        this.total = response.data.total
        this.listLoading = false
      }).catch(() => {
        this.listLoading = false
      })
    },
    getOverview() {
      getLogOverview().then(response => {
        if (response && response.data) {
          this.overview = {
            today: response.data.today_logs_count,
            week: response.data.week_logs_count,
            month: response.data.month_logs_count,
            total: response.data.total_logs_count
          };
        } else {
          this.overview = { today: 0, week: 0, month: 0, total: 0 };
        }
      }).catch(() => {
        this.overview = { today: 0, week: 0, month: 0, total: 0 };
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleDetail(row) {
      this.currentLog = Object.assign({}, row)
      this.dialogVisible = true
    },
    getOperationTypeName(type) {
      const option = this.operationTypeOptions.find(item => item.key === type);
      return option ? option.display_name : type;
    },
    getOperationTypeColor(type) {
      const colorMap = {
        'login': 'info',
        'user_manage': 'primary',
        'create_heritage': 'success',
        'update_heritage': 'success',
        'delete_heritage': 'danger',
        'backup': 'warning'
      }
      return colorMap[type] || ''
    },
    handleDownload() {
      this.downloadLoading = true
      const params = Object.assign({}, this.listQuery)
      delete params.page
      delete params.limit
      
      exportLogs(params).then(response => {
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        const fileName = `操作日志_${new Date().getTime()}.csv`
        link.setAttribute('download', fileName)
        document.body.appendChild(link)
        link.click()
        this.downloadLoading = false
      }).catch(() => {
        this.downloadLoading = false
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.overview-cards {
  margin-bottom: 20px;
  
  .overview-count {
    font-size: 24px;
    font-weight: bold;
    color: #409EFF;
    text-align: center;
  }
}
</style> 