# M@rio+
### CSCI 319 Final Project

## Project Authors
Armando Mendez, Will Xue


## Project Game Information

Attach two controllers and run `python3 main.py`. Requires python and pygame 

Game menu will be displayed with three game modes and a quit button. Use the 'select' button to choose an option. Whenever a game is completed, either a player has won or been killed, a screen will display either Game over or the winner, along with options to replay, return to menu, or quit game. 


### Control Scheme -
**KEYBOARD** - 
Only intended to be used in *single player* mode, but can be used to control both players in either the *two-player* or *gun game* modes. 

Keyboard controls consist of the basic arrowkey movements Left/Right/Up. When in gun game, the *space button* may be used to shoot bullets, and the *1* / *2* number buttons can be used to switch guns.

**CONTROLS** (provided by professor Matthews) - 
Can be used in all game modes. ***Controls must be plugged in before running program***

The control *arrow pad* is used for standard Left/Right movments
The control *B-Button* is used for jumping
The control *Select* button is used for selecting options in the menu
The control *Start* button is used for pausing in game

- **Gun Game Only** -
The control *Back-Right* button is used to shoot gun 
The control *Back-Left* button is used to switch gun 

### Game Modes - 

**Single Player** - 
Based off the original Super Mario Bros. 
Try to reach the end of the world without dying! Players can die from falling off the map and running into enemies like goombas.

**Two Player** - 
Identical to single player, with the addiition of a split screen allowing two player to play simultaniously, on diffrent portions of the map.
When the end is reached a player is decleared as the winner.

**Gun Game** - 
Fight to the death! Each player has access to a rocket launcher and an AK47. The rocket launcher deals much more damage, but also takes longer to reload and is slower, while the AK47 shoots and reloads faster but deals less damage. Player health is shown at the top!

### Known Bugs 
- Glitch through corners of blocks 
It seemes that when the player collides with the edge of a block (and this can be a block in between blocks) in just the right position, the player will either fall through or be pushed up. Sometimes players will glitch into walls or the floor. If that happens try to kill the player and select `replay`, and if that doesn't work press `M` on the keyboard to go to the main menu and restart. 


