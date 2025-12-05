"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Line, Text, Circle } from "@react-three/drei";
import { motion } from "framer-motion";
import { Minimize2, Maximize2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import * as THREE from "three";

interface BlochSphereProps {
    theta?: number;
    phi?: number;
}

// Animated state vector component with smooth transitions
function AnimatedStateVector({ theta, phi }: { theta: number; phi: number }) {
    const sphereRef = useRef<any>(null);
    const pulseRef = useRef<any>(null);
    const [currentPos, setCurrentPos] = useState({ x: 0, y: 0, z: 1 }); // Start at |0⟩
    const [isPulsing, setIsPulsing] = useState(false);
    const lastTheta = useRef(theta);
    const lastPhi = useRef(phi);
    const targetPos = useRef({ x: 0, y: 0, z: 1 });

    // Detect state changes for pulse animation
    useEffect(() => {
        if (Math.abs(theta - lastTheta.current) > 0.01 || Math.abs(phi - lastPhi.current) > 0.01) {
            setIsPulsing(true);
            setTimeout(() => setIsPulsing(false), 600);
            lastTheta.current = theta;
            lastPhi.current = phi;
        }
        
        // Update target position
        targetPos.current = {
            x: Math.sin(theta) * Math.cos(phi),
            y: Math.sin(theta) * Math.sin(phi),
            z: Math.cos(theta)
        };
    }, [theta, phi]);

    useFrame((state, delta) => {
        // Smooth lerp to target position
        setCurrentPos(prev => ({
            x: prev.x + (targetPos.current.x - prev.x) * delta * 8,
            y: prev.y + (targetPos.current.y - prev.y) * delta * 8,
            z: prev.z + (targetPos.current.z - prev.z) * delta * 8
        }));

        // Update state sphere position
        if (sphereRef.current) {
            sphereRef.current.position.set(currentPos.x, currentPos.y, currentPos.z);
        }

        // Pulse animation and position update
        if (pulseRef.current) {
            pulseRef.current.position.set(currentPos.x, currentPos.y, currentPos.z);
            
            if (isPulsing) {
                const pulseScale = 1 + Math.sin(state.clock.elapsedTime * 15) * 0.3;
                pulseRef.current.scale.setScalar(pulseScale);
                pulseRef.current.material.opacity = 0.4 + Math.sin(state.clock.elapsedTime * 15) * 0.2;
            } else {
                pulseRef.current.scale.setScalar(1);
                pulseRef.current.material.opacity = Math.max(0, pulseRef.current.material.opacity - delta * 2);
            }
        }
    });

    return (
        <group>
            <Line
                points={[[0, 0, 0], [currentPos.x, currentPos.y, currentPos.z]]}
                color="#FFD700"
                lineWidth={4}
            />
            <mesh ref={sphereRef} position={[currentPos.x, currentPos.y, currentPos.z]}>
                <sphereGeometry args={[0.08, 16, 16]} />
                <meshStandardMaterial color="#FFD700" emissive="#FFD700" emissiveIntensity={0.8} />
            </mesh>
            {/* Pulse effect */}
            <mesh
                ref={pulseRef}
                position={[currentPos.x, currentPos.y, currentPos.z]}
            >
                <sphereGeometry args={[0.12, 16, 16]} />
                <meshStandardMaterial
                    color="#FFD700"
                    transparent
                    opacity={0}
                    emissive="#FFD700"
                    emissiveIntensity={1}
                />
            </mesh>
        </group>
    );
}

export default function BlochSphere({ theta = Math.PI / 2, phi = 0 }: BlochSphereProps) {
    const [isMinimized, setIsMinimized] = useState(false);

    // Calculate Cartesian coordinates for state labels
    const x = Math.sin(theta) * Math.cos(phi);
    const y = Math.sin(theta) * Math.sin(phi);
    const z = Math.cos(theta);

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={`glass-card border border-qcyan-500/30 ${isMinimized ? 'h-16' : 'h-full'} flex flex-col overflow-hidden`}
        >
            <div className="flex items-center justify-between p-4 border-b border-qcyan-500/20">
                <div>
                    <h3 className="text-lg font-bold text-qcyan-500">Bloch Sphere</h3>
                    <p className="text-xs text-gray-400">Qubit State Visualization</p>
                </div>
                <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    className="p-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                >
                    {isMinimized ? (
                        <Maximize2 className="w-4 h-4 text-qcyan-500" />
                    ) : (
                        <Minimize2 className="w-4 h-4 text-qcyan-500" />
                    )}
                </button>
            </div>

            {!isMinimized && (
                <div className="flex-1 relative bg-gradient-to-br from-black/50 to-black/30">
                    <Canvas camera={{ position: [2.5, 2.5, 2.5], fov: 50 }} className="bg-transparent">
                        <ambientLight intensity={0.6} />
                        <pointLight position={[10, 10, 10]} intensity={0.8} />

                        <mesh>
                            <sphereGeometry args={[1, 64, 64]} />
                            <meshBasicMaterial color="#00D9FF" wireframe transparent opacity={0.15} />
                        </mesh>

                        <Circle args={[1, 64]} rotation={[Math.PI / 2, 0, 0]}>
                            <meshBasicMaterial color="#00D9FF" side={THREE.DoubleSide} transparent opacity={0.2} />
                        </Circle>

                        <Line
                            points={Array.from({ length: 65 }, (_, i) => {
                                const angle = (i / 64) * Math.PI * 2;
                                return [Math.cos(angle), Math.sin(angle), 0];
                            })}
                            color="#00D9FF"
                            lineWidth={2}
                        />

                        <Line points={[[-1.4, 0, 0], [1.4, 0, 0]]} color="#888888" lineWidth={1.5} />
                        <Text position={[1.6, 0, 0]} fontSize={0.15} color="#CCCCCC">x</Text>

                        <Line points={[[0, -1.4, 0], [0, 1.4, 0]]} color="#888888" lineWidth={1.5} />
                        <Text position={[0, 1.6, 0]} fontSize={0.15} color="#CCCCCC">y</Text>

                        <Line points={[[0, 0, -1.4], [0, 0, 1.4]]} color="#00D9FF" lineWidth={2.5} />
                        <Text position={[0, 0, 1.7]} fontSize={0.2} color="#00D9FF">z</Text>

                        <AnimatedStateVector theta={theta} phi={phi} />

                        {/* Z-basis (Computational basis) */}
                        <Text position={[0, 0, 1.3]} fontSize={0.18} color="#FFFFFF">|0⟩</Text>
                        <Text position={[0, 0, -1.3]} fontSize={0.18} color="#FFFFFF">|1⟩</Text>

                        {/* X-basis (Hadamard basis) - Green */}
                        <Text position={[1.3, 0, 0]} fontSize={0.16} color="#00FFA3">|+⟩</Text>
                        <Text position={[-1.3, 0, 0]} fontSize={0.16} color="#00FFA3">|-⟩</Text>

                        {/* Y-basis - Orange */}
                        <Text position={[0, 1.3, 0]} fontSize={0.16} color="#FF9500">|i⟩</Text>
                        <Text position={[0, -1.3, 0]} fontSize={0.16} color="#FF9500">|-i⟩</Text>

                        <OrbitControls enableZoom={true} enablePan={false} minDistance={2} maxDistance={5} />
                    </Canvas>

                    <div className="absolute bottom-4 left-4 glass-card border border-qcyan-500/30 p-3">
                        <div className="text-xs space-y-1.5">
                            <div className="flex items-center gap-2">
                                <span className="text-gray-400">θ:</span>
                                <span className="text-qcyan-500 font-mono font-bold">
                                    {(theta * (180 / Math.PI)).toFixed(1)}°
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                <span className="text-gray-400">φ:</span>
                                <span className="text-qgreen-500 font-mono font-bold">
                                    {(phi * (180 / Math.PI)).toFixed(1)}°
                                </span>
                            </div>
                            <div className="mt-2 pt-2 border-t border-qcyan-500/20">
                                <span className="text-gray-400">State:</span>
                                <span className="text-yellow-400 font-mono ml-2 font-bold">
                                    {z > 0.99 ? "|0⟩" :
                                        z < -0.99 ? "|1⟩" :
                                            x > 0.99 ? "|+⟩" :
                                                x < -0.99 ? "|-⟩" :
                                                    y > 0.99 ? "|i⟩" :
                                                        y < -0.99 ? "|-i⟩" : "|ψ⟩"}
                                </span>
                            </div>
                            <div className="text-xs text-gray-500 mt-2">
                                Drag • Zoom • Rotate
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </motion.div>
    );
}
