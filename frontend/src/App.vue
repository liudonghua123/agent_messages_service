<template>
  <div id="app">
    <a-layout style="min-height: 100vh">
      <a-layout-header style="background: #001529; padding: 0 24px">
        <div style="color: white; font-size: 18px; font-weight: bold">
          Agent Messages Service
        </div>
      </a-layout-header>
      
      <a-layout-content style="padding: 24px">
        <div style="background: white; padding: 24px; border-radius: 8px">
          <!-- Status Card -->
          <a-card title="系统状态" style="margin-bottom: 24px">
            <a-row :gutter="16">
              <a-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <a-statistic 
                  title="运行状态" 
                  :value="status.status"
                />
              </a-col>
              <a-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <a-statistic 
                  title="运行时间" 
                  :value="status.uptime"
                />
              </a-col>
              <a-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <a-statistic 
                  title="数据库类型" 
                  :value="status.database_type"
                />
              </a-col>
              <a-col :xs="12" :sm="6" :md="6" :lg="6" :xl="6">
                <a-statistic 
                  title="总记录数" 
                  :value="status.total_chats"
                />
              </a-col>
            </a-row>
          </a-card>

          <!-- Search Form -->
          <a-card title="搜索条件" style="margin-bottom: 24px">
            <a-form layout="vertical" :model="searchForm" @finish="handleSearch" class="search-form">
              <!-- 基础搜索条件 -->
              <a-row :gutter="16">
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="用户">
                    <a-input 
                      v-model:value="searchForm.user" 
                      placeholder="请输入用户名" 
                      allowClear
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="会话">
                    <a-input 
                      v-model:value="searchForm.session" 
                      placeholder="请输入会话名称" 
                      allowClear
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="是否正确回答">
                    <a-select 
                      v-model:value="searchForm.fullfill" 
                      placeholder="请选择" 
                      allowClear
                    >
                      <a-select-option :value="true">是</a-select-option>
                      <a-select-option :value="false">否</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="处理时间(ms)">
                    <a-input-group compact>
                      <a-select v-model:value="searchForm.processTimeOperator" style="width: 30%">
                        <a-select-option value="eq">等于</a-select-option>
                        <a-select-option value="gt">大于</a-select-option>
                        <a-select-option value="ge">大于等于</a-select-option>
                        <a-select-option value="lt">小于</a-select-option>
                        <a-select-option value="le">小于等于</a-select-option>
                      </a-select>
                      <a-input-number 
                        v-model:value="searchForm.processTime" 
                        placeholder="请输入处理时间" 
                        style="width: 70%" 
                        :min="0"
                      />
                    </a-input-group>
                  </a-form-item>
                </a-col>
              </a-row>
              
              <!-- 时间范围选择 -->
              <a-row :gutter="16">
                <a-col :xs="24" :sm="24" :md="12" :lg="8" :xl="8">
                  <a-form-item label="时间范围类型">
                    <a-radio-group 
                      v-model:value="searchForm.dateTimeType" 
                      @change="handleDateTimeTypeChange"
                    >
                      <a-radio-button value="range">自定义时间范围</a-radio-button>
                      <a-radio-button value="special">快速时间选择</a-radio-button>
                    </a-radio-group>
                  </a-form-item>
                </a-col>
              </a-row>
              
              <!-- 自定义时间范围 -->
              <a-row :gutter="16" v-if="searchForm.dateTimeType === 'range'">
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="开始时间">
                    <a-date-picker 
                      v-model:value="searchForm.startDateTime" 
                      show-time 
                      format="YYYY-MM-DD HH:mm:ss"
                      placeholder="请选择开始时间"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="结束时间">
                    <a-date-picker 
                      v-model:value="searchForm.endDateTime" 
                      show-time 
                      format="YYYY-MM-DD HH:mm:ss"
                      placeholder="请选择结束时间"
                      style="width: 100%"
                    />
                  </a-form-item>
                </a-col>
              </a-row>
              
              <!-- 快速时间选择 -->
              <a-row :gutter="16" v-if="searchForm.dateTimeType === 'special'">
                <a-col :xs="24" :sm="12" :md="8" :lg="6" :xl="6">
                  <a-form-item label="快速时间选择">
                    <a-select 
                      v-model:value="searchForm.specialDateTime" 
                      placeholder="请选择时间范围" 
                      allowClear
                    >
                      <a-select-option value="last_5_minutes">最近5分钟</a-select-option>
                      <a-select-option value="last_15_minutes">最近15分钟</a-select-option>
                      <a-select-option value="last_30_minutes">最近30分钟</a-select-option>
                      <a-select-option value="last_1_hours">最近1小时</a-select-option>
                      <a-select-option value="last_2_hours">最近2小时</a-select-option>
                      <a-select-option value="last_6_hours">最近6小时</a-select-option>
                      <a-select-option value="last_12_hours">最近12小时</a-select-option>
                      <a-select-option value="last_24_hours">最近24小时</a-select-option>
                    </a-select>
                  </a-form-item>
                </a-col>
              </a-row>
              
              <!-- 操作按钮 -->
              <a-row>
                <a-col :span="24">
                  <a-form-item>
                    <a-space size="middle">
                      <a-button type="primary" html-type="submit" :loading="loading">
                        搜索
                      </a-button>
                      <a-button @click="handleReset">
                        重置
                      </a-button>
                    </a-space>
                  </a-form-item>
                </a-col>
              </a-row>
            </a-form>
          </a-card>

          <!-- Data Table -->
          <a-card title="聊天记录">
            <template #extra>
              <a-button 
                type="primary" 
                danger 
                :disabled="!hasSelected"
                @click="handleBatchDelete"
                :loading="deleteLoading"
              >
                批量删除 ({{ selectedRowKeys.length }})
              </a-button>
            </template>

            <a-table
              :columns="columns"
              :data-source="dataSource"
              :row-selection="rowSelection"
              :pagination="pagination"
              :loading="loading"
              @change="handleTableChange"
              :scroll="{ x: isMobile ? 600 : 1200 }"
              :size="isMobile ? 'small' : 'middle'"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'fullfill'">
                  <a-tag :color="record.fullfill ? 'green' : 'red'">
                    {{ record.fullfill ? '是' : '否' }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'datetime'">
                  {{ formatDateTime(record.datetime) }}
                </template>
                <template v-else-if="column.key === 'process_time'">
                  {{ record.process_time }}ms
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-space>
                    <a-button type="link" size="small" @click="showDetail(record)">
                      详情
                    </a-button>
                    <a-button 
                      type="link" 
                      size="small" 
                      danger 
                      @click="handleDelete(record.id)"
                      :loading="deleteLoading"
                    >
                      删除
                    </a-button>
                  </a-space>
                </template>
              </template>
            </a-table>
          </a-card>
        </div>
      </a-layout-content>
    </a-layout>

    <!-- Detail Modal -->
    <a-modal
      v-model:open="detailVisible"
      title="聊天记录详情"
      :footer="null"
      :width="isMobile ? '95%' : '800px'"
    >
      <a-descriptions :column="isMobile ? 1 : 2" bordered v-if="currentRecord">
        <a-descriptions-item label="ID">{{ currentRecord.id }}</a-descriptions-item>
        <a-descriptions-item label="会话">{{ currentRecord.session }}</a-descriptions-item>
        <a-descriptions-item label="用户">{{ currentRecord.user }}</a-descriptions-item>
        <a-descriptions-item label="是否正确回答">
          <a-tag :color="currentRecord.fullfill ? 'green' : 'red'">
            {{ currentRecord.fullfill ? '是' : '否' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="处理时间">{{ currentRecord.process_time }}ms</a-descriptions-item>
        <a-descriptions-item label="时间">{{ formatDateTime(currentRecord.datetime) }}</a-descriptions-item>
        <a-descriptions-item label="问题" :span="2">
          <div style="max-height: 200px; overflow-y: auto; white-space: pre-wrap">
            {{ currentRecord.question }}
          </div>
        </a-descriptions-item>
        <a-descriptions-item label="回答" :span="2">
          <div style="max-height: 300px; overflow-y: auto; white-space: pre-wrap">
            {{ currentRecord.answer }}
          </div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import api from './api/index.js'

export default {
  name: 'App',
  setup() {
    const loading = ref(false)
    const deleteLoading = ref(false)
    const dataSource = ref([])
    const selectedRowKeys = ref([])
    const detailVisible = ref(false)
    const currentRecord = ref(null)
    const isMobile = ref(false)
    
    const status = reactive({
      status: '',
      uptime: '',
      database_type: '',
      total_chats: 0
    })

    const searchForm = reactive({
      user: '',
      session: '',
      fullfill: null,
      processTime: null,
      processTimeOperator: 'eq',
      dateTimeType: 'range',
      startDateTime: null,
      endDateTime: null,
      specialDateTime: null
    })

    const pagination = reactive({
      current: 1,
      pageSize: 10,
      total: 0,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`
    })

    const columns = computed(() => {
      const baseColumns = [
        {
          title: 'ID',
          dataIndex: 'id',
          key: 'id',
          width: isMobile.value ? 60 : 80,
          sorter: true
        },
        {
          title: '用户',
          dataIndex: 'user',
          key: 'user',
          width: isMobile.value ? 80 : 100
        },
        {
          title: '会话',
          dataIndex: 'session',
          key: 'session',
          width: isMobile.value ? 100 : 150,
          ellipsis: true
        }
      ]

      // 在非移动设备上显示更多列
      if (!isMobile.value) {
        baseColumns.push(
          {
            title: '问题',
            dataIndex: 'question',
            key: 'question',
            width: 200,
            ellipsis: true
          },
          {
            title: '回答',
            dataIndex: 'answer',
            key: 'answer',
            width: 200,
            ellipsis: true
          }
        )
      }

      baseColumns.push(
        {
          title: '时间',
          dataIndex: 'datetime',
          key: 'datetime',
          width: isMobile.value ? 120 : 150,
          sorter: true
        },
        {
          title: '正确',
          dataIndex: 'fullfill',
          key: 'fullfill',
          width: isMobile.value ? 60 : 100
        }
      )

      // 在非移动设备上显示处理时间
      if (!isMobile.value) {
        baseColumns.push({
          title: '处理时间',
          dataIndex: 'process_time',
          key: 'process_time',
          width: 100
        })
      }

      baseColumns.push({
        title: '操作',
        key: 'action',
        width: isMobile.value ? 80 : 120,
        fixed: 'right'
      })

      return baseColumns
    })

    const rowSelection = {
      selectedRowKeys: selectedRowKeys,
      onChange: (keys) => {
        selectedRowKeys.value = keys
      }
    }

    const hasSelected = computed(() => selectedRowKeys.value.length > 0)

    // 响应式检测
    const checkIsMobile = () => {
      isMobile.value = window.innerWidth <= 768
    }

    const handleResize = () => {
      checkIsMobile()
    }

    const formatDateTime = (datetime) => {
      return dayjs(datetime).format('YYYY-MM-DD HH:mm:ss')
    }

    const fetchStatus = async () => {
      try {
        const response = await api.getStatus()
        Object.assign(status, response.data)
      } catch (error) {
        message.error('获取状态失败')
      }
    }

    const buildQueryParams = () => {
      const params = {
        pagenum: pagination.current,
        pagesize: pagination.pageSize
      }
      
      // Basic filters
      if (searchForm.user) {
        params.user = searchForm.user
      }
      if (searchForm.session) {
        params.session = searchForm.session
      }
      if (searchForm.fullfill !== null) {
        params.fullfill = searchForm.fullfill
      }
      
      // Process time filter
      if (searchForm.processTime !== null && searchForm.processTime !== '') {
        const key = `process_time-${searchForm.processTimeOperator}`
        params[key] = searchForm.processTime
      }
      
      // DateTime filters
      if (searchForm.dateTimeType === 'range') {
        if (searchForm.startDateTime && searchForm.endDateTime) {
          const startTime = dayjs(searchForm.startDateTime).format('YYYY-MM-DDTHH:mm:ss')
          const endTime = dayjs(searchForm.endDateTime).format('YYYY-MM-DDTHH:mm:ss')
          params['datetime-between'] = `${startTime},${endTime}`
        } else if (searchForm.startDateTime) {
          const startTime = dayjs(searchForm.startDateTime).format('YYYY-MM-DDTHH:mm:ss')
          params['datetime-ge'] = startTime
        } else if (searchForm.endDateTime) {
          const endTime = dayjs(searchForm.endDateTime).format('YYYY-MM-DDTHH:mm:ss')
          params['datetime-le'] = endTime
        }
      } else if (searchForm.dateTimeType === 'special' && searchForm.specialDateTime) {
        params['datetime-ge'] = searchForm.specialDateTime
      }
      
      return params
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const params = buildQueryParams()
        const response = await api.getChats(params)
        dataSource.value = response.data.map(item => ({
          ...item,
          key: item.id
        }))
        
        // Note: This is a simple implementation. In a real app, you'd want
        // the backend to return total count for proper pagination
        pagination.total = response.data.length
      } catch (error) {
        message.error('获取数据失败')
        console.error('Fetch data error:', error)
      } finally {
        loading.value = false
      }
    }

    const handleSearch = () => {
      pagination.current = 1
      fetchData()
    }

    const handleReset = () => {
      Object.assign(searchForm, {
        user: '',
        session: '',
        fullfill: null,
        processTime: null,
        processTimeOperator: 'eq',
        dateTimeType: 'range',
        startDateTime: null,
        endDateTime: null,
        specialDateTime: null
      })
      pagination.current = 1
      fetchData()
    }

    const handleDateTimeTypeChange = () => {
      // Clear datetime values when switching types
      searchForm.startDateTime = null
      searchForm.endDateTime = null
      searchForm.specialDateTime = null
    }

    const handleTableChange = (pag, filters, sorter) => {
      pagination.current = pag.current
      pagination.pageSize = pag.pageSize
      fetchData()
    }

    const showDetail = (record) => {
      currentRecord.value = record
      detailVisible.value = true
    }

    const handleDelete = async (id) => {
      Modal.confirm({
        title: '确认删除',
        content: '确定要删除这条记录吗？',
        okText: '确定',
        cancelText: '取消',
        onOk: async () => {
          deleteLoading.value = true
          try {
            await api.deleteChat(id)
            message.success('删除成功')
            fetchData()
          } catch (error) {
            message.error('删除失败')
          } finally {
            deleteLoading.value = false
          }
        }
      })
    }

    const handleBatchDelete = () => {
      Modal.confirm({
        title: '确认批量删除',
        content: `确定要删除选中的 ${selectedRowKeys.value.length} 条记录吗？`,
        okText: '确定',
        cancelText: '取消',
        onOk: async () => {
          deleteLoading.value = true
          try {
            await api.batchDeleteChats(selectedRowKeys.value)
            message.success('批量删除成功')
            selectedRowKeys.value = []
            fetchData()
          } catch (error) {
            message.error('批量删除失败')
          } finally {
            deleteLoading.value = false
          }
        }
      })
    }

    onMounted(() => {
      fetchStatus()
      fetchData()
      checkIsMobile()
      window.addEventListener('resize', handleResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', handleResize)
    })

    return {
      loading,
      deleteLoading,
      dataSource,
      selectedRowKeys,
      detailVisible,
      currentRecord,
      status,
      searchForm,
      pagination,
      columns,
      rowSelection,
      hasSelected,
      formatDateTime,
      handleSearch,
      handleReset,
      handleTableChange,
      showDetail,
      handleDelete,
      handleBatchDelete,
      handleDateTimeTypeChange,
      isMobile
    }
  }
}
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.ant-layout-header {
  display: flex;
  align-items: center;
}

/* 搜索表单样式 */
.search-form .ant-form-item {
  margin-bottom: 16px;
}

.search-form .ant-form-item-label > label {
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .ant-layout-content {
    padding: 16px !important;
  }
  
  .ant-layout-content > div {
    padding: 16px !important;
  }
  
  .search-form .ant-form-item {
    margin-bottom: 12px;
  }
  
  .ant-card {
    margin-bottom: 16px !important;
  }
  
  .ant-table-thead > tr > th {
    padding: 8px 4px;
    font-size: 12px;
  }
  
  .ant-table-tbody > tr > td {
    padding: 8px 4px;
    font-size: 12px;
  }
}

@media (max-width: 576px) {
  .ant-layout-content {
    padding: 12px !important;
  }
  
  .ant-layout-content > div {
    padding: 12px !important;
  }
  
  .search-form .ant-form-item {
    margin-bottom: 8px;
  }
}

/* 表格响应式优化 */
@media (max-width: 992px) {
  .ant-table-scroll {
    overflow-x: auto;
  }
}
</style>