<template>
  <div class="app-container">
    <div class="filter-container">
      <el-button v-if="hasPermission('backup_manage')" class="filter-item" type="primary" icon="el-icon-plus" @click="handleCreate">
        创建备份
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

      <el-table-column align="center" label="备份名称" width="220">
        <template slot-scope="{row}">
          <span>{{ row.backup_name }}</span>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="备份类型" width="120">
        <template slot-scope="{row}">
          <el-tag :type="row.backup_type === 'manual' ? 'primary' : 'success'">
            {{ row.backup_type === 'manual' ? '手动备份' : '自动备份' }}
          </el-tag>
        </template>
      </el-table-column>
      
      <el-table-column align="center" label="文件大小" width="100">
        <template slot-scope="{row}">
          <span>{{ formatFileSize(row.backup_size) }}</span>
        </template>
      </el-table-column>
      
      <!-- 
      <el-table-column align="center" label="数据表" width="300">
        <template slot-scope="{row}">
          <el-tooltip 
            v-if="row.tables && row.tables.length > 0" 
            class="item" 
            effect="dark" 
            :content="row.tables.join(', ')" 
            placement="top"
          >
            <span>{{ row.tables.join(', ') | ellipsis }}</span>
          </el-tooltip>
          <span v-else>全部表</span>
        </template>
      </el-table-column>
      -->

      <el-table-column align="center" label="创建时间" width="180">
        <template slot-scope="{row}">
          <span>{{ row.backup_time }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="状态" width="100">
        <template slot-scope="{row}">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'">
            {{ row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column align="center" label="描述/错误信息" min-width="200">
        <template slot-scope="{row}">
          <span style="white-space: pre-wrap;">{{ row.description }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作" width="300" fixed="right">
        <template slot-scope="{row}">
          <el-button v-if="hasPermission('backup_manage') && row.status === 'success'" type="primary" size="mini" @click="handleRestore(row)">
            恢复
          </el-button>
          <el-button v-if="row.status === 'success'" type="success" size="mini" @click="handleDownload(row)">
            下载
          </el-button>
          <el-button v-if="hasPermission('backup_manage')" type="danger" size="mini" @click="handleDelete(row)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <!-- 创建备份对话框 -->
    <el-dialog title="创建备份" :visible.sync="dialogVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="120px" style="width: 400px; margin-left:50px;">
        <el-form-item label="备份名称" prop="name">
          <el-input v-model="temp.name" placeholder="备份名称，如：手动备份-20230601" />
        </el-form-item>
        
        <el-form-item label="备份表" prop="tables">
          <el-select
            v-model="temp.tables"
            multiple
            placeholder="请选择要备份的表（不选则备份全部）"
            style="width: 100%"
          >
            <el-option v-for="item in tableOptions" :key="item" :label="item" :value="item" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="备份描述" prop="description">
          <el-input v-model="temp.description" type="textarea" :rows="3" placeholder="备份描述，如：系统更新前的备份" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" :loading="createLoading" @click="createData">
          创建
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getBackupList, createBackup, restoreBackup, deleteBackup, downloadBackup } from '@/api/backup'
import { hasPermission } from '@/utils/auth'

export default {
  name: 'BackupList',
  filters: {
    ellipsis(value) {
      if (!value) return ''
      if (value.length > 30) {
        return value.slice(0, 30) + '...'
      }
      return value
    }
  },
  data() {
    return {
      list: null,
      listLoading: true,
      dialogVisible: false,
      createLoading: false,
      temp: {
        name: '',
        tables: [],
        description: ''
      },
      tableOptions: [
        'admin_users',
        'users',
        'heritage_items',
        'operation_logs',
        'backup_records'
      ],
      rules: {
        name: [{ required: true, message: '备份名称为必填项', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    hasPermission,
    getList() {
      this.listLoading = true
      getBackupList().then(response => {
        console.log('API Response (Axios):', response) // 打印原始Axios响应
        // 正确的路径应该是 response.data (后端返回的JSON) -> .data (后端JSON中的data字段) -> .items
        if (response && response.data && response.data.data && response.data.data.items) {
          this.list = response.data.data.items
          console.log('Assigned to this.list:', this.list) 
        } else {
          console.error('Invalid response structure or missing items. Full backend response:', response.data)
          this.list = [] 
        }
        this.listLoading = false
      }).catch(error => {
        console.error('Error fetching backup list:', error) 
        this.listLoading = false
        this.list = [] 
      })
    },
    handleCreate() {
      this.temp = {
        name: `手动备份-${this.formatDate(new Date())}`,
        tables: [],
        description: ''
      }
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          this.createLoading = true
          createBackup(this.temp).then(() => {
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '创建备份成功',
              type: 'success',
              duration: 2000
            })
            this.getList()
            this.createLoading = false
          }).catch(() => {
            this.createLoading = false
          })
        }
      })
    },
    handleRestore(row) {
      this.$confirm('恢复备份将覆盖当前数据，是否继续?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true
        restoreBackup(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '恢复备份成功',
            type: 'success',
            duration: 2000
          })
          this.listLoading = false
        }).catch(() => {
          this.listLoading = false
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消恢复'
        })
      })
    },
    handleDownload(row) {
      window.open(`${process.env.VUE_APP_BASE_API}/api/backup/${row.id}/download`)
    },
    handleDelete(row) {
      this.$confirm('确定要删除该备份吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteBackup(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除备份成功',
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
    },
    formatFileSize(size) {
      if (!size) return '0 B'
      
      let numericSize = parseFloat(size) // 将传入的 size 显式转换为数字
      
      if (isNaN(numericSize) || numericSize === 0) { // 检查转换后是否为有效数字且不为0
        return '0 B'
      }
      
      const units = ['B', 'KB', 'MB', 'GB', 'TB']
      let index = 0
      let formattedSize = numericSize // 使用转换后的数字
      
      while (formattedSize >= 1024 && index < units.length - 1) {
        formattedSize /= 1024
        index++
      }
      
      return `${formattedSize.toFixed(2)} ${units[index]}`
    },
    formatDate(date) {
      const year = date.getFullYear()
      const month = (date.getMonth() + 1).toString().padStart(2, '0')
      const day = date.getDate().toString().padStart(2, '0')
      return `${year}${month}${day}`
    }
  }
}
</script> 