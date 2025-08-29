import pygame 
import sys
import math
from blob import Blob

pygame.init()

SCREEN_WIDTH = 1600
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (50, 50, 50) # Dark gray
WALL_COLOR = (255, 255, 255) # White
FLOOR_COLOR = (100, 100, 100) # Gray

class PhysicsSimulation:
    """
    Simulation manager for physics simulation
    """

    def __init__(self):
        """
        Constructor for our simulation manager
        """
        # sets up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("3blue1brown Inspired Physics Simulation")

        #clock for controlling frame rate
        self.clock = pygame.time.Clock()

        # physics constants
        self.ground_level = SCREEN_HEIGHT - 100 # creates floor
        self.wall_x = 50

        # counter
        self.collision_count = 0

        self.left_blob = None
        self.right_blob = None

        self.running = True
        self.simulation_started = False

        self.last_collision_count = 0
        self.stable_count = 0

    def get_user_input(self):
        """
        Get right mass from user - left mass is constant 1kg, velocity is set to constant 1 m/s
        """
        print("\n Simulation Setup")
        print("Left mass is fixed at 1kg for proper pi collision counting")

        # get right blob mass (moving)
        while True:
            try:
                right_power = int(input("Enter power of 100 for RIGHT mass (1-9): "))
                if 1 <= right_power <= 9:
                    right_mass = 100 ** (right_power-1)
                    expected_collision = int(math.pi * math.sqrt(right_mass))
                    break
                else:
                    print("Please enter a number between 1 and 9")
            except ValueError:
                print("Please enter a valid integer.")

        return right_mass
    
    def setup_blobs(self, right_mass):
        """
        Object instantiation, create blobs from class above
        Left mass is always 1kg, visual velocity scales with mass for constant 1 m/s physics velocity
        """
        # calculate visual velocity for proper physics
        # use scaling based on mass for realistic pi approximation
        visual_velocity = -50
        
        # Create left blob (stationary) - always 1kg for pi collision counting
        self.left_blob = Blob(
            x = 200,
            y = self.ground_level - 50, 
            width = 50, 
            height = 50, 
            mass = 1,  # Fixed at 1kg
            color = (255, 100, 100),
            velocity = 0
        )  

        # Create right blob (moving) - always 1 m/s in physics but scaled visually
        self.right_blob = Blob(
            x = 400, 
            y = self.ground_level - 50, 
            width = 50,
            height = 50,
            mass = right_mass,
            color = (100, 100, 255),
            velocity = visual_velocity
        )
    
    def calculate_adpative_speed(self):
        """
        Similar to adjust playback speed of a video but for the simulation
        """
        if not self.right_blob:
            return 1

        mass_ratio = self.right_blob.mass / self.left_blob.mass

        # The larger the mass ratio, the more we need to speed up
        if mass_ratio >= 10000000:
            return 2000
        elif mass_ratio >= 1000000:
            return 1500
        elif mass_ratio >= 10000:
            return 1000
        elif mass_ratio >= 1000:
            return 500
        elif mass_ratio >= 100:
            return 200
        elif mass_ratio >= 10:
            return 50
        else:
            return 20
        
    def should_use_burst_mode(self):
        """
        Fast physics, minimal visuals
        """
        if not self.right_blob:
            return False
        
        # Calc expected total collision
        mass_ratio = self.right_blob.mass / self.left_blob.mass
        expected_collisions = int(math.pi * math.sqrt(mass_ratio))

        # use burst if we have more collision to go
        remaining_collisions = max(0, expected_collisions - self.collision_count)

        # check if both objects are moving
        objects_moving = (abs(self.left_blob.velocity) > 0.01 or
                          abs(self.right_blob.velocity) > 0.01)

        return remaining_collisions > 50 and objects_moving
    
    def run_physics_burst(self, iterations):
        """
        fast-foward through collision-heavy part
        """
        dt_small = 1.0 / 60000.0

        for i in range(iterations):
            # Update positions with wall awareness for left blob
            self.left_blob.update_position(dt_small, self.wall_x)
            self.right_blob.update_position(dt_small)

            # check collisions
            self.check_collisions_precise()

            # show progess every 500 iterations
            if i % 500 == 0:
                self.draw()
                pygame.display.flip()

                for event in pygame.event.get():
                    if (event.type == pygame.QUIT or
                        (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)):
                        return False
                    
                if (abs(self.left_blob.velocity) < 0.01 and
                    abs(self.right_blob.velocity) < 0.01):
                    print("Objects are at rest - simulation done")
                    return True
                
        return True
    
    def check_collisions_precise(self):
        """
        precise collision detection to prevent wall penetration
        """
        # wall collision detection to prevent tunneling at high speeds
        if self.left_blob.x <= self.wall_x:
            # snap to wall position (prevent any penetration)
            self.left_blob.x = self.wall_x
            
            # perfect elastic collision with wall (reverse velocity if moving toward wall)
            if self.left_blob.velocity < 0:
                self.left_blob.velocity = -self.left_blob.velocity
                self.collision_count += 1
                print(f"Wall Collision {self.collision_count}")

        # if blob somehow gets behind wall, force it back
        if self.left_blob.x < self.wall_x:
            print(f"Warning: Blob tunneled through wall! Forcing back to wall position.")
            self.left_blob.x = self.wall_x
            # Ensure velocity is positive (moving away from wall)
            if self.left_blob.velocity < 0:
                self.left_blob.velocity = abs(self.left_blob.velocity)
                self.collision_count += 1
                print(f"Corrective Wall Collision {self.collision_count}")

        # blob-to-blob collision detection
        left_right_edge = self.left_blob.x + self.left_blob.width
        right_left_edge = self.right_blob.x

        # Check for any overlap at all - immediate collision response
        if left_right_edge >= right_left_edge:
            print(f"Blob collision detected at positions: Red={self.left_blob.x:.1f}, Blue={self.right_blob.x:.1f}")
            self.handle_blob_collision_precise()
            
        # when red blob somehow get past blue blob, fix it immediately
        elif self.left_blob.x > self.right_blob.x:
            print(f"EMERGENCY: Red blob passed through blue blob! Red at {self.left_blob.x:.1f}, Blue at {self.right_blob.x:.1f}")
            # force proper separation with red blob to the left
            self.left_blob.x = self.right_blob.x - self.left_blob.width - 5
            # make sure we don't violate wall constraint
            if self.left_blob.x < self.wall_x:
                self.left_blob.x = self.wall_x
                self.right_blob.x = self.wall_x + self.left_blob.width + 5
            print(f"Corrected positions: Red at {self.left_blob.x:.1f}, Blue at {self.right_blob.x:.1f}")
    
    def handle_blob_collision_precise(self):
        """
        handle blob collisions with proper physics and seperation
        """
        # get masses and velocities before collision
        m1 = self.left_blob.mass
        m2 = self.right_blob.mass
        v1 = self.left_blob.velocity
        v2 = self.right_blob.velocity

        print(f"Before collision: Red v={v1:.3f}, Blue v={v2:.3f}")

        # elastic collision formulas (1D conservation of momentum and energy)
        v1_new = ((m1 - m2) * v1 + 2 * m2 * v2) / (m1 + m2)
        v2_new = ((m2 - m1) * v2 + 2 * m1 * v1) / (m1 + m2)

        self.left_blob.velocity = v1_new
        self.right_blob.velocity = v2_new

        print(f"After collision: Red v={v1_new:.3f}, Blue v={v2_new:.3f}")

        # always separate blobs with red blob to the left of blue blob
        # this prevents red blob passing through blue blob for high inputs (5-9)
        seperation_distance = 5  
        
        # force red blob to ALWAYS be positioned to the left of blue blob after collision
        self.left_blob.x = self.right_blob.x - self.left_blob.width - seperation_distance
        
        # critical ensure red blob never goes behind wall
        if self.left_blob.x < self.wall_x:
            print(f"Warning: Collision positioning would put red blob behind wall! Correcting...")
            self.left_blob.x = self.wall_x
            # Adjust blue blob position to maintain proper separation
            self.right_blob.x = self.wall_x + self.left_blob.width + seperation_distance

        self.collision_count += 1
        print(f"Blob Collision {self.collision_count}")

    def check_collisions(self):
        """
        implements basic physics collision detection and response
        """
        self.check_collisions_precise()
    
    def handle_blob_collision(self):
        """
        Physics formula: m1*v1 + m2*v2 = m1*v1' + m2*v2'
        For elastic collision, we also conserve kinetic energy.
        """
        self.handle_blob_collision_precise()

    def draw(self):
        """
        draw everything on screen
        """
        # clear screen with background color
        self.screen.fill(BACKGROUND_COLOR)

        # draw ground line
        pygame.draw.line(self.screen, FLOOR_COLOR, (0, self.ground_level), (SCREEN_WIDTH, self.ground_level), 3)

        # now left wall
        wall_top_limit = 120
        pygame.draw.line(self.screen, WALL_COLOR, (self.wall_x, wall_top_limit), (self.wall_x, self.ground_level), 8)

        # now blobs
        if self.left_blob and self.right_blob:
            self.left_blob.draw(self.screen)
            self.right_blob.draw(self.screen)
        
        # collision counter
        font = pygame.font.Font(None, 36)
        text = font.render(f"Collision: {self.collision_count}", True, (255, 255, 255))
        self.screen.blit(text, (10, 10))

        # show pi approximation
        if self.right_blob: 
            mass_ratio = self.right_blob.mass / self.left_blob.mass
            expected = math.pi * math.sqrt(mass_ratio)
            font_small = pygame.font.Font(None, 24)
            pi_text = font_small.render(f"Expected: {expected:.1f} (π×√{int(mass_ratio)})", True, (200, 255, 200))
            self.screen.blit(pi_text, (10, 50))

            if mass_ratio > 0:
                current_pi_approximation = self.collision_count / math.sqrt(mass_ratio)
                current_pi_approx = self.collision_count / math.sqrt(mass_ratio)
                approx_text = font_small.render(f"Current π approximation: {current_pi_approx:.4f}", True, (255, 255, 100))
                self.screen.blit(approx_text, (10, 80))

        font_small = pygame.font.Font(None, 24)
        instructions = [
            "left blob (red) starts stationary",
            "right blob (blue) has inital velocity",
            "Press ESC to quit"
        ]
        for i, instruction in enumerate(instructions):
            text = font_small.render(instruction, True, (200, 200, 200))
            self.screen.blit(text, (10, SCREEN_HEIGHT - 100 + i * 20))

        pygame.display.flip()

    def run(self):
        """
        Main game loop
        """
        right_mass = self.get_user_input()
        self.setup_blobs(right_mass)

        print(f"\n Simulation Started")
        print(f"Left blob: mass = 1kg, velocity = 0")
        print(f"Right blob: mass = {right_mass}kg, velocity = 1 m/s (visual scaling applied)")
        print("Close the windor or press ESC to quit")

        while self.running:
            dt = self.clock.tick(60) / 1000.0

            # handle closing window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            if self.left_blob and self.right_blob:
                # Decide whether to use burst mode or normal mode
                if self.should_use_burst_mode():
                    print(f"\nEntering BURST MODE - Current collisions: {self.collision_count}")
                    print("Running fast physics calculations...")
                    
                    success = self.run_physics_burst(2000)  # Run 2000 physics steps quickly
                    
                    if not success:  # User quit during burst
                        break
                        
                    print(f"Burst complete - Collisions now: {self.collision_count}")
                else:
                    # Normal mode - good for watching the final collisions
                    speed_multiplier = min(50, self.calculate_adpative_speed())  # Cap at 50 for stability
                    
                    for _ in range(speed_multiplier):
                        self.left_blob.update_position(dt / speed_multiplier, self.wall_x)  # Wall-aware movement
                        self.right_blob.update_position(dt / speed_multiplier)
                        self.check_collisions()
                        
                        # Stop if objects are essentially at rest
                        if (abs(self.left_blob.velocity) < 0.001 and 
                            abs(self.right_blob.velocity) < 0.001):
                            print(f"\nSimulation Complete!")
                            print(f"Total collisions: {self.collision_count}")
                            mass_ratio = self.right_blob.mass / self.left_blob.mass
                            pi_approximation = self.collision_count / math.sqrt(mass_ratio)
                            print(f"π approximation: {pi_approximation:.6f}")
                            print(f"Actual π: {math.pi:.6f}")
                            print(f"Error: {abs(pi_approximation - math.pi):.6f}")

            # draw everything
            self.draw()

        # clean
        pygame.quit()
        sys.exit()