from lxml import html
import requests
import urllib2
import os
import sys
import random
from robobrowser import RoboBrowser

from multiprocessing.dummy import Pool as ThreadPool

artist_name = ''


# Downloads a single image given an image page and a directory to save it
def download_img(deviation_page, directory_to_save):
        # Grab all images within a 'view-deviation' div, since these img elements are on the gallery page
    image_urls = html.fromstring(deviation_page).xpath('//div[@class="dev-view-deviation"]/img/@src')
    filename = ''
    # If image_urls has length 2 then we have scraped a low and high quality image, so take the high quality one
    if len(image_urls) == 2:
        filename = image_urls[1].split('/')[-1]
    elif len(image_urls) == 1:
        filename = image_urls[0].split('/')[-1]
    # If a valid url was available from the img src (image_urls had length greater than 0) then just open the page
    # and grab the image, before saving it to the desktop. NOTE if a file with this name already exists it will
    # be overwritten.
    if filename != '':
        image_file = urllib2.urlopen(image_urls[1])
        # Get rid of the artist's name
        img_name = filename.split('_by_')[0]
        # Extract the file ending as well
        file_ending = filename.split('.')[-1]
        # Piece it back together without the artist's name
        fullname = directory_to_save + img_name + '.' + file_ending
        # And write it to the directory
        if os.path.isfile(fullname):
            fullname = fullname.split('.')[0] + str(random.randrange(0, 100000)) + '.' + file_ending
        try:
            out = open(fullname, "wb")
            out.write(image_file.read())
            out.close()
            return True
        except OSError:
            return False


# Returns all valid urls from a gallery page that link to a deviation page
def get_image_urls(urls):
    valid_urls = []
    for url in urls:
        if artist_name + '.deviantart.com/art' in url:
            valid_urls.append(url)
    return valid_urls


def get_folder(page_url):
    page_url = page_url[7:]
    outer_folder = page_url.split('.')[0]
    cur_dir = ''
    if len(page_url.split("/")) < 3:
        cur_dir = '~\\Desktop\\' + outer_folder + "\\"
    else:
        str_arr = page_url.split("/")
        inner_folder = str_arr[len(str_arr) - 1]
        inner_folder = inner_folder.split("?offset")[0]
        cur_dir = '~\\Desktop\\' + outer_folder + "\\" + inner_folder + "\\"
    if not os.path.isdir(os.path.expanduser(cur_dir)):
        os.mkdir(os.path.expanduser(cur_dir))
    return os.path.expanduser(cur_dir)


def scrape_this_page(page_name):
    page = requests.get(page_name)
    if page.status_code == requests.codes.ok:
        # If a folder on the desktop does not already exist for this given artist, create one, then set it as the
        # directory to save images to
        pictures = get_image_urls(
            html.fromstring(page.content).xpath('//a[not(ancestor::div[@class="gr-body"])]/@href'))
        downloaded_images = []
        s = requests.session()
        s.headers.update({'Referer': 'http://www.deviantart.com/'})
        USERAGENTS = (
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.202 Safari/535.1',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
            'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
            'Opera/9.99 (Windows NT 5.1; U; pl) Presto/9.9.9',
            'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-US) AppleWebKit/530.5 (KHTML, like Gecko) Chrome/ Safari/530.5',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.2 (KHTML, like Gecko) Chrome/6.0',
            'Mozilla/5.0 (Windows; U; Windows NT 6.1; pl; rv:1.9.1) Gecko/20090624 Firefox/3.5 (.NET CLR 3.5.30729)'
        )
        browser = RoboBrowser(history=False, session=s, tries=3, user_agent=random.choice(USERAGENTS))
        browser.open(
            'https://www.deviantart.com/users/login?ref=http%3A%2F%2Fwww.deviantart.com%2F&remember_me=1')
        form = browser.get_forms()[1]
        form['username'] = 'Mesmer12345'
        form['password'] = 'OROsirian#629'
        browser.submit_form(form)
        for picture in pictures:
            # Make sure image has not already been downloaded, and that it is not simply a duplicate url with
            # the comments section open
            if picture not in downloaded_images and '#comments' not in picture:
                browser.open(picture)
                deviation_page = str(browser.parsed)
                if download_img(deviation_page, get_folder(page_name)):
                    print("Grabbed " + picture)
                    downloaded_images.append(picture)
    else:
        print('Bad Url')
    return len(downloaded_images)


def start_threading(number_of_pages, page_names):
    pool = ThreadPool(number_of_pages)
    pool.map(scrape_this_page, page_names)
    pool.close()
    pool.join()


def grab_sub_folders(main_page):
    sub_folders = html.fromstring(main_page).xpath('//div[@class="stream col-thumbs"]/div/div/div/a/@href')
    searched_folders = []
    for folder in sub_folders:
        if folder in searched_folders:
            continue
        searched_folders.append(folder)
        start(folder, True)


def start(page_url, is_folder):
    print(page_url)
    # Unless a second argument is supplied assume user wants to download images from all pages
    gallery_page_number = 0
    if len(sys.argv) > 2:
        gallery_page_number = int(sys.argv[2])
    # Use all_pages to store the number of gallery pages so that we can extract the number of pages in the
    # deviant's gallery
    page_content = requests.get(page_url).content
    all_pages = html.fromstring(page_content).xpath(
        '//div[@id="gallery_pager"]/div/ul/li[@class="number"]/a//text()')
    if len(all_pages) == 0:
        last_page = 1
    else:
        last_page = int(all_pages[len(all_pages) - 1])
    number_of_pages = last_page - gallery_page_number

    # page_names stores all the target urls that we want to scrape for images (i.e. each gallery page in a deviant's
    # gallery
    page_names = []
    # Then go through for all the pages we want to scrape, create an url with an offset equal to the number of
    # deviations per page (24) multiplied by the page number. This will scrape all gallery pages.
    while gallery_page_number < last_page:
        offset = '?offset=' + str(24 * gallery_page_number)
        current_page = page_url + offset
        page_names.append(current_page)
        gallery_page_number += 1
    start_threading(number_of_pages, page_names)
    if not is_folder:
        grab_sub_folders(page_content)
    print("Finished!")


if len(sys.argv) > 1:
    global artist_name
    artist_names = sys.argv[1]
    artist_names.replace("\"", "")
    artist_names = artist_names.split(",")
    for artist_name in artist_names:
        start('http://' + artist_name + '.deviantart.com/gallery/', False)
else:
    print("Please supply a deviant's name as an argument.")