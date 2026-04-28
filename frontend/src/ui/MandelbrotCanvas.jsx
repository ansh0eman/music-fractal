import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { MapControls } from '@react-three/drei';
import * as THREE from 'three';

const MandelbrotShaderMaterial = {
  uniforms: {
    u_resolution: { value: new THREE.Vector2() },
    u_zoom: { value: 1.0 },
    u_center: { value: new THREE.Vector2(0, 0) },
    u_max_iter: { value: 100 },
    u_color_type: { value: 0 },
    u_audio_energy: { value: 0.0 }
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      // Bypass camera matrices to ensure the plane exactly fills the entire screen
      gl_Position = vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    uniform vec2 u_resolution;
    uniform float u_zoom;
    uniform vec2 u_center;
    uniform int u_max_iter;
    uniform int u_color_type;
    uniform float u_audio_energy;
    
    varying vec2 vUv;

    vec3 get_color(float iter, float max_iter) {
      if (iter == max_iter) return vec3(0.0);
      
      float t = iter / max_iter;
      
      if (u_color_type == 0) {
        // Cool (Blues)
        return vec3(0.1, 0.4 * t, 0.9 * t + 0.1);
      } else if (u_color_type == 1) {
        // Warm (Reds)
        return vec3(0.9 * t + 0.1, 0.4 * t, 0.1);
      } else {
        // Vibrant
        float r = 0.5 + 0.5 * cos(6.28318 * (1.0 * t + 0.0));
        float g = 0.5 + 0.5 * cos(6.28318 * (1.0 * t + 0.33));
        float b = 0.5 + 0.5 * cos(6.28318 * (1.0 * t + 0.67));
        return vec3(r, g, b);
      }
    }

    void main() {
      // Normalize coordinates
      vec2 c = vUv * 2.0 - 1.0;
      c.x *= u_resolution.x / u_resolution.y; // Aspect ratio
      
      // Apply audio energy to zoom (pulsing effect)
      float dynamic_zoom = u_zoom * (1.0 + u_audio_energy * 0.2);
      c = c / dynamic_zoom + u_center;

      vec2 z = vec2(0.0);
      float iter = 0.0;
      float max_iter_f = float(u_max_iter);
      
      for(int i = 0; i < 1000; i++) {
        if (float(i) >= max_iter_f) break;
        
        float x = (z.x * z.x - z.y * z.y) + c.x;
        float y = (z.y * z.x + z.x * z.y) + c.y;
        
        if ((x * x + y * y) > 4.0) break;
        
        z.x = x;
        z.y = y;
        iter++;
      }

      // Smooth coloring
      if (iter < max_iter_f) {
        float log_zn = log(z.x*z.x + z.y*z.y) / 2.0;
        float nu = log(log_zn / log(2.0)) / log(2.0);
        iter = iter + 1.0 - nu;
      }

      vec3 color = get_color(iter, max_iter_f);
      // Brighten color based on audio energy
      color += vec3(u_audio_energy * 0.3);
      gl_FragColor = vec4(color, 1.0);
    }
  `
};

const ShaderPlane = ({ uniforms, audioData, dynamicParams }) => {
  const meshRef = useRef();
  const { size } = useThree();

  const material = useMemo(() => {
    const mat = new THREE.ShaderMaterial({
      vertexShader: MandelbrotShaderMaterial.vertexShader,
      fragmentShader: MandelbrotShaderMaterial.fragmentShader,
      uniforms: THREE.UniformsUtils.clone(MandelbrotShaderMaterial.uniforms)
    });
    return mat;
  }, []);

  useFrame((state) => {
    if (material) {
      material.uniforms.u_resolution.value.set(size.width, size.height);
      
      // Update audio energy uniform safely
      if (audioData && audioData.current !== undefined) {
        material.uniforms.u_audio_energy.value = audioData.current;
      }

      // Read zoom and pan from dynamicParams
      material.uniforms.u_zoom.value = dynamicParams.current.zoom;
      material.uniforms.u_center.value.set(
        dynamicParams.current.center_x,
        dynamicParams.current.center_y
      );
      
      material.uniforms.u_max_iter.value = uniforms.max_iter;
      
      let cType = 0;
      if (uniforms.palette === "warm") cType = 1;
      if (uniforms.palette === "vibrant") cType = 2;
      material.uniforms.u_color_type.value = cType;
    }
  });

  return (
    <mesh ref={meshRef}>
      <planeGeometry args={[2, 2]} />
      <primitive object={material} attach="material" />
    </mesh>
  );
};

export function MandelbrotCanvas({ uniforms, audioData }) {
  const shaderParams = useRef({
    zoom: uniforms.zoom,
    center_x: uniforms.center_x,
    center_y: uniforms.center_y
  });

  const isDragging = useRef(false);
  const previousMouse = useRef({ x: 0, y: 0 });

  const handlePointerDown = (e) => {
    isDragging.current = true;
    previousMouse.current = { x: e.clientX, y: e.clientY };
  };

  const handlePointerUp = () => {
    isDragging.current = false;
  };

  const handlePointerMove = (e) => {
    if (isDragging.current) {
      const dx = e.clientX - previousMouse.current.x;
      const dy = e.clientY - previousMouse.current.y;
      
      const panSpeed = 0.003 / shaderParams.current.zoom;
      shaderParams.current.center_x -= dx * panSpeed;
      shaderParams.current.center_y += dy * panSpeed;
      
      previousMouse.current = { x: e.clientX, y: e.clientY };
    }
  };

  const handleWheel = (e) => {
    e.stopPropagation();
    const zoomFactor = 1.1;
    if (e.deltaY < 0) {
      shaderParams.current.zoom *= zoomFactor;
    } else {
      shaderParams.current.zoom /= zoomFactor;
    }
  };

  const zoomIn = (e) => {
    e.stopPropagation();
    shaderParams.current.zoom *= 1.5;
  };

  const zoomOut = (e) => {
    e.stopPropagation();
    shaderParams.current.zoom /= 1.5;
  };

  return (
    <div className="w-full h-full relative">
      <div 
        className="w-full h-full touch-none"
        onPointerDown={handlePointerDown}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
        onPointerMove={handlePointerMove}
        onWheel={handleWheel}
      >
        <Canvas 
          camera={{ position: [0, 0, 1], zoom: 1, near: 0.1, far: 1000 }} 
          orthographic
        >
          <ShaderPlane uniforms={uniforms} audioData={audioData} dynamicParams={shaderParams} />
        </Canvas>
      </div>

      {/* Floating Controls */}
      <div className="absolute top-6 right-6 flex gap-4 z-[100] pointer-events-auto">
        <button 
          onClick={zoomIn} 
          className="bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-full flex items-center justify-center font-bold tracking-widest uppercase text-xs shadow-[0_0_20px_rgba(255,255,255,0.4)] transition-all"
        >
          Zoom In (+)
        </button>
        <button 
          onClick={zoomOut} 
          className="bg-white text-black hover:bg-gray-200 px-6 py-3 rounded-full flex items-center justify-center font-bold tracking-widest uppercase text-xs shadow-[0_0_20px_rgba(255,255,255,0.4)] transition-all"
        >
          Zoom Out (-)
        </button>
      </div>
    </div>
  );
}
