import os
import requests

ACCESS_TOKEN = 'Bearer uqt8a2SlZ0mOLS1pR2xIUvs490eaxxLH9XY9fcXJOpj'

file_name = 'screenshot.png'
path = os.path.dirname(os.path.realpath(__file__))
path_img = r"{}\{}".format(path, file_name)

print(path_img)
print(os.path.basename(path_img))