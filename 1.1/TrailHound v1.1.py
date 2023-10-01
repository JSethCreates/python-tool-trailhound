# TrailHound v1.1
# This program grabs the links of trailer options from youtube and will download the files on requests
# Attempt to cut off the videos where extra time has been added on youtube for other bumpers

import os
import webbrowser
import requests
import threading
import tempfile
from tkinter import *
from tkinter import ttk
from pytube import YouTube
from moviepy.editor import VideoFileClip

# Constants for the GUI
API_KEY = 'AIzaSyBnmuyKHzxX-m3UT6ZaOLg6H7ZhziJ0QS0'
FONT_NAME = "Segoe UI Symbol"
FONT_SIZE = 13

# Initialize the main window
root = Tk()
root.title("TrailHound 🐶 v1.1")
root.geometry("1010x1280")
current_selected_link = StringVar(value="none")

# Initialize the counters
trailer_and_notrailer_count = 0
movies_status = {}

def scan_movie_folders():
    movies = {}
    global trailer_and_notrailer_count
    trailer_and_notrailer_count = 0
    for folder in os.listdir():
        if os.path.isdir(folder) and '(' in folder and ')' in folder:
            status = "📽"
            if any(fname.endswith("-trailer.mp4") for fname in os.listdir(folder)):
                status = "✔"
                trailer_and_notrailer_count += 1
            elif 'notrailer.sad' in os.listdir(folder):
                status = "❌"
                trailer_and_notrailer_count += 1
            movies[folder] = status
    return movies
    
def fetch_youtube_links(movie_name):
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&maxResults=5&q={movie_name} trailer&type=video&key={API_KEY}"
    response = requests.get(search_url)
    return [(item["snippet"]["title"], "https://www.youtube.com/watch?v=" + item["id"]["videoId"]) for item in response.json()["items"]]

def on_movie_select(event):
    global current_selected_link, end_times
    current_movie = movie_tree.focus()
    movie_name = movie_tree.item(current_movie)["text"]

    for widget in youtube_frame.winfo_children():
        widget.destroy()

    current_selected_link.set("none")
    end_times = {}  # Dictionary to hold the end time entries for each video

    if movies_status[movie_name] == "📽" or movies_status[movie_name] == "❌":
        links = fetch_youtube_links(movie_name)
        for i, (title, url) in enumerate(links):
            ttk.Separator(youtube_frame, orient=HORIZONTAL).grid(row=i*2, column=0, pady=5, sticky='ew')
            
            r = Radiobutton(youtube_frame, text=title, variable=current_selected_link, value=url, font=(FONT_NAME, FONT_SIZE))
            r.grid(row=i*2+1, column=0, sticky="w", padx=5, pady=2)
            
            # Entry for cutoff time
            end_time_entry = Entry(youtube_frame, width=10, font=(FONT_NAME, FONT_SIZE))
            end_time_entry.grid(row=i*2+1, column=1, sticky="w", padx=5)
            end_times[url] = end_time_entry  # Store the entry widget in the dictionary

            link_label = Label(youtube_frame, text=url, cursor="hand2", fg="blue", font=(FONT_NAME, FONT_SIZE))
            link_label.grid(row=i*2+1, column=2, sticky="w", padx=5)
            link_label.bind("<Button-1>", lambda e, u=url: (current_selected_link.set(u), webbrowser.open(u)))

    ttk.Separator(youtube_frame, orient=HORIZONTAL).grid(row=50, column=0, pady=10, sticky='ew')

def Download(link, movie_folder, movie_name, cutoff_time=None):
    try:
        youtubeObject = YouTube(link)
        videoStream = youtubeObject.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{videoStream.subtype}", dir=movie_folder) as tmp_file:
            tmp_path = tmp_file.name
            videoStream.download(output_path=os.path.dirname(tmp_path), filename=os.path.basename(tmp_path))
        
        file_name = f"{movie_name}-trailer.{videoStream.subtype}"
        final_path = os.path.join(movie_folder, file_name)

        if cutoff_time:
            cutoff_time = int(cutoff_time)  # Convert cutoff_time to integer
            with VideoFileClip(tmp_path) as video:
                end_time = video.duration - cutoff_time
                new = video.subclip(0, end_time)
                new.write_videofile(final_path, codec="libx264")
        else:
            os.rename(tmp_path, final_path)
        
        movies_status[movie_name] = "✔"
        update_tree_view(movie_name, "✔")
        
        # Update the trailer counter
        global trailer_and_notrailer_count
        trailer_and_notrailer_count += 1
        update_counter_display()
        
    except Exception as e:
        print(f"An error has occurred: {e}")
    
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def update_tree_view(movie_name, status):
    for item in movie_tree.get_children():
        if movie_tree.item(item)["text"] == movie_name:
            movie_tree.item(item, values=(status))

def download_trailer():
    current_movie = movie_tree.focus()
    movie_name = movie_tree.item(current_movie)["text"]
    link = current_selected_link.get()
    cutoff_time = end_times.get(link).get() if link in end_times and end_times[link].get() else None  # Get the cutoff time if specified

    if link == "manual":
        link = manual_entry.get()
        
    if link:
        Download(link, movie_name, movie_name, cutoff_time)

    for item in movie_tree.get_children():
        if movie_tree.item(item)["text"] == movie_name:
            tag = movie_tree.item(item)['tags'][0]
            movie_tree.tag_configure(tag, foreground='black')

    notrailer_file = os.path.join(movie_name, 'notrailer.sad')
    if os.path.exists(notrailer_file):
        os.remove(notrailer_file)

def open_folder():
    current_movie = movie_tree.focus()
    movie_name = movie_tree.item(current_movie)["text"]
    os.startfile(movie_name)

def no_trailer():
    current_movie = movie_tree.focus()
    movie_name = movie_tree.item(current_movie)["text"]
    with open(os.path.join(movie_name, 'notrailer.sad'), 'w') as f:
        pass
    movies_status[movie_name] = "❌"
    update_tree_view(movie_name, "❌")
    
    tag = movie_tree.item(current_movie)['tags'][0]
    movie_tree.tag_configure(tag, foreground='black')
    
    # Update the trailer counter
    global trailer_and_notrailer_count
    trailer_and_notrailer_count += 1
    update_counter_display()

def update_counter_display():
    global trailer_and_notrailer_count
    count_label.config(text=f"Trailers Snurfed: {trailer_and_notrailer_count}/{len(movies_status)}")

def update_movie_tree_view():
    first_movie_without_trailer_id = None

    for i, (movie, status) in enumerate(movies_status.items()):
        color = '#ECECEC' if i % 2 == 1 else 'white'
        movie_tree.tag_configure(f"color{i}", background=color)
        if status == "📽":
            movie_tree.tag_configure(f"color{i}", foreground='red')

        # Inserting movie to tree and getting its ID
        item_id = movie_tree.insert("", END, text=movie, values=(status), tags=(f"color{i}"))

        # Tracking the first movie without a trailer or notrailer.sad
        if not first_movie_without_trailer_id and status == "📽":
            first_movie_without_trailer_id = item_id

    # Scroll to the first movie without a trailer or notrailer.sad
    if first_movie_without_trailer_id:
        movie_tree.see(first_movie_without_trailer_id)

    loading_label.pack_forget()
    youtube_frame.pack(pady=20, padx=20)
    btn_frame.pack(pady=20, side=BOTTOM, fill=X)
    
def scan_movie_folders_threaded():
    global movies_status
    movies_status = scan_movie_folders()
    count_label.config(text=f"Trailers Snurfed: {trailer_and_notrailer_count}/{len(movies_status)}")
    root.after(0, update_movie_tree_view)

# GUI code below

# Frame for the Youtube links
youtube_frame = Frame(root, pady=5, padx=5)

# Counter label
count_label = Label(root, text=f"Trailers Snurfed: {trailer_and_notrailer_count}/{len(movies_status)}", font=(FONT_NAME, FONT_SIZE))
count_label.pack(pady=5)

# Loading label
loading_label = Label(root, text="Scanning folders...", font=(FONT_NAME, FONT_SIZE))
loading_label.pack(pady=50)

# Frame for the bottom buttons
btn_frame = Frame(root, pady=10)
download_btn = Button(btn_frame, text="Download Trailer", command=download_trailer, width=20, height=2, bg="#4CAF50", fg="white", font=(FONT_NAME, FONT_SIZE))
open_folder_btn = Button(btn_frame, text="📂", command=open_folder, width=53, height=2, bg="#FFC107", font=(FONT_NAME, FONT_SIZE))
no_trailer_btn = Button(btn_frame, text="No Trailer", command=no_trailer, width=20, height=2, bg="#F44336", fg="white", font=(FONT_NAME, FONT_SIZE))

download_btn.grid(row=0, column=2, padx=5)
open_folder_btn.grid(row=0, column=1, padx=5)
no_trailer_btn.grid(row=0, column=0, padx=5)

# Define constants for treeview frame height and width
TREE_FRAME_WIDTH = 1000  # Subtracting some padding; you can adjust as necessary
TREE_FRAME_HEIGHT = 550  # Adjust as necessary

# Create Frame for treeview and scrollbar
tree_frame = Frame(root, width=TREE_FRAME_WIDTH, height=TREE_FRAME_HEIGHT)
tree_frame.grid_propagate(0)  # Prevents frame from resizing to fit its content
tree_frame.pack(pady=20, padx=20)

# Add a scrollbar
scrollbar = ttk.Scrollbar(tree_frame)
scrollbar.grid(row=0, column=1, sticky='ns')

# Movie tree view
movie_tree = ttk.Treeview(tree_frame, columns=("Status"), show="tree headings", selectmode="browse", yscrollcommand=scrollbar.set, height=35)
movie_tree.heading("#0", text="Movie Name")
movie_tree.heading("Status", text="Status")
movie_tree.column("#0", width=TREE_FRAME_WIDTH - 150)  # Adjust the width for the Movie Name column
movie_tree.column("Status", width=150)  # Adjust the width for the Status column

# Place the treeview to make it fill the tree_frame width using grid
movie_tree.grid(row=0, column=0, sticky='nsew')

# Link the scrollbar to the treeview
scrollbar.config(command=movie_tree.yview)

movie_tree.bind('<<TreeviewSelect>>', on_movie_select)

# Start a thread to scan the folders and populate the tree view
threading.Thread(target=scan_movie_folders_threaded).start()

root.mainloop()
