<template>
  <div style="padding: 16px">
    <a-layout style="min-height: 100vh">
      <a-layout-header style="background:#001529; padding:0 24px">
        <div style="color:white; font-size:18px; font-weight:bold">
          Report
        </div>
      </a-layout-header>

      <a-layout-content style="padding: 16px">
        <div style="background:white; padding:16px; border-radius:8px; max-width:1200px; margin:0 auto">
          <!-- 顶部过滤与信息 -->
          <a-space style="width:100%; margin-bottom: 12px" direction="vertical" size="small">
            <div style="display:flex; gap:12px; align-items:center; flex-wrap:wrap">
              <a-input
                v-model:value="keywordInput"
                placeholder="输入关键词（搜索 question / answer），按回车或失焦触发"
                allowClear
                style="max-width:420px"
                @change="onKeywordChange"
              />
              <a-tag color="blue">
                时间: {{ queryInfoDisplay }}
              </a-tag>
              <a-tag :color="fullfillParam === true ? 'green' : (fullfillParam === false ? 'red' : 'default')">
                fullfill: {{ fullfillParam === null ? '未指定' : (fullfillParam ? 'true' : 'false') }}
              </a-tag>
              <a-button type="primary" :loading="loading" @click="fetchData">刷新</a-button>
            </div>
            <div style="color:#999; font-size:12px">
              支持 URL 参数：datetime-between=YYYY-MM-DDTHH:mm:ss,YYYY-MM-DDTHH:mm:ss 或 datetime-ge=last_1_hours（默认）；fullfill=false（默认）
            </div>
          </a-space>

          <!-- 结果统计 -->
          <div style="margin: 8px 0 16px; display:flex; gap:12px; align-items:center; flex-wrap:wrap">
            <a-statistic title="总记录" :value="records.length" />
            <a-statistic title="过滤后" :value="filteredRecords.length" />
            <a-statistic title="关键词" :value="keyword || '无'" />
          </div>

          <!-- 卡片列表 -->
          <a-row :gutter="[16,16]">
            <a-col
              v-for="item in filteredRecords"
              :key="item.id"
              :xs="24"
              :sm="12"
              :md="12"
              :lg="8"
              :xl="6"
            >
              <a-card
                :title="`#${item.id} - ${item.session || '未知会话'}`"
                :hoverable="true"
                @click="openDetail(item)"
                style="height: 100%; cursor: pointer"
              >
                <template #extra>
                  <a-tag :color="item.fullfill ? 'green' : 'red'">
                    {{ item.fullfill ? '正确' : '不正确' }}
                  </a-tag>
                </template>

                <div style="margin-bottom:8px; color:#666; font-size:12px">
                  <span>{{ formatDateTime(item.datetime) }}</span>
                  <span v-if="item.process_time !== undefined" style="margin-left:8px">
                    · {{ item.process_time }}ms
                  </span>
                </div>

                <div style="margin-bottom:8px; font-weight:600">Question</div>
                <div class="text-multiline" v-html="highlight(item.question)"></div>

                <div style="margin:10px 0 8px; font-weight:600">Answer</div>
                <div class="text-multiline" v-html="highlight(item.answer)"></div>
              </a-card>
            </a-col>
          </a-row>

          <a-empty v-if="!loading && filteredRecords.length === 0" style="margin-top: 24px" />

          <div style="text-align:center; margin-top: 16px">
            <a-button @click="backToTop" v-if="filteredRecords.length > 8">回到顶部</a-button>
          </div>
        </div>
      </a-layout-content>
    </a-layout>

    <!-- 详情弹窗 -->
    <a-modal v-model:open="detailVisible" title="详情" :footer="null" :width="isMobile ? '95%' : 800">
      <a-descriptions :column="isMobile ? 1 : 2" bordered v-if="current">
        <a-descriptions-item label="ID">{{ current.id }}</a-descriptions-item>
        <a-descriptions-item label="会话">{{ current.session }}</a-descriptions-item>
        <a-descriptions-item label="用户">{{ current.user }}</a-descriptions-item>
        <a-descriptions-item label="正确">
          <a-tag :color="current.fullfill ? 'green' : 'red'">
            {{ current.fullfill ? '是' : '否' }}
          </a-tag>
        </a-descriptions-item>
        <a-descriptions-item label="处理时间">{{ current.process_time }}ms</a-descriptions-item>
        <a-descriptions-item label="时间">{{ formatDateTime(current.datetime) }}</a-descriptions-item>
        <a-descriptions-item label="问题" :span="2">
          <div class="detail-box">{{ current.question }}</div>
        </a-descriptions-item>
        <a-descriptions-item label="回答" :span="2">
          <div class="detail-box">{{ current.answer }}</div>
        </a-descriptions-item>
      </a-descriptions>
    </a-modal>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
import { message } from 'ant-design-vue'
import api from './api/index.js'

export default {
  name: 'Report',
  setup() {
    const loading = ref(false)
    const records = ref([])
    const keyword = ref('')
    const keywordInput = ref('')
    const detailVisible = ref(false)
    const current = ref(null)
    const isMobile = ref(false)

    // URL 参数解析（默认 datetime-ge=last_1_hours, fullfill=false）
    const url = new URL(window.location.href)
    const paramBetween = url.searchParams.get('datetime-between')
    const paramGe = url.searchParams.get('datetime-ge')
    const paramFullfillRaw = url.searchParams.get('fullfill')

    const fullfillParam = ref(null)
    if (paramFullfillRaw === null) {
      fullfillParam.value = false
    } else if (paramFullfillRaw === 'true') {
      fullfillParam.value = true
    } else if (paramFullfillRaw === 'false') {
      fullfillParam.value = false
    } else {
      fullfillParam.value = null
    }

    const queryInfoDisplay = computed(() => {
      if (paramBetween) return `between ${paramBetween}`
      const ge = paramGe || 'last_1_hours'
      return `ge ${ge}`
    })

    const buildParams = () => {
      const params = {}
      // 默认分页可取大一点，便于卡片展示
      params.pagenum = 1
      params.pagesize = 200

      if (fullfillParam.value !== null) {
        params.fullfill = fullfillParam.value
      }

      if (paramBetween) {
        params['datetime-between'] = paramBetween
      } else {
        params['datetime-ge'] = paramGe || 'last_1_hours'
      }

      return params
    }

    const fetchData = async () => {
      loading.value = true
      try {
        const response = await api.getChats(buildParams())
        records.value = (response?.data || []).map(x => ({ ...x }))
      } catch (e) {
        console.error(e)
        message.error('获取数据失败')
      } finally {
        loading.value = false
      }
    }

    // 关键词过滤（change 触发）
    const onKeywordChange = (e) => {
      const val = typeof e?.target?.value === 'string' ? e.target.value : keywordInput.value
      keyword.value = (val || '').trim()
    }

    // 高亮函数（先转义，再替换）
    const escapeHtml = (s) => {
      return (s ?? '').toString()
        .replace(/&/g, '&')
        .replace(/</g, '<')
        .replace(/>/g, '>')
    }

    const highlight = (text) => {
      const esc = escapeHtml(text)
      if (!keyword.value) return esc
      try {
        const pattern = keyword.value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
        const re = new RegExp(`(${pattern})`, 'gi')
        return esc.replace(re, '<mark class="hl">$1</mark>')
      } catch {
        return esc
      }
    }

    const filteredRecords = computed(() => {
      if (!keyword.value) return records.value
      const k = keyword.value.toLowerCase()
      return records.value.filter(r => {
        const q = (r.question || '').toLowerCase()
        const a = (r.answer || '').toLowerCase()
        return q.includes(k) || a.includes(k)
      })
    })

    const openDetail = (item) => {
      current.value = item
      detailVisible.value = true
    }

    const formatDateTime = (dt) => {
      return dayjs(dt).format('YYYY-MM-DD HH:mm:ss')
    }

    const backToTop = () => window.scrollTo({ top: 0, behavior: 'smooth' })

    const checkIsMobile = () => { isMobile.value = window.innerWidth <= 768 }
    const onResize = () => checkIsMobile()

    onMounted(() => {
      fetchData()
      checkIsMobile()
      window.addEventListener('resize', onResize)
    })

    onUnmounted(() => {
      window.removeEventListener('resize', onResize)
    })

    return {
      loading,
      records,
      keyword,
      keywordInput,
      filteredRecords,
      highlight,
      onKeywordChange,
      openDetail,
      detailVisible,
      current,
      formatDateTime,
      queryInfoDisplay,
      fullfillParam,
      fetchData,
      backToTop,
      isMobile
    }
  }
}
</script>

<style>
.text-multiline {
  max-height: 160px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 6;
  -webkit-box-orient: vertical;
  white-space: pre-wrap;
  word-break: break-word;
}

.detail-box {
  max-height: 300px;
  overflow-y: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

mark.hl {
  background-color: #ffe58f;
  padding: 0 2px;
}

@media (max-width: 768px) {
  .text-multiline {
    -webkit-line-clamp: 8;
    max-height: 200px;
  }
}
</style>