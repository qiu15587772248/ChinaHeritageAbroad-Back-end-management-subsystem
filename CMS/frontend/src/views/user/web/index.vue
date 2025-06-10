<!-- Web User Management Component -->
<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.username" placeholder="用户名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.status" placeholder="状态" clearable style="width: 120px" class="filter-item">
        <el-option label="正常" value="正常" />
        <el-option label="禁用" value="禁用" />
      </el-select>
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        添加网页用户
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
      <el-table-column align="center" label="ID" prop="id" width="80" />
      <el-table-column align="center" label="用户名" prop="username" width="180" />
      <el-table-column align="center" label="邮箱" prop="email" />
      <el-table-column align="center" label="状态" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.status === '正常' ? 'success' : 'danger'">{{ row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column align="center" label="注册时间" prop="registration_time" width="180" />
      <el-table-column align="center" label="最后登录" prop="last_login" width="180">
        <template slot-scope="{row}">
          <span>{{ row.last_login || '-' }}</span>
        </template>
      </el-table-column>
      <el-table-column align="center" label="操作" width="200" fixed="right">
        <template slot-scope="{row}">
          <el-button type="primary" size="mini" @click="handleUpdate(row)">编辑</el-button>
          <el-button type="danger" size="mini" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />

    <el-dialog :title="dialogType==='create'?'创建网页用户':'编辑网页用户'" :visible.sync="dialogVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="80px" style="width: 400px; margin-left:50px;">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="temp.username" :disabled="dialogType==='update' && !canEditUsername" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="temp.password" type="password" :placeholder="dialogType==='create'?'请输入密码':'留空则不修改'" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
        <el-form-item label="状态" prop="status">
          <el-select v-model="temp.status" placeholder="请选择状态">
            <el-option label="正常" value="正常"></el-option>
            <el-option label="禁用" value="禁用"></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="dialogType==='create'?createData():updateData()">确认</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
// Placeholder for API calls - replace with actual API functions
import { getWebUsers, createWebUser, updateWebUser, deleteWebUser } from '@/api/user' 
import Pagination from '@/components/Pagination' // Assuming a Pagination component exists

export default {
  name: 'WebUserManagement',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        username: '',
        status: ''
      },
      temp: {
        id: undefined,
        username: '',
        password: '',
        email: '',
        status: '正常'
      },
      dialogVisible: false,
      dialogType: 'create',
      canEditUsername: true, 
      rules: {
        username: [{ required: true, message: '用户名为必填项', trigger: 'blur' }],
        password: [
          { required: false, message: '请输入密码', trigger: 'blur' },
          { validator: this.validatePasswordOnCreate, trigger: 'blur'}
        ],
        email: [{ type: 'email', message: '请输入正确的邮箱地址', trigger: ['blur', 'change'] }],
        status: [{ required: true, message: '状态为必选项', trigger: 'change' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    validatePasswordOnCreate(rule, value, callback) {
      if (this.dialogType === 'create' && !value) {
        callback(new Error('创建用户时密码不能为空'));
      } else {
        callback();
      }
    },
    getList() {
      this.listLoading = true
      getWebUsers(this.listQuery).then(response => {
        console.log('API Response for getWebUsers:', response); // 添加调试日志 (可选)
        // 检查 response.data 是否存在，并且 response.data.data 是否存在
        if (response && response.data && response.data.data) {
          this.list = response.data.data.users || [] 
          this.total = response.data.data.total || 0 
        } else {
          this.list = []
          this.total = 0
          console.error('Unexpected API response structure for getWebUsers:', response);
        }
        this.listLoading = false
      }).catch((err) => { 
        console.error('Error fetching web users:', err);
        this.$message.error('获取网页端用户列表失败'); 
        this.listLoading = false
        this.list = []
        this.total = 0
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        username: '',
        password: '',
        email: '',
        status: '正常'
      }
    },
    handleCreate() {
      this.resetTemp()
      this.dialogType = 'create'
      this.canEditUsername = true
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createWebUser(this.temp).then(() => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '网页用户创建成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(err => {
            this.$message.error(err.response?.data?.message || '创建失败');
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row) 
      this.temp.password = '' 
      this.dialogType = 'update'
      this.canEditUsername = false
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          if (!tempData.password) { 
            delete tempData.password
          }
          updateWebUser(tempData.id, tempData).then(() => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '网页用户信息更新成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(err => {
            this.$message.error(err.response?.data?.message || '更新失败');
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该网页用户吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteWebUser(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '网页用户删除成功',
            type: 'success',
            duration: 2000
          })
          this.getList()
        }).catch(err => {
            this.$message.error(err.response?.data?.message || '删除失败');
        })
      })
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}
</style> 