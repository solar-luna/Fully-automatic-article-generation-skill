#!/usr/bin/env python3
"""
Neural Reasoning Cover Art Generator
Creates a sophisticated, museum-quality cover image for the AI autonomous driving article.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
import random
from pathlib import Path

# Canvas dimensions (16:9 ratio, high resolution)
WIDTH = 2560
HEIGHT = 1440

# Color palette
BG_COLOR = (5, 8, 12)  # Deep void dark
PRIMARY_GREEN = (118, 185, 0)  # Nvidia green
SECONDARY_GREEN = (80, 140, 0)  # Darker green
GLOW_GREEN = (150, 220, 50)  # Bright glow
DIM_GREEN = (40, 70, 10)  # Dim pathway
TEXT_COLOR = (240, 242, 245)  # Off-white

def create_neural_network_background(draw):
    """Create layered network of neural connections."""
    # Generate multiple layers of pathways
    for layer in range(3):
        alpha = 30 - layer * 8
        num_paths = 40 - layer * 10

        for _ in range(num_paths):
            # Random start and end points
            x1 = random.randint(0, WIDTH)
            y1 = random.randint(0, HEIGHT)
            x2 = random.randint(0, WIDTH)
            y2 = random.randint(0, HEIGHT)

            # Create curved pathways (Bezier-like)
            control_x = random.randint(0, WIDTH)
            control_y = random.randint(0, HEIGHT)

            # Draw curve segments
            segments = 30
            points = []
            for t in range(segments + 1):
                t_norm = t / segments
                # Quadratic Bezier
                bx = (1-t_norm)**2 * x1 + 2*(1-t_norm)*t_norm * control_x + t_norm**2 * x2
                by = (1-t_norm)**2 * y1 + 2*(1-t_norm)*t_norm * control_y + t_norm**2 * y2
                points.append((bx, by))

            # Draw the pathway
            for i in range(len(points) - 1):
                intensity = int(255 * (1 - abs(i - segments/2) / (segments/2)) * (alpha/100))
                color = (*DIM_GREEN, intensity)
                draw.line([points[i], points[i+1]], width=1, fill=color)

def create_node_network(draw, center_x, center_y, radius):
    """Create a central network of connected nodes representing neural processing."""
    num_nodes = 12
    nodes = []

    # Generate node positions in a circular pattern
    for i in range(num_nodes):
        angle = 2 * math.pi * i / num_nodes
        # Vary the radius for organic feel
        r = radius * (0.7 + 0.3 * math.sin(3 * angle))
        nx = center_x + r * math.cos(angle)
        ny = center_y + r * math.sin(angle)
        nodes.append((nx, ny))

    # Draw connections between nearby nodes
    for i, (x1, y1) in enumerate(nodes):
        for j, (x2, y2) in enumerate(nodes[i+1:], i+1):
            dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)
            if dist < radius * 1.2:
                alpha = int(100 * (1 - dist/(radius*1.2)))
                draw.line([(x1, y1), (x2, y2)], width=2, fill=(*PRIMARY_GREEN, alpha))

    # Draw the nodes themselves with glow effect
    for i, (nx, ny) in enumerate(nodes):
        # Outer glow
        for r_glow in range(15, 0, -2):
            alpha = int(30 * (1 - r_glow/15))
            draw.ellipse([nx-r_glow, ny-r_glow, nx+r_glow, ny+r_glow],
                        fill=(*GLOW_GREEN, alpha))

        # Core node
        node_size = 4 + (i % 3)
        draw.ellipse([nx-node_size, ny-node_size, nx+node_size, ny+node_size],
                    fill=PRIMARY_GREEN)

def create_car_silhouette(draw, center_x, center_y):
    """Create a stylized, minimal car silhouette."""
    scale = 0.8

    # Car body - sleek, modern profile
    body_points = [
        (center_x - 180*scale, center_y + 30*scale),  # Front bottom
        (center_x - 160*scale, center_y),  # Front wheel well
        (center_x - 120*scale, center_y - 25*scale),  # Hood start
        (center_x - 40*scale, center_y - 45*scale),  # Hood end
        (center_x + 20*scale, center_y - 50*scale),  # Windshield base
        (center_x + 80*scale, center_y - 45*scale),  # Roof front
        (center_x + 150*scale, center_y - 35*scale),  # Roof rear
        (center_x + 170*scale, center_y),  # Trunk
        (center_x + 190*scale, center_y + 30*scale),  # Rear bottom
    ]

    # Draw car body as gradient outline
    for i in range(len(body_points) - 1):
        alpha = int(180 * (1 - abs(i - len(body_points)/2) / (len(body_points)/2)))
        draw.line([body_points[i], body_points[i+1]], width=3, fill=(*PRIMARY_GREEN, alpha))

    # Wheels as glowing nodes
    for wheel_x in [center_x - 130*scale, center_x + 130*scale]:
        wheel_y = center_y + 30*scale
        # Glow
        for r_glow in range(20, 0, -3):
            alpha = int(40 * (1 - r_glow/20))
            draw.ellipse([wheel_x-r_glow, wheel_y-r_glow, wheel_x+r_glow, wheel_y+r_glow],
                        fill=(*GLOW_GREEN, alpha))
        # Core
        draw.ellipse([wheel_x-8, wheel_y-8, wheel_x+8, wheel_y+8], fill=PRIMARY_GREEN)

def create_circuit_patterns(draw):
    """Add subtle circuit board patterns."""
    for _ in range(8):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)

        # Horizontal line with dots
        length = random.randint(100, 300)
        draw.line([(x, y), (x+length, y)], width=1, fill=(*DIM_GREEN, 40))

        # Connection dots
        for i in range(random.randint(2, 5)):
            dx = x + random.randint(0, length)
            dy = y + random.choice([-20, 20])
            draw.line([(dx, y), (dx, dy)], width=1, fill=(*DIM_GREEN, 30))
            draw.ellipse([dx-3, dy-3, dx+3, dy+3], fill=(*DIM_GREEN, 50))

def create_gradient_overlay(img):
    """Create a subtle vignette effect."""
    overlay = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Edge darkening
    for i in range(100):
        alpha = int(2 * (1 - i/100))
        draw.rectangle([i, i, WIDTH-i, HEIGHT-i], outline=(0, 0, 0, alpha), width=1)

    return Image.alpha_composite(img.convert('RGBA'), overlay)

def add_text_with_font(img, title, subtitle):
    """Add typography with careful spacing and hierarchy."""
    draw = ImageDraw.Draw(img)

    # Try to load fonts, fall back to default if not available
    font_dir = Path('/home/ubuntu/.claude/skills/canvas-design/canvas-fonts')

    try:
        # Try different font options
        title_font_paths = [
            font_dir / 'Inter' / 'Inter-Bold.ttf',
            font_dir / 'NotoSansSC' / 'NotoSansSC-Bold.ttf',
            font_dir / 'Roboto' / 'Roboto-Bold.ttf',
        ]
        subtitle_font_paths = [
            font_dir / 'Inter' / 'Inter-Regular.ttf',
            font_dir / 'NotoSansSC' / 'NotoSansSC-Regular.ttf',
            font_dir / 'Roboto' / 'Roboto-Regular.ttf',
        ]

        title_font = None
        subtitle_font = None

        for path in title_font_paths:
            if path.exists():
                title_font = ImageFont.truetype(str(path), 72)
                break

        for path in subtitle_font_paths:
            if path.exists():
                subtitle_font = ImageFont.truetype(str(path), 42)
                break

        if title_font is None:
            title_font = ImageFont.load_default()
        if subtitle_font is None:
            subtitle_font = ImageFont.load_default()

    except Exception as e:
        print(f"Font loading error: {e}, using default")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Position text in lower center
    title_y = HEIGHT - 280
    subtitle_y = HEIGHT - 180

    # Measure text for centering
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]

    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

    title_x = (WIDTH - title_width) // 2
    subtitle_x = (WIDTH - subtitle_width) // 2

    # Draw subtitle first (smaller, lighter)
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font,
              fill=(*TEXT_COLOR, 200), anchor='lt')

    # Draw title with subtle shadow
    shadow_offset = 4
    draw.text((title_x + shadow_offset, title_y + shadow_offset), title, font=title_font,
              fill=(*PRIMARY_GREEN, 80), anchor='lt')
    draw.text((title_x, title_y), title, font=title_font,
              fill=TEXT_COLOR, anchor='lt')

def main():
    """Main generation function."""
    print("Creating Neural Reasoning cover art...")

    # Create base image with RGBA
    img = Image.new('RGBA', (WIDTH, HEIGHT), (*BG_COLOR, 255))
    draw = ImageDraw.Draw(img)

    # Layer 1: Neural network background
    print("Generating neural pathways...")
    create_neural_network_background(draw)

    # Layer 2: Circuit patterns
    print("Adding circuit patterns...")
    create_circuit_patterns(draw)

    # Layer 3: Central composition - node network
    center_x = WIDTH // 2
    center_y = HEIGHT // 2 - 50
    print("Creating central neural network...")
    create_node_network(draw, center_x, center_y, 250)

    # Layer 4: Car silhouette integrated into network
    print("Adding vehicle silhouette...")
    create_car_silhouette(draw, center_x, center_y)

    # Layer 5: Gradient overlay for depth
    print("Applying gradient overlay...")
    img = create_gradient_overlay(img)

    # Layer 6: Typography
    print("Adding typography...")
    title = "自动驾驶的AI思考革命"
    subtitle = "Nvidia Alpamayo让汽车学会像人一样推理"
    add_text_with_font(img, title, subtitle)

    # Convert to RGB for final output
    final_img = Image.alpha_composite(
        Image.new('RGBA', (WIDTH, HEIGHT), (*BG_COLOR, 255)),
        img
    ).convert('RGB')

    # Apply subtle sharpening for crispness
    final_img = final_img.filter(ImageFilter.SHARPEN)

    # Save
    output_path = Path('/home/ubuntu/.claude/skills/ai-content-publisher/assets/cover_alpamayo.png')
    final_img.save(output_path, 'PNG', quality=95, optimize=True)

    print(f"Cover art saved to: {output_path}")
    print(f"Dimensions: {WIDTH}x{HEIGHT}")

    return output_path

if __name__ == '__main__':
    main()
