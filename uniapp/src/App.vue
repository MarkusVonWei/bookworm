<script>
import { useUser } from './composables/useUser'

export default {
  onLaunch() {
    console.log('App Launch')
    // 初始化用户（验证缓存、必要时重建）
    const { initUser } = useUser()
    initUser().catch(err => {
      console.error('用户初始化失败:', err)
    })
  },
  onShow() {
    console.log('App Show')
  },
  onHide() {
    console.log('App Hide')
  }
}
</script>

<style>
/* 全局样式变量 - 暖色书卷风 */
page {
  /* 颜色 */
  --color-bg-page: #F5F0E8;
  --color-bg-card: #FFFEF9;
  --color-bg-warm: #F0E8D8;
  --color-bg-soft: #F8F4EC;
  --color-bg-overlay: rgba(26, 26, 26, 0.45);

  --color-primary: #8B7355;
  --color-primary-hover: #7A6548;
  --color-finished: #5B8C5A;

  --color-text-primary: #1A1A1A;
  --color-text-secondary: #6B6560;
  --color-text-muted: #B8A88A;
  --color-text-white: #FFFEF9;

  --color-border: #E0D8CC;
  --color-border-light: #EDE8E0;
  --color-danger: #C45B5B;

  /* 圆角 */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 999px;

  /* 间距 */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 16px;
  --space-lg: 24px;
  --space-xl: 32px;

  /* 阴影 */
  --shadow-card: 0 2px 8px rgba(139, 115, 85, 0.08);
  --shadow-float: 0 4px 16px rgba(139, 115, 85, 0.12);
  --shadow-book: 0 4px 12px rgba(139, 115, 85, 0.15);

  background-color: var(--color-bg-page);
  color: var(--color-text-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

/* 通用按钮 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border-radius: var(--radius-full);
  font-size: 14px;
  font-weight: 500;
  border: none;
  cursor: pointer;
}

.btn--primary {
  background: var(--color-primary);
  color: var(--color-text-white);
}

.btn--primary:active {
  background: var(--color-primary-hover);
}

.btn--ghost {
  background: var(--color-bg-soft);
  color: var(--color-text-secondary);
}

.btn:disabled {
  opacity: 0.5;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 16px;
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.empty-hint {
  font-size: 13px;
  color: var(--color-text-muted);
}

/* 加载状态 */
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--color-text-muted);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 8px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
