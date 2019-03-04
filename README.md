# Blind Checkers

Not uploaded yet.

This repository is related to the final project of Computational Modeling class in Seoul National University. The goal of the project is to create an artificial intelligence of "Blind Checkers" to be explained.

The Blind Checkers is a variation of the Checkers. It is almost similar to international Checkers, except you cannot see all of your opponents. More precisely, each piece in Blind Checkers has own field of view, and you cannot see anything out of sight. Therefore, not only catching opponent pieces but securing a broad view will be an important strategy.

You can adjust the detailed rules of the game: the size of Checkers board, the sight of uncrowned pieces, the sight of kings, the attack range of kings (If this is set to 1, the only difference between kings and uncrowned pieces is that kings can go backwards. If this is set to the board size, kings become flying kings.), whether you should catch piece when possible, and whether uncrowned pieces can catch backwards. By default, 10x10 board is used, two spaces of view for both uncrowned pieces and kings (It means that 5x5 box centered at each piece is visible.), kings can go at most two spaces (In practice, flying kings are too strong in Blind Checkers), and both mandatory catch rule and backward catch rule are used. Also for easy implementation, any catched pieces are removed from the board immediately. (In international Checkers, catched pieces are removed after each turn.)

The implementation is done with pygame, so you should install pygame to 
