"""
Vue 原型页面生成脚本
根据配置生成单个 Vue 页面文件（.vue 和 data.ts）

用法:
    python generate_page.py --input '{JSON配置}'
    python generate_page.py --config page_config.json --prototype my-prototype
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional


def to_camel_case(name: str) -> str:
    """转换为驼峰命名（用于变量名）"""
    name = name.replace('页面', '').replace('管理', '').strip()
    words = re.split(r'[\s_\-]+', name)
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:]) if words else ''


def to_pascal_case(name: str) -> str:
    """转换为 PascalCase（用于组件名）"""
    name = name.replace('页面', '').replace('管理', '').strip()
    words = re.split(r'[\s_\-]+', name)
    return ''.join(word.capitalize() for word in words if word)


def to_kebab_case(name: str) -> str:
    """转换为 kebab-case（用于目录名）"""
    name = name.replace('页面', '').replace('管理', '').strip()
    # 先处理驼峰
    name = re.sub(r'([a-z])([A-Z])', r'\1-\2', name)
    # 处理空格和下划线
    name = re.sub(r'[\s_]+', '-', name)
    return name.lower().strip('-')


def generate_list_page_tsx(config: Dict) -> tuple:
    """生成列表页的 index.vue 和 data.ts"""
    page_name = config.get('page_name', '列表页')
    clarification = config.get('clarification', {})
    data_config = clarification.get('data', {})

    page_name_pascal = to_pascal_case(page_name) + 'Page'
    page_name_camel = to_camel_case(page_name)
    page_dir = to_kebab_case(page_name)

    columns = data_config.get('columns', [
        {'title': '名称', 'dataIndex': 'name', 'width': 150},
        {'title': '状态', 'dataIndex': 'status', 'width': 100},
        {'title': '创建时间', 'dataIndex': 'createTime', 'width': 180},
        {'title': '操作', 'dataIndex': 'action', 'fixed': 'right', 'width': 150},
    ])

    search_fields = data_config.get('search_fields', [
        {'field': 'name', 'label': '名称', 'component': 'Input'},
        {'field': 'status', 'label': '状态', 'component': 'Select'},
    ])

    # 生成 columns 配置
    columns_str = json.dumps(columns, ensure_ascii=False, indent=2)

    # 生成 searchSchema
    search_schema_items = []
    for field in search_fields:
        schema_item = {
            'field': field['field'],
            'component': field['component'],
            'componentProps': {
                'placeholder': field.get('label', field['field'])
            }
        }
        if field['component'] == 'Select':
            schema_item['componentProps']['options'] = [{'label': '全部', 'value': ''}, {'label': '启用', 'value': 1}, {'label': '禁用', 'value': 0}]
        search_schema_items.append(schema_item)

    search_schema_str = json.dumps(search_schema_items, ensure_ascii=False, indent=2)

    # 生成 data.ts
    data_ts = f'''/**
 * {page_name} - 配置文件
 */

/**
 * vue组件导出名称，需和路由名称一致，需要全局唯一
 */
export const PAGE_NAME = '{page_name_pascal}';

/**
 * 表格列配置
 */
export const columns = {columns_str};

/**
 * 状态枚举
 */
export enum statusEnum {{
  DISABLED = 0,
  ENABLED = 1,
}}

/**
 * 状态选项
 */
export const statusOptions = [
  {{ label: '禁用', value: statusEnum.DISABLED, status: 'error' }},
  {{ label: '启用', value: statusEnum.ENABLED, status: 'success' }},
];

/**
 * 搜索表单配置
 */
export const searchSchema: YcForm.Schema[] = {search_schema_str};
'''

    # 生成 index.vue
    index_vue = f'''<script setup lang="ts">
import {{ columns, PAGE_NAME, searchSchema, statusOptions }} from './data';
import EditForm from './components/EditForm.vue';
import {{ mockGetTableData, mockDelete }} from '@/api/mock-api';
import {{ getLabelByValue }} from '@/utils';
import useDrawer from '@/hooks/useDrawer';
import {{ useForm }} from '@/hooks/useForm';

defineOptions({{ name: PAGE_NAME }});

/** 筛选项 */
const inParams = reactive({{
  name: '',
  status: '',
}});

const {{ VBind: searchVBind, resetFields: reset }} = useForm({{
  schemas: searchSchema,
  modelRef: inParams,
  isForm: false,
  onEnter: () => search(),
}});

/** 表格数据 */
const tableData = ref<any[]>([]);
const loading = ref(false);
const pagination = reactive({{
  current: 1,
  pageSize: 10,
  total: 0,
}});

const getTableData = async () => {{
  loading.value = true;
  try {{
    const res = await mockGetTableData({{
      pageNo: pagination.current,
      pageSize: pagination.pageSize,
      ...inParams,
    }});
    if (res.code === 200) {{
      tableData.value = res.data.records;
      pagination.total = res.data.total;
    }}
  }} finally {{
    loading.value = false;
  }}
}};

const search = () => {{
  pagination.current = 1;
  getTableData();
}};

/** 表格操作 */
const handleDelete = (row: any) => {{
  Modal.confirm({{
    title: '确定删除？',
    onOk: async () => {{
      const res = await mockDelete(row.id);
      if (res.code === 200) {{
        message.success('删除成功');
        await getTableData();
      }}
    }},
    cancelText: '取消',
  }});
}};

/** 抽屉 */
const {{ drawer }} = useDrawer(PAGE_NAME);
const editForm = ref();
const handleSave = async () => {{
  try {{
    await editForm.value?.save();
    drawer.close();
    getTableData();
  }} catch (e) {{
    console.error(e);
  }}
}};

/** 初始化 */
const init = async () => {{
  await getTableData();
}};
init();
</script>

<template>
  <div class="prototype-page">
    <a-card title="{page_name}" :bordered="false">
      <!-- 搜索区域 -->
      <div class="search-area">
        <a-form layout="inline" :model="inParams">
          <a-form-item v-for="schema in searchSchema" :key="schema.field" :label="schema.componentProps?.placeholder">
            <a-input
              v-if="schema.component === 'Input'"
              v-model:value="inParams[schema.field as string]"
              :placeholder="`请输入${{schema.componentProps?.placeholder}}`"
              allow-clear
            />
            <a-select
              v-else-if="schema.component === 'Select'"
              v-model:value="inParams[schema.field as string]"
              :placeholder="`请选择${{schema.componentProps?.placeholder}}`"
              style="width: 180px"
              allow-clear
            >
              <a-select-option v-for="opt in schema.componentProps?.options" :key="opt.value" :value="opt.value">
                {{{{ opt.label }}}}
              </a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item>
            <a-button type="primary" @click="search">查询</a-button>
            <a-button style="margin-left: 8px" @click="reset">重置</a-button>
            <a-button type="primary" style="margin-left: 8px" @click="drawer.open('add', '新增')">
              新增
            </a-button>
          </a-form-item>
        </a-form>
      </div>

      <!-- 表格区域 -->
      <a-table
        :columns="columns"
        :data-source="tableData"
        :loading="loading"
        :pagination="false"
        row-key="id"
      >
        <template #bodyCell="{{ column, record }}">
          <template v-if="column.dataIndex === 'status'">
            <a-tag :color="record.status === 1 ? 'success' : 'error'">
              {{{{ getLabelByValue(record.status, statusOptions) }}}}
            </a-tag>
          </template>
          <template v-if="column.dataIndex === 'action'">
            <a-button type="link" @click="drawer.open('detail', '详情', record)">详情</a-button>
            <a-button type="link" @click="drawer.open('edit', '编辑', record)">编辑</a-button>
            <a-button type="link" danger @click="handleDelete(record)">删除</a-button>
          </template>
        </template>
      </a-table>

      <!-- 分页 -->
      <a-pagination
        v-model:current="pagination.current"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-size-options="['10', '20', '50']"
        show-size-changer
        show-quick-jumper
        show-total
        style="margin-top: 20px; text-align: right"
      />
    </a-card>

    <!-- 抽屉 -->
    <a-drawer
      v-model:visible="drawer.visible"
      :title="drawer.title"
      width="600px"
      :destroy-on-close="true"
    >
      <edit-form v-if="['add', 'edit'].includes(drawer.mode)" ref="editForm" :mode="drawer.mode" :record="drawer.record" @save="handleSave" />
      <div v-else-if="drawer.mode === 'detail'">
        <a-descriptions bordered :column="2">
          <a-descriptions-item label="ID">{{{{ drawer.record?.id }}}}</a-descriptions-item>
          <a-descriptions-item label="名称">{{{{ drawer.record?.name }}}}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag :color="drawer.record?.status === 1 ? 'success' : 'error'">
              {{{{ getLabelByValue(drawer.record?.status, statusOptions) }}}}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="创建时间">{{{{ drawer.record?.createTime }}}}</a-descriptions-item>
        </a-descriptions>
      </div>
      <template v-if="['add', 'edit'].includes(drawer.mode)" #footer>
        <a-button @click="drawer.close">取消</a-button>
        <a-button type="primary" style="margin-left: 8px" @click="handleSave">保存</a-button>
      </template>
      <template v-else #footer>
        <a-button @click="drawer.close">关闭</a-button>
      </template>
    </a-drawer>
  </div>
</template>

<style scoped lang="less">
.prototype-page {{
  padding: 24px;
}}

.search-area {{
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}}
</style>
'''

    return index_vue, data_ts, page_dir


def generate_edit_form_component(config: Dict) -> str:
    """生成编辑表单组件"""
    clarification = config.get('clarification', {})
    data_config = clarification.get('data', {})
    columns = data_config.get('columns', [])

    # 过滤掉操作列，生成表单字段
    form_fields = [col for col in columns if col.get('dataIndex') != 'action']

    form_items = []
    for field in form_fields:
        data_index = field.get('dataIndex', 'field')
        title = field.get('title', '字段')
        form_items.append(f'''
      <a-form-item label="{title}" name="{data_index}">
        <a-input v-model:value="formData.{data_index}" placeholder="请输入{title}" />
      </a-form-item>''')

    form_items_str = ''.join(form_items)

    # 生成表单字段的初始值
    form_data_fields = []
    for field in form_fields:
        data_index = field.get('dataIndex', 'field')
        form_data_fields.append(f"{data_index}: ''")
    form_data_str = ',\n    '.join(form_data_fields)

    return f'''<script setup lang="ts">
import {{ mockUpdate }} from '@/api/mock-api';

const props = defineProps<{{
  mode: 'add' | 'edit';
  record?: any;
}}>();

const emit = defineEmits(['save']);

const formRef = ref();
const formData = reactive({{
  {form_data_str}
}});

const rules = {{
  {', '.join([f"{f.get('dataIndex', 'field')}: [{{ required: true, message: '请输入{f.get('title', '字段')}', trigger: 'blur' }}]" for f in form_fields if f.get('required')])}
}};

const init = () => {{
  if (props.mode === 'edit' && props.record) {{
    Object.assign(formData, props.record);
  }}
}};

const save = async () => {{
  await formRef.value.validate();
  const res = await mockUpdate({{ ...formData, id: props.record?.id }});
  if (res.code === 200) {{
    message.success(props.mode === 'add' ? '新增成功' : '编辑成功');
    emit('save');
  }}
}};

defineExpose({{ save }});

init();
</script>

<template>
  <a-form
    ref="formRef"
    :model="formData"
    :rules="rules"
    layout="vertical"
  >{form_items_str}
  </a-form>
</template>
'''


def generate_page(config: Dict, prototype_name: Optional[str] = None) -> Dict:
    """
    生成单个页面原型

    Args:
        config: 页面配置
        prototype_name: 原型项目名称

    Returns:
        {
            "status": "success|error",
            "message": "...",
            "files": [...],
            "path": "..."
        }
    """
    try:
        page_name = config.get('page_name')
        page_type = config.get('page_type', 'list')
        prototype = prototype_name or config.get('prototype_name', 'default-prototype')

        if not page_name:
            return {"status": "error", "message": "缺少 page_name 参数"}

        # 确定输出路径
        output_dir = Path('docs/prototype') / prototype / 'src' / 'pages'
        output_dir.mkdir(parents=True, exist_ok=True)

        # 生成页面
        if page_type == 'list':
            index_vue, data_ts, page_dir_name = generate_list_page_tsx(config)
        else:
            # 其他类型暂时使用列表模板
            index_vue, data_ts, page_dir_name = generate_list_page_tsx(config)

        # 创建页面目录
        page_path = output_dir / page_dir_name
        components_path = page_path / 'components'
        components_path.mkdir(parents=True, exist_ok=True)

        # 写入文件
        (page_path / 'index.vue').write_text(index_vue, encoding='utf-8')
        (page_path / 'data.ts').write_text(data_ts, encoding='utf-8')

        # 生成编辑表单组件
        edit_form = generate_edit_form_component(config)
        (components_path / 'EditForm.vue').write_text(edit_form, encoding='utf-8')

        # 更新路由
        update_router(prototype, page_dir_name, to_pascal_case(page_name) + 'Page')

        return {
            "status": "success",
            "message": f"页面 '{page_name}' 生成成功",
            "files": [
                str(page_path / 'index.vue'),
                str(page_path / 'data.ts'),
                str(components_path / 'EditForm.vue'),
            ],
            "path": str(page_path),
            "page_info": {
                "name": page_name,
                "type": page_type,
                "route": f"/{page_dir_name}",
            }
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error": traceback.format_exc()
        }


def update_router(prototype_name: str, page_dir: str, page_component: str):
    """更新路由配置，添加新页面"""
    router_path = Path('docs/prototype') / prototype_name / 'src' / 'router' / 'index.ts'
    if not router_path.exists():
        return

    content = router_path.read_text(encoding='utf-8')

    # 检查是否已存在该路由
    if f"path: '/{page_dir}'" in content:
        return

    # 构建新的路由项
    new_route = f'''  {{
    path: '/{page_dir}',
    name: '{page_component}',
    component: () => import('@/pages/{page_dir}/index.vue'),
    meta: {{ title: '{page_component}' }},
  }},'''

    # 插入到 routes 数组中
    if 'const routes: RouteRecordRaw[] = [];' in content:
        content = content.replace(
            'const routes: RouteRecordRaw[] = [];',
            f'const routes: RouteRecordRaw[] = [\n{new_route}\n];'
        )
    elif 'const routes: RouteRecordRaw[] = [' in content:
        # 在最后一个路由项后添加
        content = content.replace(
            '];',
            f'  {new_route}\n];'
        )

    router_path.write_text(content, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description='生成 Vue 原型页面')
    parser.add_argument('--input', '-i', help='JSON格式的输入配置')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--prototype', '-p', help='原型项目名称')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    # 读取配置
    if args.input:
        config = json.loads(args.input)
    elif args.config:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    else:
        config = json.loads(sys.stdin.read())

    # 生成页面
    result = generate_page(config, args.prototype)

    # 输出结果
    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
