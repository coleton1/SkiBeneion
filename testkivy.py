from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp
from PIL import Image as PILImage
import urllib.request
from io import BytesIO
import requests
from bs4 import BeautifulSoup
import pytesseract
from datetime import datetime 
import re

class MyApp(App):
    def build(self):
        Window.size = (375, 812) #600,400 375x812 to emulate iphone 
        Window.title = "Ski Ben Eion App" #THIS DOESNT WORK, FIXXXXXXXXXXXXXXXXX
        layout = GridLayout(cols=1, spacing=5, padding=dp(90))
        

        # Set background color for the entire window
        with layout.canvas.before:
            Color(0.4, 0.6, 0.9, 1)  # Darker blue background color
            self.rect = Rectangle(size=Window.size, pos=layout.pos)

        # Scraping Image Source and Extracting Text
        url = "https://skibeneoin.com/"
        skip_count = 1
        img_src = self.scrape_img_src(url, skip_count)
        image = self.get_image_from_url(img_src)
        image_path = 'temp_image.jpg'
        logo = 'ski.png'
        image.save(image_path)                                        
        extracted_text = self.extract_text_from_image(image_path)       
        cleaned_text = self.clean_extracted_text(extracted_text)
        cleaned_text = self.capitalize(cleaned_text)

        # Displaying Ski Ben Eion logo
        image_widget = Image(source=logo)
        layout.add_widget(image_widget)


        # match the time pattern 
        time_pattern = r"\b\d{1,2}(?:am|pm)\b"

        # Insert newline character after the time
        cleaned_text = re.sub(time_pattern, r"\g<0>\n\n\n", cleaned_text)
        #THIS DISPLAYS ORIG CLEAN TEXT DONT UNCOMMENT
        # Displaying Text
        #text_layout = Label(text=cleaned_text, font_size='20sp', markup=True, size_hint_y=None, halign='center',height=dp(200))
        #text_layout.bind(size=text_layout.setter('text_size'))
        #text_layout.bind(texture_size=text_layout.setter('size'))
        #text_layout.background_color = (0, 0, 0, 0)  # Transparent background color
        #text_layout.padding = (dp(10), dp(10))
        print(cleaned_text)#for debugging 
        #layout.add_widget(text_layout)
        
        #display time and date in bottom of screen
        now = datetime.now()
        current_date_time = now.strftime("%Y-%m-%d %I:%M %p")
        date_time_label = Label(text=current_date_time, size_hint_y=None, height=dp(50))
        layout.add_widget(date_time_label)
        #color rectangle at bottom of the screen that is behind the date and time 
        with date_time_label.canvas.before:
            Color(0.05, 0.15, 0.3, 1)  # pain in the arse
            self.rect_time = Rectangle(size=(Window.width, date_time_label.height), pos=(0, date_time_label.y))
            Line(rectangle=(0, date_time_label.y, Window.width, date_time_label.height), width=2)
            self.containstring(cleaned_text,layout)
            self.opentimeclose(cleaned_text,layout)

        return layout
    #this function just capitalizes Open and Closed because OCR doesnt like to capitalize them
    def capitalize(self,text):
        words = text.split()
        
        for i, word in enumerate(words):
            if word.lower() == "open":
                words[i] = "Open"
            elif word.lower() == "closed":
                words[i] = "Closed"

        return " ".join(words)
    #looks for image to scrape using the img and src tag and skips the first image and scrapes the second img 
    def scrape_img_src(self, url, skip_count):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            img_tags = soup.find_all('img')
            img_tags_skipped = img_tags[skip_count:]

            if img_tags_skipped:
                src = img_tags_skipped[0].get('src')
                return src
            else:
                print("No img tags found after skipping.")
                return None
        else:
            print(f"Failed to fetch page: {url}")
            return None
    #gets image and from url, pretty self explanitory i do not take credit for this  
    def get_image_from_url(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            image_data = response.read()
        image = PILImage.open(BytesIO(image_data))
        return image
    #pretty self explanitory but it uses a OCR to extract text from the image that has just been downloaded 
    def extract_text_from_image(self, image_path):
        text = pytesseract.image_to_string(PILImage.open(image_path))
        return text.strip()
    #NEEDS FIXING,    the header words are used in a font OCR cant read so it comes out with garbage so this tells it get rid of it 
    def clean_extracted_text(self, text):
        cleaned_text = text.replace("VEYA KR peel Pam CENA Ser ale el", "")
        return cleaned_text.strip()
    #list of hills and checks if the hill is mentioned in the clean text the returns what hills are mentioned 
    def hills(self, cleaned_text):
        # Define all hills
        all_hills = {"Redtail", "Eagle", "Bunny Hill", "Timberdoodle", "Loonback", "Whiskey Jack", "Sandpiper","Groovy Goose"}
        
        # Check if each hill is mentioned in the cleaned text
        hills_status = {hill: hill in cleaned_text for hill in all_hills}
        
        return hills_status
    #separates hills depending on status and lists hills from open to closed
    def containstring(self, cleaned_text, layout):

        hills_status = self.hills(cleaned_text)

        open_hills = []
        closed_hills = []

     # Separate hills based on status
        for hill, status in hills_status.items():
            if status:
                open_hills.append((hill, status))
            else:
                closed_hills.append((hill, status))

     # Display open hills first
        for hill, status in open_hills:
            status_label = Label(text=f"{hill}: {'Open' if status else 'Closed'}", font_size='20sp', markup=True, size_hint_y=None, halign='center', height=dp(30))
            status_label.padding = [0, 20]
            layout.add_widget(status_label)

     # Display closed hills next
        for hill, status in closed_hills:
            status_label = Label(text=f"{hill}: {'Open' if status else 'Closed'}", font_size='20sp', markup=True, size_hint_y=None, halign='center', height=dp(30))
            status_label.padding = [0, 20]
            layout.add_widget(status_label)
    #this functions purpose is to check what time it opens and closes but this will break when they change the opening time ffs
    def opentimeclose(self,cleaned_text,layout):
        pattern = r'(Open|Closed) \d{1,4}(am|pm) to \d{1,4}(am|pm)'
        
     #Search for the pattern in the text
        match = re.search(pattern, cleaned_text)

     #If a match is found, extract the matched text
        if match:
            opening_hours = match.group(0)
            print(opening_hours)
            opening_label = Label(text=opening_hours,font_size='18sp', size_hint_y=None, height=dp(50))
            layout.add_widget(opening_label)
        else:
            print("No opening hours found")
    #i dont need to explain this 
if __name__ == '__main__':
    MyApp().run()


#PSEUDO CODEEEEEEEE


#Scrapes skibeneion website for 2nd picture on homescreen because second picture displays hills that are open 

#Gets image from the src url and downloads it

#Uses a OCR module to extract text from the picture it just downloaded

#Takes the extracted text and cleans it up 

#list all hills that skibeneion has and checks if they are mentioned in the new cleanly extracted text

#separates the hills depending on if they are open or closed and displays them in a kivy GUI 





