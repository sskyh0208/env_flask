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
        this.typeSuccessCountSpan = document.getElementById('success');
        // 失敗回数表示用spanタグ
        this.typeMissCountSpan = document.getElementById('failed');
        // タイプ中の単語の文字列を格納のする配列
        this.checkTexts = [];
        // 表示用・登録用スコアの辞書を入れる配列
        this.scoreWords = [];
        // 初期化
        this.typingWord = '';
        // タイプ中の単語をスコア登録するための辞書
        this.typeWordScore = {}
        // タイプ成功した単語のカウント
        this.totalTypeSuccessCount = 0;
        // 全単語の総ミスカウント
        this.totalTypeMissCount = 0;
        // タイプ中の単語のミスカウント
        this.typeMissCount = 0;

        this.typeSuccessCountSpan.textContent = this.totalTypeSuccessCount;
        this.typeMissCountSpan.textContent = this.totalTypeMissCount;
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
        this.p.remove();
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
        
        
        if (this.totalTypeMissCount > 0) {
            this.h1.textContent = 'よく間違えた単語';
            // ミスタイプ表のヘッダー作成。
            var header = this.generateMissTypeTableHeader()
            div.appendChild(header);
            
            // ミス回数を降順ソート
            this.scoreSortDesc()
            
            // 10行までしか表示しない
            var rowNum = this.scoreWords.length;
            if (rowNum > 10) {
                rowNum = 10;
            }
            
            // ミスタイプ表の作成
            for (var i = 0; i < rowNum; i++) {
                var row = this.generateMissTypeTableRow(i);
                div.appendChild(row);
            }
            
            
        } else {
            this.h1.textContent = 'パーフェクト！';
        }
        
        var links = this.generateMissTypeTableLinks();
        result.appendChild(links);
    }
    
    // スコアを降順にソート
    scoreSortDesc() {
        this.scoreWords.sort(function(a, b) {
            if(a.totalCount < b.totalCount) return 1;
            if(a.totalCount > b.totalCount) return -1;
            return 0;
        });
    }

    // 最後のスコアテーブルのヘッダー部作成
    generateMissTypeTableHeader() {
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
        return h_dl
    }

    // 最後のスコアテーブルの行を作成
    generateMissTypeTableRow(i) {
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
        dd2.textContent = this.scoreWords[i].totalCount;
        
        // 子要素にぶち込む
        dl.appendChild(dt);
        dl.appendChild(dd1);
        dl.appendChild(dd2);
        return dl
    }

    // 最後のスコアテーブルのリンク部を作成
    generateMissTypeTableLinks() {
        var div = document.createElement('div');
        div.classList.add('result__links');
        // もう一度りんく挿入
        var replay = document.createElement('a');
        replay.id = 'replay-btn';
        replay.classList.add('m-btn');
        replay.classList.add('app-btn');
        replay.textContent = 'もう一度';
        replay.href = '/game/' + this.book_id;
        div.appendChild(replay)
        
        // スコアリンク挿入
        var scores = document.createElement('a');
        scores.id = 'scores-btn';
        scores.classList.add('m-btn');
        scores.classList.add('app-btn');
        scores.textContent = 'スコア';
        scores.href = '/score/' + this.book_id;
        div.appendChild(scores)
        // 戻るリンク挿入
        var back = document.createElement('a');
        back.id = 'back-btn';
        back.classList.add('m-btn');
        back.classList.add('app-btn');
        back.textContent = 'もどる';
        back.href = '/books';
        div.appendChild(back)
        return div
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
        this.typeWordScore = {"book_id": this.book_id, "word_id": this.words[0].id, "text": this.words[0].text, "comment": this.words[0].comment, "count": 0, "totalCount": 0};
        // spanを作り、一文字ずつspanに入れる
        var splitWord = this.words[0].text.split('');
        for (var i = 0; i < splitWord.length; i++) {
            var span = this.generateSpan(splitWord[i]);
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
            this.typeSuccess();
        // タイプミス判定
        } else {
            this.typeMiss();
        }
    }

    // タイプ成功した文字のスタイルを変化
    checkTextsTransform() {
        this.checkTexts[0].className = 'add-blue';
    }

    // 次の単語確認
    nextWordCheck() {
        // スコア辞書を配列に格納
        if (this.typeWordScore['count']) {
            this.scoreWords.push(this.typeWordScore);
        }
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
    
    // タイプ成功
    typeSuccess() {
        this.totalTypeSuccessCount ++;
        this.checkTextsTransform()
        // タイプ文字列の削除
        this.checkTexts.shift();
        // タイプ文字列が存在しなくなったら、次のワード作成へ
        if(!this.checkTexts.length) {
            // 成功カウントを1増やす
            this.typeSuccessCountSpan.textContent ++;
            // タイプミスが1以上ならスコアに登録
            if (this.typeMissCount) {
                this.typeWordScore['count'] = 1;
            }
            // タイプミスカウントを0にする
            this.typeMissCount = 0;
            // 表示しているミスカウントを0にする
            this.typeMissCountSpan.textContent = 0;
            this.nextWordCheck()
        }
    }

    // タイプ失敗
    typeMiss() {
        this.totalTypeMissCount ++;
        this.typeMissCount ++;
        this.typeMissCountSpan.textContent ++;
        this.typeWordScore['totalCount'] ++;
    }
}

class NormalGame extends Game {
    // 初期状態が非表示のspanタグ作成
    generateSpan(char) {
        var span = document.createElement('span');
        span.textContent = char;
        // 非表示にする
        span.style.visibility = 'hidden';
        return span;
    }

    // タイプ成功した文字のスタイルを変化
    checkTextsTransform() {
        super.checkTextsTransform();
        // 表示させる
        this.checkTexts[0].style.visibility = 'visible';
    }
}

class HardGame extends NormalGame {
    // 間違えると即座に次の単語へ進む
    typeMiss() {
        super.typeMiss();
        this.checkTexts = [];
        // スコア辞書を配列に格納
        this.scoreWords.push(this.typeWordScore);
        // ワードの削除
        this.words.shift();
        // 残りのワード数が0だったらゲーム終了
        if (!this.words.length) {
            this.endGame();
        // 残りのワード数が0じゃなったら続行
        } else {
            this.createText();
        }
    }
}
