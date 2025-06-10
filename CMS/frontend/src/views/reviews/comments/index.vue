<template>
  <div class="app-container">
    <!-- Filter Section -->
    <div class="filter-container">
      <el-input v-model="listQuery.keyword" placeholder="评论内容/用户名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-select v-model="listQuery.passed" placeholder="审核状态" clearable style="width: 140px" class="filter-item">
        <el-option label="待审核/未通过" value="0" />
        <el-option label="已通过" value="1" />
      </el-select>
      <el-input v-model="listQuery.user" placeholder="用户ID/用户名" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
    </div>

    <!-- Table Section -->
    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
      style="width: 100%;"
    >
      <el-table-column label="评论ID" prop="id" align="center" width="80" />
      <el-table-column label="评论内容" prop="comment" align="left" min-width="200" show-overflow-tooltip />
      <el-table-column label="文物ID" prop="artifact_id" align="center" width="100" />
      <el-table-column label="评论用户" align="center" width="180">
        <template slot-scope="{row}">
          <div>ID: {{ row.user_id }}</div>
          <div>用户: {{ row.mobile_username || 'N/A' }}</div>
        </template>
      </el-table-column>
      <el-table-column label="用户状态" align="center" width="120">
        <template slot-scope="{row}">
          <el-tag :type="row.mobile_user_status === '正常' ? 'success' : 'danger'">
            {{ row.mobile_user_status || '未知' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="评论时间" prop="comment_time" align="center" width="160">
        <template slot-scope="{row}">
          <span>{{ row.comment_time }}</span>
        </template>
      </el-table-column>
      <el-table-column label="审核状态" prop="passed" align="center" width="120">
        <template slot-scope="{row}">
          <el-tag :type="row.passed === 1 ? 'success' : (row.passed === 0 ? 'warning' : 'info')">
            {{ row.passed === 1 ? '已通过' : (row.passed === 0 ? '未通过/待审' : '未知') }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column label="操作" align="center" width="300" fixed="right">
        <template slot-scope="{row}">
          <el-button v-if="row.passed !== 1" type="success" size="mini" @click="handleReviewComment(row, 1)">
            通过
          </el-button>
          <el-button v-if="row.passed !== 0" type="warning" size="mini" @click="handleReviewComment(row, 0)">
            不通过
          </el-button>
          <el-button 
            v-if="row.mobile_user_status === '正常'" 
            type="danger" 
            size="mini" 
            style="margin-left: 10px;"
            @click="handleChangeUserStatus(row.user_id, '禁用', row.mobile_username)">
            禁用用户
          </el-button>
          <el-button 
            v-if="row.mobile_user_status === '禁用'" 
            type="primary" 
            size="mini" 
            style="margin-left: 10px;"
            @click="handleChangeUserStatus(row.user_id, '正常', row.mobile_username)">
            启用用户
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination Section -->
    <pagination v-show="total>0" :total="total" :page.sync="listQuery.page" :limit.sync="listQuery.limit" @pagination="getList" />
  </div>
</template>

<script>
import { getCommentsForReview, updateCommentStatus, updateMobileUserStatusByReview } from '@/api/review'
import Pagination from '@/components/Pagination' // Secondary package based on el-pagination

export default {
  name: 'CommentReview',
  components: { Pagination },
  data() {
    return {
      list: [],
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        keyword: '',
        passed: null, // null for all, '0' for not passed, '1' for passed
        user: '' // User ID or username
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getCommentsForReview(this.listQuery).then(response => {
        console.log('API Response:', response); // 调试：打印原始响应
        if (response && response.data && response.data.data) { // 检查 response.data.data 是否存在
          console.log('Data to be assigned:', response.data.data); // 调试：打印将要赋值的数据
          this.list = response.data.data.comments || []
          this.total = response.data.data.total || 0
          console.log('Assigned list:', this.list); // 调试：打印赋值后的列表
          console.log('Assigned total:', this.total); // 调试：打印赋值后的总数
        } else {
          this.list = []
          this.total = 0
          this.$message.error('获取评论列表失败: 数据格式不正确或无数据返回');
          console.error('Error in response structure or no data:', response); // 调试：打印错误情况下的响应
        }
        this.listLoading = false
      }).catch(err => {
        this.$message.error('获取评论列表加载失败: ' + (err.message || ''));
        this.listLoading = false
        console.error('API call failed:', err); // 调试：打印API调用失败的错误
      })
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleReviewComment(row, passedStatus) {
      const statusText = passedStatus === 1 ? '通过' : '不通过';
      this.$confirm(`确定要将评论 (ID: ${row.id}) 审核为 "${statusText}" 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        updateCommentStatus(row.id, passedStatus).then(() => {
          this.$notify({
            title: '成功',
            message: `评论 ${row.id} 审核状态已更新为 ${statusText}`,
            type: 'success',
            duration: 2000
          })
          // Refresh only the row or the list
          // For simplicity, refresh the list. For better UX, update the row locally.
          this.getList() 
        }).catch(err => {
          this.$message.error('更新评论审核状态失败: ' + (err.response?.data?.message || err.message));
        })
      }).catch(() => {
        // User cancelled
      });
    },
    handleChangeUserStatus(userId, newStatus, username) {
      const currentStatusText = newStatus === '正常' ? '启用' : '禁用';
      this.$confirm(`确定要将用户 "${username || ('ID: ' + userId)}" 的状态更改为 "${newStatus}" 吗?`, '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        updateMobileUserStatusByReview(userId, newStatus).then(() => {
          this.$notify({
            title: '成功',
            message: `用户 ${username || userId} 状态已更新为 ${newStatus}`,
            type: 'success',
            duration: 2000
          })
          this.getList() // Refresh list to show updated user status
        }).catch(err => {
          this.$message.error('更新用户状态失败: ' + (err.response?.data?.message || err.message));
        })
      }).catch(() => {
        // User cancelled
      });
    }
  }
}
</script>

<style scoped>
.filter-container {
  padding-bottom: 10px;
}
.app-container {
  padding: 20px;
}
</style> 