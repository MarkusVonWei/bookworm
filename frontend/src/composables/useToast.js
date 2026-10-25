import { ref } from 'vue'

const toastRef = ref(null)

export function useToast() {
  function register(el) {
    toastRef.value = el
  }

  function show(message, type = 'info', duration = 2500) {
    if (toastRef.value) {
      toastRef.value.show(message, type, duration)
    }
  }

  function success(message) { show(message, 'success') }
  function error(message) { show(message, 'error') }
  function warning(message) { show(message, 'warning') }
  function info(message) { show(message, 'info') }

  return { register, show, success, error, warning, info }
}
