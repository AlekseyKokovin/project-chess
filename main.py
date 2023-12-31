import sqlite3
import sys
from copy import deepcopy

from PyQt5.QtCore import Qt, QEventLoop
from PyQt5.QtGui import QPixmap, QImage, QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QRadioButton, QPushButton


# поменять размер - self.pixmap = self.pixmap.scaled(150, 150, Qt.KeepAspectRatio)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(0, 0, 675, 715)
        self.setWindowTitle('Шахматы')
        self.result_text = QLabel(self)
        self.result_text.move(0, 10)

        self.field_label = QLabel(self)
        self.field_pixmap = QPixmap('файлы проекта/шахматная доска.jpg')
        self.field_pixmap = self.field_pixmap.scaled(651, 661, Qt.KeepAspectRatio)
        self.field_label.setPixmap(self.field_pixmap)
        self.field_label.resize(self.field_pixmap.size())
        self.field_label.move(10, 50)

        selected_figure_image = QImage('файлы проекта/selected_figure.png')
        selected_figure_pixmap = QPixmap(selected_figure_image)
        self.selected_figure_label = QLabel(self)
        self.selected_figure_label.setPixmap(selected_figure_pixmap)
        self.selected_figure_label.resize(selected_figure_pixmap.size())
        self.selected_figure_label.hide()

        self.do_paint = False
        self.print_change_flag = False
        self.repaint_selected_figure_flag = False

        self.start_game = QPushButton(self)
        self.start_game.move(300, 10)
        self.start_game.resize(100, 30)
        self.start_game.setText('Начало игры')
        self.start_game.clicked.connect(self.unitUi)

        """Добавление умной оценки позиции фигуры"""
        self.cost = {'пешка': [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
            [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
            [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
            [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
            [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        ], 'конь': [
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
            [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
            [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
            [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
            [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
            [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
            [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
            [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
        ], 'слон': [
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
            [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
            [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
            [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
            [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
            [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
        ], 'ладья': [
            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
            [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
        ], 'королева': [
            [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
            [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
            [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
            [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
            [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
            [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
            [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
        ], 'король': [
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
            [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
            [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
            [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
            [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
        ]}
        """простая оценка фигуры"""
        self.cost_basic = {'пешка': 10, 'конь': 30, 'слон': 30, 'ладья': 50, 'королева': 90, 'король': 900}

    def mousePressEvent(self, event):
        if 28 <= event.x() <= 647 and 66 <= event.y() <= 687:
            self.clicked_coords = self.get_possition(event.x(), event.y())
            self.loop.exit(0)

    def wait_for_click(self):
        """Создается QeventLoop, который закончить (self.loop.exit(0)) может только mousePressEvent"""
        self.loop = QEventLoop(self)
        self.loop.exec_()

    def get_possition(self, x, y):
        """Определение координат на доске по координатам на окне"""
        return (7 - (y - 66) // 79), (x - 28) // 78

    def paintEvent(self, event):
        """С помощью флагов распределяем что нужно перерисовать"""
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
        # сначала прячем все изображения
        for i in self.figures:
            for j in self.figures[i]:
                j.hide()
        # а теперь добавим нужные
        for y in range(len(board.field_layout)):
            for x in range(len(board.field_layout[y])):
                if board.field_layout[y][x]:
                    try:
                        self.figures[board.field_layout[y][x].figure()][
                            board.field_layout[y][x].number_of_figure].show()
                        self.figures[board.field_layout[y][x].figure()][board.field_layout[y][x].number_of_figure].move(
                            28 + x * 77, 66 + (7 - y) * 78)
                    except Exception:
                        pass

    def print_change(self, moves):
        # вывод изображений, подсказывающих куда можно ходить
        green_image_image = QImage('файлы проекта/green_image.png')
        green_image_pixmap = QPixmap(green_image_image)

        red_image_image = QImage('файлы проекта/red_image.png')
        red_image_pixmap = QPixmap(red_image_image)

        self.labels_for_print_change = []
        for i in range(len(moves)):
            y, x = moves[i]
            label = QLabel(self)
            if self.board.field_layout[y][x]:
                label.setPixmap(red_image_pixmap)
                label.resize(red_image_pixmap.size())
            else:
                label.setPixmap(green_image_pixmap)
                label.resize(green_image_pixmap.size())
            label.show()
            label.move(28 + x * 77, 66 + (7 - y) * 77)
            self.labels_for_print_change.append(label)

    def clear_labels_after_change(self):
        # очистка изображений, подсказывающих куда можно ходить
        for i in self.labels_for_print_change:
            i.hide()

    def repaint_selected_figure(self, y, x):
        # добавление изображение на выделенную фигуру
        self.selected_figure_label.show()
        self.selected_figure_label.move(28 + x * 77, 66 + (7 - y) * 78)

    def unitUi(self):
        def minimax(board, depth, alpha, beta, max_min):
            if depth == 0 or board.mat(*board.king('черный'), 'черный') or board.mat(*board.king('белый'), 'белый'):
                value = 0
                for j in range(len(board.field_layout)):
                    for i in range(len(board.field_layout[j])):
                        if (board.field_layout[j][i] and board.field_layout[j][i].figure().split()[0]
                                == self.opposite_color):
                            value += (self.cost_basic[board.field_layout[j][i].figure().split()[1]] +
                                      self.cost[board.field_layout[j][i].figure().split()[1]][7 - j][i])
                        elif board.field_layout[j][i]:
                            value -= (self.cost_basic[board.field_layout[j][i].figure().split()[1]] +
                                      self.cost[board.field_layout[j][i].figure().split()[1]][j][i])
                return value
            board_copy = deepcopy(board)
            possible_moves = board_copy.possible_moves_team(self.opposite_color)
            if max_min:
                max_value = -100000
                for move in possible_moves:
                    if board_copy.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                        board_copy.move(*move, type_of_figure='королева')
                    else:
                        board_copy.move(*move)
                        if board_copy.shah(self.opposite_color):
                            board_copy = deepcopy(board)
                            continue
                    num = minimax(board_copy, depth - 1, alpha, beta, False)
                    board_copy = deepcopy(board)
                    max_value = max(num, max_value)
                    alpha = max(alpha, max_value)
                    if beta <= alpha:
                        break
                return max_value
            else:
                min_value = 10000000
                for move in possible_moves:
                    if board_copy.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                        board_copy.move(*move, type_of_figure='королева')
                    else:
                        board_copy.move(*move)
                    if board_copy.shah(self.opposite_color):
                        board_copy = deepcopy(board)
                        continue
                    num = minimax(board, depth - 1, alpha, beta, True)
                    board_copy = deepcopy(board)
                    min_value = min(num, min_value)
                    beta = min(beta, min_value)
                    if beta <= alpha:
                        break
                return min_value

        def best_move(board):
            """реализация бота с помощью поиска Min/Max с alpha beta отсечением minmax alrogithm:
            https://en.wikipedia.org/wiki/Minimax#:~:text=A%20minimax%20algorithm%20is%20a,or%20state%20of%20the%20game.
            """
            possible_moves = board.possible_moves_team(self.opposite_color)
            board_copy = deepcopy(board)
            best_num = -100000
            best_bot_move = ''
            for move in possible_moves:
                if board_copy.field_layout[move[0]][move[1]].figure().split()[1] == 'пешка' and move[2] == 0:
                    board_copy.move(*move, type_of_figure='королева')
                else:
                    board_copy.move(*move)
                if board_copy.shah(self.opposite_color):
                    board_copy = deepcopy(board)
                    continue
                num = minimax(board_copy, 2, -1000000, 1000000, False)
                board_copy = deepcopy(board)
                if num > best_num:
                    best_num = num
                    best_bot_move = move
            return best_bot_move

        def get_moves_clean(y, x, color):
            # Очистка всех ходов фигуры. Очищаем те, которые приводят к шаху
            possible_moves = self.board.field_layout[y][x].get_moves(self.board.field_layout, y, x)
            delete_indexes = []
            for move in range(len(possible_moves)):
                board_copy = deepcopy(self.board)
                board_copy.move(y, x, possible_moves[move][0], possible_moves[move][1])
                if board_copy.shah(color):
                    delete_indexes.append(move)
            for index in delete_indexes[::-1]:
                del possible_moves[index]
            return possible_moves

        def get_person_move():
            self.clicked_coords = None
            self.wait_for_click()
            y, x = self.clicked_coords
            if self.num_of_clicks == 0:
                # при первом проходе нужно вернуть координаты выбранной фигуры, поэтому используем цикл пока не найдем
                # фигуру
                while not self.board.field_layout[y][x] or (
                        self.board.field_layout[y][x] and self.board.field_layout[y][x].figure().split()[0]
                        == self.opposite_color):
                    self.statusBar().showMessage('Неправильная фигура')
                    self.wait_for_click()
                    y, x = self.clicked_coords
                self.repaint_selected_figure_flag = True
                self.y_selected_figure, self.x_selected_figure = y, x
                self.repaint()
                self.statusBar().showMessage('')
                self.moves_for_figure = get_moves_clean(y, x, self.main_color)
                self.print_change_flag = True
                self.repaint()
                return y, x, 1
            while (y, x) not in self.moves_for_figure:
                # при втором проходе нужно определить координаты куда фигура перейдет, либо если человек нажмет на
                # другую белую фигуру, переключиться на нее
                if (self.board.field_layout[y][x] and self.board.field_layout[y][x].figure().split()[0]
                        != self.opposite_color):
                    self.clear_labels_after_change()
                    self.repaint_selected_figure_flag = True
                    self.y_selected_figure, self.x_selected_figure = y, x
                    self.repaint()
                    self.moves_for_figure = get_moves_clean(y, x, self.main_color)
                    self.print_change_flag = True
                    self.repaint()
                    return y, x, True
                self.wait_for_click()
                y, x = self.clicked_coords
            self.clear_labels_after_change()
            return y, x, False

        def check_board():
            # проверка на исходы победа/проигрыш/ничья
            if self.board.mat(*self.board.king(self.main_color), self.main_color):
                self.result_text.setText('Бот выиграл')
                return True
            if check_for_draw(self.board.field_layout):
                self.result_text.setText('Ничья')
                return True
            if self.board.mat(*self.board.king(self.opposite_color), self.opposite_color):
                self.result_text.setText('Вы выиграли')
                return True
            return False

        def main():
            self.figures = {}
            i_name = 'белый '
            # создание нескольких qlabel, так как во время игры с учетом всех проеденных пешек может получиться 10
            # одинаковых фигур, то нужно создать 10 qlable для каждой фигуры
            for i in ['figures_white', 'figures_black']:
                for j in ['конь', 'пешка', 'слон', 'король', 'королева', 'ладья']:
                    link = sqlite3.connect('файлы проекта/шахматы/chess.db').cursor().execute(
                        f"""SELECT link FROM {i} WHERE name = '{j}'""").fetchone()
                    all_the_labels = []
                    for time in range(10):
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
            self.result_text.setText('')
            self.start_game.setEnabled(False)
            color_first = 'белый'
            color_second = 'черный'
            self.opposite_color = color_second
            self.main_color = color_first
            # основной код
            self.board = Board(color_first, color_second)
            # спрячем все фигуры, на случай если игра была начата заново
            for name in self.figures:
                for label in self.figures[name]:
                    label.hide()
            while True:
                if check_board():
                    break
                flag = True
                self.do_paint = True
                self.repaint()
                self.num_of_clicks = 0
                while self.num_of_clicks == 0:
                    y, x, self.num_of_clicks = get_person_move()
                while flag:
                    y_to, x_to, flag = get_person_move()
                    if flag:
                        y = y_to
                        x = x_to
                self.selected_figure_label.hide()
                self.type_of_figure = ''
                if self.board.field_layout[y][x].figure() == 'белый пешка' and y == 6 and y_to == 7:
                    # в случае если фигура дошла до конца, нужно открыть окно с выбором фигуры
                    promotion_figure = Promotion(parent=self)
                    promotion_figure.show()
                    promotion_figure.main()
                    if not self.type_of_figure:
                        # пользователь может закрыть окно, то тогда мы переходим на следующею
                        # итерацию(ход начинается заново)
                        continue
                if self.type_of_figure:
                    self.board.move(y, x, y_to, x_to, type_of_figure=self.type_of_figure)
                else:
                    self.board.move(y, x, y_to, x_to)
                if check_board():
                    break
                self.do_paint = True
                self.repaint()
                move_bot = best_move(self.board)
                if not move_bot:
                    self.result_text.setText('Вы выиграли')
                    break
                if (self.board.field_layout[move_bot[0]][move_bot[1]].
                        figure() == 'черный пешка' and move_bot[2] == 0):
                    self.board.move(*move_bot, type_of_figure='королева')
                else:
                    self.board.move(*move_bot)
                self.do_paint = True
                self.repaint()
            # так как игра закончилась, разблокируем кнопку начла игры и доресуем все
            self.do_paint = True
            self.repaint()
            self.start_game.setEnabled(True)

        def check_for_draw(board):
            # ничья тогда, когда на поле остались только два короля
            amout_of_figures = 0
            for row in board:
                for figure in row:
                    if figure:
                        amout_of_figures += 1
            return amout_of_figures == 2

        class Board:
            def __init__(self, first_color, second_color):
                self.game_over = False
                # порядковые номера фигур, используются для определения своего label
                self.number_of_label = {'слон': 1, 'конь': 1, 'королева': 0, 'ладья': 1}
                # создаем поле
                self.field_layout = []
                for row in range(8):
                    self.field_layout.append([None] * 8)
                self.field_layout[0] = [
                    Rook(first_color, 0), Knight(first_color, 0), Bishop(first_color, 0), Queen(first_color, 0),
                    King(first_color, 0), Bishop(first_color, 1), Knight(first_color, 1), Rook(first_color, 1)
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
                    Rook(second_color, 0), Knight(second_color, 0), Bishop(second_color, 0), Queen(second_color, 0),
                    King(second_color, 0), Bishop(second_color, 1), Knight(second_color, 1), Rook(second_color, 1)
                ]

            def king(self, color):
                for y in range(8):
                    for x in range(8):
                        if self.field_layout[y][x] and self.field_layout[y][x].figure() == color + ' ' + 'король':
                            return y, x

            def mat(self, y_king, x_king, color):
                # проверка на мат, смотрим если нет возможности куда-то сходить у короля
                if color == 'черный':
                    color_to_get_move = 'белый'
                elif color == 'белый':
                    color_to_get_move = 'черный'
                moves = list(map(lambda x: (x[2], x[3]), self.possible_moves_team(color_to_get_move, True)))
                for y in range(y_king - 1, y_king + 1):
                    for x in range(x_king - 1, x_king + 1):
                        if 0 <= y <= 7 and 0 <= x <= 7 and (y, x) not in moves:
                            return False
                return True

            def shah(self, color):
                # Смотрим если на короля есть возможность атаки. В possible_moves_team в случае значения
                # flag=True возвращаются все возможный ходы, даже которые "едят" короля
                if color == 'черный':
                    color_for_moves = 'белый'
                elif color == 'белый':
                    color_for_moves = 'черный'
                possible_moves_of = self.possible_moves_team(color_for_moves, flag=True)
                for move in possible_moves_of:
                    if (self.field_layout[move[2]][move[3]] and self.field_layout[move[2]][move[3]]
                            .figure() == f'{color} король'):
                        return True
                return False

            def possible_moves_team(self, color, flag=False):
                all_possible_moves = []
                for y in range(len(self.field_layout)):
                    for x in range(len(self.field_layout[y])):
                        if self.field_layout[y][x] and self.field_layout[y][x].figure().split()[0] == color:
                            all_possible_moves.extend(
                                [(y, x) + j for j in self.field_layout[y][x].get_moves(self.field_layout, y, x) if
                                 (self.field_layout[j[0]][j[1]] and self.field_layout[j[0]][j[1]].figure().split()[1]
                                  != 'король') or flag or not self.field_layout[j[0]][j[1]]])
                return all_possible_moves

            def move(self, y_now, x_now, y_to, x_to, type_of_figure=None):
                # type_of_figure - фигура на которую меняем пешку, в случае если переменныя действительна,
                # мы делаем замену
                if type_of_figure:
                    number = self.number_of_label[type_of_figure.lower()] + 1
                    self.number_of_label[type_of_figure.lower()] += 1
                    if type_of_figure.lower() == 'ладья':
                        self.field_layout[y_to][x_to] = Rook(self.field_layout[y_now][x_now].figure().split()[0],
                                                             number)
                    elif type_of_figure.lower() == 'королева':
                        self.field_layout[y_to][x_to] = Queen(self.field_layout[y_now][x_now].figure().split()[0],
                                                              number)
                    elif type_of_figure.lower() == 'слон':
                        self.field_layout[y_to][x_to] = Bishop(self.field_layout[y_now][x_now].figure().split()[0],
                                                               number)
                    elif type_of_figure.lower() == 'конь':
                        self.field_layout[y_to][x_to] = Knight(self.field_layout[y_now][x_now].figure().split()[0],
                                                               number)
                    self.field_layout[y_now][x_now] = None
                    return True
                # проверка на рокировку
                if (self.field_layout[y_now][x_now] and self.field_layout[y_now][x_now].figure().split()[1]
                        == 'король' and y_now - y_to == 0 and abs(x_to - x_now) > 1):
                    if not self.field_layout[y_now][x_now - 1] and not self.field_layout[y_now][x_now - 2] and not \
                            self.field_layout[y_now][x_now - 3] and self.field_layout[y_now][x_now - 4] and \
                            self.field_layout[y_now][x_now - 4].figure().split()[1] == 'ладья' and \
                            self.field_layout[y_now][x_now - 4].moves == 0:
                        self.field_layout[y_now][x_now - 4], self.field_layout[y_now][x_now - 1] = None, \
                            self.field_layout[y_now][x_now - 4]
                    if not self.field_layout[y_now][x_now + 1] and not self.field_layout[y_now][x_now + 2] and \
                            self.field_layout[y_now][x_now + 3] and \
                            self.field_layout[y_now][x_now + 3].figure().split()[1] == 'ладья' and \
                            self.field_layout[y_now][x_now + 3].moves == 0:
                        self.field_layout[y_now][x_now + 3], self.field_layout[y_now][x_now + 1] = None, \
                            self.field_layout[y_now][x_now + 3]
                self.field_layout[y_now][x_now], self.field_layout[y_to][x_to] = None, self.field_layout[y_now][x_now]
                # у короля и ладьи есть атрибут "moves" - количество ходов (то есть если король/ладья двинется, чтобы
                # нельзя было делать рокировку)
                try:
                    self.field_layout[y_to][x_to].moves += 1
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

                for coficeint in range(1, 8):
                    if y_now + coficeint > 7 or x_now + coficeint > 7 or y_now + coficeint < 0 or x_now + coficeint < 0:
                        break
                    if board[y_now + coficeint][x_now + coficeint] and \
                            board[y_now + coficeint][x_now + coficeint].figure().split()[0] != self.color:
                        moves_possible.append((y_now + coficeint, x_now + coficeint))
                        break
                    elif board[y_now + coficeint][x_now + coficeint] and \
                            board[y_now + coficeint][x_now + coficeint].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y_now + coficeint, x_now + coficeint))

                for coficeint in range(1, 8):
                    if y_now - coficeint > 7 or x_now - coficeint > 7 or y_now - coficeint < 0 or x_now - coficeint < 0:
                        break
                    if board[y_now - coficeint][x_now - coficeint] and \
                            board[y_now - coficeint][x_now - coficeint].figure().split()[0] != self.color:
                        moves_possible.append((y_now - coficeint, x_now - coficeint))
                        break
                    elif board[y_now - coficeint][x_now - coficeint] and \
                            board[y_now - coficeint][x_now - coficeint].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y_now - coficeint, x_now - coficeint))

                for coficeint in range(1, 8):
                    if y_now - coficeint > 7 or x_now + coficeint > 7 or y_now - coficeint < 0 or x_now + coficeint < 0:
                        break
                    if board[y_now - coficeint][x_now + coficeint] and \
                            board[y_now - coficeint][x_now + coficeint].figure().split()[0] != self.color:
                        moves_possible.append((y_now - coficeint, x_now + coficeint))
                        break
                    elif board[y_now - coficeint][x_now + coficeint] and \
                            board[y_now - coficeint][x_now + coficeint].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y_now - coficeint, x_now + coficeint))

                for coficeint in range(1, 8):
                    if y_now + coficeint > 7 or x_now - coficeint > 7 or y_now + coficeint < 0 or x_now - coficeint < 0:
                        break
                    if board[y_now + coficeint][x_now - coficeint] and \
                            board[y_now + coficeint][x_now - coficeint].figure().split()[0] != self.color:
                        moves_possible.append((y_now + coficeint, x_now - coficeint))
                        break
                    elif board[y_now + coficeint][x_now - coficeint] and \
                            board[y_now + coficeint][x_now - coficeint].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y_now + coficeint, x_now - coficeint))
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
                        if x != x_now and board[y][x] and board[y][x].figure().split()[0] != self.color:
                            moves_possible.append((y, x))
                        elif x != x_now:
                            continue
                        if x == x_now and board[y][x]:
                            # в случае если встретилось препятствие, то мы не можем перейти через 2
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
                for y in range(y_now - 1, -1, -1):
                    if board[y][x_now] and board[y][x_now].figure().split()[0] != self.color:
                        moves_possible.append((y, x_now))
                        break
                    elif board[y][x_now] and board[y][x_now].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y, x_now))
                for y in range(y_now + 1, 8):
                    if board[y][x_now] and board[y][x_now].figure().split()[0] != self.color:
                        moves_possible.append((y, x_now))
                        break
                    elif board[y][x_now] and board[y][x_now].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y, x_now))
                for x in range(x_now + 1, 8):
                    if board[y_now][x] and board[y_now][x].figure().split()[0] != self.color:
                        moves_possible.append((y_now, x))
                        break
                    elif board[y_now][x] and board[y_now][x].figure().split()[0] == self.color:
                        break
                    else:
                        moves_possible.append((y_now, x))
                for x in range(x_now - 1, -1, -1):
                    if board[y_now][x] and board[y_now][x].figure().split()[0] != self.color:
                        moves_possible.append((y_now, x))
                        break
                    elif board[y_now][x] and board[y_now][x].figure().split()[0] == self.color:
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
                    if self.check_numbers(y, x) and (
                            (board[y][x] and board[y][x].figure().split()[0] != self.color) or not board[y][x]):
                        move_possible.append((y, x))
                return move_possible

            def check_numbers(self, y, x):
                return 0 <= x <= 7 and 0 <= y <= 7

        class King:
            def __init__(self, color, n):
                self.number_of_figure = n
                self.color = color
                self.moves = 0

            def moved(self):
                self.moves += 1

            def figure(self):
                return f"{self.color} король"

            def get_moves(self, board, y_now, x_now):
                moves_possible = []
                # возможность рокировки
                if (self.moves == 0 and x_now == 4 and board[y_now][x_now - 4] and
                        board[y_now][x_now - 4].figure().split()[1] == 'ладья' and board[y_now][x_now - 4].
                        moves == 0 and not board[y_now][x_now - 1] and not board[y_now][x_now - 2] and not
                        board[y_now][x_now - 3]):
                    moves_possible.append((y_now, x_now - 2))
                if (self.moves == 0 and x_now == 4 and board[y_now][x_now + 3] and
                        board[y_now][x_now + 3].figure().split()[1] == 'ладья' and board[y_now][x_now + 3].
                        moves == 0 and not board[y_now][x_now + 1] and not board[y_now][x_now + 2]):
                    moves_possible.append((y_now, x_now + 2))
                for y in range(y_now - 1, y_now + 2):
                    for x in range(x_now - 1, x_now + 2):
                        if (x, y != x_now, y_now) and self.check_numbers(y, x):
                            flag = True
                            for y_ in range(y - 1, y + 2):
                                for x_ in range(x - 1, x + 2):
                                    if self.check_numbers(y_, x_) and board[y_][x_] and board[y_][x_].figure() \
                                            .split()[1] == 'король' and \
                                            board[y_][x_].figure().split()[0] != self.color:
                                        # запрещаем зод если рядом есть король другого цветы
                                        flag = False
                                        break
                                if not flag:
                                    break
                            if flag:
                                if board[y][x]:
                                    if board[y][x].figure().split()[0] != self.color:
                                        moves_possible.append((y, x))
                                else:
                                    moves_possible.append((y, x))
                return moves_possible

            def check_numbers(self, y, x):
                return 0 <= x <= 7 and 0 <= y <= 7

        class Queen:
            def __init__(self, color, n):
                self.color = color
                self.number_of_figure = n

            def figure(self):
                return f"{self.color} королева"

            def get_moves(self, board, y_now, x_now):
                first = Bishop(self.color, 100)
                second = Rook(self.color, 100)
                # создаем две несуществующие фигуры, чтобы определить движение королевы(ход королевы = ладья + слон)
                return first.get_moves(board, y_now, x_now) + second.get_moves(board, y_now, x_now)

        main()


class Promotion(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent=None)
        self.parent = parent
        self.setGeometry(500, 500, 240, 70)
        self.setWindowTitle('Выберите фигуру')
        self.coords = []

        self.explain_label = QLabel(self)
        self.explain_label.move(0, 0)
        self.explain_label.setText('Выберите фигуру для замены')

        queen_qpixmap = QPixmap('файлы проекта/шахматы/белые/королева.png')
        queen_qpixmap = queen_qpixmap.scaled(50, 40, Qt.KeepAspectRatio)
        self.queen_label = QLabel(self)
        self.queen_label.setPixmap(queen_qpixmap)
        self.queen_label.resize(queen_qpixmap.size())
        self.queen_label.move(10, 30)

        knight_qpixmap = QPixmap('файлы проекта/шахматы/белые/конь.png')
        knight_qpixmap = knight_qpixmap.scaled(50, 40, Qt.KeepAspectRatio)
        self.knight_label = QLabel(self)
        self.knight_label.setPixmap(knight_qpixmap)
        self.knight_label.resize(knight_qpixmap.size())
        self.knight_label.move(70, 30)

        rook_qpixmap = QPixmap('файлы проекта/шахматы/белые/ладья.png')
        rook_qpixmap = rook_qpixmap.scaled(50, 40, Qt.KeepAspectRatio)
        self.rook_label = QLabel(self)
        self.rook_label.setPixmap(rook_qpixmap)
        self.rook_label.resize(rook_qpixmap.size())
        self.rook_label.move(130, 30)

        bishop_qpixmap = QPixmap('файлы проекта/шахматы/белые/слон.png')
        bishop_qpixmap = bishop_qpixmap.scaled(50, 40, Qt.KeepAspectRatio)
        self.bishop_label = QLabel(self)
        self.bishop_label.setPixmap(bishop_qpixmap)
        self.bishop_label.resize(bishop_qpixmap.size())
        self.bishop_label.move(190, 30)

    def get_promotion_figure(self, x):
        if 0 <= x <= 70:
            return 'королева'
        if 70 <= x <= 130:
            return 'конь'
        if 130 <= x <= 190:
            return 'ладья'
        if 190 <= x <= 240:
            return 'слон'

    def main(self):
        self.wait_for_push()
        if not self.coords:
            # если человек закрыл окно, то self.coords будут пустыми поэтому не будем ничего менять
            self.parent.type_of_figure = None
        else:
            self.parent.type_of_figure = self.get_promotion_figure(self.coords[0])
        self.close()

    def wait_for_push(self):
        self.loop = QEventLoop(self)
        self.loop.exec_()

    def mousePressEvent(self, event):
        self.coords = event.x(), event.y()
        self.loop.exit(0)

    def closeEvent(self, event):
        self.loop.exit(0)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
