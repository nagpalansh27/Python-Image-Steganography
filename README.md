# Stegano-X &bull; Digital Image Steganography Engine

[![Live Web Demo](https://img.shields.io/badge/Live_Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://python-image-steganography.vercel.app)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![JavaScript](https://img.shields.io/badge/Web-HTML5_Canvas-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

An institutional-grade digital image steganography suite providing **Least Significant Bit (LSB) pixel-level payload concealment**. Includes both a **native Python Tkinter desktop engine** and a **zero-install, client-side WebAssembly / HTML5 Canvas web application**.

🌐 **Instant Live Web Demo**: **[python-image-steganography.vercel.app](https://python-image-steganography.vercel.app)**

---

## 🏛️ System Architecture & How It Works

Steganography is the science of hiding data in plain sight. Unlike encryption which masks content but reveals a secret exists, steganography conceals the very presence of communication.

```
[ Secret Payload ] (Text / File / Cryptographic Key)
        │
        ▼  (Binary Bitstream Conversion)
  01010011 01010100 01000101 01000111 ...
        │
        ▼  (Least Significant Bit Substitution)
  Original Pixel:  R: 11010110   G: 10101101   B: 01101111
  Payload Bits:         │ (1)          │ (0)          │ (1)
  Modified Pixel:  R: 11010111   G: 10101100   B: 01101111
                        ▲              ▲              ▲
               (Imperceptible &plusmn;1 LSB delta, delta-E < 0.3)
```

1. **Carrier Image Reading**: The image is mapped into an uncompressed RGBA pixel buffer (each channel $0 \dots 255$, 8 bits).
2. **Payload Serialization**: The input text/data is prepended with a magic marker (`STEG27::`), length descriptor, and converted to a continuous stream of binary bits.
3. **LSB Replacement**: For each byte in the RGB channels, the least significant bit (bit 0) is replaced with a payload bit:
   $$\text{Pixel}' = (\text{Pixel} \ \& \ \sim 1) \ | \ \text{bit}$$
4. **Visual Integrity**: The change in luminance is $\le 1/256 \approx 0.39\%$, completely invisible to human vision ($\Delta E < 0.3$) and immune to casual visual inspection.

---

## 📂 Project Structure & Key Files

```
Python-Image-Steganography/
├── index.html        # P0: Production web application (Client-side HTML5 Canvas LSB engine)
├── stegano.py        # P0: Desktop GUI application (Python 3, Tkinter, Pillow/PIL)
└── README.md         # P1: Documentation & Developer specification
```

---

## 🚀 How to Run & Test

### 1. Web Application (Zero Install / Instant)
- **Live Vercel Production**: [python-image-steganography.vercel.app](https://python-image-steganography.vercel.app)
- **Local Testing**: Simply double-click `index.html` in any modern web browser.

### 2. Desktop Python GUI
```bash
# Clone the repository
git clone https://github.com/nagpalansh27/Python-Image-Steganography.git
cd Python-Image-Steganography

# Install dependencies
pip install pillow

# Launch the desktop GUI
python stegano.py
```

---

## 🤖 AI & Developer Tweaking Cheatsheet

If an AI agent or developer is modifying this tool, follow these exact guidelines:

| File | Component | What to Tweak | How to Modify |
| :--- | :--- | :--- | :--- |
| `index.html` | Header Delimiter | Change magic byte header | Modify `const HEADER = "STEG27::";` and terminator `::END`. |
| `index.html` | Bit Depth | Increase capacity from 1-bit to 2-bit LSB | Change `(data[i] & ~1) | bit` to `(data[i] & ~3) | two_bits`. |
| `stegano.py` | GUI Layout | Adjust Tkinter frame geometry & colors | Modify `tk.Tk()` canvas dimensions in `SteganoApp.__init__`. |
| `stegano.py` | Carrier Types | Add image format support | Modify `filetypes=[("Images", "*.png *.bmp *.webp *.tiff")]`. |

### ⚠️ Critical Constraints:
- **Never use JPEG for Stego output**: JPEG lossy DCT compression quantizes high-frequency coefficients, destroying LSB bits upon save. Always save encoded stego images as **PNG** or **BMP**.
- **Alpha Channel Preservation**: Always skip byte index `(i + 1) % 4 === 0` in web canvas to prevent image transparency corruption.
