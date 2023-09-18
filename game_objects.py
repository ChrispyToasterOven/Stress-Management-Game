import pygame
from pygame.locals import *
import math
import os
import random

pixel_ratio = 16 / 60
pixel_scale = 60 / 16
one_ps = 1 / 60


def init_game():
    global basic_font
    basic_font = pygame.font.Font("fonts/hp-simplified.ttf", 18)

    # global player
    # player = Player()
    global main_camera
    global book_bg
    global title
    global game
    book_bg = Book()
    game = Game()
    spawn(game)
    main_camera = Camera()
    # main_camera.follow(player)
    spawn(main_camera, False)
    # spawn(player)

    spawn(book_bg)

    title = Title()
    spawn(title, add_to_game=True)


    scale_all(main_camera.zoom)

    global sounds
    sounds = {}
    for sound in os.listdir("sounds"):
        if sound.endswith(".mp3"):
            sounds[sound.split("mp3")[0]] = pygame.mixer.Sound("sounds/" + sound)
        else:
            s_group = []
            for rand_s in os.listdir(f"sounds/{sound}"):
                s_group.append(pygame.mixer.Sound(f"sounds/{sound}/{rand_s}"))
            sounds[sound] = s_group

    global music_wait
    music_wait = 5


def spawn(obj, draw=True, add_to_game=False):
    update_sprites.add(obj)
    if draw:
        render_sprites.add(obj)
    if add_to_game:
        game.sprites.add(obj)


def play_sound(name):
    if type(sounds[name]) == str:
        sounds[name].play()
    else:
        random.choice(sounds[name]).play()


def play_music(file, fade=1):
    global fadeout_time
    global fadein_time
    global next_song
    fadeout_time = fade
    fadein_time = fade
    next_song = file
    pygame.mixer.music.fadeout(fade * 1000)


fadeout_time = 0
fadein_time = 0
next_song = ""


def update_music():
    global fadeout_time
    if fadeout_time >= 0:
        fadeout_time -= one_ps
        if fadeout_time <= 0 and next_song != "":
            pygame.mixer.music.unload()
            pygame.mixer.music.load(f"music/{next_song}")
            pygame.mixer.music.play(-1, 0, fadein_time * 1000)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.Surface((60, 60))
        self.rect = pygame.Rect(0, 0, 60, 60)
        self.offset = [0, 0]
        self.pos = [0, 0]


class Book(pygame.sprite.Sprite):
    def __init__(self):
        self._layer = -1
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.original_image = pygame.Surface((0, 0))
        self.offset = [0, 0]
        self.area = None

        self.page_image = scale_image(pygame.image.load("images/note.png").convert(), pixel_scale)

        self.spine = scale_image(pygame.image.load("images/spine.png").convert_alpha(), pixel_scale)

        self.p_widdy = 168 * pixel_scale
        self.p_hiddy = 192 * pixel_scale
        self.full_bg = pygame.Surface((self.p_widdy * 2, 192 * pixel_scale))
        self.full_bg.blit(self.page_image, (0, 0))
        self.full_bg.blit(self.page_image, (self.p_widdy, 0))
        self.full_bg.blit(self.spine, (self.p_widdy - 32, 0))

        self.spine.set_alpha(20)
        self.turn_time = 0
        self.max_turn_time = 0.5

        self.rect.size = self.p_widdy * 2, self.p_hiddy

        self.turn_shadow = pygame.Surface((300, self.p_hiddy))
        self.turn_shadow.set_alpha(10)

    def draw(self, surface):
        self.rect.topleft = (60, 30)
        surface.blit(self.full_bg, self.rect.topleft)
        if self.turn_time > 0:
            self.turn_time -= one_ps
            if self.turn_time < 0:
                self.turn_time = 0

            surface.blit(self.turn_shadow, (self.rect.right - (math.cos((self.turn_time / self.max_turn_time) * (math.pi / 2)) * self.p_widdy * 2), 0))

            tp_wid = self.p_widdy - ((self.turn_time / self.max_turn_time) * self.p_widdy)
            turn_page_area = pygame.Rect(0, 0, tp_wid, self.p_hiddy)
            surface.blit(self.page_image, (self.rect.left + ((self.turn_time / self.max_turn_time) * (self.p_widdy * 2)), self.rect.y), turn_page_area)
            surface.blit(self.spine, ((self.rect.right - tp_wid) - 32, self.rect.y))

            # pygame.draw.rect(surface, (255, 0, 0), turn_page_area, 1)

    def turn_page(self):
        self.turn_time = self.max_turn_time
        play_sound("page_turn")


class Title(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.original_image = pygame.image.load("images/title.png").convert_alpha()

        self.rect = pygame.Rect(0, 0, 0, 0)
        self.area = None
        self.offset = [0, 0]
        self.b_time = 0
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 30)

        self.subtitle = self.font.render("A stress management game for new Computer Science Students", True, (100, 100, 100))
        self.sub_rect = self.subtitle.get_rect()

        self.author = self.font.render("Created by Christopher Sledd", True, (100, 100, 100))
        self.author_rect = self.author.get_rect()

    def update(self):
        mid_scr = window_size[0] / 2
        self.rect.size = self.image.get_size()
        self.rect.center = (mid_scr, 140)
        self.b_time += one_ps
        self.offset[1] = math.sin((self.b_time / 6) * math.pi * 2) * 25

        self.sub_rect.midtop = mid_scr, 300
        self.author_rect.midtop = mid_scr, 650

    def draw(self, surface):

        surface.blit(self.subtitle, self.sub_rect)
        surface.blit(self.author, self.author_rect)


def wrap_text_surface(string, font, width, height):
    tags = {}
    min_tag_find = 0
    for tag in range(string.count("<")):
        old_string = string
        tag_range = (string.find("<", min_tag_find) + 1, string.find(">", min_tag_find))
        tag_str = string[tag_range[0]: tag_range[1]]
        tags[tag_range[0] - 1] = tag_str
        do_space = " " * int(tag_str == "n")
        string = string[0: tag_range[0] - 1] + do_space + string[tag_range[1] + 1:]
        min_tag_find = (tag_range[1] + 1) - (len(old_string) - len(string))
    word_list = string.split()
    lines = [[]]
    text_color = (80, 80, 80)
    line_str = ""
    total_str_len = 0
    for word in word_list:
        line_num = len(lines) - 1
        if total_str_len in tags:
            new_line_condition = tags[total_str_len] == "n"
        else:
            new_line_condition = False
        if font.size(line_str)[0] + font.size(word)[0] <= width and not new_line_condition:
            lines[line_num].append(word + " ")
            line_str += word + " "
        else:
            lines.append([word + " "])
            line_str = word + " "
        total_str_len += len(word + " ")

    text_x = 0
    text_y = 0
    y_change = font.get_height()
    if y_change * len(lines) < height:
        height = y_change * len(lines)
    text_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    char_num = 0
    for line in lines:
        text_x = 0
        for word in line:
            for letter in word:
                if char_num in tags:
                    str_tag = tags[char_num]

                    split_tag = str_tag.split()

                    if split_tag[0] == "color":
                        text_color = (int(split_tag[1]), int(split_tag[2]), int(split_tag[3]))
                char_num += 1

                rendered_text = font.render(letter, True, text_color)
                text_surf.blit(rendered_text, (text_x, text_y))
                text_x += font.size(letter)[0]

        text_y += y_change

    return text_surf


class Game(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.offset = 0, 0
        self.original_image = pygame.Surface((0, 0))
        self.area = None

        self.screen = "title"
        self.first_click = True
        self.sprites = pygame.sprite.Group()

        self.load_timer = 0
        self.time_active = -1

        self.order_index = 0
        self.order = ["title", "info_1", "info_game_1", "Exercise", "info_post_game_1", "info_game_2", "Touch Grass",
                      "info_post_game_2", "info_game_3", "Connect with Others", "info_post_game_3", "info_game_4",
                      "info_big_picture", "end"]
        self.game_music_cue = ["info_game_1", "info_game_2", "info_game_3", "info_game_4", "info_big_picture"]
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 25)
        self.big_font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 50)
        self.level_info_dict = {
            "info_1": ["For each minigame, there is a time limit. Your objective is to score as many points (smiles) as possible within the time limit. ", "It's good to partake in stress management activities; however, remember that there's a limited time to do them.", "Click to begin!"],
            "info_game_1": ["", "", "Keeping your body active, and maintaining good physical health will contribute to good mental health as well."],
            "info_post_game_1": ["", "", "It’s recommended that adults should aim for 150 hours/week of exercise.", "The exercise doesn’t need to be extremely intense, but doing even something light can help reduce stress."],
            "info_game_2": ["", "", "It’s easy to lose touch with nature nowadays. Research suggests that having just a view of nature from an office, for example, is enough to relieve some stress.", "Have you gone outside today?"],
            "info_post_game_2": ["", "", "Cortisol is a hormone that leads to stress, and being in nature reduces this hormone.", "Nature also increases dopamine production in the brain, which will lead to more happiness."],
            "info_game_3": ["", "", "Friends and family can help you get your mind off of something stressful for a little while. On the other hand, they can also give new perspectives on whatever stressor you may be dealing with."],
            "info_post_game_3": ["", "", "Talking to, and being around other people can also naturally reduce stress. Physical touch is proven to help aswell.", "Don’t be afraid to reach out to someone you know!", "Sadly, beyond this point, I was unable to finish the last game, and ending scene; however, there's still information on stress relieving techniques!"],
            "info_game_4": ["", "", "Mindfulness is the act of becoming highly aware of the present, while blocking out the stress which stems from fears of the future, and regrets of the past. Mindfulness meditation is a great way to reduce stress."],
            "info_big_picture": ["", "", "The 5th technique for handling stress is to look at the bigger picture.", "Of course the things that you do in your day to day life are important; however, it’s important to also understand that if one small thing goes wrong, it’s not the end of the world."],
            "end": ["", "", "Thank you for playing :)"]

        }
        self.games = ["Exercise", "Touch Grass", "Connect with Others", "Meditation", "Look at the Bigger Picture"]
        self.info = []
        self.is_info = True

        self.technique_text = pygame.Surface((0, 0))
        self.tech_num_text = pygame.Surface((0, 0))
        self.tm_rect = pygame.Rect(0, 0, 0, 0)
        self.t_rect = pygame.Rect(0, 0, 0, 0)

        f = pygame.image.load("images/continue.png").convert_alpha()
        f = scale_image(f, pixel_scale)
        self.flash_button = FlashingImage(f, 1)

        self.flash_time = FlashingImage(self.big_font.render("", True, (80, 80, 80)), 1)
        self.count_down = 0

        self.paused = True
        self.smiles = 0
        self.smile_display = SmileDisplay()
        render_sprites.add(self.smile_display)

        self.play_rect = pygame.Rect(0, 0, book_bg.p_widdy, book_bg.p_hiddy - 180)
        self.play_rect.bottomright = book_bg.rect.bottomright

        self.misc_delay = 0

    def update(self):
        if self.load_timer > 0:
            self.load_timer -= one_ps
            if self.load_timer <= 0:
                self.load_timer = 0
                self.load_scence()

        if self.time_active < 10:
            self.time_active += one_ps

        click = pygame.mouse.get_pressed()[0] and self.first_click

        if self.misc_delay > 0:
            self.misc_delay -= one_ps
            if self.misc_delay < 0:
                self.misc_delay = 0
                self.change_scene()

        elif self.count_down > 0:
            self.count_down -= one_ps
            if self.count_down <= 0:
                self.count_down = 0
                if self.screen in self.games:
                    if self.time_active > 10:
                        self.paused = True
                        self.misc_delay = 1.5
                    else:
                        self.count_down = 34
                        self.paused = False
                else:
                    self.paused = True
                    self.change_scene()

        elif self.is_info:
            if click and self.time_active > 2:
                self.change_scene()

        if self.screen in self.games and not self.paused:
            self.sprites.update()

        self.first_click = not pygame.mouse.get_pressed()[0]

    def draw(self, surface):
        end_y = 0
        for inf in self.info:
            surface.blit(inf, (120, 120 + end_y))

            end_y += inf.get_height() + 30

        if self.time_active > 2 and self.count_down <= 0:
            self.flash_button.draw(surface, (1200, 660))

        if self.count_down > 0:
            self.flash_time.image = self.big_font.render(str(int(self.count_down) + 1), True, (80, 80, 80))
            self.flash_time.draw(surface, (1200, 660))

        self.tm_rect.center = window_size[0] / 2, 80
        self.t_rect.center = window_size[0] / 2, 120
        surface.blit(self.technique_text, self.t_rect)
        surface.blit(self.tech_num_text, self.tm_rect)

    def change_scene(self, force_scene=None):
        book_bg.turn_page()
        if force_scene is None:
            self.order_index += 1
        else:
            self.order_index = self.order.index(force_scene)
        self.screen = self.order[self.order_index]
        self.unlaod_scene()
        self.load_timer = 0.6
        self.time_active = 0
        self.is_info = self.screen in self.level_info_dict
        if self.screen in self.game_music_cue and self.screen != "info_big_picture":
            play_music("minigame.mp3")
        elif self.is_info:
            if next_song != "title_screen.mp3":
                play_music("title_screen.mp3")

        if self.screen in self.game_music_cue:
            if self.screen != "info_big_picture":
                self.count_down = 10
            cue_index = self.game_music_cue.index(self.screen)
            self.tech_num_text = self.font.render(f"Technique {cue_index + 1}:", True, (160, 160, 160))
            self.tm_rect = self.tech_num_text.get_rect()
            self.technique_text = self.big_font.render(self.games[cue_index], True, (80, 80, 80))
            self.t_rect = self.technique_text.get_rect()

        if self.screen in self.games:
            self.count_down = 3

        if self.screen == "Exercise":
            self.spawn(BenchPress())

        elif self.screen == "Touch Grass":
            self.spawn(TouchGrass())

        elif self.screen == "Connect with Others":
            self.spawn(ConnectWithOthers())

    def spawn(self, spr):
        self.sprites.add(spr)
        render_sprites.add(spr)

    def load_scence(self):
        if self.is_info:
            for inf in self.level_info_dict[self.screen]:
                # self.info.append(self.font.render(inf, True, (120, 120, 120)))
                self.info.append(wrap_text_surface(inf, self.font, 510, 800))

    def unlaod_scene(self):
        for sprite in self.sprites:
            sprite.kill()
        self.info.clear()

    def add_smile(self, pos):
        self.smiles += 1
        self.smile_display.smile_effects.append([1, pos])


class SmileDisplay(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.offset = 0, 0
        self.original_image = pygame.Surface((0, 0))
        self.image = pygame.Surface((0, 0))
        self.area = None
        self.rect = pygame.Rect(0, 0, 0, 0)

        self.smile_effects = []
        self.smile_image = scale_image(pygame.image.load("images/smile.png").convert_alpha(), pixel_scale)
        self.smile_rect = self.smile_image.get_rect()
        self.smile_counter_rect = pygame.Rect(120, 600, 60, 60)
        self.angle = 0
        self.time = 0
        self.max_time = 1
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", 70)

    def draw(self, surface):
        self.time += one_ps
        if self.time > self.max_time:
            self.time = 0
        self.angle = math.sin((self.time / self.max_time) * (math.pi * 2)) * 10
        rot_smile = rotate_image(self.smile_image, self.angle)[0]
        surface.blit(rot_smile, self.smile_counter_rect)
        amount_img = self.font.render(str(game.smiles), True, (90 + (self.angle * 2), 90, 90 + (self.angle * 3)))
        surface.blit(amount_img, self.smile_counter_rect.topright)

        for smile in self.smile_effects:
            tot_x = smile[1][0] - self.smile_counter_rect.centerx
            tot_y = smile[1][1] - self.smile_counter_rect.centery
            self.smile_rect.centerx = self.smile_counter_rect.centerx + math.sin((smile[0] / 1) * (math.pi / 2)) * tot_x
            self.smile_rect.centery = self.smile_counter_rect.centery + math.sin((smile[0] / 1) * (math.pi / 2)) * tot_y
            surface.blit(self.smile_image, self.smile_rect)
            print(self.smile_rect.center)

            smile[0] -= one_ps
            if smile[0] < 0:
                self.smile_effects.remove(smile)


# Game sprites ==========================================================================================


class BenchPress(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.offset = 0, 0
        self.original_image = pygame.Surface((0, 0))
        self.image = pygame.Surface((0, 0))
        self.area = None
        self.angle = 0

        self.head = scale_image(pygame.image.load("images/bench_head.png").convert_alpha(), pixel_scale)
        self.bar = scale_image(pygame.image.load("images/bar.png").convert_alpha(), pixel_scale)
        self.rect = self.head.get_rect()
        self.bar_rect = self.bar.get_rect()

        self.rect.center = game.play_rect.center
        self.bar_rect.center = self.rect.centerx, self.rect.centery + 100
        self.hit_bottom = False

    def update(self):
        self.rect.center = game.play_rect.center
        m_pos = list(pygame.mouse.get_pos())
        if m_pos[0] > game.play_rect.right:
            m_pos[0] = game.play_rect.right
        if m_pos[0] < game.play_rect.x:
            m_pos[0] = game.play_rect.x
        if self.angle > 0:
            mult = 1
        else:
            mult = -1

        if abs(m_pos[1] - self.bar_rect.centery) < 300:
            self.bar_rect.centery = m_pos[1]
        else:
            self.bar_rect.centery += 2

        if self.bar_rect.centery < self.rect.y - 80:
            self.bar_rect.centery = self.rect.y - 80
        elif self.bar_rect.centery > self.rect.y + 60:
            self.bar_rect.centery = self.rect.y + 60

        self.angle += ((self.bar_rect.centerx - m_pos[0]) / 100) + ((self.angle / 50) * mult)
        if self.angle > 8:
            self.angle = 8
        if self.angle < -8:
            self.angle = -8
        print(self.angle)
        self.bar_rect.centerx = self.rect.centerx

        if self.bar_rect.centery < self.rect.y - 65:
            if self.hit_bottom:
                self.hit_bottom = False
                game.add_smile(self.bar_rect.center)

        if self.bar_rect.centery > self.rect.y + 50:
            self.hit_bottom = True

    def draw(self, surface):
        rot_bar, bar_offset = rotate_image(self.bar, self.angle)
        surface.blit(rot_bar, (self.bar_rect.x + bar_offset[0], self.bar_rect.y + bar_offset[1]))
        surface.blit(self.head, self.rect)

        pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)
        pygame.draw.rect(surface, (255, 0, 0), self.bar_rect, 1)


class TouchGrass(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.offset = 0, 0
        self.original_image = pygame.Surface((0, 0))
        self.image = pygame.Surface((0, 0))
        self.area = None
        self.angle = 0
        self.rect = pygame.Rect(0, 0, 180, 180)
        self.grass = scale_image(pygame.image.load("images/grass.png").convert_alpha(), pixel_scale)

        self.rect.center = random.randint(game.play_rect.x, game.play_rect.right), \
                           random.randint(game.play_rect.y, game.play_rect.bottom)

        self.prev_x_cond = False
        self.rub_amount = 5

    def update(self):
        m_pos = pygame.mouse.get_pos()
        if self.rub_amount <= 0:
            game.add_smile(self.rect.center)
            self.rect.center = random.randint(game.play_rect.x, game.play_rect.right), \
                               random.randint(game.play_rect.y, game.play_rect.bottom)
            self.rub_amount = 5

        current_x_cond = m_pos[0] > self.rect.centerx
        if current_x_cond != self.prev_x_cond:
            self.grass.set_alpha(200)
            self.rub_amount -= 1
        else:
            self.grass.set_alpha(255)
        self.prev_x_cond = current_x_cond

    def draw(self, surface):
        surface.blit(self.grass, self.rect)


class ConnectWithOthers(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.offset = 0, 0
        self.original_image = pygame.Surface((0, 0))
        self.image = pygame.Surface((0, 0))
        self.area = None
        self.angle = 0
        self.rect = pygame.Rect(0, 0, 26 * pixel_scale, 26 * pixel_scale)
        self.rect.center = game.play_rect.center
        self.yap_rect = self.rect.copy()

        self.images = []
        for img in os.listdir("images/yappy"):
            self.images.append(scale_image(pygame.image.load(f"images/yappy/{img}").convert_alpha(), pixel_scale))

        self.yap_time = 0
        self.max_yap = 0.8
        self.img_index = 1
        self.click = True

        self.connected_points = []

    def update(self):
        m_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and self.click:
            for i in range(5):
                game.add_smile((self.rect.centerx + random.randint(-70, 70), (self.rect.centery + random.randint(-70, 70))))
            self.connected_points.append(self.rect.center)
            self.rect.center = random.randint(game.play_rect.x, game.play_rect.right), \
                               random.randint(game.play_rect.y, game.play_rect.bottom)

        self.yap_time -= one_ps
        if self.yap_time <= 0:
            self.yap_time = self.max_yap
            if self.img_index == 1:
                self.img_index = 2
            else:
                self.img_index = 1

        self.click = not pygame.mouse.get_pressed()[0]

    def draw(self, surface):
        iterate = 0
        for yap in self.connected_points:
            self.yap_rect.center = yap
            surface.blit(self.images[self.img_index], self.yap_rect)

        surface.blit(self.images[0], self.rect)

        if len(self.connected_points) > 1:
            pygame.draw.polygon(surface, (80, 10, 120), self.connected_points, 1)


# =======================================================================================================


class FlashingImage:
    def __init__(self, surface, rate=0.5):
        self.image = surface
        self.time = 0
        self.max_time = 1 / rate
        self.prev_tick = 0

    def draw(self, surface, pos):
        if self.prev_tick != tick - 1:
            self.time = 0
        self.prev_tick = tick
        self.time += one_ps
        if self.time >= self.max_time:
            self.time = 0
        sin_range = -math.cos(((self.time / self.max_time) * math.pi * 2)) + 1
        alpha = sin_range * 127.5
        self.image.set_alpha(int(alpha))

        surface.blit(self.image, pos)


class Camera(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.pos = [0, 0]
        self.rect = pygame.Rect(0, 0, 100, 100)
        self.following_ship = None
        self.zoom = 1
        self.up_press = True
        self.down_press = True

    def update(self):
        self.rect.width = window_size[0] / main_camera.zoom
        self.rect.height = window_size[1] / main_camera.zoom
        if self.following_ship is not None:
            self.pos[0] += (self.following_ship.pos[0] - self.pos[0]) / 30
            self.pos[1] += (self.following_ship.pos[1] - self.pos[1]) / 30
            self.rect.center = self.pos
        self.change_zoom()

    def follow(self, ship):
        self.following_ship = ship

    def change_zoom(self):
        if pygame.key.get_pressed()[K_UP] and self.up_press:
            print("ZOOM", self.zoom)
            self.zoom += 0.2
            self.up_press = False
            scale_all(self.zoom)
        if pygame.key.get_pressed()[K_DOWN] and self.down_press and self.zoom > 0.4:
            print("ZOOM", self.zoom)
            self.zoom -= 0.2
            self.down_press = False
            scale_all(self.zoom)


        self.up_press = not pygame.key.get_pressed()[K_UP]
        self.down_press = not pygame.key.get_pressed()[K_DOWN]


def rotate_image(surface, angle):
    og_center = surface.get_rect().center
    new_image = pygame.transform.rotate(surface, angle)
    offset = -((new_image.get_width() / 2) - og_center[0]), -((new_image.get_height() / 2) - og_center[1])
    return new_image, offset


def scale_image(surface, scale_mult):
    old_size = surface.get_size()
    return pygame.transform.scale(surface, (old_size[0] * scale_mult, old_size[1] * scale_mult))


def scale_all(scale):
    for spr in render_sprites:
        spr.image = scale_image(spr.original_image, scale * pixel_scale)


def get_angle(pos_1, pos_2):
    dist_x = pos_2[0] - pos_1[0]
    dist_y = pos_2[1] - pos_1[1]
    return math.atan2(dist_y, dist_x)


def get_angle_flipped(pos_1, pos_2):
    dist_x = pos_2[0] - pos_1[0]
    dist_y = pos_2[1] - pos_1[1]
    return math.atan2(-dist_y, dist_x)


def move_angle(pos, direction, amount):
    return pos[0] + (math.cos(direction) * amount), pos[1] + (math.sin(direction) * amount)


update_sprites = pygame.sprite.Group()
render_sprites = pygame.sprite.LayeredUpdates()
show_grid = False
tick = 0


def update_game(_window_size):
    global music_wait
    if music_wait > 0:
        music_wait -= one_ps
        if music_wait <= 0:
            play_music("title_screen.mp3", 0)
    global tick
    global window_size
    window_size = _window_size[0], _window_size[1]
    update_sprites.update()
    update_music()

    tick += 1


def render_all(surface, fps=0):
    for spr in render_sprites:
        draw_pos = spr.rect.x + spr.offset[0], spr.rect.y + spr.offset[1]
        surface.blit(spr.image, draw_pos, spr.area)

        if hasattr(spr, "draw"):
            spr.draw(surface)

    if show_grid:
        for x in range(0, int(window_size[0]), 60):
            pygame.draw.line(surface, (255, 0, 0), (x, 0), (x, window_size[1]))
        for y in range(0, int(window_size[1]), 60):
            pygame.draw.line(surface, (255, 0, 0), (0, y), (window_size[0], y))

    fps_text = basic_font.render(str(int(fps)), True, (0, 0, 0))
    surface.blit(fps_text, (0, 0))

