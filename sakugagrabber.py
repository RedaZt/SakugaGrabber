import os, re, urllib3
from bs4 import BeautifulSoup as bs
from typing import List

specialCharacters = {'?' : '', '"' : '', '*' : '', '/' : '', '#' : '', '\\': '', ':' : '', '_' : ' ', '|' : '', '<' : '', '>' : ''}
mainFolder = "Sakugabooru Downloads"
http = urllib3.PoolManager()

def search(infos : List, className : str) -> List:
    lst = []
    for element in infos:
        if element["class"] == [className]:
            childElement = element.findChildren('a')
            for target in childElement:
                if target.text != '?':
                    lst += [target.text]
    return lst

def namingFiles(res, id : str) -> str:
    soup = bs(res.data,"html.parser")
    data = soup.find('ul', id="tag-sidebar")
    infos = data.findChildren('li')
    ext = soup.find('a', id="highres")["href"].split('.')[-1]

    artists = ' & '.join(search(infos, "tag-type-artist"))
    copyrights = ' '.join(search(infos, "tag-type-copyright"))

    fileName = f"{copyrights} By {artists} ({id}).{ext}".translate(str.maketrans(specialCharacters))

    return fileName

def postGrabber(folder : str, id : str):
    link = f"https://www.sakugabooru.com/post/show/{id}"
    res = http.request('GET', link)
    mediaLink = bs(res.data, "html.parser").find('a', id="highres")["href"]

    media = namingFiles(res, id)
    print(f"DOWNLOADING : {media}")

    if not os.path.exists(folder):
        os.makedirs(folder)

    filepath = f"{folder}/{media}"

    with open(filepath, 'wb+') as targetfile:
        dt = http.request('GET', mediaLink)
        targetfile.write(dt.data)
    print(f"SUCCESS : {media}")

def getId(link : str) -> str:
    return re.search(r"(\d+)", link).group(1)

def idDownloader(link : str):
    id = getId(link)
    postGrabber(mainFolder, id)

def bulkDownloader(link : str):
    tags = link.split("=")[-1] 
    tagsLink = f"https://www.sakugabooru.com/post.xml?tags={tags}"
    pageNumber = 1

    res = http.request('GET', tagsLink)
    soup = bs(res.data, "lxml")
    posts = soup.find("posts")
    postCount = int(posts["count"])

    print(f"{postCount} posts found.")
    print("Downloading ...")

    while postCount > 0:
        url = f"{tagsLink}&limit=100&page={pageNumber}"

        res = http.request('GET', url)
        soup = bs(res.data, "lxml")
        posts = soup.findAll("post")

        for post in posts:
            postGrabber(mainFolder, post["id"])
        
        postCount -= 100
        pageNumber += 1

def poolDownloader(link : str):
    res = http.request('GET', link)
    soup = bs(res.data, "html.parser")
    posts = soup.find_all('span', attrs={"class" : "plid"})
    poolTitle = soup.find("div", attrs={"id" : "pool-show"}).find("h4").text.split(':')[-1].strip()
    
    folder = f"{mainFolder}/{poolTitle}"

    for post in posts:
        postGrabber(folder, getId(post.text))

if __name__ == "__main__":
    link = input("Paste your link here : ").strip()                   

    if "tags=" in link:
        bulkDownloader(link)
    elif "pool" in link: 
        poolDownloader(link)
    else : 
        idDownloader(link)

    print("DONE !!")