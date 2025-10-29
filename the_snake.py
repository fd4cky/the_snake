from random import randint
import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Базовый игровой объект с позицией и цветом тела.

    Attributes:
        position (tuple[int, int]): Координаты верхнего левого угла клетки.
        body_color (tuple[int, int, int]): Цвет объекта в формате RGB.
    """

    def __init__(self, position=(0, 0), body_color=(255, 255, 255)):
        """Инициализирует объект (по умолчанию (0, 0) и (255, 255, 255)).

        Args:
            position (tuple[int, int]): Позиция на поле в пикселях
                (кратна GRID_SIZE).
            body_color (tuple[int, int, int]): Цвет отрисовки объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):  # pragma: no cover - графика
        """Абстрактный метод отрисовки на экране.

        Raises:
            NotImplementedError: Метод должен быть переопределён в подклассе.
        """
        raise NotImplementedError


class Snake(GameObject):
    """Змейка: управляемый игроком объект, состоящий из сегментов.

    Хранит список координат сегментов, движение дискретное по сетке.
    """

    def __init__(self):
        """Создаёт змейку в центре экрана, движущуюся вправо.

        Инициализирует длину змейки, список позиций сегментов,
        направление движения и вспомогательные атрибуты.
        """
        center = (
            (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE,
            (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE,
        )
        super().__init__(position=center, body_color=SNAKE_COLOR)
        self.length = 1
        self.positions = [center]
        self.direction = RIGHT
        self.next_direction = None
        # последняя ячейка для затирания следа
        self.last = None

    def get_head_position(self):
        """Возвращает координаты головы змейки.

        Returns:
            tuple[int, int]: Координаты головы змейки в пикселях.
        """
        return self.positions[0]

    def update_direction(self):
        """Применяет отложенное направление, если оно задано.

        Обновляет текущее направление движения змейки
        на следующее, если оно установлено.

        Returns:
            None: Метод не возвращает значений.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Сдвигает змейку на одну клетку в текущем направлении.

        Добавляет новую голову и при необходимости удаляет хвост.
        Реализует «сквозные» стены (тор).

        Returns:
            None: Метод не возвращает значений.
        """
        x, y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )

        # Самопересечение — сбросим игру
        # (обработаем в main повторно для единообразия)
        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()  # для затирания
        else:
            self.last = None

        self.position = new_head

    def reset(self):
        """Возвращает змейку в стартовое состояние.

        Сбрасывает основные параметры и вспомогательные атрибуты змейки.

        Returns:
            None: Метод не возвращает значений.
        """
        center = (
            (SCREEN_WIDTH // 2 // GRID_SIZE) * GRID_SIZE,
            (SCREEN_HEIGHT // 2 // GRID_SIZE) * GRID_SIZE,
        )
        self.length = 1
        self.positions = [center]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.position = center

    def draw(self):  # pragma: no cover - графика
        """Отрисовывает все сегменты и затирает след.

        Отрисовывает тело и голову змейки с границами,
        а также очищает последнюю ячейку хвоста.

        Returns:
            None: Метод не возвращает значений.
        """
        # Тело (кроме головы)
        for position in self.positions[1:]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Голова
        head_pos = self.positions[0]
        head_rect = pygame.Rect(head_pos, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)


class Apple(GameObject):
    """Яблоко: статический объект, появляющийся в случайной клетке."""

    def __init__(self):
        """Создаёт яблоко и задаёт случайную позицию.

        Инициализирует объект с цветом яблока и
        случайной позицией на поле.
        """
        super().__init__((0, 0), APPLE_COLOR)
        self.randomize_position()

    def randomize_position(self):
        """Ставит яблоко в случайную клетку поля.

        Обновляет позицию яблока случайным образом в пределах игрового поля.

        Returns:
            None: Метод не возвращает значений.
        """
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):  # pragma: no cover - графика
        """Отрисовывает яблоко как закрашенную клетку.

        Рисует яблоко с заданным цветом и границей на игровом экране.

        Returns:
            None: Метод не возвращает значений.
        """
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш и ставит следующее направление.

    Нельзя мгновенно развернуться на 180°.

    Args:
        game_object (Snake): Объект змейки, для которого обновляется
            направление движения.

    Returns:
        None: Функция не возвращает значений.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Точка входа: инициализация объектов и основной игровой цикл.

    Инициализирует PyGame, создаёт объекты змейки и яблока,
    запускает игровой цикл с обработкой событий,
    обновлением состояния и отрисовкой.

    Returns:
        None: Функция не возвращает значений.
    """
    # Инициализация PyGame:
    pygame.init()

    # Создаём игровые объекты
    snake = Snake()
    apple = Apple()

    # Заливка фона перед первым кадром
    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        # 1) События
        handle_keys(snake)

        # 2) Применить направление и сдвинуться
        snake.update_direction()
        snake.move()

        head = snake.get_head_position()

        # 3) Проверка поедания яблока
        if head == apple.position:
            snake.length += 1
            apple.randomize_position()

        # 4) Самопересечение — рестарт
        if head in snake.positions[1:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position()

        # 5) Отрисовка текущего кадра
        apple.draw()
        snake.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()