"""
Vue 原型页面生成脚本
根据页面需求生成单个 HTML 预览文件（使用 Vue 3 + Ant Design Vue CDN）

用法:
    python generate_page.py --config <json_config_path>
    python generate_page.py --input '{"page_name": "...", "page_type": "...", ...}'
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import re


def generate_base_html(title: str, prototype_content: str, description_content: str) -> str:
    """生成基础HTML框架（Vue 3 + Ant Design Vue CDN）"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vue原型 - {title}</title>
  <!-- Vue 3 -->
  <script src="https://cdn.jsdmirror.com/npm/vue@3/dist/vue.global.js"></script>
  <!-- Ant Design Vue CSS -->
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/reset.css" />
  <link rel="stylesheet" href="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.css" />
  <!-- Ant Design Vue JS -->
  <script src="https://cdn.jsdmirror.com/npm/ant-design-vue@4.0.0/dist/antd.min.js"></script>
  <!-- Ant Design Icons -->
  <script src="https://cdn.jsdmirror.com/npm/@ant-design/icons-vue@6.1.0/dist/index.umd.min.js"></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol", "Noto Color Emoji"; }}

    /* 页面级布局 */
    .prototype-container {{ display: flex; height: 100vh; overflow: hidden; }}
    .prototype-left {{ width: 1200px; background: #f0f2f5; overflow: auto; flex-shrink: 0; position: relative; }}
    .prototype-right {{ flex: 1; background: #f5f5f5; padding: 24px; overflow: auto; }}

    /* 后台布局样式 - Ant Design 风格 */
    .layout-container {{ min-height: 100vh; display: flex; flex-direction: column; }}
    .layout-header {{ height: 64px; background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); }}
    .layout-header-left {{ display: flex; align-items: center; gap: 16px; }}
    .layout-logo {{ width: 32px; height: 32px; background: #1677ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold; }}
    .layout-title {{ font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85); }}
    .layout-user {{ display: flex; align-items: center; gap: 16px; }}
    .layout-avatar {{ width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%; }}

    .layout-body {{ display: flex; flex: 1; }}
    .layout-sidebar {{ width: 200px; background: #001529; flex-shrink: 0; }}
    .layout-menu {{ padding: 16px 0; }}
    .layout-menu-item {{ padding: 12px 24px; color: rgba(255,255,255,0.65); cursor: pointer; display: flex; align-items: center; gap: 10px; transition: all 0.3s; }}
    .layout-menu-item:hover {{ background: rgba(255,255,255,0.05); color: #fff; }}
    .layout-menu-item.active {{ background: #1677ff; color: #fff; }}

    .layout-main {{ flex: 1; padding: 24px; overflow: auto; }}
    .breadcrumb {{ margin-bottom: 16px; font-size: 14px; }}
    .breadcrumb-item {{ color: rgba(0,0,0,0.45); }}
    .breadcrumb-item.active {{ color: rgba(0,0,0,0.85); }}

    /* 右侧说明文档样式 */
    .doc-section {{ background: #fff; border-radius: 8px; padding: 20px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.03); }}
    .doc-title {{ font-size: 18px; font-weight: 600; color: rgba(0,0,0,0.85); margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid #f0f0f0; }}
    .doc-item {{ display: flex; gap: 12px; margin-bottom: 12px; font-size: 14px; line-height: 1.6; }}
    .doc-label {{ font-weight: 500; color: rgba(0,0,0,0.65); min-width: 100px; flex-shrink: 0; }}
    .doc-content {{ color: rgba(0,0,0,0.45); }}
  </style>
</head>
<body>
  <div class="prototype-container">
    <!-- 左侧：原型页面（1200px固定宽度） -->
    <div class="prototype-left" id="app">
{prototype_content}
    </div>

    <!-- 右侧：交互说明 -->
    <div class="prototype-right">
{description_content}
    </div>
  </div>

  <script>
    const {{ createApp, ref, reactive }} = Vue;
    const {{ message, Modal }} = antd;

__PROTOTYPE_SCRIPT__
  </script>
</body>
</html>'''


def generate_list_page(config: Dict) -> tuple:
    """生成列表页原型 - 返回 (template_html, script_js)"""
    page_name = config.get('page_name', '列表页')
    data = config.get('data', {})
    interactions = config.get('interactions', {})

    columns = data.get('columns', [])
    buttons = interactions.get('buttons', [])

    # 构建表格列 - Ant Design Vue 格式
    table_columns = []
    for col in columns:
        data_index = col.get('dataIndex', 'field')
        title = col['title']
        if col.get('type') == 'actions':
            col_def = f"        {{ title: '{title}', key: 'action', width: 150, fixed: 'right' }}"
        elif col.get('type') == 'tag':
            col_def = f"        {{ title: '{title}', dataIndex: '{data_index}', key: '{data_index}', width: 100 }}"
        else:
            col_def = f"        {{ title: '{title}', dataIndex: '{data_index}', key: '{data_index}' }}"
        table_columns.append(col_def)

    table_columns_js = ',\n'.join(table_columns)

    # 构建搜索表单字段 - Ant Design Vue 格式
    search_fields = []
    for col in columns[:3]:
        if col.get('type') != 'actions':
            data_index = col.get('dataIndex', 'field')
            search_fields.append(f'''
            <a-form-item label="{col['title']}" name="{data_index}">
              <a-input v-model:value="searchForm.{data_index}" placeholder="请输入{col['title']}" allow-clear />
            </a-form-item>''')

    search_form_html = ''.join(search_fields)

    # 构建操作按钮 - Ant Design Vue 格式
    action_buttons = []
    for btn in buttons:
        btn_type = 'primary' if btn in ['新增', '创建', '添加'] else 'default'
        action_buttons.append(f'<a-button type="{btn_type}" @click="handle{btn}">{btn}</a-button>')

    action_buttons_html = '\n                '.join(action_buttons)

    template_html = f'''<div class="layout-container">
      <!-- 顶栏 -->
      <header class="layout-header">
        <div class="layout-header-left">
          <div class="layout-logo">S</div>
          <span class="layout-title">系统后台</span>
        </div>
        <div class="layout-user">
          <span style="color: rgba(0,0,0,0.65);">管理员</span>
          <div class="layout-avatar"></div>
        </div>
      </header>

      <div class="layout-body">
        <!-- 侧边栏 -->
        <aside class="layout-sidebar">
          <div class="layout-menu">
            <div class="layout-menu-item">
              <home-outlined />
              <span>首页</span>
            </div>
            <div class="layout-menu-item active">
              <unordered-list-outlined />
              <span>{page_name}</span>
            </div>
          </div>
        </aside>

        <!-- 主内容 -->
        <main class="layout-main">
          <!-- 面包屑 -->
          <div class="breadcrumb">
            <span class="breadcrumb-item">首页</span>
            <span style="margin: 0 8px; color: rgba(0,0,0,0.45);">/</span>
            <span class="breadcrumb-item active">{page_name}</span>
          </div>

          <!-- 搜索卡片 -->
          <a-card style="margin-bottom: 20px;">
            <a-form :model="searchForm" layout="inline">
{search_form_html}
              <a-form-item>
                <a-button type="primary" @click="handleSearch">
                  <search-outlined />搜索
                </a-button>
                <a-button @click="handleReset" style="margin-left: 8px;">重置</a-button>
              </a-form-item>
            </a-form>
          </a-card>

          <!-- 操作栏 -->
          <a-card style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <div style="display: flex; gap: 10px;">
                {action_buttons_html}
              </div>
            </div>
          </a-card>

          <!-- 表格 -->
          <a-card>
            <a-table :columns="columns" :data-source="tableData" :pagination="false" bordered>
              <template #bodyCell="{{ column, record }}">
                <template v-if="column.key === 'action'">
                  <a-button type="link" @click="handleEdit(record)">编辑</a-button>
                  <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
                </template>
                <template v-else-if="column.key === 'status'">
                  <a-tag :color="record.status === '启用' ? 'success' : 'error'">{{{{ record.status }}}}</a-tag>
                </template>
              </template>
            </a-table>

            <!-- 分页 -->
            <a-pagination
              v-model:current="currentPage"
              v-model:page-size="pageSize"
              :total="total"
              :page-size-options="['10', '20', '50']"
              show-size-changer
              show-quick-jumper
              show-total
              :total-text="'共 {{total}} 条'"
              style="margin-top: 20px; text-align: right;"
            />
          </a-card>
        </main>
      </div>

      <!-- 抽屉：新增/编辑 -->
      <a-drawer v-model:open="drawerVisible" :title="drawerTitle" width="520px">
        <a-form :model="formData" layout="vertical">
          <a-form-item v-for="col in formColumns" :key="col.dataIndex" :label="col.title" :name="col.dataIndex">
            <a-input v-model:value="formData[col.dataIndex]" :placeholder="'请输入' + col.title" />
          </a-form-item>
        </a-form>
        <template #footer>
          <a-button @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleSave" style="margin-left: 8px;">确定</a-button>
        </template>
      </a-drawer>
    </div>'''

    script_js = f'''
    const {{ HomeOutlined, UnorderedListOutlined, SearchOutlined }} = icons;

    const app = createApp({{
      setup() {{
        // 搜索表单
        const searchForm = reactive({{
{', '.join([f"{col.get('dataIndex', 'field')}: ''" for col in columns[:3] if col.get('type') != 'actions'])}
        }});

        // 表格数据
        const tableData = ref([
          {{ key: 1, name: '示例数据1', status: '启用', createTime: '2024-03-25' }},
          {{ key: 2, name: '示例数据2', status: '禁用', createTime: '2024-03-24' }},
          {{ key: 3, name: '示例数据3', status: '启用', createTime: '2024-03-23' }},
        ]);

        // 分页
        const currentPage = ref(1);
        const pageSize = ref(10);
        const total = ref(100);

        // 抽屉
        const drawerVisible = ref(false);
        const drawerTitle = ref('新增');
        const formData = reactive({{}});

        // 表格列定义
        const columns = [
{table_columns_js}
        ];

        // 表单列（排除操作列）
        const formColumns = {json.dumps([c for c in columns if c.get('type') != 'actions'], ensure_ascii=False)};

        // 方法
        const handleSearch = () => {{
          message.success('搜索成功（模拟）');
          console.log('搜索条件:', searchForm);
        }};

        const handleReset = () => {{
          Object.keys(searchForm).forEach(key => {{
            searchForm[key] = '';
          }});
          message.success('重置成功');
        }};

        const handle新增 = () => {{
          drawerTitle.value = '新增';
          Object.keys(formData).forEach(key => delete formData[key]);
          drawerVisible.value = true;
        }};

        const handleEdit = (row) => {{
          drawerTitle.value = '编辑';
          Object.assign(formData, row);
          drawerVisible.value = true;
        }};

        const handleDelete = (row) => {{
          Modal.confirm({{
            title: '确认删除',
            content: '确定要删除该记录吗？此操作不可撤销。',
            okText: '确定',
            cancelText: '取消',
            onOk: () => {{
              message.success('删除成功（模拟）');
            }}
          }});
        }};

        const handleSave = () => {{
          message.success('保存成功（模拟）');
          drawerVisible.value = false;
        }};

        return {{
          searchForm,
          tableData,
          currentPage,
          pageSize,
          total,
          drawerVisible,
          drawerTitle,
          formData,
          columns,
          formColumns,
          handleSearch,
          handleReset,
          handle新增,
          handleEdit,
          handleDelete,
          handleSave,
          HomeOutlined,
          UnorderedListOutlined,
          SearchOutlined
        }};
      }}
    }});

    app.use(antd);
    app.component('HomeOutlined', HomeOutlined);
    app.component('UnorderedListOutlined', UnorderedListOutlined);
    app.component('SearchOutlined', SearchOutlined);
    app.mount('#app');
'''

    return template_html, script_js


def generate_form_page(config: Dict) -> tuple:
    """生成表单页原型"""
    page_name = config.get('page_name', '表单页')
    data = config.get('data', {})
    fields = data.get('fields', [])

    # 构建表单字段 - Ant Design Vue 格式
    form_items = []
    for field in fields:
        required = field.get('required', False)
        required_attr = ':required="true"' if required else ''

        if field.get('type') == 'select':
            options = ''.join([f'<a-select-option value="{opt}">{opt}</a-select-option>' for opt in field.get('options', ['选项1', '选项2'])])
            input_html = f'<a-select v-model:value="formData.{field["key"]}" placeholder="请选择{field["label"]}" style="width: 100%;"><a-select-option value="">请选择</a-select-option>{options}</a-select>'
        elif field.get('type') == 'textarea':
            input_html = f'<a-textarea v-model:value="formData.{field["key"]}" :rows="3" placeholder="请输入{field["label"]}" />'
        elif field.get('type') == 'date':
            input_html = f'<a-date-picker v-model:value="formData.{field["key"]}" placeholder="选择{field["label"]}" style="width: 100%;" />'
        elif field.get('type') == 'switch':
            input_html = f'<a-switch v-model:checked="formData.{field["key"]}" />'
        elif field.get('type') == 'radio':
            options = ''.join([f'<a-radio value="{opt}">{opt}</a-radio>' for opt in field.get('options', ['选项1', '选项2'])])
            input_html = f'<a-radio-group v-model:value="formData.{field["key"]}">{options}</a-radio-group>'
        else:
            input_html = f'<a-input v-model:value="formData.{field["key"]}" placeholder="请输入{field["label"]}" />'

        form_items.append(f'''
          <a-form-item label="{field['label']}" name="{field['key']}" {required_attr}>
            {input_html}
          </a-form-item>''')

    form_items_html = ''.join(form_items)

    # 构建表单数据
    form_data_fields = ', '.join([f"{f['key']}: ''" for f in fields if f.get('type') != 'switch'])
    form_data_fields_switch = ', '.join([f"{f['key']}: true" for f in fields if f.get('type') == 'switch'])
    if form_data_fields and form_data_fields_switch:
        form_data_fields += ', ' + form_data_fields_switch
    elif form_data_fields_switch:
        form_data_fields = form_data_fields_switch

    template_html = f'''<div class="layout-container">
      <!-- 顶栏 -->
      <header class="layout-header">
        <div class="layout-header-left">
          <div class="layout-logo">S</div>
          <span class="layout-title">系统后台</span>
        </div>
        <div class="layout-user">
          <span style="color: rgba(0,0,0,0.65);">管理员</span>
          <div class="layout-avatar"></div>
        </div>
      </header>

      <div class="layout-body">
        <!-- 侧边栏 -->
        <aside class="layout-sidebar">
          <div class="layout-menu">
            <div class="layout-menu-item">
              <home-outlined />
              <span>首页</span>
            </div>
            <div class="layout-menu-item active">
              <form-outlined />
              <span>{page_name}</span>
            </div>
          </div>
        </aside>

        <!-- 主内容 -->
        <main class="layout-main">
          <!-- 面包屑 -->
          <div class="breadcrumb">
            <span class="breadcrumb-item">首页</span>
            <span style="margin: 0 8px; color: rgba(0,0,0,0.45);">/</span>
            <span class="breadcrumb-item active">{page_name}</span>
          </div>

          <!-- 表单卡片 -->
          <a-card style="max-width: 800px;">
            <template #title>
              <span style="font-size: 16px; font-weight: 500;">{page_name}</span>
            </template>
            <a-form ref="formRef" :model="formData" :rules="formRules" layout="vertical">
{form_items_html}
              <a-form-item>
                <a-button type="primary" @click="handleSubmit">提交</a-button>
                <a-button @click="handleCancel" style="margin-left: 8px;">取消</a-button>
              </a-form-item>
            </a-form>
          </a-card>
        </main>
      </div>
    </div>'''

    # 构建验证规则
    rules_js = ''
    for field in fields:
        if field.get('required'):
            rules_js += f"{field['key']}: [{{ required: true, message: '请输入{field['label']}', trigger: 'change' }}],\n          "

    script_js = f'''
    const {{ HomeOutlined, FormOutlined }} = icons;

    const app = createApp({{
      setup() {{
        const formRef = ref(null);

        const formData = reactive({{
          {form_data_fields}
        }});

        const formRules = reactive({{
          {rules_js}
        }});

        const handleSubmit = () => {{
          formRef.value.validate().then(() => {{
            message.success('提交成功（模拟）');
            console.log('提交数据:', formData);
          }}).catch((error) => {{
            console.log('验证失败:', error);
          }});
        }};

        const handleCancel = () => {{
          message.info('取消操作');
        }};

        return {{
          formRef,
          formData,
          formRules,
          handleSubmit,
          handleCancel,
          HomeOutlined,
          FormOutlined
        }};
      }}
    }});

    app.use(antd);
    app.component('HomeOutlined', HomeOutlined);
    app.component('FormOutlined', FormOutlined);
    app.mount('#app');
'''

    return template_html, script_js


def generate_detail_page(config: Dict) -> tuple:
    """生成详情页原型"""
    page_name = config.get('page_name', '详情页')
    data = config.get('data', {})
    groups = data.get('groups', [])

    # 构建详情分组 - Ant Design Vue 格式
    groups_html = ''
    for group in groups:
        items = []
        for field in group.get('fields', []):
            prop = field.get('key', field.get('name', 'field')) if isinstance(field, dict) else field
            label = field.get('label', prop) if isinstance(field, dict) else field
            items.append(f"{{{{ detailData.{prop} || '—' }}}}")

        items_labels = [field.get('label', field.get('key', field.get('name', 'field'))) if isinstance(field, dict) else field for field in group.get('fields', [])]

        descriptions_items = ''
        for field in group.get('fields', []):
            prop = field.get('key', field.get('name', 'field')) if isinstance(field, dict) else field
            label = field.get('label', prop) if isinstance(field, dict) else field
            if prop == 'status':
                descriptions_items += f'''
              <a-descriptions-item label="{label}">
                <a-tag :color="detailData.status === '启用' ? 'success' : 'error'">{{{{ detailData.status || '—' }}}}</a-tag>
              </a-descriptions-item>'''
            else:
                descriptions_items += f'''
              <a-descriptions-item label="{label}">{{{{ detailData.{prop} || '—' }}}}</a-descriptions-item>'''

        groups_html += f'''
          <!-- {group.get('title', '基本信息')} -->
          <a-card style="margin-bottom: 20px;">
            <template #title>
              <span style="font-size: 16px; font-weight: 500;">{group.get('title', '基本信息')}</span>
            </template>
            <a-descriptions :column="2" bordered>{descriptions_items}
            </a-descriptions>
          </a-card>'''

    template_html = f'''<div class="layout-container">
      <!-- 顶栏 -->
      <header class="layout-header">
        <div class="layout-header-left">
          <div class="layout-logo">S</div>
          <span class="layout-title">系统后台</span>
        </div>
        <div class="layout-user">
          <span style="color: rgba(0,0,0,0.65);">管理员</span>
          <div class="layout-avatar"></div>
        </div>
      </header>

      <div class="layout-body">
        <!-- 侧边栏 -->
        <aside class="layout-sidebar">
          <div class="layout-menu">
            <div class="layout-menu-item">
              <home-outlined />
              <span>首页</span>
            </div>
            <div class="layout-menu-item active">
              <file-text-outlined />
              <span>{page_name}</span>
            </div>
          </div>
        </aside>

        <!-- 主内容 -->
        <main class="layout-main">
          <!-- 面包屑 -->
          <div class="breadcrumb">
            <span class="breadcrumb-item">首页</span>
            <span style="margin: 0 8px; color: rgba(0,0,0,0.45);">/</span>
            <span class="breadcrumb-item active">{page_name}</span>
          </div>

          <!-- 操作栏 -->
          <div style="margin-bottom: 20px;">
            <a-button type="primary" @click="handleEdit">编辑</a-button>
            <a-button @click="handleBack" style="margin-left: 8px;">返回</a-button>
          </div>

          <!-- 详情内容 -->
{groups_html}
        </main>
      </div>

      <!-- 抽屉：编辑 -->
      <a-drawer v-model:open="drawerVisible" title="编辑详情" width="520px">
        <a-form :model="editData" layout="vertical">
          <a-form-item v-for="(value, key) in editData" :key="key" :label="key">
            <a-input v-model:value="editData[key]" />
          </a-form-item>
        </a-form>
        <template #footer>
          <a-button @click="drawerVisible = false">取消</a-button>
          <a-button type="primary" @click="handleSave" style="margin-left: 8px;">保存</a-button>
        </template>
      </a-drawer>
    </div>'''

    # 生成 mock 数据
    detail_data = {}
    for group in groups:
        for field in group.get('fields', []):
            prop = field.get('key', field.get('name', 'field')) if isinstance(field, dict) else field
            detail_data[prop] = f'示例{prop}值'

    script_js = f'''
    const {{ HomeOutlined, FileTextOutlined }} = icons;

    const app = createApp({{
      setup() {{
        const drawerVisible = ref(false);

        const detailData = reactive({json.dumps(detail_data, ensure_ascii=False)});
        const editData = reactive({{ ...detailData }});

        const handleEdit = () => {{
          Object.assign(editData, detailData);
          drawerVisible.value = true;
        }};

        const handleBack = () => {{
          message.info('返回列表页（模拟）');
        }};

        const handleSave = () => {{
          Object.assign(detailData, editData);
          message.success('保存成功（模拟）');
          drawerVisible.value = false;
        }};

        return {{
          drawerVisible,
          detailData,
          editData,
          handleEdit,
          handleBack,
          handleSave,
          HomeOutlined,
          FileTextOutlined
        }};
      }}
    }});

    app.use(antd);
    app.component('HomeOutlined', HomeOutlined);
    app.component('FileTextOutlined', FileTextOutlined);
    app.mount('#app');
'''

    return template_html, script_js


def generate_description(config: Dict) -> str:
    """生成右侧说明文档"""
    page_name = config.get('page_name', '页面')
    clarification = config.get('clarification', {})
    interactions = clarification.get('interactions', {})
    boundary = clarification.get('boundary', {})

    # 构建交互说明
    interactions_html = ''
    if interactions.get('buttons'):
        interactions_html += '<h4 style="font-weight: 500; margin-bottom: 8px;">操作按钮</h4><ul style="list-style: disc; padding-left: 20px; margin-bottom: 16px;">'
        for btn in interactions['buttons']:
            interactions_html += f'<li>{btn}: 点击后触发相应操作</li>'
        interactions_html += '</ul>'

    # 构建边界说明
    boundary_html = '<ul style="list-style: disc; padding-left: 20px;">'
    if boundary.get('empty_state'):
        boundary_html += f'<li><span style="font-weight: 500;">空数据:</span> {boundary["empty_state"]}</li>'
    if boundary.get('loading_state'):
        boundary_html += f'<li><span style="font-weight: 500;">加载中:</span> {boundary["loading_state"]}</li>'
    if boundary.get('error_state'):
        boundary_html += f'<li><span style="font-weight: 500;">错误:</span> {boundary["error_state"]}</li>'
    boundary_html += '</ul>'

    return f'''<div style="max-width: 600px;">
  <div class="doc-section">
    <div class="doc-title">Vue 原型说明</div>
    <p style="color: rgba(0,0,0,0.45); font-size: 14px; margin-bottom: 16px;">版本: v1.0 | 更新日期: {datetime.now().strftime('%Y-%m-%d')}</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">1. 页面概述</div>
    <p style="color: rgba(0,0,0,0.65); line-height: 1.6;">本页面为{page_name}的 Vue 3 + Ant Design Vue 原型，左侧展示可交互的页面原型，右侧为说明文档。</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">2. 技术栈</div>
    <ul style="list-style: disc; padding-left: 20px;">
      <li><span style="font-weight: 500;">Vue 3:</span> 使用 Composition API + setup 语法</li>
      <li><span style="font-weight: 500;">Ant Design Vue:</span> UI 组件库</li>
      <li><span style="font-weight: 500;">CDN 引入:</span> 无需构建工具，直接浏览器打开</li>
    </ul>
  </div>

  <div class="doc-section">
    <div class="doc-title">3. 交互说明</div>
    {interactions_html if interactions_html else '<p style="color: rgba(0,0,0,0.65);">标准交互逻辑</p>'}
    <h4 style="font-weight: 500; margin: 16px 0 8px;">抽屉交互</h4>
    <ul style="list-style: disc; padding-left: 20px;">
      <li><span style="font-weight: 500;">打开:</span> 点击新增/编辑按钮</li>
      <li><span style="font-weight: 500;">关闭:</span> 点击遮罩层、关闭按钮或取消按钮</li>
    </ul>
  </div>

  <div class="doc-section">
    <div class="doc-title">4. 边界场景</div>
    {boundary_html}
  </div>
</div>'''


def to_pascal_case(name: str) -> str:
    """将页面名称转换为 PascalCase"""
    name = name.replace('页面', '').replace('管理', '').strip()
    words = re.split(r'[\s_\-]+', name)
    return ''.join(word.capitalize() for word in words if word)


def generate_file_name(output_dir: Path, page_name: str, scenario: str, old_file_name: Optional[str]) -> str:
    """生成文件名（HTML格式）"""
    date_str = datetime.now().strftime('%Y%m%d')
    pascal_name = to_pascal_case(page_name)

    if scenario == 'refactor' and old_file_name:
        # 从旧文件名提取版本号
        match = re.search(r'V(\d+)\.html$', old_file_name)
        old_version = int(match.group(1)) if match else 1
        new_version = old_version + 1
        file_name = f'VuePrototype{pascal_name}V{new_version}.html'
        while (output_dir / file_name).exists():
            new_version += 1
            file_name = f'VuePrototype{pascal_name}V{new_version}.html'
    else:
        file_name = f'VuePrototype{pascal_name}.html'
        if (output_dir / file_name).exists():
            version = 2
            while (output_dir / f'VuePrototype{pascal_name}V{version}.html').exists():
                version += 1
            file_name = f'VuePrototype{pascal_name}V{version}.html'

    return file_name


def generate_page(config: Dict) -> Dict:
    """生成单个页面原型"""
    try:
        page_name = config.get('page_name')
        page_type = config.get('page_type', 'list')
        output_path_str = config.get('output_path', '.dev/prototype')
        scenario = config.get('scenario', 'new')

        if not page_name:
            return {"status": "error", "message": "缺少 page_name 参数"}

        output_dir = Path(output_path_str)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成文件名（HTML格式）
        file_name = generate_file_name(output_dir, page_name, scenario, config.get('old_file_name'))

        # 根据页面类型生成内容
        page_generators = {
            'list': generate_list_page,
            'form': generate_form_page,
            'detail': generate_detail_page,
        }

        generator = page_generators.get(page_type, generate_list_page)
        prototype_template, prototype_script = generator(config)

        # 生成说明文档
        description_content = generate_description(config)

        # 生成完整HTML
        full_html = generate_base_html(page_name, prototype_template, description_content)
        # 插入脚本
        full_html = full_html.replace('__PROTOTYPE_SCRIPT__', prototype_script)

        # 保存文件
        file_path = output_dir / file_name
        file_path.write_text(full_html, encoding='utf-8')

        # 提取版本号
        version_match = re.search(r'V(\d+)\.html$', file_name)
        version = int(version_match.group(1)) if version_match else 1

        return {
            "file_path": str(file_path),
            "file_name": file_name,
            "status": "success",
            "message": "生成成功" if scenario == 'new' else f"改造成功，已生成新版本",
            "page_info": {
                "name": page_name,
                "type": page_type,
                "scenario": scenario,
                "version": version
            }
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error": {"type": "generation_error", "detail": traceback.format_exc()}
        }


def main():
    parser = argparse.ArgumentParser(description='生成 Vue 原型页面 HTML')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--input', '-i', help='JSON格式的输入参数')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    # 读取配置
    if args.config:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    elif args.input:
        config = json.loads(args.input)
    else:
        # 从stdin读取
        config = json.loads(sys.stdin.read())

    # 生成页面
    result = generate_page(config)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    # 返回退出码
    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
