import pygame


class Button:
    def __init__(self, screen, position, text, text_size, func):
        self.clicked = False
        self.f = pygame.font.SysFont("Californian FB", text_size)
        self.text = text
        self.text_render = self.f.render(self.text, True, (255, 255, 255) if not self.clicked else (204, 204, 204))
        self.text_rect = self.text_render.get_rect()
        self.position = position
        self.text_rect.center = self.position
        self.screen = screen
        self.func = func

    def draw(self):
        self.text_render = self.f.render(self.text, True, (255, 255, 255) if not self.clicked else (127, 127, 127))
        self.text_rect = self.text_render.get_rect()
        self.text_rect.center = self.position
        pygame.draw.rect(self.screen, (0, 0, 0), self.text_rect)
        self.screen.blit(self.text_render, self.text_rect)

    # put in pygame event MOUSEDOWN after checking for desired press
    def handle_button(self):
        x, y = pygame.mouse.get_pos()
        if self.text_rect.left <= x <= self.text_rect.right and self.text_rect.top <= y <= self.text_rect.bottom:
            self.clicked = not self.clicked
            self.func()
