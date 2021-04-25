'use strict';
{
  const modal = document.getElementById('modal');
  const mask = document.getElementById('mask');
  const close = document.getElementById('close');

  mask.addEventListener('click', function () {
    modal.classList.add('hidden');
    mask.classList.add('hidden');
  });

  close.addEventListener('click', function () {
    modal.classList.add('hidden');
    mask.classList.add('hidden');
  });


};

function changeMode(book_id, mode_num) {
    var data = {"book_id": book_id, "mode_num": mode_num};
    $.ajax({
        url: '/change_mode',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data)
    }).done(function(data) {
        return;
    }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
        return;
    })
    const modal = document.getElementById('modal');
    const mask = document.getElementById('mask');
    setTimeout(() => {
        modal.classList.add('hidden');
        mask.classList.add('hidden');
    }, 500);
};

function changeOnclickFunction(book_id) {
    modal.classList.remove('hidden');
    mask.classList.remove('hidden');
    var eazyBtn = document.getElementById('mode_eazy');
    var normalBtn = document.getElementById('mode_normal');
    var hardBtn = document.getElementById('mode_hard');

    eazyBtn.onclick = function(){changeMode(book_id, 0)};
    normalBtn.onclick = function(){changeMode(book_id, 1)};
    hardBtn.onclick = function(){changeMode(book_id, 2)};
};


