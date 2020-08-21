from PIL import Image, ImageDraw

def randomNoise(*args):
    pass

def grayShades(pix, draw, width, height):
    for i in range(width):
        for j in range(height):
            r = pix[i, j][0]
            g = pix[i, j][1]
            b = pix[i, j][2]
            average = (r + g + b) // 3
            draw.point((i, j), (average, average, average))
    return pix

if __name__ == "__main__":
    pass