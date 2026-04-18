---
applyTo: "**/*.{tsx,ts,jsx,js,css,html,md}"
source: "https://raw.githubusercontent.com/asterwei416/thinking-hound-mode/main/ui.instructions.md"
---

# UI / UX 指令集 (Thinking Hound Upstream Snapshot)

此檔保留 upstream `ui.instructions.md` 的核心精神，供本機 skill 參考。

## 核心原則

- 拒絕平庸：不要直接產出未經調整的預設框架樣式。
- 深度延伸：把 UI 套件視為基礎，而不是終點；應依專案調性做深層客製化。
- 時間覺醒：若牽涉 fast-moving UI kit，先查官方最新版文件。

## 開發流程

1. 先抓官方文件與目前版本的元件說明。
2. 以本地元件為優先，再做客製化與樣式注入。
3. 每個互動元件都要想過狀態：default, hover, active, disabled, loading, error。

## A11y 與效能

- 互動元件要有合理的 aria / label / focus 狀態。
- 鍵盤導航不可卡死。
- 注意視覺效果對主執行緒與 Core Web Vitals 的成本。
