from bs4 import BeautifulSoup
import re
import requests
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

def main():

    datav3_API_url = "https://www.googleapis.com/youtube/v3/videos"
    cate_API_url = "https://www.googleapis.com/youtube/v3/videoCategories"
    input_file = input("Enter your file to be analysed: ").strip().strip('"')
    if not input_file:
        print("Please enter your file")
        return None
    #"C:\Users\pli39\Desktop\Demonstration\Watch_history.html"
    API_KEY = input("Enter your API key from Youtube: ")
    #AIzaSyCEdtzis0MTG1tyuechB71lIXXeqI9G7MQ
    if not API_KEY:
        print("Please enter your API_key")
        return None
    
    result=[]

    all_results = []

    with open(input_file, "r", encoding="utf-8") as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup.find_all("a", id="video-title"):
            title = tag.get("title")
            href = tag.get("href")
            match = re.search(r"v=([^&]+)", href)
            if match:
                video_id = match.group(1)
            else:
                video_id = None

            result.append({
                "title": title,
                "url": href,
                "videoID": video_id
            })

        video_id_list = []
        for item in result:
            vid = item["videoID"]
            if vid:
                video_id_list.append(vid)
                
        for i in range(0, len(video_id_list), 50):
            batch = video_id_list[i:i+50]
            id_str = ",".join(batch)

            params_data = {
                "part": "snippet,statistics,contentDetails",
                "id": id_str,
                "key": API_KEY
            }

            resp = requests.get(datav3_API_url, params=params_data)
                
            resp.raise_for_status()
            data = resp.json()
            all_results.append(data)
        
        clean_results = []

        sum_duration = 0

        for batch in all_results:
            for info in batch.get("items", []):
                vid = info["id"]
                title = info["snippet"]["title"]
                channel = info["snippet"]["channelTitle"]
                views = info["statistics"].get("viewCount", "0")
                language = info["snippet"].get("defaultAudioLanguage") or info["snippet"].get("defaultLanguage", "unknown")
                categoryID = info["snippet"]["categoryId"]
                duration = info["contentDetails"]["duration"]
                duration = iso8601_to_seconds(duration)

                clean_results.append({
                    "videoID": vid,
                    "videoTitle": title,
                    "channel": channel,
                    "views": views,
                    "language": language,
                    "categoryId": categoryID,
                    "duration": duration
                })

                sum_duration += duration

        id_list = []

        cate_counter = Counter([item["categoryId"] for item in clean_results])
        favourite_channel = Counter([item["channel"] for item in clean_results]).most_common(1)
        favourite_language = Counter([item["language"] for item in clean_results]).most_common(1)
        average_video_duration = sum_duration / len(clean_results)
        
        for item in clean_results:
            cate_id = item["categoryId"]
            if cate_id not in id_list:
                id_list.append(cate_id)
        params_data_category = ({
            "part": "snippet",
            "id": ",".join(id_list),
            "key": API_KEY
        })
        resp = requests.get(cate_API_url, params=params_data_category)
        data_cName = resp.json()

        category_map = {item["id"]: item["snippet"]["title"] 
                for item in data_cName.get("items", [])}

        cate_stats = {}
        for cid, count in cate_counter.items():
            cate_name = category_map.get(cid, "Unknown")
            cate_stats[cate_name] = count

    generate_png(cate_stats, average_video_duration, favourite_channel, favourite_language)

def generate_png(cate_data, average_duration, favourite_channel, favourite_language, top_cate = 6):
    categories, counts = zip(*sorted(cate_data.items(), key=lambda x: x[1]))
    categories = list(categories)
    counts = list(counts)

    top_categories = categories[:top_cate]
    top_counts = counts[:top_cate]

    fig, (bar_ax, data_ax) = plt.subplots(1, 2, figsize=(14, 6))

    bar_ax.bar(top_categories, top_counts)
    bar_ax.set_xticks(range(len(top_categories)))
    bar_ax.set_xticklabels(top_categories, rotation=45, ha="right")
    bar_ax.set_ylabel("Numbers of Videos of this category")
    
    data_ax.axis("off")
    text_y = 0.8
    line_spacing = 0.2

    avg_min, avg_sec = divmod(int(average_duration), 60)
    avg_str = f"{avg_min}m {avg_sec}s" if avg_min else f"{avg_sec}s"

    data_ax.text(0.1, text_y, f"Average duration for every video in html file: {avg_str}", fontsize=20)
    text_y -= line_spacing

    ch_name, ch_count = favourite_channel[0]
    data_ax.text(0.1, text_y, f"Your favourite channel: {ch_name} ({ch_count} videos)", fontsize=20)
    text_y -= line_spacing

    lang_name, lang_count = favourite_language[0]
    data_ax.text(0.1, text_y, f"Your favourite language of videos: {lang_name} ({lang_count} videos)", fontsize=20)


    plt.tight_layout()
    plt.savefig("category_stats.png", dpi=150)
    plt.show()

def iso8601_to_seconds(duration):
    h = m = s = 0
    match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
    if match:
        h, m, s = [int(x) if x else 0 for x in match.groups()]
    return h*3600 + m*60 + s

if __name__ == "__main__":
    main()