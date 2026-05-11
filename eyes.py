import time
import numpy as np
import board, digitalio, busio
from adafruit_rgb_display import st7789
from PIL import Image, ImageDraw, ImageOps

def run():
    # Pins
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D24)
    reset_pin = digitalio.DigitalInOut(board.D25)

    try:
        spi = busio.SPI(board.SCLK, MOSI=board.MOSI)
        
        # Force framebuffer size + window offsets
        disp = st7789.ST7789(
            spi,
            cs=cs_pin,
            dc=dc_pin,
            rst=reset_pin,
            width=128,   # visible width
            height=160,  # visible height
            x_offset=2,  # try 0 first
            y_offset=2,  # adjust if screen shifted
            rotation=270
        )
    except Exception as e:
        print(f"Display init failed: {e}")
        return  # Exit gracefully instead of crashing

    # Create full image
    image = Image.new("RGB", (disp.height, disp.width), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    # Your base eye pattern
    eyes_open = np.array([
        [0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0],
        [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
        [0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0],
        [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
        [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
        [1,2,2,0,0,0,1,0,0,1,2,2,0,0,0,1],
        [1,2,2,0,0,0,1,0,0,1,2,2,0,0,0,1],
        [1,2,2,0,0,0,1,0,0,1,2,2,0,0,0,1],
        [1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1],
        [0,1,1,1,1,1,0,0,0,0,1,1,1,1,1,0]
    ])

    def shift_matrix(matrix):
        h, w = matrix.shape
        shift = True

        if matrix[6,1] == 2:
            n = 0		
        elif matrix [6,2] == 2:
            n = 1
        elif matrix [6,3] == 2:
            n = 2
        else:
            shift = False

        if shift == True:
            matrix[6:9, 1+n] = 0
            matrix[6:9, 3+n] = 2
            matrix[6:9, 10+n] = 0
            matrix[6:9, 12+n] = 2
        if shift == False:
            matrix[6:9, 1] = 2
            matrix[6:9, 2] = 2
            matrix[6:9, 10] = 2
            matrix[6:9, 11] = 2
            matrix[6:9, 4] = 0
            matrix[6:9, 5] = 0
            matrix[6:9, 13] = 0
            matrix[6:9, 14] = 0

        return matrix

    def draw_matrix(avatar):

        image = Image.new("RGB", (disp.height, disp.width), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        pixel_size = 8
        avatar_size = 16 * pixel_size
        offset_x = (disp.height - avatar_size) // 2
        offset_y = (disp.width - avatar_size) // 2 + 15

        # --- Draw avatar ---
        for y, row in enumerate(avatar):
            for x, pixel in enumerate(row):
                x0 = offset_x + x * pixel_size
                y0 = offset_y + y * pixel_size
                x1 = x0 + pixel_size
                y1 = y0 + pixel_size
                if pixel == 0:
                    colour = (255,255,255)
                else:
                    colour = (0,0,0)
                draw.rectangle([x0, y0, x1, y1], fill=colour) 
        return image

    # --- Display function ---
    def show(matrix):
        img = draw_matrix(matrix)
        matrix = shift_matrix(matrix)
        disp.image(ImageOps.invert(img))

    # --- Animation loop ---
    while True:
        show(eyes_open)
        time.sleep(2)
