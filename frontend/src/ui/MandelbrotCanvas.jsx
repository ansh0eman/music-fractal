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
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
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

const ShaderPlane = ({ uniforms, audioData }) => {
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
      
      // Update audio energy uniform
      if (audioData && audioData.current) {
        material.uniforms.u_audio_energy.value = audioData.current;
      }

      // We read the camera's position to allow MapControls to pan and zoom
      // MapControls changes camera.position.x/y and camera.zoom
      material.uniforms.u_zoom.value = uniforms.zoom * state.camera.zoom;
      material.uniforms.u_center.value.set(
        uniforms.center_x + state.camera.position.x,
        uniforms.center_y + state.camera.position.y
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
  return (
    <Canvas 
      camera={{ position: [0, 0, 1], zoom: 1, near: 0.1, far: 1000 }} 
      orthographic
    >
      <ShaderPlane uniforms={uniforms} audioData={audioData} />
      <MapControls enableRotate={false} zoomSpeed={2.0} panSpeed={1.0} />
    </Canvas>
  );
}
