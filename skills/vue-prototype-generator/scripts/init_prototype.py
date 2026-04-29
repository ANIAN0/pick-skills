"""
原型项目初始化脚本
创建完整的Vue 3 + Rsbuild原型项目结构

用法:
    python init_prototype.py --name user-prototype --output docs/prototype/
    python init_prototype.py --name my-prototype --output ./prototypes --template list
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, Optional


def get_package_json(name: str) -> str:
    """生成package.json内容"""
    return json.dumps({
        "name": name,
        "private": True,
        "version": "1.0.0",
        "type": "module",
        "packageManager": "pnpm@10.30.3",
        "scripts": {
            "dev": "rsbuild dev --port 3005",
            "build": "rsbuild build",
            "preview": "rsbuild preview"
        },
        "dependencies": {
            "vue": "3.3.4",
            "ant-design-vue": "3.2.20",
            "pinia": "3.0.4",
            "vue-router": "5.0.1",
            "@vueuse/core": "14.2.0",
            "dayjs": "^1.11.19",
            "lodash-es": "^4.17.23",
            "@ant-design/icons-vue": "^6.1.0"
        },
        "devDependencies": {
            "@rsbuild/core": "^1.6.15",
            "@rsbuild/plugin-vue": "^1.2.2",
            "@types/lodash-es": "^4.17.12",
            "@types/node": "^25.1.0",
            "typescript": "~5.9.3",
            "less": "^4.5.1"
        },
        "engines": {
            "node": ">=20.10.0",
            "pnpm": ">=10.12.4"
        }
    }, indent=2, ensure_ascii=False)


def get_rsbuild_config() -> str:
    """生成rsbuild.config.ts内容"""
    return '''import { defineConfig } from '@rsbuild/core';
import { pluginVue } from '@rsbuild/plugin-vue';

export default defineConfig({
  plugins: [pluginVue()],
  source: {
    alias: {
      '@': './src',
    },
  },
  server: {
    port: 3005,
  },
  html: {
    template: './index.html',
  },
});
'''


def get_tsconfig() -> str:
    """生成tsconfig.json内容"""
    return json.dumps({
        "compilerOptions": {
            "target": "ES2020",
            "lib": ["ES2020", "DOM", "DOM.Iterable"],
            "module": "ESNext",
            "skipLibCheck": True,
            "moduleResolution": "bundler",
            "allowImportingTsExtensions": True,
            "resolveJsonModule": True,
            "isolatedModules": True,
            "noEmit": True,
            "jsx": "preserve",
            "strict": True,
            "noUnusedLocals": True,
            "noUnusedParameters": True,
            "noFallthroughCasesInSwitch": True,
            "baseUrl": ".",
            "paths": {
                "@/*": ["src/*"]
            }
        },
        "include": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.vue"],
        "references": [{"path": "./tsconfig.node.json"}]
    }, indent=2)


def get_tsconfig_node() -> str:
    """生成tsconfig.node.json内容"""
    return json.dumps({
        "compilerOptions": {
            "composite": True,
            "skipLibCheck": True,
            "module": "ESNext",
            "moduleResolution": "bundler",
            "allowSyntheticDefaultImports": True
        },
        "include": ["rsbuild.config.ts"]
    }, indent=2)


def get_index_html(title: str) -> str:
    """生成index.html内容"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} - Vue原型</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.ts"></script>
</body>
</html>
'''


def get_main_ts() -> str:
    """生成src/main.ts内容"""
    return '''import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);
app.mount('#app');
'''


def get_app_vue() -> str:
    """生成src/App.vue内容"""
    return '''<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<template>
  <router-view />
</template>

<style lang="less">
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
'''


def get_env_d_ts() -> str:
    """生成src/env.d.ts内容"""
    return '''/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue';
  const component: DefineComponent<{}, {}, any>;
  export default component;
}
'''


def get_router_index() -> str:
    """生成src/router/index.ts内容"""
    return '''import { createRouter, createWebHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;

// 动态添加路由的辅助函数
export function addRoute(route: RouteRecordRaw) {
  router.addRoute(route);
}
'''


def get_hooks_useDrawer() -> str:
    """生成src/hooks/useDrawer.ts内容（简化版）"""
    return '''import { ref, reactive } from 'vue';

export interface DrawerState {
  visible: boolean;
  title: string;
  mode: 'add' | 'edit' | 'detail' | '';
  record: any;
  spinning: boolean;
}

const drawers: Record<string, DrawerState> = {};

export default function useDrawer(pageName: string) {
  if (!drawers[pageName]) {
    drawers[pageName] = reactive<DrawerState>({
      visible: false,
      title: '',
      mode: '',
      record: null,
      spinning: false,
    });
  }

  const drawer = drawers[pageName];

  const open = (mode: 'add' | 'edit' | 'detail', title: string, record?: any) => {
    drawer.mode = mode;
    drawer.title = title;
    drawer.record = record || null;
    drawer.visible = true;
  };

  const close = () => {
    drawer.visible = false;
    drawer.record = null;
    drawer.mode = '';
  };

  const showSpinning = () => {
    drawer.spinning = true;
  };

  const hideSpinning = () => {
    drawer.spinning = false;
  };

  return {
    drawer,
    open,
    close,
    showSpinning,
    hideSpinning,
  };
}
'''


def get_hooks_useForm() -> str:
    """生成src/hooks/useForm.ts内容（简化版）"""
    return '''import { computed, ref } from 'vue';

export interface UseFormOptions {
  schemas: any[];
  modelRef: Record<string, any>;
  isForm?: boolean;
  onEnter?: () => void;
  labelCol?: { style: { width: string } };
}

export function useForm(options: UseFormOptions) {
  const { schemas, modelRef, isForm = true, onEnter, labelCol = { style: { width: '80px' } } } = options;
  const formRef = ref();

  const VBind = computed(() => ({
    schemas,
    model: modelRef,
    labelCol,
    isForm,
    onEnter,
  }));

  const resetFields = () => {
    Object.keys(modelRef).forEach((key) => {
      modelRef[key] = '';
    });
  };

  const setFields = (values: Record<string, any>) => {
    Object.assign(modelRef, values);
  };

  const validate = async () => {
    return formRef.value?.validate();
  };

  return {
    formRef,
    VBind,
    resetFields,
    setFields,
    validate,
  };
}
'''


def get_mock_api() -> str:
    """生成src/api/mock-api.ts内容"""
    return '''// Mock API 层
// 所有 API 调用都使用 mock 数据

export interface MockResponse<T = any> {
  code: number;
  data: T;
  message: string;
}

// 模拟延迟
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// 创建 mock 响应
function createMockResponse<T>(data: T, delayMs = 500): Promise<MockResponse<T>> {
  return new Promise(async (resolve) => {
    await delay(delayMs);
    resolve({
      code: 200,
      data,
      message: 'success',
    });
  });
}

// 示例：表格数据 API
export async function mockGetTableData(params: any): Promise<MockResponse<any>> {
  const pageSize = params.pageSize || 10;
  const pageNo = params.pageNo || 1;

  // 生成模拟数据
  const records = Array.from({ length: pageSize }, (_, i) => ({
    id: String((pageNo - 1) * pageSize + i + 1),
    name: `示例数据${(pageNo - 1) * pageSize + i + 1}`,
    status: Math.random() > 0.5 ? 1 : 0,
    createTime: '2024-01-01',
    updateTime: '2024-01-02',
  }));

  return createMockResponse({
    records,
    total: 100,
  });
}

// 示例：详情数据 API
export async function mockGetDetail(id: string): Promise<MockResponse<any>> {
  return createMockResponse({
    id,
    name: `示例详情${id}`,
    status: 1,
    description: '这是示例描述',
    createTime: '2024-01-01',
    updateTime: '2024-01-02',
  });
}

// 示例：保存/更新 API
export async function mockUpdate(data: any): Promise<MockResponse<null>> {
  return createMockResponse(null, 300);
}

// 示例：删除 API
export async function mockDelete(id: string): Promise<MockResponse<null>> {
  return createMockResponse(null, 300);
}
'''


def get_utils_index() -> str:
    """生成src/utils/index.ts内容"""
    return '''import dayjs from 'dayjs';

/**
 * 根据值获取标签
 */
export function getLabelByValue(
  value: any,
  options: { label: string; value: any }[],
  field: string = 'label'
): string {
  const item = options.find((opt) => opt.value === value);
  return item ? item[field as keyof typeof item] : value;
}

/**
 * 格式化日期
 */
export function formatDate(date: string | Date, format = 'YYYY-MM-DD'): string {
  return dayjs(date).format(format);
}

/**
 * 格式化日期时间
 */
export function formatDateTime(date: string | Date): string {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
}

/**
 * 生成唯一ID
 */
export function generateId(): string {
  return Math.random().toString(36).substring(2, 9);
}
'''


def get_styles_index() -> str:
    """生成src/styles/index.less内容"""
    return '''// 全局样式

// 覆盖 Ant Design Vue 样式
.ant-layout {
  min-height: 100vh;
}

// 原型页面容器
.prototype-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: 100vh;
}

// 搜索区域
.search-area {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
  margin-bottom: 24px;
}

// 表格操作区
.table-operations {
  background: #fff;
  padding: 16px 24px;
  border-radius: 4px 4px 0 0;
  border-bottom: 1px solid #f0f0f0;
}

// 分页区域
.pagination-area {
  background: #fff;
  padding: 16px 24px;
  border-radius: 0 0 4px 4px;
  text-align: right;
}
'''


def get_types_global() -> str:
    """生成src/types/global.d.ts内容"""
    return '''// 全局类型定义

declare namespace YcForm {
  interface Schema {
    field: string | string[];
    label?: string;
    component: string;
    required?: boolean;
    tip?: string;
    componentProps?: Record<string, any>;
  }
}

type CommonRes<T> = Promise<{
  code: number;
  data: T;
  message: string;
}>;
'''


def init_prototype(name: str, output_dir: str, template: str = 'default') -> Dict:
    """
    初始化原型项目

    Args:
        name: 原型项目名称
        output_dir: 输出目录
        template: 模板类型 (default, list, form, detail)

    Returns:
        {
            "status": "success|error",
            "message": "...",
            "path": "原型项目完整路径"
        }
    """
    try:
        # 创建项目目录
        project_path = Path(output_dir) / name
        src_path = project_path / 'src'

        if project_path.exists():
            return {
                "status": "error",
                "message": f"原型项目 '{name}' 已存在",
                "path": str(project_path)
            }

        # 创建目录结构
        dirs = [
            src_path,
            src_path / 'api',
            src_path / 'hooks',
            src_path / 'pages',
            src_path / 'router',
            src_path / 'utils',
            src_path / 'styles',
            src_path / 'types',
        ]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # 写入配置文件
        (project_path / 'package.json').write_text(get_package_json(name), encoding='utf-8')
        (project_path / 'rsbuild.config.ts').write_text(get_rsbuild_config(), encoding='utf-8')
        (project_path / 'tsconfig.json').write_text(get_tsconfig(), encoding='utf-8')
        (project_path / 'tsconfig.node.json').write_text(get_tsconfig_node(), encoding='utf-8')
        (project_path / 'index.html').write_text(get_index_html(name), encoding='utf-8')

        # 写入源码文件
        (src_path / 'main.ts').write_text(get_main_ts(), encoding='utf-8')
        (src_path / 'App.vue').write_text(get_app_vue(), encoding='utf-8')
        (src_path / 'env.d.ts').write_text(get_env_d_ts(), encoding='utf-8')

        # 写入 router
        (src_path / 'router' / 'index.ts').write_text(get_router_index(), encoding='utf-8')

        # 写入 hooks
        (src_path / 'hooks' / 'useDrawer.ts').write_text(get_hooks_useDrawer(), encoding='utf-8')
        (src_path / 'hooks' / 'useForm.ts').write_text(get_hooks_useForm(), encoding='utf-8')

        # 写入 api
        (src_path / 'api' / 'mock-api.ts').write_text(get_mock_api(), encoding='utf-8')

        # 写入 utils
        (src_path / 'utils' / 'index.ts').write_text(get_utils_index(), encoding='utf-8')

        # 写入 styles
        (src_path / 'styles' / 'index.less').write_text(get_styles_index(), encoding='utf-8')

        # 写入 types
        (src_path / 'types' / 'global.d.ts').write_text(get_types_global(), encoding='utf-8')

        return {
            "status": "success",
            "message": f"原型项目 '{name}' 创建成功",
            "path": str(project_path),
            "next_steps": [
                f"cd {project_path}",
                "pnpm install",
                "pnpm dev"
            ]
        }

    except Exception as e:
        import traceback
        return {
            "status": "error",
            "message": str(e),
            "error": traceback.format_exc()
        }


def main():
    parser = argparse.ArgumentParser(description='初始化 Vue 原型项目')
    parser.add_argument('--name', '-n', required=True, help='原型项目名称')
    parser.add_argument('--output', '-o', default='docs/prototype', help='输出目录')
    parser.add_argument('--template', '-t', default='default', help='模板类型')
    parser.add_argument('--output-result', help='输出结果到文件')

    args = parser.parse_args()

    result = init_prototype(args.name, args.output, args.template)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output_result:
        Path(args.output_result).write_text(output, encoding='utf-8')
    else:
        print(output)

    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
