// static/js/login.js

document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // 辅助函数：显示错误信息
    function displayError(inputElement, message) {
        // 查找或创建错误提示元素
        let errorSpan = inputElement.parentElement.querySelector('.error-message');
        if (!errorSpan) {
            errorSpan = document.createElement('span');
            errorSpan.className = 'error-message';
            inputElement.parentElement.appendChild(errorSpan);
        }
        errorSpan.textContent = message;
        inputElement.classList.add('is-invalid'); // 添加错误样式类
    }

    // 辅助函数：清除错误信息
    function clearError(inputElement) {
        const errorSpan = inputElement.parentElement.querySelector('.error-message');
        if (errorSpan) {
            errorSpan.remove();
        }
        inputElement.classList.remove('is-invalid'); // 移除错误样式类
    }

    // 核心函数：执行前端验证
    function validateForm() {
        let isValid = true;

        // 1. 验证用户名
        const usernameValue = usernameInput.value.trim();
        clearError(usernameInput);
        if (usernameValue === '') {
            displayError(usernameInput, '用户名不能为空。');
            isValid = false;
        }
        // 可以添加更多验证，例如长度、特殊字符等...
        // else if (usernameValue.length < 4) {
        //     displayError(usernameInput, '用户名至少需要4个字符。');
        //     isValid = false;
        // }


        // 2. 验证密码
        const passwordValue = passwordInput.value;
        clearError(passwordInput);
        if (passwordValue === '') {
            displayError(passwordInput, '密码不能为空。');
            isValid = false;
        }
        // 可以添加密码复杂度验证
        // else if (passwordValue.length < 6) {
        //     displayError(passwordInput, '密码长度不能少于6位。');
        //     isValid = false;
        // }

        return isValid;
    }

    // 监听表单提交事件
    loginForm.addEventListener('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault(); // 阻止表单提交
        }
        // 如果 validateForm 返回 true，表单将正常提交到后端
    });

    // 实时清除错误（可选：用户输入时清除错误提示）
    usernameInput.addEventListener('input', () => clearError(usernameInput));
    passwordInput.addEventListener('input', () => clearError(passwordInput));
});