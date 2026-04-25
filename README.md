# Fractal Resonance 🌌🎵

**Fractal Resonance** is a full-stack, mathematics-driven generative art platform that converts any song into an infinite, self-repeating fractal. It uses audio signal processing and lyrical analysis to dynamically mutate complex mathematical equations (like the Mandelbrot Set and Koch Snowflake), rendering a completely unique, mathematically perfect visual signature for every track.

## ✨ Features
- **Acoustic Mathematics:** Replaces generic noise algorithms with true recursive fractals. Choose between the Mandelbrot Set, Koch Snowflake, Dragon Curve, or an Organic Recursive Tree.
- **Intelligent Audio Analysis:** Powered by `librosa`, the backend extracts the exact Tempo (BPM), Energy, Brightness, and Timbral Complexity from an uploaded `.mp3` or `.wav`.
- **Lyrical Topology:** Integrates with the iTunes Search API for intelligent typo resolution, then fetches the raw lyrics to calculate symmetry and structural repetition scores.
- **Dynamic Chromatics:** The generated fractal is rendered using a color palette and zoom level perfectly mapped to the song's energy and emotional brightness.
- **Immersive UI:** A stunning, Awwwards-inspired React frontend featuring Framer Motion animations, a premium glassmorphic control panel, and dynamic background wallpapers that adapt to the generated fractal.
- **The Mathematics Exposed:** A dedicated UI section that reveals the exact equations, axioms, and rules used to render your specific image, detailing exactly how the audio mutated the math.

## 🛠 Tech Stack
### Frontend
- **React.js & Vite** for lightning-fast module bundling.
- **TailwindCSS** for a responsive, modern, brutalist design system.
- **Framer Motion** for buttery-smooth scroll animations and layout transitions.

### Backend
- **FastAPI** (Python) for a highly performant, asynchronous backend architecture.
- **Librosa & NumPy** for deep audio signal processing and complex mathematical generation.
- **Pillow (PIL)** for rendering and post-processing the high-resolution fractal arrays.
- **httpx** for asynchronous external API requests (iTunes & Lyrics.ovh).

## 🚀 Getting Started

### Prerequisites
Make sure you have Node.js (v18+) and Python (v3.9+) installed.

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Install the required Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
3. Start the FastAPI server:
   ```bash
   python3 -m uvicorn app.main:app --reload
   ```
   *The backend will be running at `http://localhost:8000`.*

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node modules:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   *The frontend will be running at `http://localhost:5173`.*

## 🧠 How It Works
1. **The Input:** You submit a song title, artist name, and optionally an audio file.
2. **The Analysis:** The backend uses iTunes to intelligently correct typos, fetches the lyrics, and uses `librosa` to extract the acoustic footprint (BPM, Energy, Symmetry).
3. **The Mutation:** These acoustic features are injected into a mathematical equation (e.g. $Z_{n+1} = Z_n^2 + C$). For instance, the song's Energy alters the focal point $C$, and the BPM dictates the zoom level.
4. **The Render:** A uniquely seeded, high-resolution fractal is generated, bloomed, and passed back to the frontend to act as your dynamic, immersive wallpaper!

## 📝 License
This project is open-source and available under the MIT License.
