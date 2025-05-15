#!/usr/bin/env python3
"""
Icon Generator for Unique Browser
Creates a simple browser icon in multiple sizes and formats
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_browser_icon(output_dir="icons", sizes=[16, 32, 48, 64, 128, 256], formats=["ico", "png"]):
    """
    Create a modern browser icon in multiple sizes and formats

    Args:
        output_dir (str): Directory to save icons
        sizes (list): List of icon sizes to generate
        formats (list): List of formats to save (ico, png)
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate icons for each size
    for size in sizes:
        # Create a new image with transparent background
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calculate dimensions
        padding = int(size * 0.08)  # Reduced padding for more space

        # Create a gradient background for the icon (circular gradient)
        for y in range(size):
            for x in range(size):
                # Calculate distance from center
                distance = ((x - size/2)**2 + (y - size/2)**2)**0.5
                max_distance = (size/2)**0.5 * 1.5

                # Normalize distance to 0-1 range
                normalized_distance = min(1.0, distance / max_distance)

                # Create gradient from teal to deep blue
                r = int(0 + (20 - 0) * normalized_distance)
                g = int(150 + (80 - 150) * normalized_distance)
                b = int(180 + (220 - 180) * normalized_distance)

                # Set pixel if it's within the circular boundary
                if distance <= size/2 - padding/2:
                    img.putpixel((x, y), (r, g, b, 255))

        # Add a subtle outer glow
        if size >= 32:
            # Create a circular mask for the glow
            mask = Image.new('L', (size, size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([(padding/2, padding/2), (size-padding/2, size-padding/2)], fill=255)

            # Create a blurred version for the glow
            glow = Image.new('RGBA', (size, size), (0, 180, 200, 0))
            glow_draw = ImageDraw.Draw(glow)
            glow_draw.ellipse([(padding/4, padding/4), (size-padding/4, size-padding/4)], fill=(0, 180, 200, 120))

            # Apply the glow with the mask
            if size >= 64:
                for i in range(3):
                    glow = glow.filter(ImageFilter.GaussianBlur(radius=size/30))
                img = Image.alpha_composite(glow, img)

        # Draw a stylized globe in the center
        if size >= 32:
            center_x = size // 2
            center_y = size // 2
            radius = int(size * 0.35)  # Larger globe

            # Draw the globe base (gradient from light blue to darker blue)
            for y in range(center_y - radius, center_y + radius + 1):
                for x in range(center_x - radius, center_x + radius + 1):
                    # Check if the pixel is within the circle
                    if ((x - center_x)**2 + (y - center_y)**2) <= radius**2:
                        # Calculate normalized position for gradient
                        nx = (x - (center_x - radius)) / (2 * radius)
                        ny = (y - (center_y - radius)) / (2 * radius)

                        # Create a radial gradient
                        distance = ((nx - 0.5)**2 + (ny - 0.5)**2)**0.5

                        # Adjust colors for a more vibrant globe with teal/turquoise tones
                        r = int(max(0, min(255, 50 - distance * 30)))
                        g = int(max(0, min(255, 200 - distance * 60)))
                        b = int(max(0, min(255, 220 - distance * 40)))

                        # Only set pixel if it's within bounds
                        if 0 <= x < size and 0 <= y < size:
                            img.putpixel((x, y), (r, g, b, 255))

            # Draw enhanced continents with 3D effect
            if size >= 48:
                # Base continent color (darker green)
                continent_color = (30, 130, 90, 255)

                # Highlight color for 3D effect
                highlight_color = (40, 160, 110, 255)

                # Shadow color for 3D effect
                shadow_color = (20, 100, 70, 255)

                # Draw North America with 3D effect
                na_points = [
                    (center_x - int(radius * 0.5), center_y - int(radius * 0.3)),
                    (center_x - int(radius * 0.2), center_y - int(radius * 0.5)),
                    (center_x + int(radius * 0.1), center_y - int(radius * 0.2)),
                    (center_x - int(radius * 0.3), center_y + int(radius * 0.1))
                ]
                draw.polygon(na_points, fill=continent_color)

                # Add highlight to North America (slightly offset)
                if size >= 64:
                    na_highlight = [(x + 1, y - 1) for x, y in na_points]
                    draw.polygon(na_highlight, fill=highlight_color)
                    # Blend the two polygons
                    draw.polygon(na_points, fill=continent_color)

                # Draw Europe/Africa with more detail
                eu_points = [
                    (center_x + int(radius * 0.1), center_y - int(radius * 0.4)),
                    (center_x + int(radius * 0.3), center_y - int(radius * 0.1)),
                    (center_x + int(radius * 0.2), center_y + int(radius * 0.4)),
                    (center_x - int(radius * 0.1), center_y + int(radius * 0.1))
                ]
                draw.polygon(eu_points, fill=continent_color)

                # Add highlight to Europe/Africa
                if size >= 64:
                    eu_highlight = [(x + 1, y - 1) for x, y in eu_points]
                    draw.polygon(eu_highlight, fill=highlight_color)
                    draw.polygon(eu_points, fill=continent_color)

                # Draw Asia/Australia with more detail
                as_points = [
                    (center_x + int(radius * 0.4), center_y - int(radius * 0.3)),
                    (center_x + int(radius * 0.6), center_y),
                    (center_x + int(radius * 0.3), center_y + int(radius * 0.3)),
                    (center_x + int(radius * 0.5), center_y + int(radius * 0.5))
                ]
                draw.polygon(as_points, fill=continent_color)

                # Add highlight to Asia/Australia
                if size >= 64:
                    as_highlight = [(x + 1, y - 1) for x, y in as_points]
                    draw.polygon(as_highlight, fill=highlight_color)
                    draw.polygon(as_points, fill=continent_color)

                # Add small islands for larger icons
                if size >= 96:
                    # Pacific islands
                    draw.ellipse(
                        [(center_x - int(radius * 0.1), center_y + int(radius * 0.2)),
                         (center_x, center_y + int(radius * 0.3))],
                        fill=continent_color
                    )

                    # Indonesia/Philippines
                    draw.ellipse(
                        [(center_x + int(radius * 0.4), center_y + int(radius * 0.1)),
                         (center_x + int(radius * 0.5), center_y + int(radius * 0.2))],
                        fill=continent_color
                    )

                    # Add a small Antarctica
                    ant_points = [
                        (center_x - int(radius * 0.2), center_y + int(radius * 0.6)),
                        (center_x + int(radius * 0.2), center_y + int(radius * 0.6)),
                        (center_x, center_y + int(radius * 0.7))
                    ]
                    draw.polygon(ant_points, fill=continent_color)

            # Add enhanced 3D effects with multiple highlights and reflections
            if size >= 64:
                # Main highlight (top-left quadrant)
                highlight = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                highlight_draw = ImageDraw.Draw(highlight)

                # Create a white-to-transparent gradient for the top-left quadrant
                for y in range(center_y - radius, center_y + 1):
                    for x in range(center_x - radius, center_x + 1):
                        # Check if the pixel is within the circle
                        if ((x - center_x)**2 + (y - center_y)**2) <= radius**2:
                            # Calculate distance from top-left of circle
                            dx = x - (center_x - radius)
                            dy = y - (center_y - radius)

                            # Normalize to 0-1
                            nx = dx / radius
                            ny = dy / radius

                            # Create highlight intensity
                            intensity = max(0, 1 - (nx + ny) / 1.2)
                            alpha = int(120 * intensity)  # Increased intensity

                            # Only set pixel if it's within bounds
                            if 0 <= x < size and 0 <= y < size:
                                highlight.putpixel((x, y), (255, 255, 255, alpha))

                # Apply the main highlight
                img = Image.alpha_composite(img, highlight)

                # Add a secondary highlight (specular reflection)
                if size >= 96:  # Only for larger icons
                    specular = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                    spec_radius = int(radius * 0.3)
                    spec_center_x = center_x - int(radius * 0.3)
                    spec_center_y = center_y - int(radius * 0.3)

                    # Create a small bright spot
                    for y in range(spec_center_y - spec_radius, spec_center_y + spec_radius):
                        for x in range(spec_center_x - spec_radius, spec_center_x + spec_radius):
                            # Check if within the small circle
                            dist = ((x - spec_center_x)**2 + (y - spec_center_y)**2)**0.5
                            if dist <= spec_radius:
                                # Create a radial gradient for the specular highlight
                                intensity = 1 - (dist / spec_radius)
                                alpha = int(200 * intensity**2)  # Sharper falloff

                                # Only set pixel if it's within bounds
                                if 0 <= x < size and 0 <= y < size:
                                    specular.putpixel((x, y), (255, 255, 255, alpha))

                    # Apply the specular highlight
                    img = Image.alpha_composite(img, specular)

                # Add a subtle rim light on the right edge
                rim_light = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                for y in range(center_y - radius, center_y + radius):
                    # Calculate x position on the right edge of the circle
                    x_edge = int(center_x + (radius**2 - (y - center_y)**2)**0.5)
                    if x_edge >= size:
                        continue

                    # Create a small gradient from the edge inward
                    for x in range(max(0, x_edge - int(radius * 0.15)), x_edge + 1):
                        if 0 <= x < size and 0 <= y < size:
                            # Calculate intensity based on distance from edge
                            intensity = 1 - ((x_edge - x) / (radius * 0.15))
                            alpha = int(70 * intensity)
                            rim_light.putpixel((x, y), (180, 230, 255, alpha))  # Slight blue tint

                # Apply the rim light
                img = Image.alpha_composite(img, rim_light)

        # Add enhanced shadow effects for more dimension
        if size >= 48:
            # Create main drop shadow
            shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow)

            # Draw an ellipse at the bottom for shadow
            shadow_height = int(size * 0.12)  # Slightly taller shadow
            shadow_offset = int(size * 0.03)  # Slight offset for 3D effect
            shadow_draw.ellipse(
                [(center_x - radius + shadow_offset, center_y + radius - shadow_height/2),
                 (center_x + radius + shadow_offset, center_y + radius + shadow_height/2)],
                fill=(0, 0, 0, 100)  # Darker shadow
            )

            # Blur the shadow
            if size >= 64:
                shadow = shadow.filter(ImageFilter.GaussianBlur(radius=size/25))  # More blur

            # Add a second, larger and softer shadow for more depth
            if size >= 96:
                outer_shadow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                outer_shadow_draw = ImageDraw.Draw(outer_shadow)

                # Larger ellipse
                outer_shadow_draw.ellipse(
                    [(center_x - radius*1.1 + shadow_offset, center_y + radius - shadow_height),
                     (center_x + radius*1.1 + shadow_offset, center_y + radius + shadow_height*1.5)],
                    fill=(0, 0, 0, 50)  # More transparent
                )

                # More blur for outer shadow
                outer_shadow = outer_shadow.filter(ImageFilter.GaussianBlur(radius=size/15))

                # Create a new image with both shadows and the main image
                final_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                final_img = Image.alpha_composite(final_img, outer_shadow)
                final_img = Image.alpha_composite(final_img, shadow)
                final_img = Image.alpha_composite(final_img, img)
            else:
                # Create a new image with just the main shadow and the image
                final_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                final_img = Image.alpha_composite(final_img, shadow)
                final_img = Image.alpha_composite(final_img, img)

            img = final_img

        # Save in each requested format
        for fmt in formats:
            if fmt.lower() == "ico" and size in [16, 32, 48, 64, 128, 256]:
                # For ICO format, we'll collect all sizes and save them in one file later
                img.save(f"{output_dir}/unique_browser_{size}.png", "PNG")
            elif fmt.lower() == "png":
                img.save(f"{output_dir}/unique_browser_{size}.png", "PNG")

    # Create ICO file with multiple sizes if requested
    if "ico" in formats:
        # Get all the PNG files we just created
        ico_sizes = [s for s in sizes if s in [16, 32, 48, 64, 128, 256]]
        if ico_sizes:
            images = []
            for size in ico_sizes:
                img_path = f"{output_dir}/unique_browser_{size}.png"
                if os.path.exists(img_path):
                    images.append(Image.open(img_path))

            # Save as ICO if we have images
            if images:
                images[0].save(
                    f"{output_dir}/unique_browser.ico",
                    format="ICO",
                    sizes=[(img.width, img.height) for img in images]
                )
                print(f"Created ICO file with sizes: {[img.size for img in images]}")

    print(f"Icons created in {output_dir} directory")
    return f"{output_dir}/unique_browser.ico"

if __name__ == "__main__":
    icon_path = create_browser_icon()
    print(f"Main icon file: {icon_path}")
