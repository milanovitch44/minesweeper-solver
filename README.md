# minesweeper-solver

This project is a Python Minesweeper solver that uses set-based logic to deduce safe tiles and bomb locations. I made this project in my free time. For each revealed tile, the solver builds sets of unknown neighboring tiles and tracks how many bombs must be among them. It then combines and simplifies these sets, looking for overlaps and contradictions. When a set’s size matches the number of bombs it must contain, the solver can safely flag all tiles in that set as bombs, or open them if they must be safe. This approach allows the solver to quickly solve complex boards.

![minesweeper_demo-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/bd45f168-3c59-411a-944b-3b2431867b53)
