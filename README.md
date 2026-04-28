# Fractal Resonance 🌌🎵

**Fractal Resonance** is a full-stack, mathematics-driven generative art platform that converts any song into an infinite, self-repeating fractal. It uses audio signal processing (`librosa`) and lyrical analysis to dynamically mutate complex mathematical equations. 

The application has been engineered to production standards, featuring **Interactive WebGL GPU Shaders**, **Real-Time Audio Reactivity**, **MP4 Video Exporting**, and full **Docker containerization**.

## ✨ Core Features

### 1. Interactive 3D GPU Rendering (WebGL)
Instead of static images, the **Mandelbrot Set** engine is fully WebGL-accelerated using `Three.js` and custom GLSL fragment shaders. 
- **Infinite Zoom:** Click and drag to pan, and use your scroll wheel or the floating UI controls to infinitely zoom into the mathematical structure in real-time at 60 FPS.
- **Audio Reactivity:** Built with the **Web Audio API**, the fractal physically pulses, zooms, and shifts chromatic intensity in real-time to the beat of your playing audio file.

### 2. Acoustic Mathematics & Signal Processing
The backend uses `librosa` to extract the exact Tempo (BPM), Energy, Brightness, and Timbral Complexity from uploaded audio. These features are injected as *mutation vectors* into mathematical equations (Mandelbrot Set, Koch Snowflake, Dragon Curve, Sierpinski Geometry).
- For example, the song's **Energy** alters the focal point $C$ in the Mandelbrot equation, and the **BPM** dictates the recursive depth.

### 3. Server-Side Video Export
The backend features an asynchronous video rendering pipeline utilizing `imageio` and `ffmpeg`. It mathematically calculates and renders unique fractal frames over time, compiling them into a smooth H.264 MP4 looping video ready for social media.

### 4. Lyrical Topology
Integrates with the iTunes Search API for intelligent typo resolution, then fetches the raw lyrics to calculate symmetry and structural repetition scores.

### 5. Immersive "Glassmorphic" UI
A stunning, Awwwards-inspired React frontend featuring `Framer Motion` animations, a premium glassmorphic control panel, and dynamic background wallpapers that sync to the currently generated fractal.

---

## 🛠 Tech Stack

### Frontend & Graphics
- **React.js & Vite** for lightning-fast module bundling.
- **Three.js, React Three Fiber & Drei** for WebGL 3D/2D canvas rendering and custom GPU shaders.
- **Web Audio API** for real-time frequency analysis.
- **TailwindCSS** for responsive, brutalist styling.
- **Framer Motion** for buttery-smooth scroll animations.

### Backend & Audio Processing
- **FastAPI (Python)** for a highly performant, asynchronous backend architecture.
- **Librosa & NumPy** for deep audio signal processing and complex math generation.
- **ImageIO & FFmpeg** for headless MP4 video rendering.
- **Pillow (PIL)** for rendering high-resolution static fractal arrays.

### DevOps
- **Docker & Docker Compose** for instant, replicable containerized deployment.
- **GitHub Actions** for CI/CD automated syntax testing and build verification.

---

## 🚀 Getting Started

### Option 1: Run via Docker (Recommended)
You can boot up the entire full-stack application (frontend + backend + proxy networks) with a single command:
```bash
docker-compose up -d --build
```
The app will be instantly available at `http://localhost:5173`.

### Option 2: Run Locally

**1. Backend Setup**
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn app.main:app --reload
```
*Runs on `http://localhost:8000`.*

**2. Frontend Setup**
```bash
cd frontend
npm install
npm run dev
```
*Runs on `http://localhost:5173`.*

---

## 🧠 The Mathematics Exposed
The application features a dedicated "Mathematics" UI section that reveals the exact equations, axioms, and rules used to render your specific image. It details exactly how the audio mutated the math, ensuring full transparency behind the generative art.

## 📝 License
This project is open-source and available under the MIT License.
