<template>
  <div class="app-container">
    <div class="filter-container">
      <el-select v-model="listQuery.type" placeholder="用户类型" clearable style="width: 120px" class="filter-item" @change="handleFilter">
        <el-option v-for="item in userTypeOptions" :key="item.key" :label="item.display_name" :value="item.key" />
      </el-select>
      <el-input v-model="listQuery.username" placeholder="用户名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
    </div>

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

      <el-table-column align="center" label="用户名" width="180">
        <template slot-scope="{row}">
          <span>{{ row.username }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="用户类型" width="150">
        <template slot-scope="{row}">
          <el-tag :type="row.user_type === 'mobile' ? 'success' : 'primary'">
            {{ getUserTypeName(row.user_type) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="邮箱">
        <template slot-scope="{row}">
          <span>{{ row.email }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="状态" width="120">
        <template slot-scope="{row}">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
            {{ getStatusName(row.status) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="注册时间" width="180">
        <template slot-scope="{row}">
          <span>{{ row.created_at }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="最后登录" width="180">
        <template slot-scope="{row}">
          <span>{{ row.last_login || '从未登录' }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作" width="200">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">
            编辑
          </el-button>
          <el-button type="danger" size="mini" @click="handleDelete(row)">
            删除
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

    <!-- 编辑对话框 -->
    <el-dialog title="编辑用户" :visible.sync="dialogVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="temp.username" disabled />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
        
        <el-form-item label="状态" prop="status">
          <el-select v-model="temp.status" class="filter-item" placeholder="选择状态">
            <el-option v-for="item in statusOptions" :key="item.key" :label="item.display_name" :value="item.key" />
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="updateData">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getCloudUsers, updateCloudUser, deleteCloudUser } from '@/api/user'
import Pagination from '@/components/Pagination'

export default {
  name: 'CloudUser',
  components: { Pagination },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      dialogVisible: false,
      listQuery: {
        page: 1,
        limit: 20,
        type: 'all',
        username: ''
      },
      userTypeOptions: [
        { key: 'all', display_name: '全部' },
        { key: 'mobile', display_name: '掌上博物馆' },
        { key: 'knowledge', display_name: '知识服务' }
      ],
      statusOptions: [
        { key: 'active', display_name: '正常' },
        { key: 'disabled', display_name: '禁用' }
      ],
      temp: {
        id: undefined,
        username: '',
        email: '',
        status: 'active',
        user_type: ''
      },
      rules: {
        email: [
          { type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }
        ],
        status: [
          { required: true, message: '状态不能为空', trigger: 'change' }
        ]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getCloudUsers(this.listQuery).then(response => {
        this.list = response.data.users
        this.total = response.data.total
        this.listLoading = false
      })
    },
    getUserTypeName(type) {
      const typeMap = {
        'mobile': '掌上博物馆',
        'knowledge': '知识服务'
      }
      return typeMap[type] || type
    },
    getStatusName(status) {
      const statusMap = {
        'active': '正常',
        'disabled': '禁用'
      }
      return statusMap[status] || status
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateCloudUser(tempData.user_type, tempData.id, tempData).then(() => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '更新用户成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该用户吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteCloudUser(row.user_type, row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除用户成功',
            type: 'success',
            duration: 2000
          })
          this.getList()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        })
      })
    }
  }
}
</script> 