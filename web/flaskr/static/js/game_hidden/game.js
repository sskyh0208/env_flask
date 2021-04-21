class Game {
    constructor(words) {
        this.words = words;
        this.book_id = words[0].book_id;
        
        this.gameOver = false;

        // タイプ文字列表示用pタグ
        this.p = document.getElementById('text');
        // コメント文字表示用h1タグ
        this.h1 = document.getElementById('comment');
        // 成功回数表示用spanタグ
        this.success = document.getElementById('success');
        // 失敗回数表示用spanタグ
        this.failed = document.getElementById('failed');
        this.checkTexts = [];
        this.scoreWords = [];
        this.typingWord = '';
        this.typeWordScore = {}
        this.successCount = 0;
        this.failedCount = 0;

        this.success.textContent = this.successCount;
        this.failed.textContent = this.failedCount;
    };

    // ゲーム開始
    startGame() {
        this.shuffleWords();
        this.createText();
    }
    
    // ゲーム終了
    endGame(){
        this.deleteTypingContent();
        this.displayScore();
        this.registerScore();
    };
    
    // タイピング文字を消す
    deleteTypingContent() {
        this.p.textContent = '';
        this.h1.textContent = '';
    };

    // スコア表示
    displayScore() {
        // ゲーム中のタイプ判定を削除
        var score = document.getElementById('score');
        while(score.firstChild) {
            score.removeChild(score.firstChild);
        }
        
        
        var result = document.getElementById('result');
        var div = document.createElement('div');
        div.classList.add('result__table')
        result.appendChild(div);
        
        var linkDiv = document.createElement('div');
        linkDiv.classList.add('result__table__link');
        // もう一度リンク挿入
        var replay = document.createElement('a');
        replay.textContent = 'もう一度';
        replay.href = '/game/' + this.book_id;
        linkDiv.appendChild(replay);

        var a_score = document.createElement('a');
        a_score.textContent = 'スコア';
        a_score.href = '/score/' + this.book_id;
        linkDiv.appendChild(a_score);

        // 戻るリンク挿入
        var back = document.createElement('a');
        back.textContent = '戻る';
        back.href = '/books';
        linkDiv.appendChild(back);
        
        div.appendChild(linkDiv);

        if (this.failedCount > 0) {
            this.h1.textContent = 'よく間違えた単語';
            // ミスタイプ票のヘッダー作成。
            var h_dl = document.createElement('dl');
            h_dl.classList.add('result__table__head');
            var h_dt = document.createElement('dt');
            h_dt.textContent = '単語';
            var h_dd1 = document.createElement('dd');
            h_dd1.textContent = '意味';
            var h_dd2 = document.createElement('dd');
            h_dd2.textContent = 'ミス';
            h_dl.appendChild(h_dt);
            h_dl.appendChild(h_dd1);
            h_dl.appendChild(h_dd2);
            div.appendChild(h_dl);
            
            // ミス回数を降順ソート
            this.scoreWords.sort(function(a, b) {
                if(a.count < b.count) return 1;
                if(a.count > b.count) return -1;
                return 0;
            });
            
            // 10行までしか表示しない
            var rowNum = this.scoreWords.length;
            if (rowNum > 10) {
                rowNum = 10;
            }
            // ミスタイプ表の作成
            for (var i = 0; i < rowNum; i++) {
                var dl = document.createElement('dl');
                dl.classList.add('result__table__row');
                // 単語挿入
                var dt = document.createElement('dt');
                dt.textContent = this.scoreWords[i].text;
                // 意味挿入
                var dd1 = document.createElement('dd');
                dd1.textContent = this.scoreWords[i].comment;
                // ミス回数挿入
                var dd2 = document.createElement('dd');
                dd2.textContent = this.scoreWords[i].count;
                
                // 子要素にぶち込む
                dl.appendChild(dt);
                dl.appendChild(dd1);
                dl.appendChild(dd2);
                div.appendChild(dl);
            }
        } else {
            this.h1.textContent = 'パーフェクト！';
        }
    }

    // ゲームスコア登録
    registerScore(){
        $.ajax({
            url: '/game/score',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(this.scoreWords)
        }).done(function(data) {
            return;
        }).fail(function(XMLHttpRequest, textStatus, errorThrown) {
            return;
        })

    }

    // タイピング文字列の順番をシャッフル
    shuffleWords() {
        for (var i = (this.words.length - 1); 0 < i; i--) {
            var r = Math.floor(Math.random() * (i + 1));
            [this.words[i], this.words[r]] = [this.words[r], this.words[i]];
        }
    };

    // タイピング用文字列作成
    createText() {
        // 前回の文字列を消す。
        this.p.textContent = '';
        this.h1.textContent = '';
        // コメントを変える
        this.h1.textContent = this.words[0].comment;
        // スコア用の辞書と、参照用の変数にタイピング中の文字列を入れる
        this.typeWordScore = {"id": this.words[0].id, "text": this.words[0].text, "comment": this.words[0].comment, "count": 0};
        // spanを作り、一文字ずつspanに入れる
        var splitWord = this.words[0].text.split('');
        for (var i = 0; i < splitWord.length; i++) {
            var span = this.generateSpan(splitWord[i]);
            span.style.visibility = 'hidden';
            // pタグ子要素にする
            this.p.appendChild(span);
            // チェック用配列に入れる
            if(splitWord[i] != " ") {
                this.checkTexts.push(span);
            }
        }
    };

    // spanタグ作成
    generateSpan(char) {
        var span = document.createElement('span');
        span.textContent = char;
        return span;
    }

    // タイプ判定
    typed(event){
        // タイプ成功判定
        if(event.key === this.checkTexts[0].textContent) {
            this.checkTexts[0].className = 'add-blue';
            this.checkTexts[0].style.visibility = 'visible';
            
            // タイプ文字列の削除
            this.checkTexts.shift();
            
            // タイプ文字列が存在しなくなったら、次のワード作成へ
            if(!this.checkTexts.length) {
                this.success.textContent ++;
                this.failed.textContent = 0;

                // スコア辞書を配列に格納
                if (this.typeWordScore['count']) {
                    this.scoreWords.push(this.typeWordScore);
                };

                // ワードの削除
                this.words.shift();
                
                // 残りのワード数が0だったらゲーム終了
                if (!this.words.length) {
                    this.gameOver = true;
                } else {
                    // 残りのワード数が0じゃなったら続行
                    setTimeout(() => {
                        this.createText();
                    }, 300);
                }
            }
        // タイプミス判定
        } else {
            this.typeWordScore['count'] ++;
            this.failedCount ++;
            this.failed.textContent ++;
        }
    }
}