# 条件等待

当测试或异步流程依赖 `sleep`、`setTimeout`、固定秒数等待而变得不稳定时，使用条件等待。原则：等待真实条件成立，不等待猜测出来的时间。

## 适用信号

- 测试偶尔通过、偶尔失败。
- 并发或 CI 环境下更容易超时。
- 代码里出现 `sleep(1000)`、`setTimeout`、`time.sleep()` 这类任意等待。
- 等待的是事件、状态、数量、文件、任务完成等可观察条件。

不适用：正在测试 debounce、throttle、调度间隔等真实时间行为。此时可以保留固定等待，但必须说明等待依据。

## 基本模式

```typescript
// 错误：猜时间
await new Promise(resolve => setTimeout(resolve, 50));
expect(getResult()).toBeDefined();

// 正确：等条件
await waitFor(() => getResult() !== undefined, 'result to be ready');
expect(getResult()).toBeDefined();
```

通用实现：

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const start = Date.now();

  while (true) {
    const value = condition();
    if (value) return value;

    if (Date.now() - start > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }

    await new Promise(resolve => setTimeout(resolve, 10));
  }
}
```

完整示例见 `../scripts/condition-based-waiting-example.ts`。

## 常见条件

| 场景 | 条件示例 |
|---|---|
| 等事件 | `events.find(e => e.type === 'DONE')` |
| 等状态 | `machine.state === 'ready'` |
| 等数量 | `items.length >= 5` |
| 等文件 | `fs.existsSync(path)` |
| 等复杂状态 | `obj.ready && obj.value > 10` |

## 常见错误

- 轮询太快：`setTimeout(check, 1)` 会浪费 CPU；通常 10ms 足够。
- 没有超时：条件永不成立时会卡死；必须带清晰错误信息。
- 读取旧数据：不要在循环外缓存状态；每轮都重新读取条件。
- 先 sleep 再断言：改为先等待触发条件，再验证结果。

## 完成判据

- 任意等待已替换为条件等待，或保留固定等待时已说明它验证的是时间行为。
- 超时错误能说明等待的具体条件。
- 失败时输出足够定位是条件未达成，而不是单纯“超时了”。
