<template>
  <div class="app-container">
    <div v-loading="loading" class="heritage-detail">
      <el-form ref="heritageForm" :model="heritageForm" :rules="rules" label-width="100px" class="heritage-form">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>基本信息</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="文物ID" prop="id">
                <el-input v-model="heritageForm.id" disabled />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="创建时间" prop="created_at">
                <el-input v-model="heritageForm.created_at" disabled />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="文物名称" prop="name">
                <el-input v-model="heritageForm.name" placeholder="请输入文物名称" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="文物类别" prop="category">
                <el-select v-model="heritageForm.category" placeholder="请选择文物类别" style="width: 100%">
                  <el-option v-for="item in categoryOptions" :key="item" :label="item" :value="item" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="年代" prop="year">
                <el-input v-model="heritageForm.year" placeholder="请输入年代" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="出土/收藏地" prop="location">
                <el-input v-model="heritageForm.location" placeholder="请输入出土或收藏地" />
              </el-form-item>
            </el-col>
          </el-row>
          
          <el-form-item label="描述" prop="description">
            <el-input v-model="heritageForm.description" type="textarea" :rows="4" placeholder="请输入文物描述" />
          </el-form-item>
        </el-card>
        
        <el-card class="box-card" style="margin-top: 20px;">
          <div slot="header" class="clearfix">
            <span>图片</span>
          </div>
          <el-upload
            :action="uploadUrl"
            :headers="headers"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
            list-type="picture-card"
            :limit="1"
            :file-list="fileList"
          >
            <i class="el-icon-plus" />
            <div slot="tip" class="el-upload__tip">只能上传jpg/png文件，且不超过5MB</div>
          </el-upload>
        </el-card>
        
        <div class="form-footer">
          <el-button @click="$router.back()">返回</el-button>
          <el-button type="primary" @click="submitForm" :loading="submitLoading">保存</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script>
import { getMetClearItem, updateMetClearItem } from '@/api/heritage'
import { getToken } from '@/utils/auth'

export default {
  name: 'HeritageEdit',
  data() {
    return {
      loading: true,
      submitLoading: false,
      heritageForm: {
        id: '',
        name: '',
        category: '',
        year: '',
        location: '',
        description: '',
        image_url: '',
        created_at: '',
        updated_at: ''
      },
      fileList: [],
      categoryOptions: ['陶瓷', '玉器', '青铜器', '书画', '金银器', '雕塑', '织绣', '其他'],
      rules: {
        name: [
          { required: true, message: '请输入文物名称', trigger: 'blur' },
          { min: 1, max: 100, message: '长度在 1 到 100 个字符', trigger: 'blur' }
        ],
        category: [
          { required: true, message: '请选择文物类别', trigger: 'change' }
        ]
      },
      uploadUrl: process.env.VUE_APP_BASE_API + '/api/upload/image',
      headers: {
        Authorization: 'Bearer ' + getToken()
      }
    }
  },
  created() {
    const id = this.$route.params.id
    this.fetchData(id)
  },
  methods: {
    fetchData(id) {
      this.loading = true
      getMetClearItem(id).then(response => {
        this.heritageForm = response.data
        
        // 设置文件列表
        if (this.heritageForm.image_url) {
          this.fileList = [{
            name: '文物图片',
            url: this.heritageForm.image_url
          }]
        }
        
        this.loading = false
      }).catch(() => {
        this.loading = false
      })
    },
    submitForm() {
      this.$refs.heritageForm.validate(valid => {
        if (valid) {
          this.submitLoading = true
          updateMetClearItem(this.heritageForm.id, this.heritageForm).then(response => {
            this.$notify({
              title: '成功',
              message: '更新文物成功',
              type: 'success',
              duration: 2000
            })
            this.submitLoading = false
            this.$router.push('/heritage/list')
          }).catch(() => {
            this.submitLoading = false
          })
        } else {
          console.log('error submit!!')
          return false
        }
      })
    },
    beforeUpload(file) {
      const isJPG = file.type === 'image/jpeg'
      const isPNG = file.type === 'image/png'
      const isLt5M = file.size / 1024 / 1024 < 5

      if (!isJPG && !isPNG) {
        this.$message.error('上传图片只能是 JPG 或 PNG 格式!')
      }
      if (!isLt5M) {
        this.$message.error('上传图片大小不能超过 5MB!')
      }
      return (isJPG || isPNG) && isLt5M
    },
    handleUploadSuccess(res, file) {
      this.heritageForm.image_url = res.data.url
      this.$message.success('上传成功')
    },
    handleUploadError() {
      this.$message.error('上传失败')
    }
  }
}
</script>

<style lang="scss" scoped>
.heritage-form {
  width: 800px;
  margin: 0 auto;
}

.form-footer {
  margin-top: 20px;
  text-align: center;
}

.box-card {
  margin-bottom: 20px;
}
</style> 