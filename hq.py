from PIL import Image
import nltk
import pytesseract
import os
import subprocess
import time
import threading
import Queue
import requests
from bs4 import BeautifulSoup

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

class Printer():
    def __init__(self):
        pass

    def print_statement(self, answer, percent, snippet, c, header=True):
        if header:
            print(c + answer + ": " + color.BOLD + color.UNDERLINE + str(percent) + "%" + color.END + c)
        else:
            print(c),
        snippet = snippet.replace(color.END, color.END + c)
        print(snippet)
        print(color.END)

    def print_all(self, q, a1, a2, a3, results):
        new_a1_snips = []
        new_a2_snips = []
        new_a3_snips = []
        for snip in results['a1_snip']:
            for token in results['q_tokens']:
                if token in snip and len(token) > 3:
                    snip = snip.replace(token, color.BOLD + color.UNDERLINE + token + color.END)
            new_a1_snips.append(snip)
        for snip in results['a2_snip']:
            for token in results['q_tokens']:
                if token in snip and len(token) > 3:
                    snip = snip.replace(token, color.BOLD + color.UNDERLINE + token + color.END)
            new_a2_snips.append(snip)
        for snip in results['a3_snip']:
            for token in results['q_tokens']:
                if token in snip and len(token) > 3:
                    snip = snip.replace(token, color.BOLD + color.UNDERLINE + token + color.END)
            new_a3_snips.append(snip)

        if results['a1_per'] > 50:
            self.print_statement(a1, results['a1_per'], new_a1_snips[0], color.BLUE)
            self.print_statement(a1, results['a1_per'], results['t1_snip'][0], color.BLUE)
        elif results['a1_per'] > 25:
            self.print_statement(a1, results['a1_per'], new_a1_snips[0], color.DARKCYAN)
            self.print_statement(a1, results['a1_per'], results['t1_snip'][0], color.DARKCYAN)
        else:
            self.print_statement(a1, results['a1_per'], new_a1_snips[0], color.RED)
            self.print_statement(a1, results['a1_per'], results['t1_snip'][0], color.RED)

        if results['a2_per'] > 50:
            self.print_statement(a2, results['a2_per'], new_a2_snips[0], color.BLUE)
            self.print_statement(a2, results['a2_per'], results['t2_snip'][0], color.BLUE)
        elif results['a2_per'] > 25:
            self.print_statement(a2, results['a2_per'], new_a2_snips[0], color.DARKCYAN)
            self.print_statement(a2, results['a2_per'], results['t2_snip'][0], color.DARKCYAN)
        else:
            self.print_statement(a2, results['a2_per'], new_a2_snips[0], color.RED)
            self.print_statement(a2, results['a2_per'], results['t2_snip'][0], color.RED)

        if results['a3_per'] > 50:
            self.print_statement(a3, results['a3_per'], new_a3_snips[0], color.BLUE)
            self.print_statement(a3, results['a3_per'], results['t3_snip'][0], color.BLUE)
        elif results['a3_per'] > 25:
            self.print_statement(a3, results['a3_per'], new_a3_snips[0], color.DARKCYAN)
            self.print_statement(a3, results['a3_per'], results['t3_snip'][0], color.DARKCYAN)
        else:
            self.print_statement(a3, results['a3_per'], new_a3_snips[0], color.RED)
            self.print_statement(a3, results['a3_per'], results['t3_snip'][0], color.RED)

class Search(threading.Thread):
    def __init__(self, q, id):
        self.q = q
        self.id = id
        self.should_run = True
        threading.Thread.__init__(self)

    def run(self):
        while self.should_run:
            r = requests.get("https://www.google.com/search", params={'q':self.q.get()})

            soup = BeautifulSoup(r.text, "lxml")
            res = soup.find("div", {"id": "resultStats"})
            snippets = []
            for s in soup.find_all("span", {"class" : "st"}):
                snippets.append(s.text)
            self.q.put((res.text, snippets))
            time.sleep(1) #allow for us to pick data back up

    def stop(self):
        self.should_run = False


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

class Answer:

    def __init__(self):
        self.a1_que = Queue.Queue()
        self.a2_que = Queue.Queue()
        self.a3_que = Queue.Queue()
        self.t1_que = Queue.Queue()
        self.t2_que = Queue.Queue()
        self.t3_que = Queue.Queue()

        self.a1_thread = Search(self.a1_que, "a1")
        self.a2_thread = Search(self.a2_que, "a2")
        self.a3_thread = Search(self.a3_que, "a3")
        self.t1_thread = Search(self.t1_que, "t1")
        self.t2_thread = Search(self.t2_que, "t2")
        self.t3_thread = Search(self.t3_que, "t3")

        self.a1_thread.start()
        self.a2_thread.start()
        self.a3_thread.start()
        self.t1_thread.start()
        self.t2_thread.start()
        self.t3_thread.start()

    def num_hits(self, q, a1, a2, a3, term):
        tokens = nltk.word_tokenize(q)
        tagged = nltk.pos_tag(tokens)
        nouns = [word for word,pos in tagged \
            if (pos == 'NN' or pos == 'NNP' or pos == 'NNS' or pos == 'NNPS')]
        downcased = [x.lower() for x in nouns]
        q_nouns = " ".join(downcased)

        self.a1_que.put(q_nouns + ' ' + a1)
        self.a2_que.put(q_nouns + ' ' + a2)
        self.a3_que.put(q_nouns + ' ' + a3)
        self.t1_que.put(term + ' ' + a1)
        self.t2_que.put(term + ' ' + a2)
        self.t3_que.put(term + ' ' + a3)

        time.sleep(0.1) # allow time for threads to get images

        self.a1_hits, self.a1_snippets = self.a1_que.get()
        self.a2_hits, self.a2_snippets = self.a2_que.get()
        self.a3_hits, self.a3_snippets = self.a3_que.get()
        self.t1_hits, self.t1_snippets = self.t1_que.get()
        self.t2_hits, self.t2_snippets = self.t2_que.get()
        self.t3_hits, self.t3_snippets = self.t3_que.get()

        self.a1 = [int(s) for s in self.a1_hits.replace(",", "").split() if s.isdigit()][0]
        self.a2 = [int(s) for s in self.a2_hits.replace(",", "").split() if s.isdigit()][0]
        self.a3 = [int(s) for s in self.a3_hits.replace(",", "").split() if s.isdigit()][0]
        self.t1 = [int(s) for s in self.t1_hits.replace(",", "").split() if s.isdigit()][0]
        self.t2 = [int(s) for s in self.t2_hits.replace(",", "").split() if s.isdigit()][0]
        self.t3 = [int(s) for s in self.t3_hits.replace(",", "").split() if s.isdigit()][0]

        self.a_sum = float(self.a1 + self.a2 + self.a3)
        self.a1_per = round(float(self.a1*100)/self.a_sum, 2)
        self.a2_per = round(float(self.a2*100)/self.a_sum, 2)
        self.a3_per = round(float(self.a3*100)/self.a_sum, 2)

        self.t_sum = float(self.t1 + self.t2 + self.t3)
        self.t1_per = round(float(self.t1*100)/self.t_sum, 2)
        self.t2_per = round(float(self.t2*100)/self.t_sum, 2)
        self.t3_per = round(float(self.t3*100)/self.t_sum, 2)

        return {'a1' : self.a1,
                'a2' : self.a2,
                'a3' : self.a3,
                'a_sum' : self.a_sum,
                'a1_per' : self.a1_per,
                'a2_per' : self.a2_per,
                'a3_per' : self.a3_per,
                'a1_snip' : self.a1_snippets,
                'a2_snip' : self.a2_snippets,
                'a3_snip' : self.a3_snippets,
                't_sum' : self.t_sum,
                't1_per' : self.t1_per,
                't2_per' : self.t2_per,
                't3_per' : self.t3_per,
                't1_snip' : self.t1_snippets,
                't2_snip' : self.t2_snippets,
                't3_snip' : self.t3_snippets,
                'q_tokens' : tokens,
                }

    def stop(self):
        self.a1_thread.stop()
        self.a2_thread.stop()
        self.a3_thread.stop()


class Helper:

    def __init__(self):
        self.imager = Imager()
        self.answer = Answer()
        self.printer = Printer()

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

    def print_hits(self):
        print(self.a1 + ": " + str(self.percent_hits['a1_per']))
        print(self.a2 + ": " + str(self.percent_hits['a2_per']))
        print(self.a3 + ": " + str(self.percent_hits['a3_per']))

    def search_hits(self, term):
        self.percent_hits = self.answer.num_hits(self.q, self.a1, self.a2, self.a3, term)

    def print_all(self):
        self.printer.print_all(self.q, self.a1, self.a2, self.a3, self.percent_hits)

    def stop(self):
        self.q_thread.stop()
        self.a1_thread.stop()
        self.a2_thread.stop()
        self.a3_thread.stop()
        self.answer.stop()

def main():
    helper = Helper()

    while True:
        term = raw_input()
        if term == 'q':
            os._exit(1) # ugly and terrible but whatever
        helper.run_ocr()
        #helper.print_ocr()
        helper.search_hits(term)
        #helper.print_hits()
        helper.print_all()

if __name__ == "__main__":
    main()
