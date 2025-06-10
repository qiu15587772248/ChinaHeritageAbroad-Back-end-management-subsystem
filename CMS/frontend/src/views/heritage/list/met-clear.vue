<template>
  <div class="app-container">
    <div class="filter-container">
      <el-input v-model="listQuery.title" placeholder="标题" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.artist" placeholder="艺术家" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-input v-model="listQuery.classify" placeholder="分类" style="width: 200px;" class="filter-item" @keyup.enter.native="handleFilter" />
      <el-button v-waves class="filter-item" type="primary" icon="el-icon-search" @click="handleFilter">
        搜索
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="primary" icon="el-icon-plus" @click="handleCreate">
        添加
      </el-button>
      <el-button class="filter-item" style="margin-left: 10px;" type="danger" icon="el-icon-delete" @click="handleBatchDelete" :disabled="selectedRows.length === 0">
        批量删除
      </el-button>
    </div>

    <el-table
      v-loading="listLoading"
      :data="list"
      element-loading-text="加载中..."
      border
      fit
      highlight-current-row
      @selection-change="handleSelectionChange"
    >
      <el-table-column type="selection" width="55" align="center" />
      <el-table-column align="center" label="ID" width="80">
        <template slot-scope="{row}">
          <span>{{ row.id }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="标题" min-width="150">
        <template slot-scope="{row}">
          <span>{{ row.title }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="艺术家" min-width="120">
        <template slot-scope="{row}">
          <span>{{ row.artist }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="年代" width="100">
        <template slot-scope="{row}">
          <span>{{ row.age }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="材质" width="120">
        <template slot-scope="{row}">
          <span>{{ row.material }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="尺寸" width="120">
        <template slot-scope="{row}">
          <span>{{ row.size }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="分类" width="120">
        <template slot-scope="{row}">
          <span>{{ row.classify }}</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="描述" min-width="150">
        <template slot-scope="{row}">
          <el-tooltip 
            :content="row.description" 
            placement="bottom-start"
            :disabled="!row.description || row.description.length <= 50"
            popper-class="description-tooltip"
            :popper-options="{ boundariesElement: 'viewport' }"
          >
            <span>{{ row.description ? (row.description.length > 50 ? row.description.substring(0, 50) + '...' : row.description) : '-' }}</span>
          </el-tooltip>
        </template>
      </el-table-column>

      <el-table-column align="center" label="图片" width="120">
        <template slot-scope="{row}">
          <el-image
            v-if="row.url"
            style="width: 100px; height: 70px; display: block; margin: auto;"
            :src="row.url"
            :preview-src-list="[row.url]"
            fit="contain"
          >
            <div slot="error" class="image-slot" style="display: flex; justify-content: center; align-items: center; width: 100%; height: 100%; background: #f5f7fa; color: #909399;">
              <i class="el-icon-picture-outline" style="font-size: 30px;"></i>
            </div>
          </el-image>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="外部链接" width="120">
        <template slot-scope="{row}">
          <a :href="row.link" target="_blank" v-if="row.link" style="color: #409EFF; text-decoration: none;">查看链接</a>
          <span v-else>-</span>
        </template>
      </el-table-column>

      <el-table-column align="center" label="操作" fixed="right" width="180">
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

    <el-dialog :title="textMap[dialogStatus]" :visible.sync="dialogVisible">
      <el-form ref="dataForm" :rules="rules" :model="temp" label-position="left" label-width="80px" style="width: 80%; margin-left:50px;">
        <el-form-item label="标题" prop="title">
          <el-input v-model="temp.title" />
        </el-form-item>
        <el-form-item label="艺术家">
          <el-input v-model="temp.artist" />
        </el-form-item>
        <el-form-item label="背景">
          <el-input v-model="temp.background" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="年代">
          <el-input v-model="temp.age" />
        </el-form-item>
        <el-form-item label="材质">
          <el-input v-model="temp.material" />
        </el-form-item>
        <el-form-item label="尺寸">
          <el-input v-model="temp.size" />
        </el-form-item>
        <el-form-item label="分类">
          <el-input v-model="temp.classify" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="temp.description" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="图片URL">
          <el-input v-model="temp.url" />
        </el-form-item>
        <el-form-item label="链接">
          <el-input v-model="temp.link" />
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogVisible = false">
          取消
        </el-button>
        <el-button type="primary" @click="dialogStatus === 'create' ? createData() : updateData()">
          确认
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { 
  getMetClearItems, 
  getMetClearItem, 
  createMetClearItem, 
  updateMetClearItem, 
  deleteMetClearItem,
  batchDeleteMetClearItems
} from '@/api/heritage'
import Pagination from '@/components/Pagination'
import waves from '@/directive/waves'

export default {
  name: 'MetClearList',
  components: { Pagination },
  directives: { waves },
  data() {
    return {
      list: null,
      total: 0,
      listLoading: true,
      listQuery: {
        page: 1,
        limit: 10,
        title: '',
        artist: '',
        classify: '',
        sort_by: 'id',
        order: 'asc'
      },
      selectedRows: [],
      temp: {
        id: undefined,
        title: '',
        artist: '',
        background: '',
        age: '',
        material: '',
        size: '',
        classify: '',
        description: '',
        url: '',
        link: ''
      },
      dialogVisible: false,
      dialogStatus: '',
      textMap: {
        update: '编辑',
        create: '创建'
      },
      rules: {
        title: [{ required: true, message: '标题不能为空', trigger: 'blur' }]
      }
    }
  },
  created() {
    this.getList()
  },
  methods: {
    getList() {
      this.listLoading = true
      getMetClearItems(this.listQuery).then(response => {
        console.log('API Response:', response);
        if (response && response.data && response.data.data && typeof response.data.data.total !== 'undefined') {
          this.list = response.data.data.items || [];
          this.total = response.data.data.total;
        } else {
          console.error('Invalid API response structure or missing total from response.data.data:', response);
          this.list = [];
          this.total = 0;
        }
        this.listLoading = false
      }).catch(error => {
        console.error('API Error fetching met clear items:', error);
        this.listLoading = false;
        this.list = [];
        this.total = 0;
      });
    },
    handleSelectionChange(selection) {
      this.selectedRows = selection;
    },
    handleBatchDelete() {
      if (this.selectedRows.length === 0) {
        this.$message({
          message: '请至少选择一项进行删除',
          type: 'warning'
        });
        return;
      }
      const idsToDelete = this.selectedRows.map(row => row.id);
      this.$confirm(`确定要删除选中的 ${idsToDelete.length} 条文物记录吗？此操作不可恢复。`, '警告', {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        this.listLoading = true;
        batchDeleteMetClearItems(idsToDelete).then(() => {
          this.$notify({
            title: '成功',
            message: `成功删除了 ${idsToDelete.length} 条记录`,
            type: 'success',
            duration: 2000
          });
          this.getList();
          this.selectedRows = [];
          this.listLoading = false;
        }).catch(err => {
          this.$message.error('批量删除失败: ' + (err.message || '请重试'));
          this.listLoading = false;
        });
      }).catch(() => {
        this.$message({ type: 'info', message: '已取消删除操作' });
      });
    },
    resetTemp() {
      this.temp = {
        id: undefined,
        title: '',
        artist: '',
        background: '',
        age: '',
        material: '',
        size: '',
        classify: '',
        description: '',
        url: '',
        link: ''
      }
    },
    handleFilter() {
      this.listQuery.page = 1
      this.getList()
    },
    handleCreate() {
      this.resetTemp()
      this.dialogStatus = 'create'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    createData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          createMetClearItem(this.temp).then(response => {
            this.list.unshift({
              id: response.data.data.id,
              ...this.temp
            })
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '创建成功',
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
      this.dialogStatus = 'update'
      this.dialogVisible = true
      this.$nextTick(() => {
        this.$refs['dataForm'].clearValidate()
      })
    },
    updateData() {
      this.$refs['dataForm'].validate((valid) => {
        if (valid) {
          const tempData = Object.assign({}, this.temp)
          updateMetClearItem(tempData.id, tempData).then(() => {
            for (const v of this.list) {
              if (v.id === this.temp.id) {
                const index = this.list.indexOf(v)
                this.list.splice(index, 1, this.temp)
                break
              }
            }
            this.dialogVisible = false
            this.$notify({
              title: '成功',
              message: '更新成功',
              type: 'success',
              duration: 2000
            })
          })
        }
      })
    },
    handleDelete(row) {
      this.$confirm('确认删除?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        deleteMetClearItem(row.id).then(() => {
          this.$notify({
            title: '成功',
            message: '删除成功',
            type: 'success',
            duration: 2000
          })
          const index = this.list.indexOf(row)
          this.list.splice(index, 1)
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

<style lang="scss" scoped>
.description-tooltip {
  max-width: 400px;
  word-break: break-all;
  line-height: 1.4;
}

.overview-cards {
  // ... existing code ...
}
</style> 