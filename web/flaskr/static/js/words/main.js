var rows = {}

function update(wordId) {
    var textId = 'text-' + wordId;
    var commentId = 'comment-' + wordId;
    var btnId = 'btn-' + wordId;
    
    var textElm = document.getElementById(textId);
    var commentElm = document.getElementById(commentId);
    var btnElm = document.getElementById(btnId);
    
    var text = textElm.textContent.trim();
    var comment = commentElm.textContent.trim();
    rows[wordId] = {"text": text, "comment": comment};
    
    textElm.innerHTML ='<input id="update-' + textId + '" type="text" value="' + text + '">';
    commentElm.innerHTML ='<input id="update-' + commentId + '" type="text" value="' + comment + '">';
    btnElm.innerHTML = '<button class="upd-btn" onclick="complete(\'' + wordId + '\')">完了</button>';
};

function complete(wordId) {
    var textId = 'text-' + wordId;
    var commentId = 'comment-' + wordId;
    var btnId = 'btn-' + wordId;
    var updTextElm = document.getElementById('update-' + textId);
    var updCommentElm = document.getElementById('update-' + commentId);
    var updText = updTextElm.value.trim();
    var updComment = updCommentElm.value.trim();
    
    var textElm = document.getElementById(textId);
    var commentElm = document.getElementById(commentId);
    var btnElm = document.getElementById(btnId);
    if (rows[wordId]['text'] == updText && rows[wordId]['comment'] == updComment) {
        textElm.innerHTML = '<span>' + updText + '</span>';
        commentElm.innerHTML = '<span>' + updComment + '</span>';
        btnElm.innerHTML = '<button class="upd-btn" onclick="update(\'' + wordId + '\');return false;">編集</button>';
        return;
    };

    textElm.innerHTML = '<span>' + updText + '</span>';
    commentElm.innerHTML = '<span>' + updComment + '</span>';
    btnElm.innerHTML = '<button class="upd-btn" onclick="update(\'' + wordId + '\');return false;">編集</button>';

    data = {
        'id': wordId,
        'book_id': bookId,
        'text': updText,
        'comment': updComment,
    }
    execPost(data);
};

function execPost(data) {
    var form = document.createElement("form");
    form.setAttribute("action", "/update_word");
    form.setAttribute("method", "post");
    form.style.display = "none";
    document.body.appendChild(form);
    if (data !== undefined) {
        for (var paramName in data) {
            var input = document.createElement('input');
            input.setAttribute('type', 'hidden');
            input.setAttribute('name', paramName);
            input.setAttribute('value', data[paramName]);
            form.appendChild(input);
        }
    }
    form.submit();
};