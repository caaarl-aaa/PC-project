import tkinter as tk
from tkinter import Canvas

# Create the main application window
app = tk.Tk()
app.geometry("800x600")

# Create a canvas
canvas = Canvas(app, width=800, height=600, bg="#eae7de", highlightthickness=0)
canvas.pack()

def draw_blurred_shadow(canvas, x1, y1, x2, y2, fill_color, shadow_color="#888888", shadow_offset=5, blur_radius=3):
    # Draw multiple layers of shadow to simulate blur
    for i in range(blur_radius, 0, -1):
            alpha = hex(int(255 * (1 - i / blur_radius)))[2:].zfill(2)  # Calculate transparency
            canvas.create_oval(
                x1 + shadow_offset * i, y1 + shadow_offset * i,
                x2 + shadow_offset * i, y2 + shadow_offset * i,
                fill=shadow_color + alpha, outline=""
            )
    
    # Draw the main circle
    canvas.create_oval(x1, y1, x2, y2, fill=fill_color, outline="")

# Draw a circle with a blurred shadow
draw_blurred_shadow(canvas, 100, 100, 400, 400, fill_color="#355d5b")
# Run the application
app.mainloop()