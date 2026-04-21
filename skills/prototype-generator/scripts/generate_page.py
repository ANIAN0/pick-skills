"""
原型页面生成脚本
根据页面需求生成单个HTML原型文件

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


def generate_base_html(title: str, prototype_content: str, description_content: str, existing_styles: dict = None) -> str:
    """生成基础HTML框架"""
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型 - {title}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    /* 页面级布局样式 */
    .prototype-container {{ display: flex; height: 100vh; overflow: hidden; }}
    .prototype-left {{ width: 1200px; background: white; overflow: auto; flex-shrink: 0; position: relative; }}
    .prototype-right {{ flex: 1; background: #f5f5f5; padding: 24px; overflow: auto; }}

    /* 抽屉样式 - Ant Design 风格 */
    .ant-drawer-wrapper {{ position: fixed; top: 0; right: 0; bottom: 0; left: 0; z-index: 1000; overflow: auto; pointer-events: none; }}
    .ant-drawer {{ position: absolute; top: 0; right: 0; bottom: 0; width: 520px; pointer-events: auto; }}
    .ant-drawer-mask {{ position: absolute; top: 0; right: 0; bottom: 0; left: 0; background: rgba(0,0,0,0.45); }}
    .ant-drawer-content-wrapper {{ position: absolute; top: 0; right: 0; bottom: 0; width: 100%; box-shadow: -2px 0 8px rgba(0,0,0,0.15); }}
    .ant-drawer-content {{ width: 100%; height: 100%; background: #fff; display: flex; flex-direction: column; }}
    .ant-drawer-header {{ padding: 16px 24px; border-bottom: 1px solid #f0f0f0; display: flex; justify-content: space-between; align-items: center; }}
    .ant-drawer-title {{ font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85); }}
    .ant-drawer-close {{ font-size: 16px; color: rgba(0,0,0,0.45); cursor: pointer; border: none; background: transparent; }}
    .ant-drawer-body {{ flex: 1; padding: 24px; overflow-y: auto; }}
    .ant-drawer-footer {{ padding: 10px 16px; border-top: 1px solid #f0f0f0; text-align: right; }}

    /* 弹窗样式 - Ant Design 风格 */
    .ant-modal-root {{ position: fixed; top: 0; right: 0; bottom: 0; left: 0; z-index: 1000; }}
    .ant-modal-mask {{ position: absolute; top: 0; right: 0; bottom: 0; left: 0; background: rgba(0,0,0,0.45); }}
    .ant-modal-wrap {{ position: absolute; top: 0; right: 0; bottom: 0; left: 0; overflow: auto; display: flex; align-items: center; justify-content: center; }}
    .ant-modal {{ width: auto; max-width: calc(100vw - 32px); margin: 0 auto; padding-bottom: 24px; pointer-events: auto; }}
    .ant-modal-content {{ position: relative; background: #fff; border-radius: 2px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); }}
    .ant-modal-header {{ padding: 16px 24px; border-bottom: 1px solid #f0f0f0; }}
    .ant-modal-title {{ font-size: 16px; font-weight: 500; color: rgba(0,0,0,0.85); }}
    .ant-modal-close {{ position: absolute; top: 0; right: 0; width: 56px; height: 56px; border: none; background: transparent; font-size: 16px; color: rgba(0,0,0,0.45); cursor: pointer; }}
    .ant-modal-body {{ padding: 24px; font-size: 14px; color: rgba(0,0,0,0.65); }}
    .ant-modal-footer {{ padding: 10px 16px; border-top: 1px solid #f0f0f0; text-align: right; }}

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
    <div class="prototype-left">
{prototype_content}
    </div>

    <!-- 右侧：交互说明 -->
    <div class="prototype-right">
{description_content}
    </div>
  </div>

  <script>
    // Mock 交互函数
    function mockAction(action, data) {{
      console.log('[Mock]', action, data);
      alert(action + ' 成功（模拟）');
    }}

    // 抽屉控制
    function openDrawer(title) {{
      const drawer = document.getElementById('drawer');
      if (drawer) {{
        drawer.style.display = 'block';
        const titleEl = drawer.querySelector('.ant-drawer-title');
        if (titleEl) titleEl.textContent = title || '标题';
      }}
    }}

    function closeDrawer() {{
      const drawer = document.getElementById('drawer');
      if (drawer) drawer.style.display = 'none';
    }}

    // 弹窗控制
    function openModal(title) {{
      const modal = document.getElementById('modal');
      if (modal) {{
        modal.style.display = 'block';
        const titleEl = modal.querySelector('.ant-modal-title');
        if (titleEl) titleEl.textContent = title || '标题';
      }}
    }}

    function closeModal() {{
      const modal = document.getElementById('modal');
      if (modal) modal.style.display = 'none';
    }}
  </script>
</body>
</html>'''


def generate_list_page(config: Dict) -> str:
    """生成列表页原型 - 使用纯 Ant Design 类名"""
    data = config.get('data', {})
    interactions = config.get('interactions', {})
    page_name = config.get('page_name', '列表页')

    columns = data.get('columns', [])
    buttons = interactions.get('buttons', [])

    # 构建表格列
    th_html = ''
    for col in columns:
        th_html += f'                      <th class="ant-table-cell">{col["title"]}</th>\n'

    # 构建表格数据（mock）
    tbody_html = ''
    for i in range(3):
        tbody_html += '                    <tr class="ant-table-row">\n'
        for col in columns:
            if col.get('type') == 'tag':
                tag_color = 'green' if i % 2 == 0 else 'red'
                tag_text = '启用' if i % 2 == 0 else '禁用'
                value = f'<span class="ant-tag ant-tag-{tag_color}">{tag_text}</span>'
            elif col.get('type') == 'actions':
                value = '''<a style="color: #1890ff; cursor: pointer;" onclick="openDrawer('编辑'); return false;">编辑</a>
                          <span style="margin: 0 8px; color: #d9d9d9;">|</span>
                          <a style="color: #ff4d4f; cursor: pointer;" onclick="openModal('删除确认'); return false;">删除</a>'''
            else:
                value = f'示例数据{i+1}'
            tbody_html += f'                      <td class="ant-table-cell">{value}</td>\n'
        tbody_html += '                    </tr>\n'

    # 构建操作按钮
    actions_html = ''
    for btn in buttons:
        btn_type = 'ant-btn-primary' if btn in ['新增', '创建', '添加'] else ''
        onclick = 'openDrawer("新增")' if btn in ['新增', '创建', '添加'] else f"mockAction('{btn}')"
        actions_html += f'              <button type="button" class="ant-btn {btn_type}" onclick="{onclick}">{btn}</button>\n'

    # 构建搜索区域
    search_items = ''
    for col in columns[:3]:
        if col.get('type') != 'actions':
            search_items += f'''
                  <div class="ant-col" style="padding-left: 8px; padding-right: 8px;">
                    <input class="ant-input" type="text" placeholder="{col['title']}" style="width: 200px;">
                  </div>'''

    # 生成抽屉内容（新增/编辑表单）
    drawer_fields = ''
    for col in columns:
        if col.get('type') not in ['actions', 'tag']:
            drawer_fields += f'''
                <div class="ant-row ant-form-item">
                  <div class="ant-col ant-form-item-label" style="width: 100px;">
                    <label class="ant-form-item-required">{col['title']}</label>
                  </div>
                  <div class="ant-col ant-form-item-control">
                    <div class="ant-form-item-control-input">
                      <input class="ant-input" placeholder="请输入{col['title']}" style="width: 100%;">
                    </div>
                  </div>
                </div>'''

    return f'''<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); height: 64px;">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div class="ant-layout" style="display: flex;">
    <!-- 侧边栏 -->
    <aside class="ant-layout-sider" style="background: #001529; width: 200px; flex-shrink: 0; min-height: calc(100vh - 64px);">
      <ul class="ant-menu ant-menu-dark ant-menu-root" style="background: #001529; padding: 16px 0;">
        <li class="ant-menu-item" style="padding-left: 24px; color: rgba(255,255,255,0.65);">
          <span>🏠</span>
          <span style="margin-left: 10px;">首页</span>
        </li>
        <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff; padding-left: 24px;">
          <span>📋</span>
          <span style="margin-left: 10px;">{page_name}</span>
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="ant-layout-content" style="flex: 1; padding: 24px; background: #f0f2f5; overflow: auto;">
      <!-- 面包屑 -->
      <div class="ant-breadcrumb" style="margin-bottom: 16px;">
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.45);">首页</span>
        <span class="ant-breadcrumb-separator">/</span>
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.85);">{page_name}</span>
      </div>

      <!-- 搜索区域 -->
      <div class="ant-card" style="margin-bottom: 24px;">
        <div class="ant-card-body" style="padding: 24px;">
          <form class="ant-form">
            <div class="ant-row" style="margin-left: -8px; margin-right: -8px;">{search_items}
              <div class="ant-col" style="padding-left: 8px; padding-right: 8px;">
                <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('搜索')">搜索</button>
                <button type="button" class="ant-btn" style="margin-left: 8px;" onclick="mockAction('重置')">重置</button>
              </div>
            </div>
          </form>
        </div>
      </div>

      <!-- 操作栏 -->
      <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; gap: 8px;">
{actions_html}        </div>
      </div>

      <!-- 表格 -->
      <div class="ant-card">
        <div class="ant-table-wrapper">
          <div class="ant-spin-nested-loading">
            <div class="ant-spin-container">
              <div class="ant-table">
                <div class="ant-table-container">
                  <div class="ant-table-content">
                    <table style="table-layout: auto;">
                      <thead class="ant-table-thead">
                        <tr>
{th_html}                        </tr>
                      </thead>
                      <tbody class="ant-table-tbody">
{tbody_html}                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 分页 -->
        <div style="padding: 16px; display: flex; justify-content: flex-end;">
          <ul class="ant-pagination">
            <li class="ant-pagination-total-text" style="margin-right: 8px;">共 100 条</li>
            <li class="ant-pagination-prev ant-pagination-disabled">
              <button class="ant-pagination-item-link" disabled>
                <span>&lt;</span>
              </button>
            </li>
            <li class="ant-pagination-item ant-pagination-item-1 ant-pagination-item-active">
              <a>1</a>
            </li>
            <li class="ant-pagination-item">
              <a>2</a>
            </li>
            <li class="ant-pagination-next">
              <button class="ant-pagination-item-link">
                <span>&gt;</span>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </main>
  </div>

  <!-- 抽屉：新增/编辑 -->
  <div id="drawer" class="ant-drawer-wrapper" style="display: none;">
    <div class="ant-drawer">
      <div class="ant-drawer-mask" onclick="closeDrawer()"></div>
      <div class="ant-drawer-content-wrapper">
        <div class="ant-drawer-content">
          <div class="ant-drawer-header">
            <div class="ant-drawer-title">新增</div>
            <button type="button" class="ant-drawer-close" onclick="closeDrawer()">✕</button>
          </div>
          <div class="ant-drawer-body">
            <form class="ant-form">
{drawer_fields}            </form>
          </div>
          <div class="ant-drawer-footer">
            <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('保存'); closeDrawer();">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 弹窗：删除确认 -->
  <div id="modal" class="ant-modal-root" style="display: none;">
    <div class="ant-modal-mask" onclick="closeModal()"></div>
    <div class="ant-modal-wrap">
      <div class="ant-modal" style="width: 420px;">
        <div class="ant-modal-content">
          <button type="button" class="ant-modal-close" onclick="closeModal()">✕</button>
          <div class="ant-modal-header">
            <div class="ant-modal-title">删除确认</div>
          </div>
          <div class="ant-modal-body">
            <div class="ant-modal-confirm-body-wrapper">
              <div class="ant-modal-confirm-body">
                <span class="anticon anticon-exclamation-circle" style="color: #faad14; font-size: 22px; margin-right: 16px;">⚠️</span>
                <span>确定要删除该记录吗？此操作不可撤销。</span>
              </div>
            </div>
          </div>
          <div class="ant-modal-footer">
            <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeModal()">取消</button>
            <button type="button" class="ant-btn ant-btn-danger" onclick="mockAction('删除'); closeModal();">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>'''


def generate_form_page(config: Dict) -> str:
    """生成表单页原型 - 使用纯 Ant Design 类名"""
    data = config.get('data', {})
    page_name = config.get('page_name', '表单页')
    fields = data.get('fields', [])

    # 构建表单字段
    fields_html = ''
    for field in fields:
        required = field.get('required', False)
        required_mark = '<span style="color: #ff4d4f; margin-right: 4px;">*</span>' if required else ''

        if field.get('type') == 'select':
            options = ''.join([f'<option>{opt}</option>' for opt in field.get('options', ['选项1', '选项2'])])
            input_html = f'<select class="ant-input" style="width: 100%;"><option>请选择</option>{options}</select>'
        elif field.get('type') == 'textarea':
            input_html = f'<textarea class="ant-input" rows="3" placeholder="请输入{field["label"]}" style="width: 100%;"></textarea>'
        else:
            input_html = f'<input class="ant-input" placeholder="请输入{field["label"]}" style="width: 100%;">'

        fields_html += f'''
                <div class="ant-row ant-form-item">
                  <div class="ant-col ant-form-item-label" style="width: 120px;">
                    <label>{required_mark}{field["label"]}</label>
                  </div>
                  <div class="ant-col ant-form-item-control">
                    <div class="ant-form-item-control-input">{input_html}</div>
                  </div>
                </div>'''

    # 抽屉中的子表单字段
    subform_fields = ''
    for field in fields[:4]:
        subform_fields += f'''
                <div class="ant-row ant-form-item" style="margin-bottom: 12px;">
                  <div class="ant-col ant-form-item-label" style="width: 80px;">
                    <label>{field["label"]}</label>
                  </div>
                  <div class="ant-col ant-form-item-control">
                    <input class="ant-input" placeholder="请输入" style="width: 100%;">
                  </div>
                </div>'''

    return f'''<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); height: 64px;">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div class="ant-layout" style="display: flex;">
    <!-- 侧边栏 -->
    <aside class="ant-layout-sider" style="background: #001529; width: 200px; flex-shrink: 0; min-height: calc(100vh - 64px);">
      <ul class="ant-menu ant-menu-dark ant-menu-root" style="background: #001529; padding: 16px 0;">
        <li class="ant-menu-item" style="padding-left: 24px; color: rgba(255,255,255,0.65);">
          <span>🏠</span>
          <span style="margin-left: 10px;">首页</span>
        </li>
        <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff; padding-left: 24px;">
          <span>📝</span>
          <span style="margin-left: 10px;">{page_name}</span>
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="ant-layout-content" style="flex: 1; padding: 24px; background: #f0f2f5; overflow: auto;">
      <!-- 面包屑 -->
      <div class="ant-breadcrumb" style="margin-bottom: 16px;">
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.45);">首页</span>
        <span class="ant-breadcrumb-separator">/</span>
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.85);">{page_name}</span>
      </div>

      <!-- 表单卡片 -->
      <div class="ant-card" style="max-width: 800px;">
        <div class="ant-card-head">
          <div class="ant-card-head-title">{page_name}</div>
        </div>
        <div class="ant-card-body" style="padding: 24px;">
          <form class="ant-form">
{fields_html}
            <!-- 关联数据区域 -->
            <div class="ant-row ant-form-item" style="border-top: 1px dashed #d9d9d9; padding-top: 20px; margin-top: 20px;">
              <div class="ant-col ant-form-item-label" style="width: 120px;">
                <label>关联数据</label>
              </div>
              <div class="ant-col ant-form-item-control">
                <button type="button" class="ant-btn ant-btn-dashed" onclick="openDrawer('添加关联数据')">
                  <span>+</span> 添加关联
                </button>
                <div style="margin-top: 8px; color: rgba(0,0,0,0.45); font-size: 14px;">点击添加关联数据</div>
              </div>
            </div>

            <div class="ant-row ant-form-item" style="margin-top: 24px;">
              <div class="ant-col ant-form-item-control" style="margin-left: 120px;">
                <button type="button" class="ant-btn ant-btn-primary" style="margin-right: 8px;" onclick="mockAction('提交')">提交</button>
                <button type="button" class="ant-btn" onclick="mockAction('取消')">取消</button>
                <button type="button" class="ant-btn ant-btn-link" style="margin-left: 16px;" onclick="openModal('保存草稿')">保存草稿</button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>

  <!-- 抽屉：添加关联 -->
  <div id="drawer" class="ant-drawer-wrapper" style="display: none;">
    <div class="ant-drawer">
      <div class="ant-drawer-mask" onclick="closeDrawer()"></div>
      <div class="ant-drawer-content-wrapper">
        <div class="ant-drawer-content">
          <div class="ant-drawer-header">
            <div class="ant-drawer-title">添加关联数据</div>
            <button type="button" class="ant-drawer-close" onclick="closeDrawer()">✕</button>
          </div>
          <div class="ant-drawer-body">
            <form class="ant-form">
{subform_fields}            </form>
          </div>
          <div class="ant-drawer-footer">
            <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('添加'); closeDrawer();">确定</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 弹窗：保存草稿 -->
  <div id="modal" class="ant-modal-root" style="display: none;">
    <div class="ant-modal-mask" onclick="closeModal()"></div>
    <div class="ant-modal-wrap">
      <div class="ant-modal" style="width: 420px;">
        <div class="ant-modal-content">
          <button type="button" class="ant-modal-close" onclick="closeModal()">✕</button>
          <div class="ant-modal-header">
            <div class="ant-modal-title">保存为草稿</div>
          </div>
          <div class="ant-modal-body">
            <p>确定要将当前表单保存为草稿吗？</p>
          </div>
          <div class="ant-modal-footer">
            <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeModal()">取消</button>
            <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('保存草稿'); closeModal();">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>'''


def generate_detail_page(config: Dict) -> str:
    """生成详情页原型 - 使用纯 Ant Design 类名"""
    data = config.get('data', {})
    page_name = config.get('page_name', '详情页')
    groups = data.get('groups', [])

    # 构建详情分组
    groups_html = ''
    for group in groups:
        items_html = ''
        for field in group.get('fields', []):
            items_html += f'''
                    <div class="ant-descriptions-item" style="padding-bottom: 16px;">
                      <span class="ant-descriptions-item-label" style="color: rgba(0,0,0,0.85); font-weight: 500; display: inline-block; width: 120px;">{field}:</span>
                      <span class="ant-descriptions-item-content" style="color: rgba(0,0,0,0.65);">示例{field}值</span>
                    </div>'''

        groups_html += f'''
      <div class="ant-card" style="margin-bottom: 24px;">
        <div class="ant-card-head">
          <div class="ant-card-head-title">{group.get('title', '基本信息')}</div>
        </div>
        <div class="ant-card-body">
          <div class="ant-descriptions">{items_html}
          </div>
        </div>
      </div>'''

    return f'''<div class="ant-layout" style="min-height: 100vh;">
  <!-- 顶栏 -->
  <header class="ant-layout-header" style="background: #fff; padding: 0 24px; display: flex; align-items: center; justify-content: space-between; box-shadow: 0 1px 4px rgba(0,21,41,0.08); height: 64px;">
    <div style="display: flex; align-items: center; gap: 16px;">
      <div style="width: 32px; height: 32px; background: #1890ff; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; font-weight: bold;">S</div>
      <span style="font-size: 18px; font-weight: 500; color: rgba(0,0,0,0.85);">系统后台</span>
    </div>
    <div style="display: flex; align-items: center; gap: 16px;">
      <span style="color: rgba(0,0,0,0.65);">管理员</span>
      <div style="width: 32px; height: 32px; background: #f0f0f0; border-radius: 50%;"></div>
    </div>
  </header>

  <div class="ant-layout" style="display: flex;">
    <!-- 侧边栏 -->
    <aside class="ant-layout-sider" style="background: #001529; width: 200px; flex-shrink: 0; min-height: calc(100vh - 64px);">
      <ul class="ant-menu ant-menu-dark ant-menu-root" style="background: #001529; padding: 16px 0;">
        <li class="ant-menu-item" style="padding-left: 24px; color: rgba(255,255,255,0.65);">
          <span>🏠</span>
          <span style="margin-left: 10px;">首页</span>
        </li>
        <li class="ant-menu-item ant-menu-item-selected" style="background: #1890ff; padding-left: 24px;">
          <span>📄</span>
          <span style="margin-left: 10px;">{page_name}</span>
        </li>
      </ul>
    </aside>

    <!-- 主内容 -->
    <main class="ant-layout-content" style="flex: 1; padding: 24px; background: #f0f2f5; overflow: auto;">
      <!-- 面包屑 -->
      <div class="ant-breadcrumb" style="margin-bottom: 16px;">
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.45);">首页</span>
        <span class="ant-breadcrumb-separator">/</span>
        <span class="ant-breadcrumb-link" style="color: rgba(0,0,0,0.85);">{page_name}</span>
      </div>

      <!-- 操作栏 -->
      <div style="margin-bottom: 24px;">
        <button type="button" class="ant-btn ant-btn-primary" style="margin-right: 8px;" onclick="openDrawer('编辑详情')">编辑</button>
        <button type="button" class="ant-btn" onclick="mockAction('返回')">返回</button>
        <button type="button" class="ant-btn ant-btn-dashed" style="margin-left: 8px;" onclick="openModal('分享')">🔗 分享</button>
      </div>

      <!-- 详情内容 -->
{groups_html}

      <!-- 关联记录 -->
      <div class="ant-card">
        <div class="ant-card-head" style="display: flex; justify-content: space-between; align-items: center;">
          <div class="ant-card-head-title">关联记录</div>
          <button type="button" class="ant-btn ant-btn-sm ant-btn-primary" onclick="openDrawer('添加关联')">+ 添加</button>
        </div>
        <div class="ant-card-body">
          <div class="ant-table-wrapper">
            <div class="ant-table">
              <div class="ant-table-container">
                <div class="ant-table-content">
                  <table style="table-layout: auto; width: 100%;">
                    <thead class="ant-table-thead">
                      <tr>
                        <th class="ant-table-cell">记录名称</th>
                        <th class="ant-table-cell">状态</th>
                        <th class="ant-table-cell">创建时间</th>
                        <th class="ant-table-cell">操作</th>
                      </tr>
                    </thead>
                    <tbody class="ant-table-tbody">
                      <tr class="ant-table-row">
                        <td class="ant-table-cell">关联记录1</td>
                        <td class="ant-table-cell"><span class="ant-tag ant-tag-green">已完成</span></td>
                        <td class="ant-table-cell" style="color: rgba(0,0,0,0.45);">2024-03-25</td>
                        <td class="ant-table-cell">
                          <a style="color: #1890ff; cursor: pointer;" onclick="openDrawer('查看详情'); return false;">查看</a>
                        </td>
                      </tr>
                      <tr class="ant-table-row">
                        <td class="ant-table-cell">关联记录2</td>
                        <td class="ant-table-cell"><span class="ant-tag ant-tag-blue">进行中</span></td>
                        <td class="ant-table-cell" style="color: rgba(0,0,0,0.45);">2024-03-24</td>
                        <td class="ant-table-cell">
                          <a style="color: #1890ff; cursor: pointer;" onclick="openDrawer('查看详情'); return false;">查看</a>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>

  <!-- 抽屉：编辑详情 -->
  <div id="drawer" class="ant-drawer-wrapper" style="display: none;">
    <div class="ant-drawer">
      <div class="ant-drawer-mask" onclick="closeDrawer()"></div>
      <div class="ant-drawer-content-wrapper">
        <div class="ant-drawer-content">
          <div class="ant-drawer-header">
            <div class="ant-drawer-title">编辑详情</div>
            <button type="button" class="ant-drawer-close" onclick="closeDrawer()">✕</button>
          </div>
          <div class="ant-drawer-body">
            <form class="ant-form">
              <div class="ant-row ant-form-item">
                <div class="ant-col ant-form-item-label" style="width: 100px;">
                  <label>字段一</label>
                </div>
                <div class="ant-col ant-form-item-control">
                  <input class="ant-input" placeholder="请输入" value="示例值" style="width: 100%;">
                </div>
              </div>
              <div class="ant-row ant-form-item">
                <div class="ant-col ant-form-item-label" style="width: 100px;">
                  <label>字段二</label>
                </div>
                <div class="ant-col ant-form-item-control">
                  <input class="ant-input" placeholder="请输入" value="示例值" style="width: 100%;">
                </div>
              </div>
              <div class="ant-row ant-form-item">
                <div class="ant-col ant-form-item-label" style="width: 100px;">
                  <label>状态</label>
                </div>
                <div class="ant-col ant-form-item-control">
                  <select class="ant-input" style="width: 100%;">
                    <option>启用</option>
                    <option>禁用</option>
                  </select>
                </div>
              </div>
            </form>
          </div>
          <div class="ant-drawer-footer">
            <button type="button" class="ant-btn" style="margin-right: 8px;" onclick="closeDrawer()">取消</button>
            <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('保存'); closeDrawer();">保存</button>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- 弹窗：分享 -->
  <div id="modal" class="ant-modal-root" style="display: none;">
    <div class="ant-modal-mask" onclick="closeModal()"></div>
    <div class="ant-modal-wrap">
      <div class="ant-modal" style="width: 520px;">
        <div class="ant-modal-content">
          <button type="button" class="ant-modal-close" onclick="closeModal()">✕</button>
          <div class="ant-modal-header">
            <div class="ant-modal-title">分享</div>
          </div>
          <div class="ant-modal-body">
            <p style="color: rgba(0,0,0,0.65); margin-bottom: 16px;">将此详情分享给其他人：</p>
            <div style="display: flex; gap: 8px;">
              <input class="ant-input" value="https://example.com/share/abc123" readonly style="flex: 1;">
              <button type="button" class="ant-btn ant-btn-primary" onclick="mockAction('复制链接')">复制</button>
            </div>
          </div>
          <div class="ant-modal-footer">
            <button type="button" class="ant-btn" onclick="closeModal()">关闭</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>'''


def generate_description(config: Dict) -> str:
    """生成右侧说明文档"""
    page_name = config.get('page_name', '页面')
    clarification = config.get('clarification', {})
    interactions = clarification.get('interactions', {})
    boundary = clarification.get('boundary', {})
    layout = clarification.get('layout', {})

    # 构建交互说明
    interactions_html = ''
    if interactions.get('buttons'):
        interactions_html += '<h4 style="font-weight: 500; margin-bottom: 8px;">操作按钮</h4><ul style="list-style: disc; padding-left: 20px; margin-bottom: 16px;">'
        for btn in interactions['buttons']:
            interactions_html += f'<li>{btn}: 点击后触发相应操作</li>'
        interactions_html += '</ul>'

    if interactions.get('modal_type'):
        interactions_html += f'<p style="margin-bottom: 8px;"><span style="font-weight: 500;">编辑/新增方式:</span> {interactions["modal_type"]}</p>'

    # 构建边界说明
    boundary_html = '<ul style="list-style: disc; padding-left: 20px;">'
    if boundary.get('empty_state'):
        boundary_html += f'<li><span style="font-weight: 500;">空数据:</span> {boundary["empty_state"]}</li>'
    if boundary.get('loading_state'):
        boundary_html += f'<li><span style="font-weight: 500;">加载中:</span> {boundary["loading_state"]}</li>'
    if boundary.get('error_state'):
        boundary_html += f'<li><span style="font-weight: 500;">错误:</span> {boundary["error_state"]}</li>'
    boundary_html += '</ul>'

    # 布局说明
    layout_html = f'<p style="margin-bottom: 8px;"><span style="font-weight: 500;">布局类型:</span> {layout.get("type", "顶栏+侧边栏+内容区")}</p>'
    if layout.get('modules'):
        layout_html += '<p style="font-weight: 500;">模块划分:</p><ul style="list-style: disc; padding-left: 20px; margin-bottom: 16px;">'
        for mod in layout['modules']:
            layout_html += f'<li>{mod}</li>'
        layout_html += '</ul>'

    return f'''<div style="max-width: 600px;">
  <div class="doc-section">
    <div class="doc-title">页面交互说明</div>
    <p style="color: rgba(0,0,0,0.45); font-size: 14px; margin-bottom: 16px;">版本: v1.0 | 更新日期: {datetime.now().strftime('%Y-%m-%d')}</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">1. 页面概述</div>
    <p style="color: rgba(0,0,0,0.65); line-height: 1.6;">本页面为{page_name}原型，展示页面布局、组件和交互逻辑。</p>
  </div>

  <div class="doc-section">
    <div class="doc-title">2. 布局结构</div>
    {layout_html}
  </div>

  <div class="doc-section">
    <div class="doc-title">3. 交互逻辑</div>
    {interactions_html if interactions_html else '<p style="color: rgba(0,0,0,0.65);">标准交互逻辑</p>'}
    <h4 style="font-weight: 500; margin: 16px 0 8px;">抽屉/弹窗交互</h4>
    <ul style="list-style: disc; padding-left: 20px;">
      <li><span style="font-weight: 500;">抽屉:</span> 点击新增/编辑时从右侧滑出，展示表单内容</li>
      <li><span style="font-weight: 500;">弹窗:</span> 用于确认操作（删除、保存草稿等）</li>
      <li><span style="font-weight: 500;">关闭方式:</span> 点击遮罩层、关闭按钮或取消按钮均可关闭</li>
    </ul>
  </div>

  <div class="doc-section">
    <div class="doc-title">4. 边界场景</div>
    {boundary_html}
  </div>
</div>'''


def extract_version_from_file_name(file_name: str) -> int:
    """从文件名中提取版本号"""
    match = re.search(r'-v(\d+)(?:\.html)?$', file_name)
    if match:
        return int(match.group(1))
    return 1


def generate_file_name(output_dir: Path, page_slug: str, scenario: str, old_file_name: Optional[str]) -> str:
    """生成文件名"""
    date_str = datetime.now().strftime('%Y%m%d')

    if scenario == 'refactor' and old_file_name:
        old_version = extract_version_from_file_name(old_file_name)
        new_version = old_version + 1
        file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"
        while (output_dir / file_name).exists():
            new_version += 1
            file_name = f"prototype-{date_str}-{page_slug}-v{new_version}.html"
    else:
        file_name = f"prototype-{date_str}-{page_slug}.html"
        if (output_dir / file_name).exists():
            version = 2
            while (output_dir / f"prototype-{date_str}-{page_slug}-v{version}.html").exists():
                version += 1
            file_name = f"prototype-{date_str}-{page_slug}-v{version}.html"

    return file_name


def extract_existing_styles(output_dir: Path) -> dict:
    """从现有页面提取样式信息"""
    styles = {
        'primary_color': '#1890ff',
        'sidebar_bg': '#001529',
    }

    if not output_dir.exists():
        return styles

    html_files = sorted(output_dir.glob('*.html'), key=lambda x: x.stat().st_mtime, reverse=True)
    if not html_files:
        return styles

    try:
        latest_file = html_files[0]
        content = latest_file.read_text(encoding='utf-8')

        # 提取主色调
        color_match = re.search(r'#1890ff|#1677ff|#[0-9a-fA-F]{6}', content)
        if color_match:
            styles['primary_color'] = color_match.group(0)

        print(f"已继承现有页面风格: {latest_file.name}")
    except Exception as e:
        print(f"读取现有页面样式失败: {e}")

    return styles


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

        page_slug = page_name.lower().replace(' ', '-').replace('_', '-')
        existing_styles = extract_existing_styles(output_dir)
        file_name = generate_file_name(output_dir, page_slug, scenario, config.get('old_file_name'))

        page_generators = {
            'list': generate_list_page,
            'form': generate_form_page,
            'detail': generate_detail_page,
        }

        generator = page_generators.get(page_type, generate_list_page)
        prototype_content = generator(config)
        description_content = generate_description(config)
        full_html = generate_base_html(page_name, prototype_content, description_content, existing_styles)

        file_path = output_dir / file_name
        file_path.write_text(full_html, encoding='utf-8')

        return {
            "file_path": str(file_path),
            "file_name": file_name,
            "status": "success",
            "message": "生成成功" if scenario == 'new' else f"改造成功，已生成新版本",
            "page_info": {
                "name": page_name,
                "type": page_type,
                "scenario": scenario,
                "version": extract_version_from_file_name(file_name)
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "error": {"type": "generation_error", "detail": str(e)}
        }


def main():
    parser = argparse.ArgumentParser(description='生成原型页面HTML')
    parser.add_argument('--config', '-c', help='JSON配置文件路径')
    parser.add_argument('--input', '-i', help='JSON格式的输入参数')
    parser.add_argument('--output', '-o', help='输出结果到文件')

    args = parser.parse_args()

    if args.config:
        config = json.loads(Path(args.config).read_text(encoding='utf-8'))
    elif args.input:
        config = json.loads(args.input)
    else:
        config = json.loads(sys.stdin.read())

    result = generate_page(config)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
    else:
        print(output)

    sys.exit(0 if result['status'] == 'success' else 1)


if __name__ == '__main__':
    main()
