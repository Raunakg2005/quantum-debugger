"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, ArrowRight, ArrowLeft, Check } from "lucide-react";

interface TourStep {
    title: string;
    description: string;
    target?: string;
    position?: 'top' | 'bottom' | 'left' | 'right';
}

const tourSteps: TourStep[] = [
    {
        title: "Welcome to QuantumDebugger! 🚀",
        description: "Let's take a quick tour to help you get started with building quantum circuits.",
        position: 'bottom'
    },
    {
        title: "Gate Toolbox",
        description: "Drag quantum gates from here to build your circuit. We have H, X, Y, Z, CNOT, and more!",
        target: ".gate-toolbox",
        position: 'right'
    },
    {
        title: "Circuit Canvas",
        description: "Drop gates here to build your quantum circuit. Each row represents a qubit.",
        target: ".circuit-canvas",
        position: 'left'
    },
    {
        title: "Bloch Sphere",
        description: "Watch the quantum state evolve in real-time on this 3D Bloch sphere visualization.",
        target: ".bloch-sphere",
        position: 'left'
    },
    {
        title: "Results Panel",
        description: "View measurement outcomes and circuit statistics here. Results update automatically!",
        target: ".results-panel",
        position: 'left'
    },
    {
        title: "Save & Load",
        description: "Save your circuits to work on later, or load pre-built templates to get started quickly.",
        position: 'bottom'
    },
    {
        title: "Ready to Go!",
        description: "You're all set! Start building quantum circuits and exploring quantum computing. Have fun! ✨",
        position: 'bottom'
    }
];

interface TourProps {
    onComplete: () => void;
}

export default function Tour({ onComplete }: TourProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [isVisible, setIsVisible] = useState(true);

    const handleNext = () => {
        if (currentStep < tourSteps.length - 1) {
            setCurrentStep(prev => prev + 1);
        } else {
            handleComplete();
        }
    };

    const handlePrev = () => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    };

    const handleComplete = () => {
        setIsVisible(false);
        setTimeout(() => {
            onComplete();
            localStorage.setItem('quantumDebuggerTourCompleted', 'true');
        }, 300);
    };

    const handleSkip = () => {
        handleComplete();
    };

    const step = tourSteps[currentStep];
    const progress = ((currentStep + 1) / tourSteps.length) * 100;

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 bg-black/70 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
                    onClick={handleSkip}
                >
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.9 }}
                        className="w-full max-w-lg"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="glass-card border-2 border-qcyan-500/50 p-6 rounded-2xl shadow-2xl backdrop-blur-xl bg-black/90">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex-1">
                                    <h2 className="text-xl font-bold text-qcyan-500 mb-1">
                                        {step.title}
                                    </h2>
                                    <p className="text-sm text-gray-400">
                                        Step {currentStep + 1} of {tourSteps.length}
                                    </p>
                                </div>
                                <button
                                    onClick={handleSkip}
                                    className="p-1 rounded-lg hover:bg-white/10 transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-400" />
                                </button>
                            </div>

                            <div className="mb-4 h-1 bg-black/50 rounded-full overflow-hidden">
                                <motion.div
                                    className="h-full bg-gradient-to-r from-qcyan-500 to-qgreen-500"
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    transition={{ duration: 0.3 }}
                                />
                            </div>

                            <p className="text-gray-300 mb-6 leading-relaxed">
                                {step.description}
                            </p>

                            <div className="flex items-center justify-between">
                                <button
                                    onClick={handlePrev}
                                    disabled={currentStep === 0}
                                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${currentStep === 0
                                            ? 'text-gray-600 cursor-not-allowed'
                                            : 'text-gray-400 hover:bg-white/10'
                                        }`}
                                >
                                    <ArrowLeft className="w-4 h-4" />
                                    Previous
                                </button>

                                <button
                                    onClick={handleSkip}
                                    className="text-sm text-gray-500 hover:text-gray-400 transition-colors"
                                >
                                    Skip Tour
                                </button>

                                <button
                                    onClick={handleNext}
                                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-r from-qcyan-500 to-qgreen-500 text-black font-medium hover:shadow-neon-cyan transition-all"
                                >
                                    {currentStep === tourSteps.length - 1 ? (
                                        <>
                                            Finish
                                            <Check className="w-4 h-4" />
                                        </>
                                    ) : (
                                        <>
                                            Next
                                            <ArrowRight className="w-4 h-4" />
                                        </>
                                    )}
                                </button>
                            </div>
                        </div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}

export function useTour() {
    const [showTour, setShowTour] = useState(false);

    useEffect(() => {
        const tourCompleted = localStorage.getItem('quantumDebuggerTourCompleted');
        if (!tourCompleted) {
            setTimeout(() => setShowTour(true), 1000);
        }
    }, []);

    return { showTour, setShowTour };
}
