
const loginOpen = document.getElementById('login-open');
const loginClose = document.getElementById('login-close');
const loginModal = document.getElementById('login-modal');
const loginMask = document.getElementById('login-mask');
const loginRegister = document.getElementById('login-register');

const registerClose = document.getElementById('register-close');
const registerModal = document.getElementById('register-modal');

const resultClose = document.getElementById('result-close');
const resultModal = document.getElementById('result-modal');

loginOpen.addEventListener('click', function () {
    loginModal.classList.remove('hidden');
    loginMask.classList.remove('hidden');
});
loginClose.addEventListener('click', function () {
    loginModal.classList.add('hidden');
    loginMask.classList.add('hidden');
});
loginMask.addEventListener('click', function () {
    loginModal.classList.add('hidden');
    loginMask.classList.add('hidden');
    registerModal.classList.add('hidden');
    resultModal.classList.add('hidden');
});
loginRegister.addEventListener('click', function () {
    loginModal.classList.add('hidden');
    setTimeout(() => {
        registerModal.classList.remove('hidden');
    }, 200)
});

registerClose.addEventListener('click', function () {
    registerModal.classList.add('hidden');
    loginMask.classList.add('hidden');
});

resultClose.addEventListener('click', function () {
    loginModal.classList.add('hidden');
    resultModal.classList.add('hidden');
    loginMask.classList.add('hidden');
});

$('#register-form').submit(function(e) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", "{{ register_form.csrf_token._value() }}");
            }
        }
    });
    $.ajax({
        type: 'POST',
        url: "/register",
        data: $('#register-form').serialize(),
        success: function(data, status, xhr) {
            createResultMessage(data);
            registerModal.classList.add('hidden');
            setTimeout(() => {
                resultModal.classList.remove('hidden');
            }, 200)
        }
    });
    e.preventDefault();
});

$('#login-form').submit(function(e) {
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", "{{ login_form.csrf_token._value() }}");
            }
        }
    });
    $.ajax({
        type: 'POST',
        url: "/login",
        data: $('#login-form').serialize(),
        success: function(data, status, xhr) {
            if (data.success == false) {
                // ログイン失敗
                createResultMessage(data.message);
                loginModal.classList.add('hidden');
                setTimeout(() => {
                    resultModal.classList.remove('hidden');
                }, 200)
            } else if (data.success) {
                // ログイン成功
                window.location.reload();
            }
        }
    });
    e.preventDefault();
});

function createResultMessage(message) {
    var resultModalBody = document.getElementById('result-modal__body');
    while(resultModalBody.firstChild) {
        resultModalBody.removeChild(resultModalBody.firstChild);
    }
    var p = document.createElement('p');
    p.textContent = message;
    resultModalBody.appendChild(p);
}
