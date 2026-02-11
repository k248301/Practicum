/**
 * Toast Notification System - Non-blocking user feedback
 */

let toastContainer = null;

/**
 * Initialize toast container
 */
function initToastContainer() {
    if (toastContainer) return;

    toastContainer = document.createElement("div");
    toastContainer.className = "toast-container";
    toastContainer.id = "toast-container";
    document.body.appendChild(toastContainer);
}

/**
 * Show a toast notification
 * @param {string} message - Message to display
 * @param {string} type - Type: 'success', 'error', 'warning', 'info'
 * @param {number} duration - Duration in ms (default: 3000)
 */
export function showToast(message, type = "info", duration = 3000) {
    initToastContainer();

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;

    // Icon based on type
    const icons = {
        success: "ri-checkbox-circle-line",
        error: "ri-error-warning-line",
        warning: "ri-alert-line",
        info: "ri-information-line",
    };

    toast.innerHTML = `
    <i class="${icons[type] || icons.info}"></i>
    <span class="toast-message">${message}</span>
    <button class="toast-close" aria-label="Close">
      <i class="ri-close-line"></i>
    </button>
  `;

    // Close button handler
    const closeBtn = toast.querySelector(".toast-close");
    closeBtn.onclick = () => removeToast(toast);

    toastContainer.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add("show"), 10);

    // Auto-remove after duration
    const timeoutId = setTimeout(() => removeToast(toast), duration);

    // Store timeout ID for manual close
    toast.dataset.timeoutId = timeoutId;
}

/**
 * Remove a toast notification
 * @param {HTMLElement} toast - Toast element
 */
function removeToast(toast) {
    // Clear timeout
    if (toast.dataset.timeoutId) {
        clearTimeout(parseInt(toast.dataset.timeoutId));
    }

    toast.classList.remove("show");
    setTimeout(() => {
        toast.remove();
        // Remove container if empty
        if (toastContainer && toastContainer.children.length === 0) {
            toastContainer.remove();
            toastContainer = null;
        }
    }, 300);
}

/**
 * Show success toast
 * @param {string} message - Message to display
 */
export function showSuccess(message) {
    showToast(message, "success");
}

/**
 * Show error toast
 * @param {string} message - Message to display
 */
export function showError(message) {
    showToast(message, "error", 4000); // Longer duration for errors
}

/**
 * Show warning toast
 * @param {string} message - Message to display
 */
export function showWarning(message) {
    showToast(message, "warning");
}

/**
 * Show info toast
 * @param {string} message - Message to display
 */
export function showInfo(message) {
    showToast(message, "info");
}
