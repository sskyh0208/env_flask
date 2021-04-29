'use strict';
{
  const loginOpen = document.getElementById('login-open');
  const loginClose = document.getElementById('login-close');
  const loginModal = document.getElementById('login-modal');
  const loginMask = document.getElementById('login-mask');

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
  });
}