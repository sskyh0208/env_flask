class Game {
    constructor(words) {
        this.words = words;
        
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
        this.successCount = 0;
        this.failedCount = 0;

        this.success.textContent = this.successCount;
        this.failed.textContent = this.failedCount;
    };

    // ゲーム開始
    startGame() {
        words = this.shuffle(words);
        this.createText();
    }
    
    // ゲーム終了
    endGame(){
        this.gameOver = true;
        this.p.textContent = '';
        this.h1.textContent = '終了！！！';
    };

    // タイピング文字列の順番をシャッフル
    shuffle(array) {
        for (var i = (array.length - 1); 0 < i; i--) {
            var r = Math.floor(Math.random() * (i + 1));
            [array[i], array[r]] = [array[r], array[i]];
        }
        return array;
    };

    // タイピング用文字列作成
    createText() {
        // 前回の文字列を消す。
        this.p.textContent = '';
        this.h1.textContent = '';
        // コメントを変える
        this.h1.textContent = this.words[0].comment;
        // spanを作り、一文字ずつspanに入れる
        var splitWord = this.words[0].text.split('');
        for (var i = 0; i < splitWord.length; i++) {
            var span = this.generateSpan(splitWord[i]);
            // pタグ子要素にする
            this.p.appendChild(span);
            // チェック用配列に入れる
            this.checkTexts.push(span);
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
            this.successCount ++;
            this.success.textContent = this.successCount;
            
            // タイプ文字列の削除
            this.checkTexts.shift();
            
            // タイプ文字列が存在しなくなったら、次のワード作成へ
            if(!this.checkTexts.length) {
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
        // タイプミス判定
        } else {
            this.failedCount ++;
            this.failed.textContent = this.failedCount;
        }
    }
}
