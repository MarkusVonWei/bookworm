/**
 * Toast 轻提示
 * 跨平台统一的 toast 封装
 */

export function useToast() {
  function show(title, icon = 'none', duration = 2000) {
    uni.showToast({ title, icon, duration })
  }

  function success(title, duration = 2000) {
    show(title, 'success', duration)
  }

  function error(title, duration = 2500) {
    show(title, 'none', duration)
  }

  function warning(title, duration = 2500) {
    show(title, 'none', duration)
  }

  function info(title, duration = 2000) {
    show(title, 'none', duration)
  }

  function loading(title = '加载中...') {
    uni.showLoading({ title, mask: true })
  }

  function hideLoading() {
    uni.hideLoading()
  }

  return { show, success, error, warning, info, loading, hideLoading }
}
