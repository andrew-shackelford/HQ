from PIL import Image
import pytesseract
import argparse
import os
import subprocess
import time

class OCR:

    def __init__(self, directory='~/Documents/hq/', phone_type='x'):
        self.directory = directory
        self.phone_type = phone_type
        self.img = None
        if self.phone_type == 'x':
            self.q_x = 60
            self.q_y = 280
            self.q_width = 700
            self.q_height = 580
            self.a_x = 100
            self.a1_y = 650
            self.a2_y = 775
            self.a3_y = 900
            self.a_width = 650
            self.a1_height = 710
            self.a2_height = 835
            self.a3_height = 960

    def get_quicktime_image(self):
        if self.phone_type == 'x':
            output = subprocess.check_output([
                'osascript',
                '-e',
                'tell app "Quicktime Player" to id of window 1'
            ])
            window_id = int(output.strip())
            subprocess.call([
                'screencapture',
                '-t', 'jpg',
                '-x',
                '-r',
                '-o',
                '-l{}'.format(window_id),
                'hq.png'
            ])
            self.img = Image.open('hq.png')
            os.remove('hq.png')

            self.question = self.img.crop((self.q_x, self.q_y, self.q_width, self.q_height))
            self.answer_1 = self.img.crop((self.a_x, self.a1_y, self.a_width, self.a1_height))
            self.answer_2 = self.img.crop((self.a_x, self.a2_y, self.a_width, self.a2_height))
            self.answer_3 = self.img.crop((self.a_x, self.a3_y, self.a_width, self.a3_height))

            self.question.save("q.png")
            self.answer_1.save("a1.png")
            self.answer_2.save("a2.png")
            self.answer_3.save("a3.png")


    def ocr_image(self):
        pass

def main():
    ocr = OCR()
    print(time.time())
    ocr.get_quicktime_image()
    print(time.time())


if __name__ == "__main__":
    main()
