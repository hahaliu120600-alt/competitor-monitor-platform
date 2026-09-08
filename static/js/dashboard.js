// Dashboard相关JavaScript函数

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit'
    });
}

// 格式化时间
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// 显示加载动画
function showLoading(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">加载中...</span>
                </div>
            </div>
        `;
    }
}

// 显示错误消息
function showError(elementId, message) {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="bi bi-exclamation-triangle"></i> ${message}
            </div>
        `;
    }
}

// 显示成功消息
function showSuccess(message) {
    alert(message);
}

// 显示Toast通知（如果使用Bootstrap Toast）
function showToast(message, type = 'info') {
    // 简化版，使用alert
    alert(message);
}

// 复制到剪贴板
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('已复制到剪贴板', 'success');
    }).catch(err => {
        console.error('复制失败:', err);
    });
}

// 导出为CSV
function exportToCSV(data, filename) {
    const csvContent = convertToCSV(data);
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    link.click();
}

function convertToCSV(data) {
    if (data.length === 0) return '';

    const headers = Object.keys(data[0]);
    const csvRows = [];

    csvRows.push(headers.join(','));

    for (const row of data) {
        const values = headers.map(header => {
            const value = row[header];
            return `"${value}"`;
        });
        csvRows.push(values.join(','));
    }

    return csvRows.join('\n');
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 数字格式化
function formatNumber(num) {
    if (num === null || num === undefined) return 'N/A';
    return num.toLocaleString('zh-CN');
}

// 百分比格式化
function formatPercent(num) {
    if (num === null || num === undefined) return 'N/A';
    return (num * 100).toFixed(2) + '%';
}

// 更新页面激活状态
document.addEventListener('DOMContentLoaded', function() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

    navLinks.forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPath || (currentPath === '/' && href === '/')) {
            link.classList.add('active');
        }
    });
});

// 全局错误处理
window.addEventListener('error', function(e) {
    console.error('全局错误:', e.error);
});

// Axios请求拦截器
if (typeof axios !== 'undefined') {
    axios.interceptors.response.use(
        response => response,
        error => {
            console.error('API请求失败:', error);
            if (error.response) {
                showToast(`请求失败: ${error.response.status}`, 'danger');
            } else if (error.request) {
                showToast('网络错误，请检查连接', 'danger');
            } else {
                showToast('请求配置错误', 'danger');
            }
            return Promise.reject(error);
        }
    );
}
