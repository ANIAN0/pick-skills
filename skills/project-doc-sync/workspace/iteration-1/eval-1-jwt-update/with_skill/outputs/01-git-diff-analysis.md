# Git Diff 内容分析

## 改动范围
`HEAD~1..HEAD`

## Commit 信息
```
95b7867 Update JWT token expiry, add user settings API
```

## 改动详情

### 1. 新增文件: `app/api/agent-chat/route.ts`
```typescript
// Agent Chat API Route

import { streamText } from 'ai';

export async function POST(request: Request) {
  const { messages, conversationId, agentId } = await request.json();

  // 1. Validate messages and user
  // 2. Parse model configuration
  // 3. Get sandbox tools
  // 4. Execute ToolLoopAgent.stream

  const result = streamText({
    model: 'gpt-4',
    messages,
  });

  return result.toDataStreamResponse();
}
```
**影响:** 新增 Agent Chat API 入口，使用 streamText 实现流式对话。

### 2. 新增文件: `app/api/user/settings/route.ts`
```typescript
// User Settings API Route
// GET /api/user/settings - Get user preferences
// POST /api/user/settings - Update user preferences

export async function GET(request: Request) {
  // Return user settings: theme, language, notification preferences
  return Response.json({
    settings: {
      theme: "dark",
      language: "zh-CN",
      notifications: true
    }
  });
}

export async function POST(request: Request) {
  const body = await request.json();
  // Update user settings in database
  return Response.json({ success: true });
}
```
**影响:** 新增用户设置 API，支持 GET/POST 操作，管理用户偏好设置（主题、语言、通知）。

### 3. 修改文件: `lib/auth/jwt.ts`
**变更内容:**
```diff
-const ACCESS_TOKEN_EXPIRES_IN = "15m";
-const REFRESH_TOKEN_EXPIRES_IN = "7d";
+// Updated: Access token now expires in 30 minutes for better UX
+const ACCESS_TOKEN_EXPIRES_IN = "30m";
+const REFRESH_TOKEN_EXPIRES_IN = "14d";  // Extended to 14 days
```
**影响:** JWT 令牌过期时间调整：
- Access Token: 15分钟 → 30分钟
- Refresh Token: 7天 → 14天

## 改动摘要

| 类型 | 文件路径 | 功能模块 | 关键变更 |
|------|----------|----------|----------|
| 新增 | `app/api/agent-chat/route.ts` | Agent Chat API | 新增流式对话 API 入口 |
| 新增 | `app/api/user/settings/route.ts` | User Settings API | 新增用户设置管理 API |
| 修改 | `lib/auth/jwt.ts` | 认证系统 | JWT 过期时间延长 |

## 分析日期
2026-03-29