from PIL import Image, ImageDraw, ImageFont

#1.创建图片
img = Image.new(mode='RGB', size=(120, 30), color=(255, 255, 255))

#2.创建画笔，用于在图片上画任意内容
draw = ImageDraw.Draw(img, mode='RGB')
# 第一个参数：表示字体文件路径
# 第二个参数：表示字体大小
font = ImageFont.truetype("Monaco.ttf", 28)
# 第一个参数：表示起始坐标
# 第二个参数：表示写入内容
# 第三个参数：表示颜色
# 第四个参数：表示字体
draw.text((0,0), 'python', "red", font=font)

# 保存在本地
with open('code.png', 'wb') as f:
    img.save(f, format='png')


