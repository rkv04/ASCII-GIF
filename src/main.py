import sys, os, time
from PIL import Image, ImageEnhance
from abc import ABC, abstractmethod


class GifImage:
    def __init__(self, path_to_file):
        self.__pillow_gif = self.__open_file(path_to_file)
        self.__n_frames = self.__pillow_gif.n_frames
        self.__size = self.__pillow_gif.size
        self.__frame_durations = self.__extract_frame_durations()

    def get_frame(self, index) -> Image.Image:
        self.__pillow_gif.seek(index)
        return self.__pillow_gif.copy()
    
    def get_size(self) -> tuple:
        return self.__size
    
    def get_num_frames(self) -> int:
        return self.__n_frames
    
    def get_frame_durations(self) -> list:
        return self.__frame_durations
        
    def __open_file(self, path_to_file):
        image = Image.open(path_to_file)
        return image
    
    def __extract_frame_durations(self):
        frame_durations = []
        for i in range(self.__n_frames):
            self.__pillow_gif.seek(i)
            frame_durations.append(self.__pillow_gif.info.get('duration', 100))
        return frame_durations

    # def __validate_format(self):
    #     if self.__pillow_gif.format != 'GIF':
    #         raise Exception('GIF format required!')


class GifProcessor:
    def __init__(self):
        pass

    def gif_to_ascii_frames(self, gif: GifImage, width: int, height: int, charset: str) -> list:
        ascii_frames = []
        for i in range(0, gif.get_num_frames()):
            gif_frame = gif.get_frame(i)
            grayscaled_frame = self.__convert_frame_to_grayscale(gif_frame)
            resized_frame = self.__resize_frame(grayscaled_frame, width, height)
            prepared_frame = self.__set_contrast(resized_frame, 3.0)
            ascii_frame = self.__frame_to_ascii(prepared_frame, charset)
            ascii_frames.append(ascii_frame)
        return ascii_frames

    def __frame_to_ascii(self, frame: Image.Image, charset: str):
        frame_width = frame.size[0]
        charset_length = len(charset)
        pixels_bright = list(frame.getdata())
        ascii_chars = []
        for pixel_bright in pixels_bright:
            index = int(pixel_bright / 255 * (charset_length - 1))
            ascii_chars.append(charset[index])
        ascii_frame = '';
        for i in range(0, len(ascii_chars), frame_width):
            ascii_frame += "".join(ascii_chars[i:i + frame_width]) + '\n'
        return ascii_frame

    def __set_contrast(self, frame: Image.Image, contrast: float):
        return ImageEnhance.Contrast(frame).enhance(contrast)

    def __resize_frame(self, frame: Image.Image, width: int, height: int) -> Image.Image:
        original_width, original_height = frame.size
        ratio = original_height / original_width
        new_height = int(width * ratio * 0.5)
        return frame.resize((width, new_height))
    
    def __convert_frame_to_grayscale(self, frame: Image.Image):
        return frame.convert('L')


class OutputInterface(ABC):
    @abstractmethod
    def render(self, frame):
        pass


class ConsoleDisplay(OutputInterface):
    def render(self, frame):
        os.system('clear')
        print(frame)


class AsciiAnimation:
    def __init__(self, ascii_frames: list, frame_durations: list, out: OutputInterface):
        self.__ascii_frames = ascii_frames
        self.__frame_durations = frame_durations
        self.__out = out

    def play(self):
        while True:
            for frame_number, ascii_frame in enumerate(self.__ascii_frames):
                self.__out.render(ascii_frame)
                self.__delay(self.__frame_durations[frame_number])

    def __delay(self, ms: int):
        time.sleep(ms / 1000)


def main():
    gif = GifImage('./img/4.gif')
    gif_processor = GifProcessor()
    ascii_frames = gif_processor.gif_to_ascii_frames(gif, width=180, height=100, charset=" .:-=+*#%@")
    console_display = ConsoleDisplay()
    animation = AsciiAnimation(ascii_frames, gif.get_frame_durations(), console_display)
    animation.play()


if __name__ == '__main__':
    main()

