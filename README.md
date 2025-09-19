# YouTube Interest Profiler

#### Video Demo: [Link](https://www.youtube.com/watch?v=TzsNEVOa7dQ)

#### Description
This program takes an HTML file exported from Google Takeout (YouTube watch history) or YouTube’s watch history page, together with a YouTube Data API v3 key, and generates a PNG file that visualizes the user’s profile.

#### Requirements
The program requires the following Python libraries:
- BeautifulSoup
- re
- requests
- collections.Counter
- numpy
- matplotlib.pyplot

#### How It Works
1. **Input**  
   - The program accepts an HTML file and an API key.  
   - Video IDs are extracted from the HTML using **BeautifulSoup** and **Regular Expressions**.

2. **Fetching Data**  
   - The YouTube Data API allows querying up to 50 video IDs at once.  
   - All video IDs are split into batches of 50 and requested via the API.  
   - The API returns JSON data including video metadata (title, channel, views, language, category ID, duration, etc.).

3. **Data Cleaning**  
   - Extracted information is stored in a `clean_results` list of dictionaries.  
   - Additional statistics are computed, such as:  
     - Favourite channel  
     - Favourite language  
     - Average video duration  

4. **Categories**  
   - The YouTube API is also used to map `categoryId` values to human-readable category names.  
   - A category–name mapping dictionary is created for later visualization.

5. **Output**  
   - The function `generate_png` creates a PNG image that displays:  
     - **Left side:** Bar chart of the top 6 categories (by number of videos)  
     - **Right side:** Summary statistics including average duration, favourite channel, and favourite language.  

#### Summary
In short, this program analyzes YouTube watch history, processes video metadata via the YouTube Data API, and produces a single image combining both a **bar chart of top categories** and a **summary of key viewing statistics**.

##Design Choices

I initially considered building the project as a server-based solution, where users upload their YouTube history file to the backend. The backend would call the YouTube API, store the results, and return a visualization to the user. This design would avoid requiring users to provide their own API keys, since a single 10,000-quota API key could support hundreds of users daily. However, I realized this approach raised serious privacy concerns: asking users to upload their entire watch history could be misinterpreted as data collection. To avoid any suspicion of misuse, I instead chose a local, client-side design where each user provides their own API key.

Another design decision concerned categories: YouTube’s category names differ slightly depending on region. At first I considered letting users choose a region code, but I decided against it, since users were already providing both a key and a file. For simplicity, the program requests categories in a single region. While names may vary slightly, the categories are broadly consistent.

##Future Work

I originally experimented with radar charts to display category distributions, but the visualization was messy and difficult to read. With more mathematical and visualization experience, I could return to this idea and make it work. For now, I prefer the clarity of bar charts. In the future, I also plan to enrich the left-hand visualization by combining multiple metrics (e.g., average video duration per category). Another possible extension is adding temporal analysis: determining at what times of day the user watches videos most frequently.
