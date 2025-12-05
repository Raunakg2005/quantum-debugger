import { motion } from "framer-motion";
import { useMemo } from "react";

interface BackgroundEffectsProps {
    digitalRain: Array<{ id: number; delay: number; left: string }>;
    particles: Array<{ left: string; top: string }>;
    isEntering: boolean;
}

export default function BackgroundEffects({ digitalRain, particles, isEntering }: BackgroundEffectsProps) {
    // Pre-calculate random offsets to avoid hydration mismatch
    const particleOffsets = useMemo(() =>
        particles.map(() => ({
            x: (Math.random() - 0.5) * 2500,
            y: (Math.random() - 0.5) * 2500,
        })),
        [particles]
    );

    return (
        <>
            {/* Digital Rain */}
            {digitalRain.map((drop) => (
                <motion.div
                    key={drop.id}
                    className="absolute top-0 w-px h-20"
                    style={{
                        left: drop.left,
                        background: 'linear-gradient(to bottom, transparent, rgba(0, 217, 255, 0.5), transparent)',
                    }}
                    animate={{
                        y: ['-100px', '100vh'],
                        opacity: [0, 1, 0],
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        delay: drop.delay,
                        ease: 'linear',
                    }}
                />
            ))}

            {/* Stars */}
            {particles.map((particle, i) => (
                <motion.div
                    key={i}
                    className="absolute w-1 h-1 bg-white rounded-full"
                    style={{ left: particle.left, top: particle.top }}
                    animate={isEntering ? {
                        scale: [1, 3, 0],
                        opacity: [1, 1, 0],
                        x: [0, particleOffsets[i].x],
                        y: [0, particleOffsets[i].y],
                    } : {
                        opacity: [0.3, 1, 0.3],
                        scale: [1, 1.5, 1],
                    }}
                    transition={{
                        duration: isEntering ? 1.5 : 3,
                        repeat: isEntering ? 0 : Infinity,
                    }}
                />
            ))}

            {/* Warp Tunnel */}
            {isEntering && (
                <div className="fixed inset-0 pointer-events-none">
                    {[...Array(50)].map((_, i) => (
                        <motion.div
                            key={i}
                            className="absolute border-2 rounded-full"
                            style={{
                                left: '50%',
                                top: '50%',
                                transform: 'translate(-50%, -50%)',
                                borderColor: i % 3 === 0 ? 'rgba(0, 217, 255, 0.3)' : i % 3 === 1 ? 'rgba(0, 255, 65, 0.3)' : 'rgba(255, 107, 53, 0.3)',
                            }}
                            initial={{ width: 0, height: 0, opacity: 1 }}
                            animate={{
                                width: '250%',
                                height: '250%',
                                opacity: 0,
                            }}
                            transition={{
                                duration: 2,
                                delay: i * 0.03,
                                ease: "easeOut",
                            }}
                        />
                    ))}
                </div>
            )}
        </>
    );
}
