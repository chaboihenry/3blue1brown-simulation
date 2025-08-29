import sys
import pygame

class Blob:
    """
    Main class that represents a physics blob (rectangle)
    """
    
    def __init__(self, x, y, width, height, mass, color, velocity = 0):
        """
        Constructor method (__init__).

        Parameters:
        - self: refers to the specific blob object being created
        - x, y: starting position coordinates
        - width, height: size of the rectangle
        - mass: how heavy the blob is (affects physics)
        - color: RGB color tuple for drawing
        - velocity: starting speed (default is 0 for stationary)
        """
        # Instance attributes
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.mass = mass
        self.color = color
        self.velocity = velocity

        # pygame rectangle for collision detection and drawing
        self.rect = pygame.Rect(x, y, width, height)
    
    def update_position(self, dt, wall_x=None):
        """
        method updates blob's position based on its velocity with wall collision prevention

        Parameters:
        - dt: delta time (time since last update) for smooth movement  
        - wall_x: optional wall position to prevent tunneling through
        """
        # Calculate intended movement
        dx = self.velocity * dt
        
        # If we have a wall position and we're moving left, check for tunneling
        if wall_x is not None and dx < 0:
            new_x = self.x + dx
            # If the move would put us behind the wall, stop at the wall
            if new_x < wall_x:
                self.x = wall_x
                # Don't update velocity here - let collision detection handle it
            else:
                self.x = new_x
        else:
            # Normal movement (no wall concern or moving right)
            self.x += dx

        # update pygame rectangle to match new position
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        """
        method draws blob on the screen

        Parameters:
        - dt: delta time (time since last update) for smooth movement
        """
        pygame.draw.rect(screen, self.color, self.rect)

        # Draw mass label on blob
        font = pygame.font.Font(None, 24)
        text = font.render(f"{int(self.mass)}", True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)
