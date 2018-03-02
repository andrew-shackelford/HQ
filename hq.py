from PIL import Image
import pytesseract
import os
import subprocess
import time
import threading
import Queue

class OCR(threading.Thread):

    def __init__(self, q, id):
        self.q = q
        self.id = id
        self.should_run = True
        threading.Thread.__init__(self)

    def run(self):
        while self.should_run:
            s = pytesseract.image_to_string(self.q.get())
            self.q.put(s.replace('\n', ' '))
            time.sleep(1) #allow for us to pick image back up

    def stop(self):
        self.should_run = False

class Imager:

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

            self.q_img = self.img.crop((self.q_x, self.q_y, self.q_width, self.q_height))
            self.a_img_1 = self.img.crop((self.a_x, self.a1_y, self.a_width, self.a1_height))
            self.a_img_2 = self.img.crop((self.a_x, self.a2_y, self.a_width, self.a2_height))
            self.a_img_3 = self.img.crop((self.a_x, self.a3_y, self.a_width, self.a3_height))

class Helper:

    def __init__(self):
        self.imager = Imager()

        self.q_que = Queue.Queue()
        self.a1_que = Queue.Queue()
        self.a2_que = Queue.Queue()
        self.a3_que = Queue.Queue()

        self.q_thread = OCR(self.q_que, "q")
        self.a1_thread = OCR(self.a1_que, "a1")
        self.a2_thread = OCR(self.a2_que, "a2")
        self.a3_thread = OCR(self.a3_que, "a3")

        self.q_thread.start()
        self.a1_thread.start()
        self.a2_thread.start()
        self.a3_thread.start()

    def run_ocr(self):
        self.imager.get_quicktime_image()

        self.q_que.put(self.imager.q_img)
        self.a1_que.put(self.imager.a_img_1)
        self.a2_que.put(self.imager.a_img_2)
        self.a3_que.put(self.imager.a_img_3)

        time.sleep(0.01) # allow time for threads to get images
        os.remove('hq.png') # put this here so it can take as much time as it needs while threads run

        self.q = self.q_que.get()
        self.a1 = self.a1_que.get()
        self.a2 = self.a2_que.get()
        self.a3 = self.a3_que.get()

    def print_ocr(self):
        print(self.q)
        print(self.a1)
        print(self.a2)
        print(self.a3)

    def stop(self):
        self.q_thread.stop()
        self.a1_thread.stop()
        self.a2_thread.stop()
        self.a3_thread.stop()

def main():
    helper = Helper()
    helper.run_ocr()
    helper.print_ocr()
    helper.stop()

if __name__ == "__main__":
    main()
