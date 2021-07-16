#!/bin/python3
# Requires Python 3

from collections import namedtuple
import os.path
import urllib.request
import sys
import time
import tarfile

# copied from:
# https://blog.shichao.io/2012/10/04/progress_speed_indicator_for_urlretrieve_in_python.html
def show_progress(count, block_size, total_size):
    global start_time
    if count == 0:
        start_time = time.time()
        return
    duration = time.time() - start_time
    progress_size = int(count * block_size)
    speed = int(progress_size / (1024 * duration))
    percent = int(count * block_size * 100 / total_size)
    sys.stdout.write("\r%d%%, %d MB, %d KB/s, %d seconds passed" %
                    (percent, progress_size / (1024 * 1024), speed, duration))
    sys.stdout.flush()

Download = namedtuple('Download', ['name', 'path', 'url', 'ext', 'description', 'should_untar'])


downloads = [
    Download(
        name = 'span model (probability density)',
        path = 'models/span_density_softmax.tar.gz',
        url = 'https://www.dropbox.com/s/1pmid0cdrp49efv/span_density_softmax.tar.gz?dl=1',
        ext = '',
        description = "Span detector model which is different from that of FitzGerald et al. (2018) in that"
        " it estimates a probability distribution over answer spans (matching the annotated distribution)"
        " rather that acting as a binary classifier. This doesn't work quite as well on raw metrics like F1"
        " but could be useful in some circumstances.",
        should_untar = False,
    ),
    Download(
        name = 'span -> question model',
        path = 'models/span_to_question.tar.gz',
        url = 'https://www.dropbox.com/s/monbzb3afkmo3j5/span_to_question.tar.gz?dl=1',
        ext = '',
        description = "QA-SRL question generator that conditions on an answer span.",
        should_untar = False,
    ),
    Download(
        name = 'span -> simplified question model',
        path = 'models/span_to_simplified_question.tar.gz',
        url = 'https://www.dropbox.com/s/rvuwcl9kedsb2z4/span_to_simplified_question.tar.gz?dl=1',
        ext = '',
        description = "Question generator conditioning on answer spans and producing"
        " simplified questions with normalized tense, aspect, negation, modality, and animacy."
        " Used in 'Inducing Semantic Roles Without Syntax' (https://github.com/julianmichael/qasrl-roles).",
        should_untar = False,
    ),
]

def get_download_option_prompt(num, download):
    if os.path.exists(download.path):
        color = "\u001b[32m"
        icon  = "[downloaded]"
    else:
        color = "\u001b[33m"
        icon  = "[not downloaded]"

    letter = chr(num + 97)

    desc = ("\n" + download.description).replace("\n", "\n     ")

    return u"  {}) {}{} {}\u001b[0m ".format(letter, color, download.name, icon) + desc + "\n"


def construct_prompt():
    prompt = "What would you like to download? ('all' to download all, 'q' to quit)\n"
    for i, download in enumerate(downloads):
        prompt += "\n" + get_download_option_prompt(i, download)
    return prompt

def download_item(download):
    print("Downloading {}.".format(download.name))
    if len(choice.ext) > 0 and choice.should_untar:
       tarpath = choice.path + choice.ext
       urllib.request.urlretrieve(choice.url, tarpath, show_progress)
       result = tarfile.open(tarpath)
       result.extractall(os.path.dirname(choice.path))
       result.close()
       os.remove(tarpath)
    else:
       urllib.request.urlretrieve(choice.url, choice.path, show_progress)
    print("\nDownload complete: {}".format(download.path))

a = ord('a')

should_refresh_prompt = True
while True:
    if should_refresh_prompt:
        print(construct_prompt())
    optstr = "".join([chr(i) for i in range(a, a + len(downloads))])
    print("Choose a subset ({}/*/q): ".format(optstr), end='')
    should_refresh_prompt = False
    response = input()
    if "quit".startswith(response.lower()):
        break
    elif response.lower() == "*":
        for i, download in enumerate(downloads):
            print("{}) {}".format(chr(i + a), download.description))
            if os.path.exists(download.path):
                print("Already downloaded at {}.".format(download.path))
            else:
                download_item(download)
    else:
        for c in response:
            try:
                choice = downloads[ord(c) - a]
            except ValueError or IndexError:
                print("Invalid option: {}".format(response))
                continue
            if os.path.exists(choice.path):
                print("Already downloaded at {}.".format(choice.path))
                print("Re-download? [y/N] ", end='')
                shouldDownloadStr = input()
                if shouldDownloadStr.startswith("y") or \
                shouldDownloadStr.startswith("Y"):
                    download_item(choice)
                    should_refresh_prompt = True
            else:
                download_item(choice)
                should_refresh_prompt = True
