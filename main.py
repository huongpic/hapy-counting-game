import pygame
import random
import asyncio
import platform
import numpy as np
from pygame import Vector2

# Khởi tạo Pygame
pygame.init()

# Cấu hình màn hình
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Đếm Số Vui Vẻ")

# Màu sắc
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Font
font = pygame.font.SysFont("arial", 36)
large_font = pygame.font.SysFont("arial", 48)  # Font lớn cho số táo cần thu hoạch

# Tải hình nền
background = pygame.image.load("forest.png")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Tải và phát nhạc nền (sử dụng định dạng .ogg cho web)
pygame.mixer.music.load("background_music.ogg")
pygame.mixer.music.set_volume(0.5)  # Âm lượng 50%
pygame.mixer.music.play(-1)  # Phát lặp lại vô hạn

# Dữ liệu số và từ
NUMBERS = {
    1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
    6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten"
}

# Lớp nhân vật (gấu)
class Bear:
    def __init__(self):
        self.pos = Vector2(WIDTH // 2, HEIGHT - 80)
        self.speed = 5
        self.size = 80  # Kích thước 80x80
        self.image = pygame.image.load("bear.png")  # Tải ảnh gấu
        self.image = pygame.transform.scale(self.image, (self.size, self.size))  # Điều chỉnh kích thước

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.pos.x > 0:
            self.pos.x -= self.speed
        if keys[pygame.K_RIGHT] and self.pos.x < WIDTH - self.size:
            self.pos.x += self.speed
        if keys[pygame.K_UP] and self.pos.y > 0:
            self.pos.y -= self.speed
        if keys[pygame.K_DOWN] and self.pos.y < HEIGHT - self.size:
            self.pos.y += self.speed

    def draw(self, screen):
        screen.blit(self.image, (int(self.pos.x), int(self.pos.y)))  # Vẽ ảnh gấu

# Lớp quả táo
class Apple:
    def __init__(self):
        self.pos = Vector2(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 100))
        self.size = 50  # Kích thước 50x50
        self.image = pygame.image.load("apple.png")  # Tải ảnh táo
        self.image = pygame.transform.scale(self.image, (self.size, self.size))  # Điều chỉnh kích thước

    def draw(self, screen):
        screen.blit(self.image, (int(self.pos.x - self.size // 2), int(self.pos.y - self.size // 2)))  # Vẽ ảnh táo

# Lớp chai nhựa
class PlasticBottle:
    def __init__(self):
        self.pos = Vector2(random.randint(0, WIDTH - 50), random.randint(0, HEIGHT - 100))
        self.size = 50  # Kích thước 50x50
        self.image = pygame.image.load("plastic_bottle.png")  # Tải ảnh chai nhựa
        self.image = pygame.transform.scale(self.image, (self.size, self.size))  # Điều chỉnh kích thước

    def draw(self, screen):
        screen.blit(self.image, (int(self.pos.x - self.size // 2), int(self.pos.y - self.size // 2)))  # Vẽ ảnh chai nhựa

# Tạo âm thanh đơn giản bằng NumPy (dùng làm fallback)
def create_sound():
    sample_rate = 44100
    freq = 440
    duration = 0.2
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave = 0.5 * np.sin(2 * np.pi * freq * t)
    stereo = np.ascontiguousarray(np.vstack((wave, wave)).T)
    sound = pygame.sndarray.make_sound((stereo * 32767).astype(np.int16))
    return sound

# Hàm khởi tạo trò chơi
def setup():
    global bear, apples, bottles, target_number, collected, level, score, sound, collect_sound, time_left, game_over, start_time, total_apples_collected
    bear = Bear()
    apples = [Apple() for _ in range(10)]  # Tạo 10 quả táo
    level = 1  # Khởi tạo level trước
    bottle_count = 5 if level == 1 else 7 if level == 2 else 10  # Số chai nhựa theo level
    bottles = [PlasticBottle() for _ in range(bottle_count)]  # Tạo chai nhựa
    score = 0
    sound = create_sound()  # Âm thanh dự phòng
    try:
        collect_sound = pygame.mixer.Sound("collect_apple.ogg")  # Tải âm thanh thu thập táo
        collect_sound.set_volume(0.5)  # Đặt âm lượng 50%
    except:
        collect_sound = sound  # Nếu không tải được, dùng âm thanh dự phòng
    time_left = 20  # 20 giây cho mỗi lượt
    game_over = False
    start_time = pygame.time.get_ticks() // 1000  # Thời gian bắt đầu (giây)
    total_apples_collected = 0  # Tổng số táo thu thập
    set_new_target()

# Chọn số mục tiêu mới
def set_new_target():
    global target_number, collected
    if level == 1:
        target_number = random.randint(1, 5)  # Lesson 1: 1-5
    elif level == 2:
        target_number = random.randint(6, 10)  # Lesson 2: 6-10
    else:
        target_number = random.randint(1, 10)  # Lesson 3: 1-10
    collected = 0

# Cập nhật trạng thái trò chơi
def update_loop():
    global collected, score, level, time_left, game_over, start_time, total_apples_collected, bottles
    if game_over:
        # Xử lý màn hình Game Over hoặc hết thời gian
        screen.blit(background, (0, 0))
        if time_left <= 0:
            # Màn hình hết thời gian
            summary_text = font.render(f"Time's Up! You collected {total_apples_collected} apples!", True, RED)
            screen.blit(summary_text, (WIDTH // 2 - 250, HEIGHT // 2 - 50))
        else:
            # Màn hình thua do chạm chai nhựa
            game_over_text = font.render("Game Over! You hit a plastic bottle!", True, RED)
            screen.blit(game_over_text, (WIDTH // 2 - 250, HEIGHT // 2 - 50))
        # Vẽ nút Bắt đầu chơi lại
        retry_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        pygame.draw.rect(screen, GREEN, retry_button)
        retry_text = font.render("Play Again", True, BLACK)
        screen.blit(retry_text, (WIDTH // 2 - 80, HEIGHT // 2 + 30))
        pygame.display.flip()
        # Kiểm tra click nút Bắt đầu chơi lại
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_button.collidepoint(event.pos):
                    setup()  # Reset game
                    pygame.mixer.music.play(-1)  # Phát lại nhạc nền
        return True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            return False

    keys = pygame.key.get_pressed()
    bear.move(keys)

    # Cập nhật thời gian
    current_time = pygame.time.get_ticks() // 1000
    time_left = max(0, 20 - (current_time - start_time))
    if time_left == 0:
        game_over = True
        pygame.mixer.music.pause()  # Tạm dừng nhạc nền
        return True

    # Kiểm tra va chạm với táo
    for apple in apples[:]:
        if (bear.pos.x < apple.pos.x + apple.size and
            bear.pos.x + bear.size > apple.pos.x and
            bear.pos.y < apple.pos.y + apple.size and
            bear.pos.y + bear.size > apple.pos.y):
            apples.remove(apple)
            apples.append(Apple())  # Tạo táo mới
            collected += 1
            total_apples_collected += 1  # Cộng vào tổng số táo
            collect_sound.play()  # Phát âm thanh thu thập táo
            if collected == target_number:
                score += 10
                set_new_target()
                # Chuyển level sau 3 số đúng
                if score >= 30 and level < 3:
                    level += 1
                    # Cập nhật số lượng chai nhựa khi tăng level
                    bottle_count = 5 if level == 1 else 7 if level == 2 else 10
                    bottles = [PlasticBottle() for _ in range(bottle_count)]

    # Kiểm tra va chạm với chai nhựa
    for bottle in bottles:
        if (bear.pos.x < bottle.pos.x + bottle.size and
            bear.pos.x + bear.size > bottle.pos.x and
            bear.pos.y < bottle.pos.y + bottle.size and
            bear.pos.y + bear.size > bottle.pos.y):
            game_over = True
            pygame.mixer.music.pause()  # Tạm dừng nhạc nền
            return True

    # Vẽ màn hình
    screen.blit(background, (0, 0))  # Vẽ nền khu rừng
    bear.draw(screen)
    for apple in apples:
        apple.draw(screen)
    for bottle in bottles:
        bottle.draw(screen)

    # Hiển thị số và từ
    number_text = font.render(f"Collect {target_number} apples ({NUMBERS[target_number]})", True, BLACK)
    screen.blit(number_text, (10, 10))
    score_text = font.render(f"Score: {score}  Level: {level}", True, BLACK)
    screen.blit(score_text, (10, 50))
    time_text = font.render(f"Time: {int(time_left)}s", True, BLACK)
    screen.blit(time_text, (10, 90))

    # Hiển thị số táo cần thu hoạch ở giữa phía trên
    apples_needed = max(0, target_number - collected)  # Số táo còn lại
    apples_needed_text = large_font.render(f"Apples Needed: {apples_needed}", True, BLACK)
    apples_needed_rect = apples_needed_text.get_rect(center=(WIDTH // 2, 50))
    screen.blit(apples_needed_text, apples_needed_rect)

    # Hiển thị thông báo khi hoàn thành
    if collected == target_number:
        message = font.render(f"It's {NUMBERS[target_number]}!", True, GREEN)
        screen.blit(message, (WIDTH // 2 - 100, HEIGHT // 2))

    pygame.display.flip()
    return True

# Hàm chính
async def main():
    setup()
    while True:
        if not update_loop():
            break
        await asyncio.sleep(1.0 / 60)  # 60 FPS

# Chạy trò chơi
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except RuntimeError:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(main())