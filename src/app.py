import string
from argparse import ArgumentParser, ArgumentTypeError

from PIL import ImageFont, Image, ImageDraw
from SingleLog.log import Logger

input_string = None
delay = 100
frame = 4


def check_positive(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


if __name__ == '__main__':
    logger = Logger('app')

    parser = ArgumentParser()
    parser.add_argument('-t', '--text', help="Any text you want to convert to gif", required=True)
    parser.add_argument('-f', '--frame', type=check_positive, default=5,
                        help="Frames number for each text between text")
    parser.add_argument('-d', '--delay', type=check_positive, default=100, help="The delay for each frame")
    args = parser.parse_args()

    input_string = args.text
    frame = args.frame
    delay = args.delay

    logger.debug('text', args.text)
    logger.debug('frame', frame)
    logger.debug('delay', delay)

    image_size = 100
    # load font
    font = ImageFont.truetype('/System/Library/Fonts/Arial Unicode.ttf', image_size, index=0)

    images = [Image.new('RGB', (image_size, image_size), (255, 255, 255))]
    for i, text in enumerate(input_string):

        logger.debug('text', text)
        text = text.strip()
        if text in string.whitespace:
            logger.debug('pass')
            continue

        # create image with white
        img = Image.new('RGB', (image_size, image_size), (255, 255, 255))
        d = ImageDraw.Draw(img)

        if text in string.ascii_letters:
            w, h = d.textsize(text, font=font)
            start_x = int((image_size - w) / 2)
        else:
            start_x = 0

        logger.debug('start x', start_x)
        # draw text in image
        d.text((start_x, -20), text, fill='black', font=font)

        # write image to file for debug
        # import io
        #
        # s = io.BytesIO()
        # img.save(s, 'png')
        # in_memory_file = s.getvalue()
        #
        # with open(f'{i}.png', 'wb') as f:
        #     f.write(in_memory_file)

        images.append(img)
    images.append(Image.new('RGB', (image_size, image_size), (255, 255, 255)))

    output_img = []
    for i, image in enumerate(images[:-1]):

        for f in range(1, frame):
            img = Image.new('RGB', (image_size, image_size), (255, 255, 255))
            w_crop_size_before = f * image_size // frame
            w_crop_size_after = image_size - w_crop_size_before
            img.paste(image.crop((w_crop_size_before, 0, image_size, image_size)), (0, 0))
            img.paste(images[i + 1].crop((0, 0, w_crop_size_before, image_size)), (w_crop_size_after, 0))
            output_img.append(img)

        output_img.append(images[i + 1])

    output_img.pop()

    output_name = f'{input_string[:3]} in f {frame} d {delay}.gif'

    output_img[0].save(
        fp=output_name, format='GIF', append_images=output_img[1:], save_all=True,
        duration=delay,
        loop=0)

    logger.info(output_name, 'generated')
