from PIL import Image
import pytesseract
import argparse
import cv2
import os

class OCR:

    def __init__(self, directory='~/Documents/hq/', phone_type='x'):
        self.directory = directory
        self.phone_type = phone_type




