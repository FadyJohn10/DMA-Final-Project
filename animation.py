import board
import neopixel
import time
from digitalio import DigitalInOut, Direction
import os

external_power = DigitalInOut(board.EXTERNAL_POWER)
external_power.direction = Direction.OUTPUT
external_power.value = True
num_pixels = 256
pixels = neopixel.NeoPixel(board.EXTERNAL_NEOPIXELS, num_pixels, brightness=0.2)

# figure out which pixel number corresponds to x,y position as we have 4 8*8 matrices
def get_pixel_index(x, y):
    board_x = x // 8
    board_y = y // 8
    local_x = x % 8
    local_y = y % 8
    
    board_num = board_y * 2 + board_x
    offset = board_num * 64
    idx = local_y * 8 + local_x
    
    return offset + idx

def read_bmp_pixel(filename, x, y):
    with open(filename, 'rb') as f:
        f.seek(10)
        offset = int.from_bytes(f.read(4), 'little')
        
        f.seek(18)
        width = int.from_bytes(f.read(4), 'little')
        height = int.from_bytes(f.read(4), 'little')
        
        # bmp files are upside down for some reason
        row = height - 1 - y
        
        row_size = ((width * 3 + 3) // 4) * 4
        pixel_offset = offset + (row * row_size) + (x * 3)
        
        f.seek(pixel_offset)
        b = f.read(1)[0]
        g = f.read(1)[0]
        r = f.read(1)[0]
        
        return (r, g, b)

animation_dir = "/output_neopixel_bmp"
frame_files = []

files = os.listdir(animation_dir)
frame_files = sorted([f for f in files if f.endswith('.bmp')])


print(f"found {len(frame_files)} frames")

# main animation loop
if len(frame_files) == 0:
    print("no frames found!")
else:
    while True:
        for frame_file in frame_files:
            frame_path = animation_dir + "/" + frame_file
            
            # go through each pixel and set its color
            for y in range(16):
                for x in range(16):
                    r, g, b = read_bmp_pixel(frame_path, x, y)
                    idx = get_pixel_index(x, y)
                    pixels[idx] = (r, g, b)
            
            pixels.show()