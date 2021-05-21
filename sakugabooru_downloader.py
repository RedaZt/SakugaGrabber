import os, urllib3
from bs4 import BeautifulSoup as bs

dict_art = { "+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "\\": "", "&" : "and", ":" : "", "_" : " "}
dict = { "+" : "", "!" : "", "?" : "", "%" : "", "*" : "", "/" : "", "#" : "", "\\": "", "&" : "and", ":" : ""}
http = urllib3.PoolManager()

def Filename(res, id):
    soup = bs(res.data,"html.parser")
    tags = soup.findAll('ul',id="tag-sidebar")
    ext = '.' + soup.find('a', id="highres")["href"].split('.')[-1]
    art_num = 0
    cpr_num = 0
    artist = ''
    copyright = ''
    for tag in tags:
        info = tag.findChildren('li')
        for x in info : 
            if x["data-type"] == "artist" :
                if art_num == 0 : 
                    artist = x["data-name"].translate(str.maketrans(dict_art))
                    art_num += 1
                else :
                    artist += " & " + x["data-name"].translate(str.maketrans(dict_art))
            if x["data-type"] == "copyright" :
                if art_num == 0 : 
                    copyright = x["data-name"].translate(str.maketrans(dict)).strip()
                    cpr_num += 1
                else :
                    copyright += " " + x["data-name"].translate(str.maketrans(dict)).strip()
    file_name = (str(copyright) + " By " + artist + " (" + id + ')' + ext).strip()
    return file_name

def postGrabber(id):
    link = "https://www.sakugabooru.com/post/show/"+id
    res = http.request('GET', link)
    media_link = bs(res.data, "html.parser").find('a', id="highres")["href"]

    media = Filename(res, id)

    if os.path.exists(media):
        pass
    else : 
        with open(media, 'wb') as targetfile :
            dt = http.request('GET', media_link)
            targetfile.write(dt.data)
        print("Downloaded :",media)

def idDownloader(link):
    id = link.split('/')[-1]

    folder = "Sakugabooru Downloads" 
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)

    postGrabber(id)

def bulkDownloader(link):
    limit = "&limit=100"
    page = "&page="
    page_number = 1

    res = http.request('GET', link)
    soup = bs(res.data,"xml")
    tags = soup.find("posts")
    posts_count = int(tags["count"])

    print(posts_count,"Posts found.")
    print("Downloading ...")

    while posts_count > 0 :
        print("requesting")
        url = link + limit + page + str(page_number)

        res2 = http.request('GET', url)
        soup = bs(res2.data,"xml")
        tags = soup.find("posts")
        posts = tags.find_all("post")

        folder = "sakugabooru_downloads" 
        if not os.path.exists(folder):
            os.mkdir(folder)
        os.chdir(folder)

        for post in posts:
            postGrabber(post["id"])
        
        posts_count -= 100
        page_number += 1
        

def poolDownloader(link):
    res = http.request('GET', link)
    soup = bs(res.data, "html.parser")
    posts = soup.find_all('span', attrs={"class" : "plid"})
    pool_title = soup.find("div", attrs={"id" : "pool-show"}).find("h4").text.split(':')[-1].strip()
    
    folder = "sakugabooru_downloads" 
    if not os.path.exists(folder):
        os.mkdir(folder)
    os.chdir(folder)
    
    if not os.path.exists(pool_title):
        os.mkdir(pool_title)
    os.chdir(pool_title)

    for post in posts:
        postGrabber(post.text.split('/')[-1])


if __name__ == "__main__":
    link = input("Paste your link here : ").strip()                       

    if "tags=" in link :
        link_F = "https://www.sakugabooru.com/post.xml?tags=" + link.split("=")[-1] 
        bulkDownloader(link_F)

    elif "pool" in link : 
        poolDownloader(link)

    else : 
        idDownloader(link)
