"use client";

import { motion } from "framer-motion";

interface QuantumSpinnerProps {
    size?: 'sm' | 'md' | 'lg';
    variant?: 'orbital' | 'pulse' | 'wave';
    text?: string;
}

export default function QuantumSpinner({
    size = 'md',
    variant = 'orbital',
    text
}: QuantumSpinnerProps) {
    const sizes = {
        sm: { container: 'w-12 h-12', particle: 'w-2 h-2', text: 'text-xs' },
        md: { container: 'w-16 h-16', particle: 'w-3 h-3', text: 'text-sm' },
        lg: { container: 'w-24 h-24', particle: 'w-4 h-4', text: 'text-base' }
    };

    const currentSize = sizes[size];

    if (variant === 'orbital') {
        return (
            <div className="flex flex-col items-center justify-center gap-4">
                <div className={`${currentSize.container} relative`}>
                    {/* Center core */}
                    <motion.div
                        className="absolute inset-0 m-auto w-3 h-3 rounded-full bg-gradient-to-r from-qcyan-500 to-qgreen-500"
                        animate={{
                            scale: [1, 1.2, 1],
                            opacity: [0.8, 1, 0.8]
                        }}
                        transition={{
                            duration: 2,
                            repeat: Infinity,
                            ease: "easeInOut"
                        }}
                    />

                    {/* Orbiting particles */}
                    {[0, 120, 240].map((angle, i) => (
                        <motion.div
                            key={i}
                            className={`absolute inset-0 ${currentSize.particle} rounded-full bg-qcyan-500`}
                            style={{
                                boxShadow: '0 0 10px rgba(6, 182, 212, 0.8)'
                            }}
                            animate={{
                                rotate: 360,
                            }}
                            transition={{
                                duration: 2,
                                repeat: Infinity,
                                ease: "linear",
                                delay: i * 0.2
                            }}
                        >
                            <div
                                className={`${currentSize.particle} rounded-full bg-qcyan-500 absolute`}
                                style={{
                                    top: '50%',
                                    left: '100%',
                                    transform: 'translate(-50%, -50%)'
                                }}
                            />
                        </motion.div>
                    ))}
                </div>
                {text && (
                    <motion.p
                        className={`${currentSize.text} text-qcyan-500 font-medium`}
                        animate={{ opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 2, repeat: Infinity }}
                    >
                        {text}
                    </motion.p>
                )}
            </div>
        );
    }

    if (variant === 'pulse') {
        return (
            <div className="flex flex-col items-center justify-center gap-4">
                <motion.div
                    className={`${currentSize.container} rounded-full bg-gradient-to-r from-qcyan-500 to-qgreen-500`}
                    style={{
                        boxShadow: '0 0 30px rgba(6, 182, 212, 0.6)'
                    }}
                    animate={{
                        scale: [1, 1.2, 1],
                        opacity: [0.6, 1, 0.6],
                        boxShadow: [
                            '0 0 20px rgba(6, 182, 212, 0.4)',
                            '0 0 40px rgba(6, 182, 212, 0.8)',
                            '0 0 20px rgba(6, 182, 212, 0.4)'
                        ]
                    }}
                    transition={{
                        duration: 1.5,
                        repeat: Infinity,
                        ease: "easeInOut"
                    }}
                />
                {text && (
                    <p className={`${currentSize.text} text-qcyan-500 font-medium`}>
                        {text}
                    </p>
                )}
            </div>
        );
    }

    // Wave variant
    return (
        <div className="flex flex-col items-center justify-center gap-4">
            <div className={`${currentSize.container} flex items-center justify-center gap-1`}>
                {[0, 1, 2, 3, 4].map((i) => (
                    <motion.div
                        key={i}
                        className="w-2 h-8 rounded-full bg-gradient-to-t from-qcyan-500 to-qgreen-500"
                        animate={{
                            scaleY: [1, 2, 1],
                            opacity: [0.5, 1, 0.5]
                        }}
                        transition={{
                            duration: 1,
                            repeat: Infinity,
                            delay: i * 0.1,
                            ease: "easeInOut"
                        }}
                    />
                ))}
            </div>
            {text && (
                <p className={`${currentSize.text} text-qcyan-500 font-medium`}>
                    {text}
                </p>
            )}
        </div>
    );
}
