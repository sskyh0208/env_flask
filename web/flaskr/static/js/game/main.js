var game = null;

if (mode == 0) {
    // Eazyモード
    game = new Game(words);
} else if (mode == 1) {
    // Normalモード
    game = new NormalGame(words);
} else {
    // Hardモード
    game = new HardGame(words);
}
game.startGame();

document.addEventListener('keydown', function(e){
    if (!game.gameOver) {
        game.typed(e);
        if (game.gameOver) {
            document.removeEventListener('keydown', function(e){});
            // 最後の文字を表示させてから
            setTimeout(() => {
                game.endGame();
            }, 300);
        }
    }
});