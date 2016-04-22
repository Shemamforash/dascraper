from lxml import html
import requests
import urllib.request
import os
import sys
from multiprocessing.dummy import Pool as ThreadPool

artist_name = ''


# Downloads a single image given an image page and a directory to save it
def download_img(deviation_page, directory_to_save):
    if deviation_page.status_code == requests.codes.ok:
        # Grab all images within a 'view-deviation' div, since these img elements are on the gallery page
        image_urls = html.fromstring(deviation_page.content).xpath('//div[@class="dev-view-deviation"]/img/@src')
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
            file = urllib.request.urlopen(image_urls[1])
            # Get rid of the artist's name
            img_name = filename.split('_by_')[0]
            # Extract the file ending as well
            file_ending = filename.split('.')[-1]
            # Piece it back together without the artist's name
            fullname = directory_to_save + img_name + '.' + file_ending
            # And write it to the directory
            try:
                out = open(fullname, "wb")
                out.write(file.read())
                out.close()
            except OSError:
                return


# Returns all valid urls from a gallery page that link to a deviation page
def get_image_urls(urls):
    valid_urls = []
    for url in urls:
        if artist_name + '.deviantart.com/art' in url:
            valid_urls.append(url)
    return valid_urls


def scrape_this_page(page_name):
    page = requests.get(page_name)
    if page.status_code == requests.codes.ok:
        # If a folder on the desktop does not already exist for this given artist, create one, then set it as the
        # directory to save images to
        if not os.path.isdir(os.path.expanduser('~\\Desktop\\' + artist_name)):
            os.mkdir(os.path.expanduser('~\\Desktop\\' + artist_name))
        target_directory = os.path.expanduser('~\\Desktop\\' + artist_name + '\\')
        pictures = get_image_urls(html.fromstring(page.content).xpath('//a[not(ancestor::div[@class="gr-body"])]/@href'))
        downloaded_images = []
        for picture in pictures:
            # Make sure image has not already been downloaded, and that it is not simply a duplicate url with
            # the comments section open
            if picture not in downloaded_images and '#comments' not in picture:
                print("Grabbed " + picture)
                deviation_page = requests.get(picture)
                download_img(deviation_page, target_directory)
                downloaded_images.append(picture)
    else:
        print('Bad Url')
    return len(downloaded_images)


def start_threading(number_of_pages, page_names):
    pool = ThreadPool(number_of_pages)
    pool.map(scrape_this_page, page_names)
    pool.close()
    pool.join()


def start():
    # Unless a second argument is supplied assume user wants to download images from all pages
    gallery_page_number = 0
    if len(sys.argv) > 2:
        gallery_page_number = int(sys.argv[2])
    if len(sys.argv) > 1:
        global artist_name
        artist_name = sys.argv[1]
    else:
        print("Please supply a deviant's name as an argument.")
    # Use all_pages to store the number of gallery pages so that we can extract the number of pages in the
    # deviant's gallery
    all_pages = html.fromstring(requests.get('http://' + artist_name + '.deviantart.com/gallery/').content).xpath(
        '//div[@id="gallery_pager"]/div/ul/li[@class="number"]/a//text()')
    last_page = int(all_pages[len(all_pages) - 1])
    number_of_pages = last_page - gallery_page_number

    # page_names stores all the target urls that we want to scrape for images (i.e. each gallery page in a deviant's
    # gallery
    page_names = []
    # Then go through for all the pages we want to scrape, create an url with an offset equal to the number of
    # deviations per page (24) multiplied by the page number. This will scrape all gallery pages.
    while gallery_page_number < last_page:
        offset = '?offset=' + str(24 * gallery_page_number)
        current_page = 'http://' + artist_name + '.deviantart.com/gallery/' + offset
        page_names.append(current_page)
        gallery_page_number += 1

    start_threading(number_of_pages, page_names)
    print("Finished!")

start()