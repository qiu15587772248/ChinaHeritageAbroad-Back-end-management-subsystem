<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
        添加管理员
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

      <el-table-column align="center" label="角色" width="150">
        <template slot-scope="{row}">
          <el-tag :type="row.role === 'super_admin' ? 'danger' : row.role === 'admin' ? 'primary' : 'success'">
            {{ getRoleName(row.role) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="邮箱">
        <template slot-scope="{row}">
          <span>{{ row.email }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="创建时间" width="180">
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
          <el-button 
            v-if="row.id !== currentUserId" 
            type="danger" 
            size="mini" 
            @click="handleDelete(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑对话框 -->
    <el-dialog :title="dialogType === 'create' ? '创建管理员' : '编辑管理员'" :visible.sync="dialogVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="70px" style="width: 400px; margin-left:50px;">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="temp.username" :disabled="dialogType === 'update'" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <input 
            type="password" 
            :value="temp.password" 
            @input="handleNativePasswordInput"
            placeholder="请输入密码"
            style="border: 1px solid #DCDFE6; border-radius: 4px; padding: 0 15px; height: 40px; line-height: 40px; width: 100%; font-size: 14px; box-sizing: border-box;"
          >
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="temp.role" class="filter-item" placeholder="请选择角色">
            <el-option v-for="item in roleOptions" :key="item.key" :label="item.display_name" :value="item.key" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="temp.email" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogType === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getAdminUsers, createAdminUser, updateAdminUser, deleteAdminUser } from '@/api/user'
import { getUserInfo } from '@/utils/auth'

export default {
  name: 'AdminUser',
  data() {
    return {
      list: null,
      listLoading: true,
      dialogVisible: false,
      dialogType: 'create',
      currentUserId: 0,
      roleOptions: [
        { key: 'super_admin', display_name: '超级管理员' },
        { key: 'admin', display_name: '管理员' }
      ],
      temp: {
        id: undefined,
        username: '',
        password: '',
        role: 'admin',
        email: ''
      },
      rules: {
        username: [{ required: true, message: '用户名为必填项', trigger: 'blur' }],
        // password: [{ required: true, message: '密码为必填项', trigger: 'blur' }], // 暂时注释掉
        role: [{ required: true, message: '角色为必填项', trigger: 'change' }]
      }
    }
  },
  created() {
    this.getList()
    // 获取当前用户ID
    const userInfo = getUserInfo()
    if (userInfo) {
      this.currentUserId = userInfo.id
    }
  },
  methods: {
    getList() {
      this.listLoading = true
      getAdminUsers().then(response => {
        this.list = response.data.users
        this.listLoading = false
      })
    },
    getRoleName(role) {
      const roleMap = {
        'super_admin': '超级管理员',
        'admin': '管理员'
      }
      return roleMap[role] || role
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        username: '',
        password: '',
        role: 'admin',
        email: ''
      }
    },
    handleNativePasswordInput(event) {
      const newValue = event.target.value;
      this.temp.password = newValue;
      // console.log('NATIVE PASSWORD @input HANDLED BY METHOD:', this.temp.password); // 可以按需保留或移除日志
    },
    handleCreate() {
      this.resetTemp()
      this.dialogType = 'create'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createAdminUser(this.temp).then(response => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '创建管理员成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          })
        }
      })
    },
    handleUpdate(row) {
      this.temp = Object.assign({}, row)
      this.temp.password = '' // 清空密码
      this.dialogType = 'update'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          // 如果密码为空，则不更新密码 (暂时注释掉此条件删除，以测试输入问题)
          // if (!tempData.password) {
          //   delete tempData.password
          // }
          updateAdminUser(tempData.id, tempData).then(() => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '更新管理员成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
          }).catch(err => {
            console.error("更新管理员失败:", err); 
            // 可以在这里添加更用户友好的错误提示，例如:
            // this.$message.error('更新失败，详情请查看控制台日志。');
          });
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确定要删除该管理员吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteAdminUser(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除管理员成功',
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