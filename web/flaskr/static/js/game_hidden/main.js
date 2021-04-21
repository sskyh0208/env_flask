var game = new Game(words);
game.startGame();

document.addEventListener('keydown', function(e){
    if (!game.gameOver) {
        game.typed(e);
        if (game.gameOver) {
            document.removeEventListener('keydown', function(e){});
            // 最後の文字を
            setTimeout(() => {
                game.endGame();
            }, 300);
        }
    }
});