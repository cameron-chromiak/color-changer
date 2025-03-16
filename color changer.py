import tkinter as tk
from tkinter import filedialog, colorchooser, messagebox
from PIL import Image, ImageTk
import numpy as np
import cv2

class ColorReplaceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Replace Tool")
        
        self.canvas = tk.Canvas(root, width=400, height=300, bg='lightgray')
        self.canvas.pack()
        
        self.upload_btn = tk.Button(root, text="Upload Image", command=self.upload_image)
        self.upload_btn.pack()
        
        self.color_palette_label = tk.Label(root, text="Color Palette")
        self.color_palette_label.pack()
        
        self.color_palette_frame = tk.Frame(root)
        self.color_palette_frame.pack()
        
        self.current_color_label = tk.Label(root, text="Current Color")
        self.current_color_label.pack()
        self.current_color_display = tk.Label(root, width=10, height=2, bg="white", relief=tk.SUNKEN)
        self.current_color_display.pack()
        
        self.target_color_label = tk.Label(root, text="Target Color")
        self.target_color_label.pack()
        self.target_color_display = tk.Label(root, width=10, height=2, bg="white", relief=tk.SUNKEN)
        self.target_color_display.pack()
        
        self.pick_target_color_btn = tk.Button(root, text="Pick Target Color", command=self.pick_target_color)
        self.pick_target_color_btn.pack()
        
        self.save_btn = tk.Button(root, text="Save", command=self.save_image)
        self.save_btn.pack()
        
        self.image_path = None
        self.image = None
        self.current_color = None
        self.target_color = None
        
    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])
        if file_path:
            self.image_path = file_path
            self.image = Image.open(file_path)
            self.display_image()
            self.extract_colors()
    
    def display_image(self):
        img = self.image.resize((400, 300))
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.create_image(200, 150, image=self.tk_image)
    
    def extract_colors(self):
        self.color_palette_frame.destroy()
        self.color_palette_frame = tk.Frame(self.root)
        self.color_palette_frame.pack()
        
        img_cv = cv2.imread(self.image_path)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        pixels = np.float32(img_cv.reshape(-1, 3))
        
        num_clusters = 5
        _, labels, centers = cv2.kmeans(pixels, num_clusters, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2), 10, cv2.KMEANS_RANDOM_CENTERS)
        centers = np.uint8(centers)
        
        self.color_buttons = []
        for color in centers:
            color_hex = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'
            btn = tk.Button(self.color_palette_frame, bg=color_hex, width=3, height=1, command=lambda c=color_hex: self.select_current_color(c))
            btn.pack(side=tk.LEFT)
            self.color_buttons.append(btn)
    
    def select_current_color(self, color):
        self.current_color = color
        self.current_color_display.config(bg=color)
    
    def pick_target_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.target_color = color
            self.target_color_display.config(bg=color)
    
    def save_image(self):
        if not self.current_color or not self.target_color:
            messagebox.showerror("Error", "Please select both colors.")
            return
        
        img_cv = cv2.imread(self.image_path)
        img_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
        
        current_rgb = tuple(int(self.current_color[i:i+2], 16) for i in (1, 3, 5))
        target_rgb = tuple(int(self.target_color[i:i+2], 16) for i in (1, 3, 5))
        
        lower = np.array(current_rgb) - 10
        upper = np.array(current_rgb) + 10
        
        mask = cv2.inRange(img_cv, lower, upper)
        img_cv[mask > 0] = target_rgb
        
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("JPEG files", "*.jpeg")])
        if save_path:
            Image.fromarray(img_cv).save(save_path)
            messagebox.showinfo("Success", "Image saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = ColorReplaceApp(root)
    root.mainloop()
