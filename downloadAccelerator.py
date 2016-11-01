from requests import get, head
import threading
import time
import argparse


class DownThread(threading.Thread):
    def __init__(self, url, begin, end, debug):
        threading.Thread.__init__(self)

        self.begin = begin
        self.end = end
        self.content = []
        self.url = url
        self.debug = debug

    def run(self):
        self.content = get_content(self.url, self.begin, self.end)
        # if self.debug:
        #     print self.content


def get_content(url, start=0, end=99):
    headers = {'Range': 'bytes=%s-%s' % (start, end), 'Accept-Encoding': 'identity'}
    r = get(url, headers=headers)
    return r.content


def get_total_bytes(url):
    h = head(url)
    if h.headers['Content-Length'] == "None":
        return 0
    return h.headers['Content-Length']


def main(url="", num_threads=1, debug=False):

    total_bytes = int(get_total_bytes(url))
    if total_bytes <= 0:
        print "This page doesn't have a valid Content-Length field."
        return
    split_url = url.split('/')
    name = split_url[-1]
    if url[-1] == '/':
        name = "index.html"
    if debug:
        print "name is ", name
    my_file = open(name, 'wb')

    if num_threads <= 0:
        print "The number of threads must be greater than zero."
        return

    current_start = 0
    step = total_bytes / int(num_threads) - 1
    # print "step is ", step
    current_end = step
    threads = []

    for i in range(0, int(num_threads)):
        if debug:
            print "current_start is " + str(current_start)
            print "current_end is " + str(current_end)
        temp = DownThread(url, current_start, current_end, debug)
        threads.append(temp)
        current_start += step + 1
        current_end = current_start + step
        # If it's the second to last thread
        if i == (int(num_threads) - 2):
            current_end += total_bytes % int(num_threads)
    thread_bytes = 0

    for thread in threads:
        thread.start()
        if debug:
            print thread, " has started"

    for thread in threads:
        thread.join()
        if debug:
            print thread, " has joined and printed ", len(thread.content), " bytes"
        my_file.write(thread.content)
        thread_bytes += len(thread.content)

    if debug:
        print "thread_bytes is ", thread_bytes
        print "total_bytes is ", total_bytes

    return total_bytes


# Small File
# url = "http://www2.census.gov/geo/tiger/TIGER2013/TRACT/tl_2013_10_tract.zip"
# medium file
# url = "http://www2.census.gov/geo/tiger/TIGER2013/EDGES/tl_2013_35005_edges.zip"
# Large File
# url = "http://www2.census.gov/geo/tiger/TGRGDB13/tlgdb_2013_a_39_oh.gdb.zip"
# url = "https://www.microsoft.com/en-us/research/wp-content/uploads/2014/11/WhatsaSysadminToDo.pdf"
parser = argparse.ArgumentParser()
parser.add_argument("-n", help="The number of threads you want. To use the default is 1.", default=1)
parser.add_argument("url", help="The url you want to download.")
parser.add_argument("-d", help="If you want the debug messages. Use 'f' for False and 't' for True.", default=False)
args = parser.parse_args()
num_threads = args.n
d = args.d
debug = False
if d == 't':
    debug = True
elif d == 'f':
    debug = False


start_time = time.time()
url = args.url
total_bytes = main(url, num_threads, debug)

print url, " ", num_threads, "thread(s) ", total_bytes, ("bytes %s seconds" % (time.time() - start_time))
