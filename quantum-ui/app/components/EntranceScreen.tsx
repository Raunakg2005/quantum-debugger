"use client";

import { motion } from "framer-motion";
import { useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Zap } from "lucide-react";
import BackgroundEffects from "./entrance/BackgroundEffects";
import HoldButton from "./entrance/HoldButton";
import EnteringAnimation from "./entrance/EnteringAnimation";

interface EntranceScreenProps {
    particles: Array<{ left: string; top: string }>;
}

export default function EntranceScreen({ particles }: EntranceScreenProps) {
    const router = useRouter();
    const [holdProgress, setHoldProgress] = useState(0);
    const [isEntering, setIsEntering] = useState(false);
    const [digitalRain, setDigitalRain] = useState<Array<{ id: number; delay: number; left: string }>>([]);
    const holdIntervalRef = useRef<NodeJS.Timeout | null>(null);

    useEffect(() => {
        setDigitalRain(
            Array.from({ length: 25 }, (_, i) => ({
                id: i,
                delay: Math.random() * 5,
                left: `${Math.random() * 100}%`,
            }))
        );
    }, []);

    const handleMouseDown = () => {
        setHoldProgress(0);
        holdIntervalRef.current = setInterval(() => {
            setHoldProgress((prev) => {
                const newProgress = prev + 1;
                if (newProgress >= 100) {
                    if (holdIntervalRef.current) clearInterval(holdIntervalRef.current);
                    setIsEntering(true);
                    setTimeout(() => {
                        router.push("/dashboard");
                    }, 2000);
                    return 100;
                }
                return newProgress;
            });
        }, 60);
    };

    const handleMouseUp = () => {
        if (holdIntervalRef.current) {
            clearInterval(holdIntervalRef.current);
            holdIntervalRef.current = null;
        }
        if (holdProgress < 100) {
            setHoldProgress(0);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center relative overflow-hidden bg-black">
            {/* Background Effects */}
            <BackgroundEffects
                digitalRain={digitalRain}
                particles={particles}
                isEntering={isEntering}
            />

            {/* Main Content */}
            <motion.div
                className="text-center z-10 px-4"
                animate={
                    isEntering
                        ? { scale: 0, opacity: 0 }
                        : holdProgress > 0 && holdProgress < 100
                            ? {
                                scale: 1,
                                opacity: 1,
                                x: [0, -3, 3, -3, 3, 0],
                                y: [0, -3, 3, -3, 3, 0],
                                rotate: [0, -2, 2, -2, 2, 0],
                            }
                            : { scale: 1, opacity: 1 }
                }
                transition={{
                    duration: isEntering ? 0.8 : 0.15,
                    repeat: holdProgress > 0 && holdProgress < 100 ? Infinity : 0,
                }}
            >
                {!isEntering ? (
                    <>
                        {/* Title */}
                        <div className="relative mb-3 md:mb-4">
                            <motion.h1
                                className="text-3xl sm:text-4xl md:text-5xl lg:text-7xl font-bold bg-gradient-to-r from-qcyan-500 to-qgreen-500 bg-clip-text text-transparent relative z-10"
                                animate={{
                                    textShadow: [
                                        '0 0 20px rgba(0, 217, 255, 0.5)',
                                        '0 0 40px rgba(0, 217, 255, 0.8)',
                                        '0 0 20px rgba(0, 217, 255, 0.5)',
                                    ],
                                }}
                                transition={{ duration: 2, repeat: Infinity }}
                            >
                                Welcome to Quantum World
                            </motion.h1>
                        </div>

                        {/* Subtitle */}
                        <motion.div
                            className="flex items-center justify-center gap-2 mb-8 md:mb-12 text-sm md:text-base lg:text-lg text-gray-400"
                            animate={{
                                opacity: [0.6, 1, 0.6],
                            }}
                            transition={{ duration: 2, repeat: Infinity }}
                        >
                            <Zap className="w-4 h-4 md:w-5 md:h-5 text-qcyan-500" />
                            <span>Hold to enter the quantum realm</span>
                            <Zap className="w-4 h-4 md:w-5 md:h-5 text-qcyan-500" />
                        </motion.div>

                        {/* Hold Button */}
                        <HoldButton
                            holdProgress={holdProgress}
                            onPointerDown={handleMouseDown}
                            onPointerUp={handleMouseUp}
                            onPointerLeave={handleMouseUp}
                        />
                    </>
                ) : (
                    <EnteringAnimation />
                )}
            </motion.div>
        </div>
    );
}
