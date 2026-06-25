# 原型 HTML 输出格式规范

> 本文档描述文件命名、目录结构和 index.html 规则。HTML 结构本身以 `assets/page-skeleton.html` 为准。

---

## 输出目录

`.dev/prototype/`

---

## 文件命名

| 场景 | 命名格式 | 示例 |
|------|---------|------|
| 新原型 | `prototype-{YYYYMMDD}-{页面名称}.html` | `prototype-20260624-role-list.html` |
| 改造原型 | `prototype-{YYYYMMDD}-{页面名称}-v{N}.html` | `prototype-20260624-role-list-v2.html` |

- 页面名称中的中文和字母直接保留，空格替换为 `-`
- 已有同名文件时，自动递增 `-vN` 后缀，**不覆盖已有文件**

---

## 单文件结构规则

每个 HTML 文件必须满足：

1. 可直接在浏览器打开，无控制台报错
2. 骨架来自 `assets/page-skeleton.html`，不自行重写
3. 抽屉、确认弹窗、文档面板、引导层全部合并到主文件
4. `assets/base.css` 原样内联在 `<style>` 内
5. `assets/guide-layer.js` 原样内联在 `</body>` 前
6. Mock 数据硬编码，无 API 调用

---

## 目录页（index.html）

多页面批量生成完成后，在 `.dev/prototype/` 下生成或更新 `index.html`。

**目录页模板：**

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>原型目录</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/antd/4.24.15/antd.min.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background: #f0f2f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .index-card { background: #fff; border-radius: 8px; box-shadow: 0 1px 2px rgba(0,0,0,.04); padding: 20px 24px; margin-bottom: 16px; transition: box-shadow .2s; }
    .index-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,.1); }
    .index-card a { color: #3e8dff; text-decoration: none; font-size: 16px; font-weight: 500; }
    .index-card a:hover { color: #5ea3ff; }
    .page-type-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 8px; }
    .type-list { background: #e6f7ff; color: #1890ff; }
    .type-form { background: #f6ffed; color: #52c41a; }
    .type-detail { background: #fff7e6; color: #fa8c16; }
    .type-dashboard { background: #f9f0ff; color: #722ed1; }
    .meta { color: rgba(0,0,0,.45); font-size: 13px; margin-top: 8px; }
  </style>
</head>
<body>
  <div style="max-width: 800px; margin: 0 auto; padding: 40px 24px;">
    <h1 style="font-size: 24px; font-weight: 600; color: rgba(0,0,0,.85); margin-bottom: 8px;">原型页面目录</h1>
    <p style="color: rgba(0,0,0,.45); font-size: 14px; margin-bottom: 32px;">
      生成日期：{YYYY-MM-DD} | 共 {N} 个页面
    </p>

    <!-- 每个原型一个卡片，按类型排序：list → form → detail → dashboard -->
    <div class="index-card">
      <a href="prototype-20260624-role-list.html" target="_blank">
        角色列表
        <span class="page-type-tag type-list">list</span>
      </a>
      <div class="meta">角色管理列表页，支持新增、编辑、删除和查看详情</div>
    </div>

  </div>
</body>
</html>
```

**目录页规则：**

- 每次批量生成后覆盖更新（目录页始终是最新快照）
- 按类型排序：list → form → detail → dashboard，同类型按名称排序
- 每个卡片包含：页面名称（链接）、类型标签、功能描述
