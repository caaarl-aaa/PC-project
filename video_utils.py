import os
import vlc
import tkinter as tk

def show_instructional_video(window, start_function):
    def play_video(video_path):
        if not os.path.exists(video_path):
            print(f"Error: Video file not found at {video_path}")
            return

        # VLC Instance
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(video_path)
        player.set_media(media)

        # Embed the video in the Tkinter Canvas
        player.set_hwnd(video_canvas.winfo_id())

        # Play the video
        player.play()

    # Clear the current window
    for widget in window.winfo_children():
        widget.destroy()

    # Video Canvas
    video_canvas = tk.Canvas(window, width=900, height=500, bg="black", highlightthickness=0)
    video_canvas.pack()

    # Start playing the video
    video_path = r"C:\Users\Carl\Desktop\pose-estim\pose-estimation\poseVideos\tutorial.mp4"
    play_video(video_path)