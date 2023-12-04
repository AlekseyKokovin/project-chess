import sqlite3
import sys
from copy import deepcopy

from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QPushButton


# поменять размер - self.pixmap = self.pixmap.scaled(150, 150, Qt.KeepAspectRatio)

class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 675, 715)

        self.field_label = QLabel(self)
        self.field_pixmap = QPixmap('файлы проекта/шахматная доска.jpg')
        self.field_label.setPixmap(self.field_pixmap)
        self.field_label.resize(self.field_pixmap.size())
        self.field_label.move(10, 50)

        selected_figure_image = QImage('файлы проекта/selected_figure.png')
        selected_figure_pixmap = QPixmap(selected_figure_image)
        self.selected_figure_label = QLabel(self)
        self.selected_figure_label.setPixmap(selected_figure_pixmap)
        self.selected_figure_label.resize(selected_figure_pixmap.size())

        self.do_paint = False
        self.print_change_flag = False
        self.repaint_selected_figure_flag = False

        self.white_color = QRadioButton(self)
        self.white_color.move(250, 10)
        self.white_color.setText('Белые')

        self.black_color = QRadioButton(self)
        self.black_color.move(325, 10)
        self.black_color.setText('Черные')

        self.start_game = QPushButton(self)
        self.start_game.move(425, 10)
        self.start_game.resize(100, 30)
        self.start_game.setText('Начало игры')
        self.start_game.clicked.connect(self.unitUi)

        self.figures = {}
        i_name = 'белый '
        for i in ['figures_white', 'figures_black']:
            for j in ['конь', 'пешка', 'слон', 'король', 'королева', 'ладья']:
                link = sqlite3.connect('файлы проекта/шахматы/chess.db').cursor().execute(
                    f"""SELECT link FROM {i} WHERE name = '{j}'""").fetchone()
                all_the_labels = []
                for time in range(8 if j == 'пешка' else 1 if j == 'король' or j == 'королева' else 2):
                    pic_pixmap = QPixmap(link[0])
                    pic_pixmap = pic_pixmap.scaled(70, 70, Qt.KeepAspectRatio)
                    pic_label = QLabel(self)
                    pic_label.resize(pic_pixmap.size())
                    pic_label.setPixmap(pic_pixmap)
                    pic_label.move(100, 100)
                    pic_label.hide()
                    all_the_labels.append(pic_label)
                self.figures[i_name + j] = all_the_labels
            i_name = 'черный '

        self.white_color.click()

    def mousePressEvent(self, event):
        if 28 <= event.x() <= 647 and 66 <= event.y() <= 687:
            self.clicked_coords = self.get_possition(event.x(), event.y())
            self.loop.exit(0)

    def wait_for_click(self):
        self.loop = QEventLoop(self)  # Используйте exit вместо quit
        self.loop.exec_()

    def get_possition(self, x, y):
        return (y - 66) // 79, (x - 28) // 78

    def paintEvent(self, event):
        if self.do_paint:
            self.print_board(self.board)
            self.do_paint = False
        if self.print_change_flag:
            self.print_change(self.moves_for_figure)
            self.print_change_flag = False
        if self.repaint_selected_figure_flag:
            self.repaint_selected_figure(self.y_selected_figure, self.x_selected_figure)
            self.repaint_selected_figure_flag = False

    def print_board(self, board):
        for i in self.figures:
            for j in self.figures[i]:
                j.hide()
        for y in range(len(board.field_layout)):
            for x in range(len(board.field_layout[y])):
                if board.field_layout[y][x]:
                    try:
                        self.figures[board.field_layout[y][x].figure()][
                            board.field_layout[y][x].number_of_figure].show()
                        self.figures[board.field_layout[y][x].figure()][board.field_layout[y][x].number_of_figure].move(
                            28 + x * 77, 66 + y * 78)
                    except Exception:
                        self.figures[board.field_layout[y][x].figure()][0].show()
                        self.figures[board.field_layout[y][x].figure()][0].move(28 + x * 77, 66 + y * 78)

    def print_change(self, moves):
        self.green_image_image = QImage('файлы проекта/green_image.png')
        self.green_image_pixmap = QPixmap(self.green_image_image)

        self.red_image_image = QImage('файлы проекта/red_image.png')
        self.red_image_pixmap = QPixmap(self.red_image_image)

        self.labels_for_print_change = []
        for i in range(len(moves)):
            y, x = moves[i]
            label = QLabel(self)
            if self.board.field_layout[y][x]:
                label.setPixmap(self.red_image_pixmap)
                label.resize(self.red_image_pixmap.size())
            else:
                label.setPixmap(self.green_image_pixmap)
                label.resize(self.green_image_pixmap.size())
            label.show()
            label.move(28 + x * 77, 66 + y * 78)
            self.labels_for_print_change.append(label)

    def clear_labels_after_change(self):
        for i in self.labels_for_print_change:
            i.hide()

    def repaint_selected_figure(self, y, x):
        self.selected_figure_label.show()
        self.selected_figure_label.move(28 + x * 77, 66 + y * 78)

    def unitUi(self):
        self.cost = {'пешка': 10, 'конь': 30, 'слон': 30, 'ладья': 50, 'королева': 90, 'король': 0}

        def minimax(board, depth, max_min):
            board.mat(*board.king('белый'), 'белый')
            board.mat(*board.king('черный'), 'черный')
            if depth == 0 or board.game_over:
                value = 0
                for j in board.field_layout:
                    for i in j:
                        if i and i.figure().split()[0] == self.opposite_color:
                            value -= self.cost[i.figure().split()[1]]
                        elif i:
                            value -= self.cost[i.figure().split()[1]]
                return value
            board1 = deepcopy(board)
            possible_moves = board.possible_moves_team(self.opposite_color)
            if max_min:
                max_value = float('inf')
                for move in possible_moves:
                    if board.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                        board.move(*move, type_of_figure='королева')
                    else:
                        board.move(*move)
                    num = minimax(board, depth - 1, False)
                    board = deepcopy(board1)
                    max_value = max(num, max_value)
                return max_value
            else:
                min_value = float('inf')
                for move in possible_moves:
                    if board.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                        board.move(*move, type_of_figure='королева')
                    else:
                        board.move(*move)
                    num = minimax(board, depth - 1, True)
                    board = deepcopy(board1)
                    min_value = min(num, min_value)
                return min_value

        def best_move(board):
            possible_moves = board.possible_moves_team(self.opposite_color)
            board1 = deepcopy(board)
            best_move = ''
            best_num = -1000000000000000000000000000
            for move in possible_moves:
                if board.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                    board.move(*move, type_of_figure='королева')
                else:
                    board.move(*move)
                num = minimax(board, 1, False)
                board = deepcopy(board1)
                if num > best_num:
                    best_num = num
                    best_move = move
            return best_move

        def get_person_move():
            self.clicked_coords = None
            self.wait_for_click()
            y, x = self.clicked_coords
            if self.num_of_clicks == 0:
                while (self.board.field_layout[y][x] and self.board.field_layout[y][x].figure().split()[0]
                       == self.opposite_color and self.board.field_layout[y][x].get_moves()):
                    if self.board.field_layout[y][x].figure().split()[0] != self.opposite_color:
                        self.repaint_selected_figure_flag = True
                        self.y_selected_figure, self.x_selected_figure = y, x
                        self.repaint()
                    else:
                        self.statusBar().showMessage('Неправильная фигура', 100)
                    self.wait_for_click()
                    y, x = self.clicked_coords
                self.repaint_selected_figure_flag = True
                self.y_selected_figure, self.x_selected_figure = y, x
                self.repaint()
                self.statusBar().showMessage('', 100)
                self.moves_for_figure = self.board.field_layout[y][x].get_moves(self.board.field_layout, y, x)
                self.print_change_flag = True
                self.repaint()
                return y, x, 1
            while (y, x) not in self.moves_for_figure:
                if (self.board.field_layout[y][x] and self.board.field_layout[y][x].figure().split()[0]
                        != self.opposite_color):

                self.wait_for_click()
                y, x = self.clicked_coords
            self.clear_labels_after_change()
            return y, x

        def main():
            self.start_game.setEnabled(False)
            if self.white_color.isChecked():
                color_first = 'белый'
                color_second = 'черный'
            else:
                color_first = 'черный'
                color_second = 'белый'
            self.opposite_color = color_second
            self.white_color.setEnabled(False)
            self.black_color.setEnabled(False)
            # основной код
            self.board = Board(color_first, color_second)
            while True:
                flag = True
                self.do_paint = True
                self.repaint()
                while flag:
                    self.num_of_clicks = 0
                    while self.num_of_clicks == 0:
                        y, x, self.num_of_clicks = get_person_move()
                    move, flag = get_person_move()
                self.board.move(y, x, *move)
                if self.board.mat(*self.board.king(self.opposite_color), self.opposite_color):
                    break
                self.do_paint = True
                self.repaint()
                move_bot = best_move(self.board)
                self.board.move(*move_bot)
                self.do_paint = True
                self.repaint()
            # разблокирование всех кнопок
            self.white_color.setEnabled(True)
            self.black_color.setEnabled(True)
            self.start_game.setEnabled(True)

        class Board:
            def __init__(self, first_color, second_color):
                self.game_over = False
                self.field_layout = []
                for row in range(8):
                    self.field_layout.append([None] * 8)
                self.field_layout[0] = [
                    Rook(first_color, 0), Knight(first_color, 0), Bishop(first_color, 0), Queen(first_color),
                    King(first_color), Bishop(first_color, 1), Knight(first_color, 1), Rook(first_color, 1)
                ]
                self.field_layout[1] = [
                    Pawn(first_color, 0), Pawn(first_color, 1), Pawn(first_color, 2), Pawn(first_color, 3),
                    Pawn(first_color, 4), Pawn(first_color, 5), Pawn(first_color, 6), Pawn(first_color, 7)
                ]
                self.field_layout[6] = [
                    Pawn(second_color, 0), Pawn(second_color, 1), Pawn(second_color, 2), Pawn(second_color, 3),
                    Pawn(second_color, 4), Pawn(second_color, 5), Pawn(second_color, 6), Pawn(second_color, 7)
                ]
                self.field_layout[7] = [
                    Rook(second_color, 0), Knight(second_color, 0), Bishop(second_color, 0), Queen(second_color),
                    King(second_color), Bishop(second_color, 1), Knight(second_color, 1), Rook(second_color, 1)
                ]

            def king(self, color):
                for y in range(8):
                    for x in range(8):
                        if self.field_layout[y][x] and self.field_layout[y][x].figure() == color + ' ' + 'король':
                            return y, x

            def possible_moves(self, y_now, x_now):
                return_coords = []
                for i in self.field_layout[y_now][x_now].get_moves(self.field_layout, y_now, x_now):
                    self.move(y_now, x_now, i[0], i[1])
                    if not self.shah(self.field_layout[i[0]][i[1]].figure().split()[0]):
                        j = (y_now, x_now, i[0], i[1])
                        return_coords.append(i)
                    self.move(i[0], i[1], y_now, x_now)
                return return_coords

            def mat(self, y_king, x_king, color):
                if color == 'черный':
                    color = 'белый'
                elif color == 'белыц':
                    color = 'черный'
                moves = self.possible_moves_team(color, True)
                list_of_hits = []
                for y in range(y_king - 1, y_king + 1):
                    for x in range(x_king - 1, x_king + 1):
                        if 0 <= y <= 7 and 0 <= x <= 7:
                            list_of_hits.append((y, x) in (moves[2], moves[3]))
                if all(list_of_hits):
                    self.game_over = True
                return all(list_of_hits)

            def shah(self, color):
                if color == 'черный':
                    color = 'белый'
                elif color == 'белыц':
                    color = 'черный'
                possible_moves_of = self.possible_moves_team(color, flag=True)
                return any([self.field_layout[i[2]][i[3]].figure().split()[1] == 'король' for i in possible_moves_of])

            def possible_moves_team(self, color, flag=False):
                all_possible_moves = []
                for y in range(len(self.field_layout)):
                    for x in range(len(self.field_layout[y])):
                        if self.field_layout[y][x] and self.field_layout[y][x].figure().split()[0] == color:
                            all_possible_moves.extend(
                                [(y, x) + j for j in self.field_layout[y][x].get_moves(self.field_layout, y, x) if
                                 self.field_layout[y][x].figure().split()[1] != 'король' or flag])
                return all_possible_moves

            def move(self, y_now, x_now, y_to, x_to, type_of_figure=None):
                if type_of_figure:
                    if type_of_figure.lower() == 'ладья':
                        self.field_layout[y_to][x_to] = Rook(self.field_layout[y_now][x_now].figure().split()[0])
                    elif type_of_figure.lower() == 'королева':
                        self.field_layout[y_to][x_to] = Queen(self.field_layout[y_now][x_now].figure().split()[0])
                    elif type_of_figure.lower() == 'слон':
                        self.field_layout[y_to][x_to] = Bishop(self.field_layout[y_now][x_now].figure().split()[0])
                    elif type_of_figure.lower() == 'конь':
                        self.field_layout[y_to][x_to] = Knight(self.field_layout[y_now][x_now].figure().split()[0])
                    elif type_of_figure.lower() == 'пешка' and y_now > y_to:
                        self.field_layout[y_to][x_to] = Pawn(self.field_layout[y_now][x_now].figure().split()[0])
                    self.field_layout[y_now][x_now] = None
                    return True
                self.field_layout[y_now][x_now], self.field_layout[y_to][x_to] = None, self.field_layout[y_now][x_now]
                if self.field_layout[y_to][x_to].figure().split()[1] == 'король' and abs(
                        x_to - x_now) == 2 and y_now - y_to == 0:
                    if x_to - x_now == -2:
                        self.field_layout[y_now][x_now - 4], self.field_layout[y_to][x_to + 1] = None, \
                            self.field_layout[y_now][x_now - 4]
                    else:
                        self.field_layout[y_now][x_now + 3], self.field_layout[y_to][x_to - 1] = None, \
                            self.field_layout[y_now][x_now + 3]
                try:
                    self.field_layout[y_now][x_now].moved()
                except Exception:
                    pass

        class Bishop:
            def __init__(self, color, n):
                self.number_of_figure = n
                self.color = color

            def figure(self):
                return f"{self.color} слон"

            def get_moves(self, board, y_now, x_now):
                moves_possible = []
                for y in range(y_now + 1, 8):
                    for x in range(x_now + 1, 8):
                        if board[y][x] and board[y][x].figure().split()[1] == 'король':
                            break
                        elif board[y][x] and board[y][x].figure().split()[0] != self.color:
                            moves_possible.append((y, x))
                            break
                        else:
                            moves_possible.append((y, x))
                    for x in range(x_now - 1, -1):
                        if board[y][x] and board[y][x].figure().split()[1] == 'король':
                            break
                        elif board[y][x] and board[y][x].figure().split()[0] != self.color:
                            moves_possible.append((y, x))
                            break
                        else:
                            moves_possible.append((y, x))
                for y in range(y_now - 1, -1):
                    for x in range(x_now + 1, 8):
                        if board[y][x] and board[y][x].figure().split()[1] == 'король':
                            break
                        elif board[y][x] and board[y][x].figure().split()[0] != self.color:
                            moves_possible.append((y, x))
                            break
                        else:
                            moves_possible.append((y, x))
                    for x in range(x_now, -1):
                        if board[y][x] and board[y][x].figure().split()[1] == 'король':
                            break
                        elif board[y][x] and board[y][x].figure().split()[0] != self.color:
                            moves_possible.append((y, x))
                            break
                        else:
                            moves_possible.append((y, x))
                return moves_possible

        class Pawn:
            def __init__(self, color, n):
                self.number_of_figure = n
                self.color = color
                if color == 'черный':
                    self.default_position_y = 6
                else:
                    self.default_position_y = 1

            def figure(self):
                return f"{self.color} пешка"

            def get_moves(self, board, y_now, x_now):
                if self.color == 'черный':
                    change = -1
                elif self.color == 'белый':
                    change = 1
                check_places = [(y_now + change, x_now), (y_now + change, x_now + 1), (y_now + change, x_now - 1)]
                if y_now == self.default_position_y:
                    check_places.append((y_now + 2 * change, x_now))
                moves_possible = []
                flag_found_plus_two = False
                for i in check_places:
                    y, x = i
                    if self.check_numbers(y, x):
                        if x != x_now and board[y][x] and board[y][x].figure().split()[0] != self.color and \
                                board[y][x].figure().split()[1] != 'король':
                            moves_possible.append((y, x))
                        elif x != x_now:
                            continue
                        if x == x_now and board[y][x]:
                            flag_found_plus_two = True
                        elif not flag_found_plus_two:
                            moves_possible.append((y, x))
                return moves_possible

            def check_numbers(self, y, x):
                return 0 <= x <= 7 and 0 <= y <= 7

        class Rook:
            def __init__(self, color, n):
                self.number_of_figure = n
                self.color = color
                self.moves = 0

            def moved(self):
                self.moves += 1

            def figure(self):
                return f"{self.color} ладья"

            def get_moves(self, board, y_now, x_now):
                moves_possible = []
                for y in range(y_now - 1, -1):
                    if board[y][x_now] and board[y][x_now].figure().split()[1] == 'король':
                        break
                    elif board[y][x_now] and board[y][x_now].figure().split()[0] != self.color:
                        moves_possible.append((y, x_now))
                        break
                    else:
                        moves_possible.append((y, x_now))
                for y in range(y_now + 1, 8):
                    if board[y][x_now] and board[y][x_now].figure().split()[1] == 'король':
                        break
                    elif board[y][x_now] and board[y][x_now].figure().split()[0] != self.color:
                        moves_possible.append((y, x_now))
                        break
                    else:
                        moves_possible.append((y, x_now))
                for x in range(x_now + 1, 8):
                    if board[y_now][x] and board[y_now][x].figure().split()[1] == 'король':
                        break
                    elif board[y_now][x] and board[y_now][x].figure().split()[0] != self.color:
                        moves_possible.append((y_now, x))
                        break
                    else:
                        moves_possible.append((y_now, x))
                for x in range(x_now - 1, -1):
                    if board[y_now][x] and board[y_now][x].figure().split()[1] == 'король':
                        break
                    elif board[y_now][x] and board[y_now][x].figure().split()[0] != self.color:
                        moves_possible.append((y_now, x))
                        break
                    else:
                        moves_possible.append((y_now, x))
                return moves_possible

        class Knight:
            def __init__(self, color, n):
                self.number_of_figure = n
                self.color = color

            def figure(self):
                return f"{self.color} конь"

            def get_moves(self, board, y_now, x_now):
                coordinates = [(y_now + 2, x_now + 1), (y_now + 2, x_now - 1), (y_now - 2, x_now + 1),
                               (y_now - 2, x_now - 1), (y_now + 1, x_now + 2), (y_now + 1, x_now - 2),
                               (y_now - 1, x_now + 2), (y_now - 1, x_now - 2)]
                move_possible = []
                for i in coordinates:
                    y, x = i
                    if self.check_numbers(y, x) and (board[y][x] and board[y][x].figure().split()[1] == 'король' and
                                                     board[y_now][x].figure().split()[0] != self.color):
                        move_possible.append((y, x))
                return move_possible

            def check_numbers(self, y, x):
                return 0 <= x <= 7 and 0 <= y <= 7

        class King:
            def __init__(self, color):
                self.color = color
                self.moves = 0

            def moved(self):
                self.moves += 1

            def figure(self):
                return f"{self.color} король"

            def get_moves(self, board, y_now, x_now, coords_not_allowed=None):
                if coords_not_allowed is None:
                    coords_not_allowed = []
                moves_possible = []
                # рокировка
                if self.moves == 0 and board[y_now][x_now - 4] and board[y_now][x_now - 4].figure().split()[
                    1] == 'ладья' and board[y_now][x_now - 4].moves == 0 and not board[y_now][x_now - 1] and not \
                        board[y_now][x_now - 2] and not board[y_now][x_now - 3]:
                    moves_possible.append((y_now, x_now - 4))
                if self.moves == 0 and board[y_now][x_now + 3] and board[y_now][x_now + 3].figure().split()[
                    1] == 'ладья' and board[y_now][x_now + 3].moves == 0 and not board[y_now][x_now + 1] and not \
                        board[y_now][x_now + 2]:
                    moves_possible.append((y_now, x_now + 3))
                for y in range(y_now - 1, y_now + 2):
                    for x in range(x_now - 1, x_now + 2):
                        if x != x_now and y != y_now and self.check_numbers(y, x):
                            flag = True
                            for y_ in range(y - 1, y + 2):
                                for x_ in range(x - 1, x + 2):
                                    if board[y_][x_] and board[y_][x_].figure().split()[1] != 'король':
                                        flag = False
                                        break
                                if not flag:
                                    break
                            if flag and (y, x) not in coords_not_allowed:
                                if board[y][x]:
                                    if board[y][x].figure().split()[0] != self.color:
                                        moves_possible.append((y, x))
                                else:
                                    moves_possible.append((y, x))
                return moves_possible

            def check_numbers(self, y, x):
                return 0 <= x <= 7 and 0 <= y <= 7

        class Queen:
            def __init__(self, color):
                self.color = color

            def figure(self):
                return f"{self.color} королева"

            def get_moves(self, board, y_now, x_now):
                for i in board:
                    for j in i:
                        if not j:
                            continue
                        if j.figure().split()[1] == 'слон' and j.figure().split()[0] == \
                                board[y_now][x_now].figure().split()[0]:
                            first = j
                        if j.figure().split()[1] == 'ладья' and j.figure().split()[0] == \
                                board[y_now][x_now].figure().split()[0]:
                            second = j
                return first.get_moves(board, y_now, x_now) + second.get_moves(board, y_now, x_now)

        main()

    def show_figures(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
