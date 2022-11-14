from PIL import Image, ImageFont, ImageDraw

def create(**kwargs):
    img = Image.open("_server_files/signatures/sample.png")  # Load image from file
    draw = ImageDraw.Draw(img)

    #  ImageFont.truetype(file_name, font_size)
    font = ImageFont.truetype("static/fonts/font_2.ttf", 80)  # load font

    # draw.text((x, y), string,(r,g,b))
    draw.text((20, 100),kwargs.get('n'),(0,0,247),font=font)
    draw.text((50, 170),kwargs.get('s'),(0,0,247),font=font)

    img.save(f'_server_files/signatures/{kwargs.get("u")}_signature.png')