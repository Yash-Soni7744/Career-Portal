const togglePassword = document.getElementById('togglePassword');
const password = document.getElementById('password');

function togglePasswordVisibility() {
    if (password.type === 'password') {
        password.type = 'text';
        togglePassword.src = '/static/images/close-eye.svg';
    } else {
        password.type = 'password';
        togglePassword.src = '/static/images/open-eye.svg';
    }
}