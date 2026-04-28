"""
Advanced Fractal rendering engine with mathematical breakdown.

Generates self-repeating fractal images from feature vectors using various mathematical models.
Implements Organic Recursive Tree, Sierpinski Triangle, Dragon Curve, Mandelbrot Set, and Koch Snowflake.
"""
import math
import hashlib
import uuid
from typing import Dict, Tuple, Optional
from PIL import Image, ImageDraw, ImageFilter, ImageChops
import numpy as np
import logging

logger = logging.getLogger(__name__)

class FractalRenderer:
    def __init__(self, width: int = 1024, height: int = 1024):
        self.width = width
        self.height = height

    def generate_seed(self, song_title: str, artist_name: Optional[str] = None) -> int:
        unique_id = str(uuid.uuid4())
        seed_str = f"{song_title}:{artist_name or ''}:{unique_id}"
        seed_hash = int(hashlib.md5(seed_str.encode()).hexdigest()[:8], 16)
        return seed_hash % (2**31)

    def map_features_to_params(
        self, features: Dict[str, float], seed: int, overrides: Dict[str, any] = None
    ) -> Dict[str, any]:
        
        overrides = overrides or {}
        
        bpm = features.get("normalized_tempo", 0.5)
        energy = features.get("energy", 0.5)
        brightness = features.get("brightness", 0.5)
        complexity = features.get("complexity", 0.5)
        symmetry = features.get("symmetry_score", 0.5)

        depth = overrides.get("depth") or int(5 + (complexity) * 5)
        base_angle = overrides.get("angle") or (math.pi / 4 * (0.5 + symmetry))
        length_ratio = 0.65 + energy * 0.15

        model = overrides.get("model")
        if not model or model == "auto":
            if complexity > 0.8:
                model = "mandelbrot"
            elif energy > 0.7:
                model = "dragon_curve"
            elif symmetry > 0.8:
                model = "koch_snowflake"
            elif symmetry > 0.6:
                model = "sierpinski"
            else:
                model = "organic_tree"

        if overrides.get("palette") and overrides.get("palette") != "auto":
            palette = overrides.get("palette")
        else:
            if brightness > 0.7:
                palette = "vibrant"
            elif energy > 0.5:
                palette = "warm"
            else:
                palette = "cool"

        glow_radius = overrides.get("glow_radius") or (5 + int(energy * 10))

        params = {
            "model": model,
            "depth": min(depth, 14), 
            "base_angle": base_angle,
            "length_ratio": length_ratio,
            "palette": palette,
            "glow_radius": glow_radius,
            "seed": seed,
            
            "energy": energy,
            "brightness": brightness,
            "bpm": bpm,
            "complexity": complexity
        }
        return params

    def render(self, features: Dict[str, float], song_title: str, 
               artist_name: Optional[str] = None, overrides: Dict[str, any] = None) -> Tuple[Image.Image, Dict[str, any]]:
        seed = self.generate_seed(song_title, artist_name)
        params = self.map_features_to_params(features, seed, overrides)
        
        math_details = {}
        
        if params["model"] == "dragon_curve":
            img, math_details = self.render_dragon_curve(params)
        elif params["model"] == "sierpinski":
            img, math_details = self.render_sierpinski(params)
        elif params["model"] == "mandelbrot":
            img, math_details = self.render_mandelbrot(params)
        elif params["model"] == "koch_snowflake":
            img, math_details = self.render_koch_snowflake(params)
        else:
            img, math_details = self.render_organic_tree(params)
            
        img = self.apply_bloom(img, params["glow_radius"])
        
        metadata = {
            "model": params["model"],
            "depth": params["depth"],
            "color_palette": params["palette"],
            "seed": str(seed),
            "math_details": math_details
        }
        return img, metadata

    def apply_bloom(self, img: Image.Image, radius: int) -> Image.Image:
        blurred = img.filter(ImageFilter.GaussianBlur(radius))
        return ImageChops.screen(img, blurred)

    def _get_palette(self, palette_name: str) -> list:
        palettes = {
            "cool": [(30, 80, 180), (50, 110, 220), (70, 150, 240), (100, 180, 255), (150, 220, 255)],
            "warm": [(180, 50, 30), (220, 80, 40), (250, 120, 60), (255, 160, 90), (255, 200, 130)],
            "vibrant": [(200, 40, 120), (140, 60, 200), (80, 120, 240), (40, 180, 180), (160, 220, 60)],
        }
        return palettes.get(palette_name, palettes["cool"])

    # --- ADVANCED FRACTAL MODELS ---

    def render_organic_tree(self, params: Dict[str, any]) -> Tuple[Image.Image, dict]:
        img = Image.new("RGB", (self.width, self.height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)
        rng = np.random.RandomState(params["seed"])
        
        start_x = self.width // 2
        start_y = self.height - 50
        start_length = min(self.width, self.height) * 0.25
        colors = self._get_palette(params["palette"])

        self._draw_organic_branch(draw, start_x, start_y, start_length, -math.pi / 2, 
                                  params["depth"], params, colors, rng)
                                  
        math_details = {
            "equation": "Recursive Branching: L_{n+1} = L_n * ratio, \u03b8_{n+1} = \u03b8_n \u00b1 \u0394\u03b8",
            "description": "An organic recursive tree where each branch splits into smaller sub-branches. The angle and length of each branch are determined by the song's energy and BPM, creating an organic, botanical structure.",
            "dynamic_variables": f"Length Ratio: {params['length_ratio']:.2f} (from Energy), Base Angle: {math.degrees(params['base_angle']):.1f}\u00b0 (from BPM/Symmetry)"
        }
        return img, math_details

    def _draw_organic_branch(self, draw: ImageDraw.Draw, x: float, y: float, length: float, angle: float, 
                             depth: int, params: Dict[str, any], colors: list, rng: np.random.RandomState):
        if depth <= 0 or length < 2: 
            if rng.uniform(0, 1) > 0.5:
                color = colors[-1]
                draw.ellipse([x-2, y-2, x+2, y+2], fill=color)
            return
            
        curve_angle = angle + rng.uniform(-0.1, 0.1)
        end_x = x + length * math.cos(curve_angle)
        end_y = y + length * math.sin(curve_angle)
        
        color = colors[min(len(colors) - 1 - (depth % len(colors)), len(colors) - 1)]
        thickness = max(1, int(depth * 1.5))
        
        draw.line([(int(x), int(y)), (int(end_x), int(end_y))], fill=color, width=thickness)

        num_branches = 2 if rng.uniform(0, 1) > 0.2 else 3
        for i in range(num_branches):
            offset = -params["base_angle"] + (2 * params["base_angle"] * i / (num_branches - 1)) if num_branches > 1 else 0
            new_angle = curve_angle + offset + rng.uniform(-0.2, 0.2)
            new_length = length * params["length_ratio"] * rng.uniform(0.8, 1.2)
            self._draw_organic_branch(draw, end_x, end_y, new_length, new_angle, depth - 1, params, colors, rng)

    def render_dragon_curve(self, params: Dict[str, any]) -> Tuple[Image.Image, dict]:
        img = Image.new("RGB", (self.width, self.height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)
        colors = self._get_palette(params["palette"])
        
        axiom = "FX"
        rules = {"X": "X+YF+", "Y": "-FX-Y"}
        depth = min(params["depth"] + 4, 16) 
        
        sentence = axiom
        for _ in range(depth):
            sentence = "".join(rules.get(char, char) for char in sentence)
            
        x, y = self.width * 0.3, self.height * 0.4
        angle = 0
        length = min(self.width, self.height) * 0.6 / (math.sqrt(2) ** depth)
        
        path = [(x, y)]
        for char in sentence:
            if char == "F":
                x += length * math.cos(angle)
                y += length * math.sin(angle)
                path.append((x, y))
            elif char == "+":
                angle += math.pi / 2
            elif char == "-":
                angle -= math.pi / 2
                
        for i in range(len(path) - 1):
            color = colors[int((i / len(path)) * (len(colors) - 1))]
            draw.line([path[i], path[i+1]], fill=color, width=1)
            
        math_details = {
            "equation": "Axiom: FX | Rules: (X \u2192 X+YF+), (Y \u2192 -FX-Y)",
            "description": "The Heighway Dragon Curve is an L-system fractal. It represents a single line repeatedly folded in half. The song's energy dictates the depth of the recursive folds.",
            "dynamic_variables": f"Recursion Depth: {depth} (from Energy), Segment Length: {length:.3f}px"
        }
        return img, math_details

    def render_sierpinski(self, params: Dict[str, any]) -> Tuple[Image.Image, dict]:
        img = Image.new("RGB", (self.width, self.height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)
        colors = self._get_palette(params["palette"])
        depth = min(params["depth"], 8)
        
        margin = 50
        p1 = (self.width / 2, margin)
        p2 = (margin, self.height - margin)
        p3 = (self.width - margin, self.height - margin)
        
        self._draw_sierpinski(draw, p1, p2, p3, depth, colors, 0)
        
        math_details = {
            "equation": "S_{n+1} = S_n \u222a T(S_n)",
            "description": "The Sierpinski Triangle is a fractal with an overall shape of an equilateral triangle, subdivided recursively into smaller equilateral triangles. Driven by the track's symmetry score.",
            "dynamic_variables": f"Subdivision Depth: {depth} (from Complexity), Symmetry Score: {params['symmetry_score'] if 'symmetry_score' in params else 0.8}"
        }
        return img, math_details
        
    def _draw_sierpinski(self, draw: ImageDraw.Draw, p1, p2, p3, depth, colors, color_idx):
        if depth == 0:
            color = colors[color_idx % len(colors)]
            draw.polygon([p1, p2, p3], outline=color, fill=None)
        else:
            p12 = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
            p23 = ((p2[0]+p3[0])/2, (p2[1]+p3[1])/2)
            p31 = ((p3[0]+p1[0])/2, (p3[1]+p1[1])/2)
            self._draw_sierpinski(draw, p1, p12, p31, depth-1, colors, color_idx+1)
            self._draw_sierpinski(draw, p12, p2, p23, depth-1, colors, color_idx+1)
            self._draw_sierpinski(draw, p31, p23, p3, depth-1, colors, color_idx+1)

    def render_mandelbrot(self, params: Dict[str, any]) -> Tuple[Image.Image, dict]:
        """Mandelbrot Set."""
        max_iter = 50 + int(params["depth"] * 10)
        
        # Determine zoom based on BPM and Energy to make it dynamic
        rng = np.random.RandomState(params["seed"])
        zoom = 1.0 + (params["energy"] * 2.0)
        center_x = -0.5 + rng.uniform(-0.5, 0.5) / zoom
        center_y = 0.0 + rng.uniform(-0.5, 0.5) / zoom
        
        width_range = 3.0 / zoom
        height_range = 3.0 / zoom
        
        x = np.linspace(center_x - width_range/2, center_x + width_range/2, self.width)
        y = np.linspace(center_y - height_range/2, center_y + height_range/2, self.height)
        X, Y = np.meshgrid(x, y)
        C = X + 1j * Y
        Z = np.zeros_like(C)
        
        output = np.zeros(C.shape, dtype=int)
        
        for i in range(max_iter):
            mask = np.abs(Z) < 2
            Z[mask] = Z[mask]**2 + C[mask]
            output[mask] = i
            
        img_array = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        colors = self._get_palette(params["palette"])
        
        norm_output = output / max_iter
        for i in range(len(colors)):
            threshold_low = i / len(colors)
            threshold_high = (i+1) / len(colors)
            mask = (norm_output >= threshold_low) & (norm_output < threshold_high)
            img_array[mask] = colors[i]
            
        math_details = {
            "equation": "Z_{n+1} = Z_n^2 + C, Z_0 = 0",
            "description": "The Mandelbrot Set marks the set of complex numbers 'c' for which the function does not diverge when iterated. The zoom level and focal point are driven by the track's Energy and BPM.",
            "dynamic_variables": f"Max Iterations: {max_iter}, Zoom Level: {zoom:.2f}x, Focus (C): {center_x:.2f} + {center_y:.2f}i",
            "shader_uniforms": {
                "max_iter": max_iter,
                "zoom": zoom,
                "center_x": center_x,
                "center_y": center_y,
                "palette": params["palette"]
            }
        }
        return Image.fromarray(img_array, 'RGB'), math_details

    def render_koch_snowflake(self, params: Dict[str, any]) -> Tuple[Image.Image, dict]:
        img = Image.new("RGB", (self.width, self.height), color=(5, 5, 10))
        draw = ImageDraw.Draw(img)
        colors = self._get_palette(params["palette"])
        depth = min(params["depth"] - 1, 6)
        
        margin = 100
        size = min(self.width, self.height) - 2 * margin
        height = size * math.sqrt(3) / 2
        
        # Center triangle
        p1 = (self.width/2, self.height/2 - height/3 * 2) # Top
        p2 = (self.width/2 - size/2, self.height/2 + height/3) # Bottom Left
        p3 = (self.width/2 + size/2, self.height/2 + height/3) # Bottom Right
        
        lines = [(p1, p2), (p2, p3), (p3, p1)]
        
        for _ in range(depth):
            new_lines = []
            for p_start, p_end in lines:
                x1, y1 = p_start
                x2, y2 = p_end
                
                dx = x2 - x1
                dy = y2 - y1
                
                pa = (x1 + dx/3, y1 + dy/3)
                pc = (x1 + dx*2/3, y1 + dy*2/3)
                
                angle = math.atan2(dy, dx) - math.pi/3
                dist = math.sqrt(dx**2 + dy**2) / 3
                
                pb = (pa[0] + math.cos(angle)*dist, pa[1] + math.sin(angle)*dist)
                
                new_lines.extend([(p_start, pa), (pa, pb), (pb, pc), (pc, p_end)])
            lines = new_lines
            
        color = colors[-1]
        for start, end in lines:
            draw.line([start, end], fill=color, width=2)
            
        math_details = {
            "equation": "Koch Curve Construction: Line \u2192 4 Segments per Iteration",
            "description": "The Koch Snowflake is built by starting with an equilateral triangle, and recursively replacing the middle third of every line segment with two segments that form a smaller equilateral bump. Infinite perimeter, finite area.",
            "dynamic_variables": f"Recursions: {depth} (from Complexity), Line Segments: {len(lines)}"
        }
        return img, math_details
