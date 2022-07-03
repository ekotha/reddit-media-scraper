import os
import sys
import json
import urllib.request
from urllib.parse import urljoin
import getpass
import requests
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
import subprocess
import time


now = datetime.now()
print(os.getcwd())  # kept to check current working directory

# Enter subreddit to pull images from
subreddit = input("Enter subreddit name (without r/): ")

url = f"http://www.reddit.com/r/{subreddit}.json"

def main():

    # initializing object, loads JSON
    try:
        og_url = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
        data = og_url.json()
        print(og_url.status_code)
    except:
        # print(og_url.headers)
        time.sleep(5)
        og_url = requests.get(url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
        data = og_url.json()
        print(og_url.status_code)

    # searches env for username to fill in path
    user = getpass.getuser()

    # directory used to save images
    directory = f"/Users/{user}/Documents/{subreddit}"  # dynamic elements

    # creates directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)
        print("Directory ready!")

    # Loop through the JSON URLs
    url_list = []

    count = 0

    for i in data["data"]["children"]:
        image_url = i["data"]["url"]
        url_list.append(image_url)
        try:
            time.sleep(0.2)
            img_data = requests.get(image_url).content
            time.sleep(0.5)
        except:
            pass

        count += 1
    print(len(url_list))

    i = 0

    # using time hour-min-sec for unique identifier gen.
    id_time = now.strftime("%H-%M-%S")
    other_links = []

    for item in url_list[:]:
        index_item = url_list.index(item)

        if url_list[index_item].endswith('.gifv'):
            url_list[index_item] = url_list[index_item].replace('.gifv', '.mp4')

    for item in url_list[:]:
        if (item.endswith('.png') or item.endswith('.jpg') or item.endswith('.gif') or item.endswith('.mp4') or item.endswith('.jpeg')) == False:
            print("begin: " + item)
            other_links.append(item)
            url_list.remove(item)
    
    time.sleep(1)
    while i < len(url_list):
        img_data = requests.get(url_list[i]).content  # images

        # to programmatically fill in file extension
        ex_tension = os.path.splitext(url_list[i]) 

        # index and subreddit name for id
        direct_line = str(i) + subreddit

        with open(f"image{direct_line}_{id_time}{ex_tension[1]}", "wb") as handler:
            handler.write(img_data)
        i += 1

    # prepping files in directory for moving.
    # can probably refactor this code  
    source_dir = os.listdir(os.getcwd())
    # source_dir.remove('main.py')
    remove_these = ['main.py', 'README.md','.DS_Store', '.git', '.gitignore']
    source_dir = [x for x in source_dir if x not in remove_these]
    # print(*source_dir)
    source_dir.sort()
    source_d = os.getcwd()

    # moving downloaded files to this folder path
    destination_dir = f"/Users/{user}/Documents/{subreddit}/"

    for files in source_dir:
        substring = subreddit
        if substring in files:
            shutil.move(source_d + "/" + files, destination_dir)
            # size = os.path.getsize(f'{destination_dir}/{files}')
            destination_dir_a = os.listdir(f'{destination_dir}') # maybe remove
            index_of_file = source_dir.index(files)

        else:
            print(files + " was not moved.")

    # getting url of sites, often are short form, pre-redirect
    for item in other_links[:]:
        # in the copied list, what is the index val of the item
        index_other_item = other_links.index(item) 

        # create a var that retrieves url again
        url_short = other_links[index_other_item]

        # breathing room
        time.sleep(1)
        res_short = requests.get(url_short, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
        # .url to get the last link after redirects
        url_b = res_short.url
        print(url_b)
        
        # getting post id to get the media, but check if video src exists too
        if "v.redd." in url_short:
            time.sleep(2)
            res = requests.get(url_b, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
            post_id = url_b[url_b.find('comments/') + 9:]
            # print(post_id)
            post_id = f"t3_{post_id[:post_id.find('/')]}"
            print(post_id)
            if(res.status_code == 200):    # checks if server responded with OK
                soup_pot = BeautifulSoup(res.text,'lxml')
                required_js = soup_pot.find('script',id='data') 
            
                json_data = json.loads(required_js.text.replace('window.___r = ','')[:-1])
                title = json_data['posts']['models'][post_id]['title']
                title = title.replace(' ','_')

                print(json_data['posts']['models'][post_id]['media'])

                dash_url = json_data['posts']['models'][post_id]['media']['dashUrl']
                height  = json_data['posts']['models'][post_id]['media']['height']
                dash_url = dash_url[:int(dash_url.find('DASH')) + 4]
                print(dash_url)
                # the dash URL is the main URL we need to search for
                # height is used to find the best quality of video available
                video_url = f'{dash_url}_{height}.mp4'    # this URL will be used to download the video
                audio_url = f'{dash_url}_audio.mp4'    # this URL will be used to download the audio part

                with open(f'{title}_video.mp4','wb') as file:
                    print('Downloading Video...',end='',flush = True)
                    time.sleep(2)
                    res = requests.get(video_url, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
                    if(res.status_code == 200):
                        file.write(res.content)
                        print('\rVideo Downloaded...!')
                    else:
                        print('\rVideo Download Failed..!')
                with open(f'{title}_audio.mp3','wb') as file:
                    print('Downloading Audio...',end = '',flush = True)
                    res = requests.get(audio_url,headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
                    if(res.status_code == 200):
                        file.write(res.content)
                        print('\rAudio Downloaded...!')
                    else:
                        print('\rAudio Download Failed..!')
                
                # uses subprocess calls to ffmpeg to combine audio w/ video 
                # and generate a mp4 copy and remove the component files 
                subprocess.call(['ffmpeg','-i',f'{title}_video.mp4','-i',f'{title}_audio.mp3','-map','0:v','-map','1:a','-c:v','copy',f'{title}_{subreddit}.mp4'])
                subprocess.call(['rm',f'{title}_video.mp4',f'{title}_audio.mp3'])            
        elif "gfycat" in url_b:
            gfy = requests.get(url_short, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
            if(gfy.status_code == 200):    # checking if server responded with OK
                soup_pot_gif = BeautifulSoup(gfy.text,'lxml')
                gif_vid_url = soup_pot_gif.find('meta',property='og:video') 
                gfycat_url = gif_vid_url['content']
                gfy_ex_tension = os.path.splitext(str(gfycat_url))
                img_data = requests.get(gfycat_url).content
                # print(gif_vid_url['content'])
            with open(f'image{index_other_item}{subreddit}{id_time}{gfy_ex_tension[1]}', "wb") as handler:
                handler.write(img_data)
        else:
            print("!=Reddit, continuing...")

        if url_list == False:
            print("All OK! Program completed.")
        else: # the hail mary pass for any edge case urls missed on first pass
            try:
                gfy = requests.get(url_short, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
                if(gfy.status_code == 200):    # checking if server responded with OK
                    soup_pot_gif = BeautifulSoup(gfy.text,'lxml')
                    gif_vid_url = soup_pot_gif.find('meta',property='og:video') 
                    gfycat_url = gif_vid_url['content']
                    gfy_ex_tension = os.path.splitext(str(gfycat_url))
                    img_data = requests.get(gfycat_url).content
                    # print(gif_vid_url['content'])
                with open(f'image{index_other_item}{subreddit}{id_time}{gfy_ex_tension[1]}', "wb") as handler:
                    handler.write(img_data)
                
            except TypeError:
                print("checkpoint 2 test")
                try:
                    gfy = requests.get(url_short, headers={"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15"})
                    if(gfy.status_code == 200):    # checking if server responded with OK
                        soup_pot_gif = BeautifulSoup(gfy.text,'lxml')
                        gif_vid_url = soup_pot_gif.find('source', type='video/mp4') 
                        gfycat_url = gif_vid_url['src']
                        gfy_ex_tension = os.path.splitext(str(gfycat_url))
                        img_data = requests.get(gfycat_url).content
                        # print(gif_vid_url['content'])
                    with open(f'image{index_other_item}{subreddit}{id_time}{gfy_ex_tension[1]}', "wb") as handler:
                        handler.write(img_data)
                except TypeError:
                    print("No video present")
            except:
                print("welp...")
                pass
    print("Phase complete!")


    source_dir = os.listdir(os.getcwd())
    source_dir = [x for x in source_dir if x not in remove_these]
    source_dir.sort()
    source_d = os.getcwd()


    destination_dir = f"/Users/{user}/Documents/{subreddit}/"  # moving to this folder
    for files in source_dir:
        substring = subreddit
        if substring in files:
            shutil.move(source_d + "/" + files, destination_dir)
            destination_dir_a = os.listdir(f'{destination_dir}')
            index_of_file = source_dir.index(files)

        else:
            print(files + " was not moved.")


if __name__ == "__main__":
    main()