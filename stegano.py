"""
STEGANO-X: Advanced Image Steganography Tool
Hide and extract images within images using LSB encoding
Supports: PNG, BMP, TIFF, WebP, GIF (extracts from JPEG too)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import struct
import hashlib
from io import BytesIO

class SteganographyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STEGANO-X - Image Steganography")
        self.root.geometry("700x500")
        self.root.configure(bg='#1a1a2e')
        self.root.resizable(True, True)
        
        # Variables
        self.cover_image_path = None
        self.secret_image_path = None
        self.stego_image_path = None
        self.cover_image = None
        self.secret_image = None
        
        self.setup_styles()
        self.create_widgets()
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('TNotebook', background='#1a1a2e')
        style.configure('TNotebook.Tab', 
                       background='#16213e',
                       foreground='white',
                       padding=[20, 10],
                       font=('Segoe UI', 11, 'bold'))
        style.map('TNotebook.Tab',
                 background=[('selected', '#0f3460')],
                 foreground=[('selected', '#00ff88')])
        
        style.configure('TFrame', background='#1a1a2e')
        style.configure('TLabel', background='#1a1a2e', foreground='white', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), foreground='#00ff88')
        style.configure('Status.TLabel', font=('Segoe UI', 9), foreground='#888888')
    
    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="🔐 STEGANO-X", style='Header.TLabel')
        header.pack(pady=15)
        
        subtitle = ttk.Label(self.root, text="Hide & Extract Images Within Images", style='Status.TLabel')
        subtitle.pack()
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Tab 1: Hide Image
        self.hide_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.hide_frame, text='  🔒 HIDE IMAGE  ')
        self.create_hide_tab()
        
        # Tab 2: Extract Image
        self.extract_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_frame, text='  🔓 EXTRACT IMAGE  ')
        self.create_extract_tab()
        
        # Tab 3: Analyze
        self.analyze_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.analyze_frame, text='  🔍 ANALYZE FILE  ')
        self.create_analyze_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, style='Status.TLabel')
        status_bar.pack(side='bottom', fill='x', pady=10)
    
    def create_hide_tab(self):
        # Configure grid weights for responsive layout
        self.hide_frame.columnconfigure(0, weight=1)
        self.hide_frame.columnconfigure(1, weight=1)
        self.hide_frame.rowconfigure(1, weight=1)  # Canvas row expands
        
        # Left header
        left_header = ttk.Frame(self.hide_frame)
        left_header.grid(row=0, column=0, sticky='ew', padx=10, pady=5)
        ttk.Label(left_header, text="Cover Image (carrier)", style='Header.TLabel').pack()
        
        # Right header  
        right_header = ttk.Frame(self.hide_frame)
        right_header.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        ttk.Label(right_header, text="Secret Image (to hide)", style='Header.TLabel').pack()
        
        # Left canvas frame (resizable)
        left_canvas_frame = ttk.Frame(self.hide_frame)
        left_canvas_frame.grid(row=1, column=0, sticky='nsew', padx=10, pady=5)
        left_canvas_frame.columnconfigure(0, weight=1)
        left_canvas_frame.rowconfigure(0, weight=1)
        
        self.cover_preview = tk.Canvas(left_canvas_frame, bg='#16213e', highlightthickness=2, highlightbackground='#0f3460')
        self.cover_preview.grid(row=0, column=0, sticky='nsew')
        self.cover_preview.bind('<Configure>', lambda e: self.center_placeholder(self.cover_preview))
        
        # Right canvas frame (resizable)
        right_canvas_frame = ttk.Frame(self.hide_frame)
        right_canvas_frame.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        right_canvas_frame.columnconfigure(0, weight=1)
        right_canvas_frame.rowconfigure(0, weight=1)
        
        self.secret_preview = tk.Canvas(right_canvas_frame, bg='#16213e', highlightthickness=2, highlightbackground='#0f3460')
        self.secret_preview.grid(row=0, column=0, sticky='nsew')
        self.secret_preview.bind('<Configure>', lambda e: self.center_placeholder(self.secret_preview))
        
        # Left info + button
        left_controls = ttk.Frame(self.hide_frame)
        left_controls.grid(row=2, column=0, sticky='ew', padx=10, pady=5)
        self.cover_info = ttk.Label(left_controls, text="", style='Status.TLabel')
        self.cover_info.pack()
        cover_btn = tk.Button(left_controls, text="📂 Select Cover", command=self.select_cover_image,
                             bg='#0f3460', fg='white', font=('Segoe UI', 9, 'bold'),
                             activebackground='#1a5490', cursor='hand2', relief='flat', padx=15, pady=5)
        cover_btn.pack(pady=3)
        
        # Right info + button
        right_controls = ttk.Frame(self.hide_frame)
        right_controls.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        self.secret_info = ttk.Label(right_controls, text="", style='Status.TLabel')
        self.secret_info.pack()
        secret_btn = tk.Button(right_controls, text="📂 Select Secret", command=self.select_secret_image,
                              bg='#0f3460', fg='white', font=('Segoe UI', 9, 'bold'),
                              activebackground='#1a5490', cursor='hand2', relief='flat', padx=15, pady=5)
        secret_btn.pack(pady=3)
        
        # Bottom controls spanning both columns
        bottom_frame = ttk.Frame(self.hide_frame)
        bottom_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=20, pady=5)
        
        # Password inline
        pw_frame = ttk.Frame(bottom_frame)
        pw_frame.pack()
        ttk.Label(pw_frame, text="Password:").pack(side='left', padx=3)
        self.hide_password = ttk.Entry(pw_frame, show='*', width=20)
        self.hide_password.pack(side='left', padx=3)
        
        # Capacity + Button
        self.capacity_label = ttk.Label(bottom_frame, text="", style='Status.TLabel')
        self.capacity_label.pack(pady=2)
        
        encode_btn = tk.Button(bottom_frame, text="🔒 HIDE & SAVE", command=self.hide_image,
                              bg='#00ff88', fg='#1a1a2e', font=('Segoe UI', 11, 'bold'),
                              activebackground='#00cc6a', cursor='hand2', relief='flat', padx=25, pady=8)
        encode_btn.pack(pady=5)
    
    def create_extract_tab(self):
        container = ttk.Frame(self.extract_frame)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Stego image selection
        ttk.Label(container, text="Stego Image (contains hidden data)", style='Header.TLabel').pack()
        ttk.Label(container, text="Select an image that may contain hidden content", style='Status.TLabel').pack()
        
        self.stego_preview = tk.Canvas(container, width=400, height=300, bg='#16213e', highlightthickness=2, highlightbackground='#0f3460')
        self.stego_preview.pack(pady=15)
        self.stego_preview.create_text(200, 150, text="No image selected", fill='#555555', font=('Segoe UI', 10))
        
        self.stego_info = ttk.Label(container, text="", style='Status.TLabel')
        self.stego_info.pack()
        
        stego_btn = tk.Button(container, text="📂 Select Stego Image", command=self.select_stego_image,
                             bg='#0f3460', fg='white', font=('Segoe UI', 10, 'bold'),
                             activebackground='#1a5490', cursor='hand2', relief='flat', padx=20, pady=8)
        stego_btn.pack(pady=10)
        
        # Password
        pw_frame = ttk.Frame(container)
        pw_frame.pack(pady=10)
        ttk.Label(pw_frame, text="Password (if encrypted):").pack(side='left', padx=5)
        self.extract_password = ttk.Entry(pw_frame, show='*', width=30)
        self.extract_password.pack(side='left', padx=5)
        
        # Extract button
        extract_btn = tk.Button(container, text="🔓 EXTRACT HIDDEN IMAGE", command=self.extract_image,
                               bg='#ff6b6b', fg='white', font=('Segoe UI', 12, 'bold'),
                               activebackground='#ee5a5a', cursor='hand2', relief='flat', padx=30, pady=12)
        extract_btn.pack(pady=15)
        
        # Extracted preview
        self.extracted_preview = tk.Canvas(container, width=300, height=200, bg='#16213e', highlightthickness=2, highlightbackground='#0f3460')
        self.extracted_preview.pack(pady=10)
        self.extracted_preview.create_text(150, 100, text="Extracted image will appear here", fill='#555555', font=('Segoe UI', 9))
    
    def create_analyze_tab(self):
        container = ttk.Frame(self.analyze_frame)
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(container, text="Analyze File for Hidden Data", style='Header.TLabel').pack()
        ttk.Label(container, text="Detect potential steganography in any image file", style='Status.TLabel').pack(pady=5)
        
        analyze_btn = tk.Button(container, text="📂 Select File to Analyze", command=self.analyze_file,
                               bg='#9b59b6', fg='white', font=('Segoe UI', 10, 'bold'),
                               activebackground='#8e44ad', cursor='hand2', relief='flat', padx=20, pady=8)
        analyze_btn.pack(pady=15)
        
        # Results text area
        self.analysis_text = tk.Text(container, height=20, bg='#16213e', fg='#00ff88', 
                                     font=('Consolas', 10), insertbackground='white', relief='flat')
        self.analysis_text.pack(fill='both', expand=True, pady=10)
        self.analysis_text.insert('1.0', '>>> Analysis results will appear here...\n')
        
        # Supported formats info
        formats_frame = ttk.Frame(container)
        formats_frame.pack(fill='x', pady=10)
        ttk.Label(formats_frame, text="Supported formats: PNG, BMP, TIFF, WebP, GIF, JPEG (read-only)", style='Status.TLabel').pack()
    
    def select_cover_image(self):
        filetypes = [
            ("All Images", "*.png *.bmp *.tiff *.tif *.webp *.gif"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("TIFF", "*.tiff *.tif"),
            ("WebP", "*.webp"),
            ("GIF", "*.gif")
        ]
        path = filedialog.askopenfilename(title="Select Cover Image", filetypes=filetypes)
        if path:
            self.cover_image_path = path
            self.cover_image = Image.open(path)
            self.update_preview(self.cover_preview, self.cover_image, 300, 250)
            
            # Show info
            w, h = self.cover_image.size
            capacity = (w * h * 3) // 8  # bytes that can be hidden (1 bit per color channel)
            self.cover_info.config(text=f"{w}x{h} | {self.cover_image.mode} | Capacity: {self.format_size(capacity)}")
            self.update_capacity()
            self.status_var.set(f"Loaded cover image: {os.path.basename(path)}")
    
    def select_secret_image(self):
        filetypes = [
            ("All Images", "*.png *.bmp *.tiff *.tif *.webp *.gif *.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("JPEG", "*.jpg *.jpeg"),
            ("BMP", "*.bmp"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Secret Image", filetypes=filetypes)
        if path:
            self.secret_image_path = path
            self.secret_image = Image.open(path)
            self.update_preview(self.secret_preview, self.secret_image, 300, 250)
            
            # Show info
            w, h = self.secret_image.size
            # Get file size
            file_size = os.path.getsize(path)
            self.secret_info.config(text=f"{w}x{h} | Size: {self.format_size(file_size)}")
            self.update_capacity()
            self.status_var.set(f"Loaded secret image: {os.path.basename(path)}")
    
    def select_stego_image(self):
        filetypes = [
            ("All Images", "*.png *.bmp *.tiff *.tif *.webp *.gif *.jpg *.jpeg"),
            ("PNG", "*.png"),
            ("BMP", "*.bmp"),
            ("All Files", "*.*")
        ]
        path = filedialog.askopenfilename(title="Select Stego Image", filetypes=filetypes)
        if path:
            self.stego_image_path = path
            img = Image.open(path)
            self.update_preview(self.stego_preview, img, 400, 300)
            
            w, h = img.size
            self.stego_info.config(text=f"{w}x{h} | {img.mode}")
            self.status_var.set(f"Loaded stego image: {os.path.basename(path)}")
    
    def update_preview(self, canvas, image, max_w, max_h):
        # Resize image to fit canvas
        img = image.copy()
        img.thumbnail((max_w - 20, max_h - 20), Image.Resampling.LANCZOS)
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img)
        
        # Store reference
        canvas.image = photo
        
        # Clear and draw centered
        canvas.delete('all')
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_image(w // 2, h // 2, image=photo)
    
    def center_placeholder(self, canvas):
        """Center placeholder text when canvas resizes"""
        # Only show placeholder if no image loaded
        if hasattr(canvas, 'image') and canvas.image:
            return
        canvas.delete('all')
        w = canvas.winfo_width()
        h = canvas.winfo_height()
        canvas.create_text(w // 2, h // 2, text="No image", fill='#555555', font=('Segoe UI', 10))
    
    def update_capacity(self):
        if self.cover_image and self.secret_image:
            w, h = self.cover_image.size
            capacity = (w * h * 3) // 8
            
            # Estimate secret image size when compressed
            buffer = BytesIO()
            self.secret_image.save(buffer, format='PNG')
            secret_size = len(buffer.getvalue())
            
            if secret_size <= capacity:
                self.capacity_label.config(
                    text=f"✅ Can hide! Secret: {self.format_size(secret_size)} | Capacity: {self.format_size(capacity)}",
                    foreground='#00ff88'
                )
            else:
                self.capacity_label.config(
                    text=f"❌ Too large! Secret: {self.format_size(secret_size)} > Capacity: {self.format_size(capacity)}",
                    foreground='#ff6b6b'
                )
    
    def format_size(self, size_bytes):
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def compress_to_fit(self, image, max_bytes):
        """Auto-resize/compress image to fit within max_bytes - AGGRESSIVE"""
        original_size = image.size
        
        # Try progressively smaller sizes - very aggressive scaling
        scales = [1.0, 0.75, 0.5, 0.4, 0.3, 0.25, 0.2, 0.15, 0.1, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01]
        
        for scale in scales:
            new_size = (max(10, int(original_size[0] * scale)), max(10, int(original_size[1] * scale)))
            resized = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if needed (for JPEG)
            if resized.mode == 'RGBA':
                rgb_resized = resized.convert('RGB')
            else:
                rgb_resized = resized
            
            # Try JPEG with decreasing quality (better compression than PNG)
            for quality in [80, 60, 40, 25, 15, 10, 5]:
                buffer = BytesIO()
                rgb_resized.save(buffer, format='JPEG', quality=quality, optimize=True)
                if len(buffer.getvalue()) <= max_bytes:
                    return resized, buffer.getvalue(), scale
        
        # Absolute last resort - tiny thumbnail
        tiny = image.resize((50, 50), Image.Resampling.LANCZOS)
        if tiny.mode == 'RGBA':
            tiny = tiny.convert('RGB')
        buffer = BytesIO()
        tiny.save(buffer, format='JPEG', quality=5)
        if len(buffer.getvalue()) <= max_bytes:
            return tiny, buffer.getvalue(), 0.01
        
        return None, None, 0
    
    def hide_image(self):
        if not self.cover_image or not self.secret_image:
            messagebox.showerror("Error", "Please select both cover and secret images!")
            return
        
        try:
            self.status_var.set("Encoding secret image...")
            self.root.update()
            
            # Check capacity first
            cover = self.cover_image.convert('RGB')
            w, h = cover.size
            capacity = (w * h * 3) // 8
            header_size = 9  # STEGX + 4 bytes size
            max_secret_size = capacity - header_size
            
            # Convert secret image to bytes
            buffer = BytesIO()
            self.secret_image.save(buffer, format='PNG')
            secret_bytes = buffer.getvalue()
            
            # Auto-resize if too large
            if len(secret_bytes) > max_secret_size:
                self.status_var.set("Secret too large - auto-resizing...")
                self.root.update()
                
                resized_img, secret_bytes, scale = self.compress_to_fit(self.secret_image, max_secret_size)
                
                if resized_img is None:
                    messagebox.showerror("Error", 
                        f"Cannot fit secret image even after maximum compression!\n"
                        f"Cover capacity: {self.format_size(max_secret_size)}\n"
                        f"Try using a larger cover image.")
                    return
                
                # Ask user if they want to proceed with resized version
                new_w, new_h = resized_img.size
                if not messagebox.askyesno("Auto-Resize", 
                    f"Secret image was resized to fit.\n\n"
                    f"Original: {self.secret_image.size[0]}x{self.secret_image.size[1]}\n"
                    f"Resized: {new_w}x{new_h} ({scale*100:.0f}%)\n"
                    f"Compressed size: {self.format_size(len(secret_bytes))}\n\n"
                    f"Proceed with hidden image?"):
                    return
            
            # Optional password encryption
            password = self.hide_password.get()
            if password:
                secret_bytes = self.xor_encrypt(secret_bytes, password)
            
            # Add header with size info
            header = b'STEGX' + struct.pack('>I', len(secret_bytes))
            data = header + secret_bytes
            
            # LSB encode
            self.status_var.set("Encoding into pixels...")
            self.root.update()
            
            pixels = list(cover.getdata())
            binary_data = ''.join(format(byte, '08b') for byte in data)
            
            new_pixels = []
            bit_index = 0
            
            for pixel in pixels:
                new_pixel = list(pixel)
                for i in range(3):  # R, G, B
                    if bit_index < len(binary_data):
                        new_pixel[i] = (new_pixel[i] & 0xFE) | int(binary_data[bit_index])
                        bit_index += 1
                new_pixels.append(tuple(new_pixel))
            
            # Create new image
            stego = Image.new('RGB', (w, h))
            stego.putdata(new_pixels)
            
            # Save
            save_path = filedialog.asksaveasfilename(
                title="Save Stego Image",
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("BMP", "*.bmp"), ("TIFF", "*.tiff")]
            )
            
            if save_path:
                stego.save(save_path, format=save_path.split('.')[-1].upper())
                self.status_var.set(f"✅ Successfully hidden! Saved to: {os.path.basename(save_path)}")
                messagebox.showinfo("Success", f"Image hidden successfully!\nSaved to: {save_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to hide image: {str(e)}")
            self.status_var.set("Error during encoding")
    
    def extract_image(self):
        if not self.stego_image_path:
            messagebox.showerror("Error", "Please select a stego image first!")
            return
        
        try:
            self.status_var.set("Extracting hidden data...")
            self.root.update()
            
            # Load image
            stego = Image.open(self.stego_image_path).convert('RGB')
            pixels = list(stego.getdata())
            
            # Extract bits
            bits = ''
            for pixel in pixels:
                for channel in pixel[:3]:
                    bits += str(channel & 1)
            
            # Convert to bytes
            all_bytes = bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))
            
            # Look for STEGX header
            if not all_bytes.startswith(b'STEGX'):
                messagebox.showwarning("Not Found", "No STEGX hidden image found in this file.\nTrying alternative extraction...")
                self.try_alternative_extraction(all_bytes)
                return
            
            # Extract size and data
            size = struct.unpack('>I', all_bytes[5:9])[0]
            secret_bytes = all_bytes[9:9 + size]
            
            # Decrypt if password
            password = self.extract_password.get()
            if password:
                secret_bytes = self.xor_encrypt(secret_bytes, password)
            
            # Try to load as image
            try:
                secret_image = Image.open(BytesIO(secret_bytes))
                self.update_preview(self.extracted_preview, secret_image, 300, 200)
                
                # Save option
                save_path = filedialog.asksaveasfilename(
                    title="Save Extracted Image",
                    defaultextension=".png",
                    filetypes=[("PNG", "*.png"), ("All Files", "*.*")]
                )
                
                if save_path:
                    secret_image.save(save_path)
                    self.status_var.set(f"✅ Extracted and saved: {os.path.basename(save_path)}")
                    messagebox.showinfo("Success", f"Hidden image extracted!\nSaved to: {save_path}")
                else:
                    self.status_var.set("✅ Hidden image found and displayed")
            
            except Exception as e:
                messagebox.showerror("Error", f"Data found but couldn't decode as image: {str(e)}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Extraction failed: {str(e)}")
            self.status_var.set("Error during extraction")
    
    def try_alternative_extraction(self, data):
        """Try to find commonly hidden data patterns"""
        # Look for PNG header
        png_sig = b'\x89PNG\r\n\x1a\n'
        if png_sig in data:
            start = data.find(png_sig)
            messagebox.showinfo("Found!", f"Found PNG signature at offset {start}. Data may be appended to file.")
        
        # Look for JPEG header
        jpg_sig = b'\xff\xd8\xff'
        if jpg_sig in data:
            start = data.find(jpg_sig)
            messagebox.showinfo("Found!", f"Found JPEG signature at offset {start}. Data may be appended to file.")
    
    def xor_encrypt(self, data, password):
        """Simple XOR encryption with password"""
        key = hashlib.sha256(password.encode()).digest()
        return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))
    
    def analyze_file(self):
        filetypes = [("All Files", "*.*")]
        path = filedialog.askopenfilename(title="Select File to Analyze", filetypes=filetypes)
        if not path:
            return
        
        self.analysis_text.delete('1.0', tk.END)
        self.analysis_text.insert(tk.END, f">>> Analyzing: {path}\n\n")
        
        try:
            # Basic file info
            file_size = os.path.getsize(path)
            self.analysis_text.insert(tk.END, f"📁 File Size: {self.format_size(file_size)}\n")
            
            # Read file
            with open(path, 'rb') as f:
                data = f.read()
            
            # Check for image format
            img = None
            try:
                img = Image.open(path)
                w, h = img.size
                self.analysis_text.insert(tk.END, f"🖼️ Image: {w}x{h} | Mode: {img.mode} | Format: {img.format}\n")
                
                # Calculate expected vs actual size
                expected_size = w * h * len(img.mode)
                if file_size > expected_size * 1.5:
                    self.analysis_text.insert(tk.END, f"⚠️ File larger than expected - possible appended data!\n")
            except:
                self.analysis_text.insert(tk.END, "❌ Not a valid image file\n")
            
            self.analysis_text.insert(tk.END, "\n--- SIGNATURE ANALYSIS ---\n\n")
            
            # Known steganography signatures
            signatures = {
                b'STEGX': 'STEGX (this tool)',
                b'\x89PNG\r\n\x1a\n': 'PNG',
                b'\xff\xd8\xff': 'JPEG',
                b'GIF8': 'GIF',
                b'BM': 'BMP',
                b'RIFF': 'WebP/AVI',
                b'PK\x03\x04': 'ZIP archive',
                b'Rar!': 'RAR archive',
                b'7z\xbc\xaf': '7-Zip archive',
                b'%PDF': 'PDF document',
                b'MZ': 'Windows executable',
            }
            
            found_sigs = []
            for sig, name in signatures.items():
                if sig in data:
                    positions = []
                    start = 0
                    while True:
                        pos = data.find(sig, start)
                        if pos == -1:
                            break
                        positions.append(pos)
                        start = pos + 1
                    found_sigs.append((name, positions))
            
            for name, positions in found_sigs:
                self.analysis_text.insert(tk.END, f"✅ Found {name} at: {positions[:5]}{'...' if len(positions) > 5 else ''}\n")
            
            if not found_sigs:
                self.analysis_text.insert(tk.END, "No known signatures found.\n")
            
            # LSB analysis (check for patterns in LSB)
            self.analysis_text.insert(tk.END, "\n--- LSB ANALYSIS ---\n\n")
            
            if img:
                img_rgb = img.convert('RGB')
                pixels = list(img_rgb.getdata())[:10000]  # Sample first 10k pixels
                
                lsb_bits = []
                for p in pixels:
                    for c in p[:3]:
                        lsb_bits.append(c & 1)
                
                # Check randomness
                ones = sum(lsb_bits)
                zeros = len(lsb_bits) - ones
                ratio = ones / len(lsb_bits) if lsb_bits else 0
                
                self.analysis_text.insert(tk.END, f"LSB Distribution: {zeros} zeros, {ones} ones ({ratio:.2%} ones)\n")
                
                if 0.45 < ratio < 0.55:
                    self.analysis_text.insert(tk.END, "⚠️ LSB appears random - possible steganography!\n")
                else:
                    self.analysis_text.insert(tk.END, "✅ LSB appears normal\n")
                
                # Try to decode first few bytes
                first_bytes = bytes(int(''.join(str(b) for b in lsb_bits[i:i+8]), 2) for i in range(0, min(100*8, len(lsb_bits)), 8))
                
                if first_bytes.startswith(b'STEGX'):
                    size = struct.unpack('>I', first_bytes[5:9])[0]
                    self.analysis_text.insert(tk.END, f"\n🔓 STEGX DATA DETECTED! Hidden size: {self.format_size(size)}\n")
                    self.analysis_text.insert(tk.END, "Use the EXTRACT tab to retrieve the hidden image!\n")
            
            # Check for appended data after image end
            self.analysis_text.insert(tk.END, "\n--- APPENDED DATA CHECK ---\n\n")
            
            # For PNG, look for IEND chunk and check if there's data after it
            iend = data.find(b'IEND')
            if iend != -1:
                after_iend = len(data) - (iend + 8)  # IEND + CRC
                if after_iend > 0:
                    self.analysis_text.insert(tk.END, f"⚠️ {after_iend} bytes of data after PNG end!\n")
                else:
                    self.analysis_text.insert(tk.END, "✅ No appended data after PNG\n")
            
            # For JPEG, look for FFD9 end marker
            jpg_end = data.rfind(b'\xff\xd9')
            if jpg_end != -1:
                after_jpg = len(data) - (jpg_end + 2)
                if after_jpg > 0:
                    self.analysis_text.insert(tk.END, f"⚠️ {after_jpg} bytes of data after JPEG end!\n")
            
            self.analysis_text.insert(tk.END, "\n>>> Analysis complete.\n")
            self.status_var.set(f"Analysis complete: {os.path.basename(path)}")
            
        except Exception as e:
            self.analysis_text.insert(tk.END, f"\n❌ Error: {str(e)}\n")


def main():
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
