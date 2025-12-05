"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Play, Pause, RotateCcw, ChevronRight, Zap, BarChart3, Keyboard, Info } from "lucide-react";
import { useState, useEffect, useMemo, useCallback } from "react";
import { simulateQuantumCircuit } from "../../utils/quantumSimulator";

interface Gate {
    id: string;
    type: string;
    name: string;
    qubit: number;
    step: number;
    bgGradient: string;
}

interface CircuitAnimationModalProps {
    isOpen: boolean;
    onClose: () => void;
    gates: Gate[];
    numQubits: number;
}

interface GateInfo {
    name: string;
    description: string;
    matrix: string;
    effect: string;
}

// Gate information database
const GATE_INFO: Record<string, GateInfo> = {
    'H': {
        name: 'Hadamard',
        description: 'Creates equal superposition of |0⟩ and |1⟩ states',
        matrix: '1/√2 [[1, 1], [1, -1]]',
        effect: '|0⟩ → (|0⟩ + |1⟩)/√2, |1⟩ → (|0⟩ - |1⟩)/√2'
    },
    'X': {
        name: 'Pauli-X (NOT)',
        description: 'Flips qubit state (quantum NOT gate)',
        matrix: '[[0, 1], [1, 0]]',
        effect: '|0⟩ → |1⟩, |1⟩ → |0⟩'
    },
    'Y': {
        name: 'Pauli-Y',
        description: 'Rotation around Y-axis of Bloch sphere',
        matrix: '[[0, -i], [i, 0]]',
        effect: '|0⟩ → i|1⟩, |1⟩ → -i|0⟩'
    },
    'Z': {
        name: 'Pauli-Z',
        description: 'Phase flip gate',
        matrix: '[[1, 0], [0, -1]]',
        effect: '|0⟩ → |0⟩, |1⟩ → -|1⟩'
    },
    'T': {
        name: 'T Gate',
        description: 'π/4 phase rotation',
        matrix: '[[1, 0], [0, e^(iπ/4)]]',
        effect: 'Adds π/4 phase to |1⟩'
    },
    'S': {
        name: 'S Gate',
        description: 'π/2 phase rotation',
        matrix: '[[1, 0], [0, i]]',
        effect: 'Adds π/2 phase to |1⟩'
    },
    'CNOT': {
        name: 'CNOT (Controlled-NOT)',
        description: 'Flips target qubit if control is |1⟩',
        matrix: '[[1,0,0,0], [0,1,0,0], [0,0,0,1], [0,0,1,0]]',
        effect: 'Creates entanglement between qubits'
    },
    'M': {
        name: 'Measurement',
        description: 'Collapses quantum state to classical bit',
        matrix: 'N/A (non-unitary)',
        effect: 'Measures in computational basis'
    }
};

export default function CircuitAnimationModal({
    isOpen,
    onClose,
    gates,
    numQubits
}: CircuitAnimationModalProps) {
    const [currentStep, setCurrentStep] = useState(0);
    const [isPlaying, setIsPlaying] = useState(false);
    const [speed, setSpeed] = useState(1000); // ms per step
    const [showShortcuts, setShowShortcuts] = useState(false);
    const [showGateInfo, setShowGateInfo] = useState(true);

    // Sort gates by step (memoized for performance)
    const sortedGates = useMemo(() =>
        [...gates].sort((a, b) => a.step - b.step),
        [gates]
    );

    const maxStep = useMemo(() =>
        Math.max(...gates.map(g => g.step), 0),
        [gates]
    );

    // Auto-advance animation
    useEffect(() => {
        if (!isPlaying || currentStep >= maxStep) return;

        const timer = setTimeout(() => {
            setCurrentStep(prev => Math.min(prev + 1, maxStep));
        }, speed);

        return () => clearTimeout(timer);
    }, [isPlaying, currentStep, maxStep, speed]);

    // Stop playing at the end
    useEffect(() => {
        if (currentStep >= maxStep) {
            setIsPlaying(false);
        }
    }, [currentStep, maxStep]);

    // Get gates up to current step
    const visibleGates = sortedGates.filter(g => g.step <= currentStep);

    // Simulate circuit up to current step
    const currentResults = visibleGates.length > 0
        ? simulateQuantumCircuit(visibleGates, numQubits, 1000)
        : { counts: {}, probabilities: {} };

    const totalShots = Object.values(currentResults.counts).reduce((a: number, b: number) => a + b, 0) || 0;
    const maxCount = Math.max(...Object.values(currentResults.counts).map(v => Number(v)), 1);

    // Event handlers (memoized with useCallback)
    const handlePlay = useCallback(() => {
        if (currentStep >= maxStep) {
            setCurrentStep(0);
        }
        setIsPlaying(!isPlaying);
    }, [currentStep, maxStep, isPlaying]);

    const handleReset = useCallback(() => {
        setCurrentStep(0);
        setIsPlaying(false);
    }, []);

    const handleNext = useCallback(() => {
        if (currentStep < maxStep) {
            setCurrentStep(prev => prev + 1);
        }
    }, [currentStep, maxStep]);

    const handlePrevious = useCallback(() => {
        if (currentStep > 0) {
            setCurrentStep(prev => prev - 1);
        }
    }, [currentStep]);

    // Keyboard shortcuts handler
    useEffect(() => {
        if (!isOpen) return;

        const handleKeyPress = (e: KeyboardEvent) => {
            switch (e.key) {
                case ' ': // Space - Play/Pause
                    e.preventDefault();
                    handlePlay();
                    break;
                case 'ArrowRight': // Next step
                    e.preventDefault();
                    handleNext();
                    break;
                case 'ArrowLeft': // Previous step
                    e.preventDefault();
                    handlePrevious();
                    break;
                case 'r':
                case 'R': // Reset
                    e.preventDefault();
                    handleReset();
                    break;
                case 'Escape': // Close modal
                    onClose();
                    break;
                case '?': // Toggle shortcuts help
                    setShowShortcuts(prev => !prev);
                    break;
            }
        };

        window.addEventListener('keydown', handleKeyPress);
        return () => window.removeEventListener('keydown', handleKeyPress);
    }, [isOpen, handlePlay, handleNext, handlePrevious, handleReset, onClose]);

    return (
        <AnimatePresence>
            {isOpen && (
                <>
                    {/* Backdrop */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
                    />

                    {/* Modal */}
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95, y: 20 }}
                            animate={{ opacity: 1, scale: 1, y: 0 }}
                            exit={{ opacity: 0, scale: 0.95, y: 20 }}
                            className="glass-card border border-qcyan-500/30 rounded-2xl max-w-7xl w-full max-h-[90vh] overflow-hidden flex flex-col"
                        >
                            {/* Header */}
                            <div className="p-6 border-b border-qcyan-500/20 bg-gradient-to-r from-qcyan-500/10 to-qgreen-500/10">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-qcyan-500 flex items-center gap-3">
                                            <Zap className="w-7 h-7" />
                                            Circuit Execution Animation
                                        </h2>
                                        <p className="text-sm text-gray-400 mt-1">
                                            Step-by-step quantum circuit simulation
                                        </p>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        {/* Keyboard Shortcuts Button */}
                                        <div className="relative">
                                            <button
                                                onClick={() => setShowShortcuts(!showShortcuts)}
                                                className={`p-2 rounded-lg transition-colors ${showShortcuts ? 'bg-qcyan-500/30' : 'bg-qcyan-500/10 hover:bg-qcyan-500/20'
                                                    }`}
                                                title="Keyboard Shortcuts (Press ?)"
                                            >
                                                <Keyboard className="w-5 h-5 text-qcyan-500" />
                                            </button>
                                            <AnimatePresence>
                                                {showShortcuts && (
                                                    <motion.div
                                                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                                        className="absolute top-full right-0 mt-2 p-4 rounded-lg bg-black/95 border border-qcyan-500/30 min-w-[280px] z-50 shadow-xl"
                                                    >
                                                        <h3 className="text-sm font-bold text-qcyan-500 mb-3">Keyboard Shortcuts</h3>
                                                        <div className="space-y-2 text-xs">
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Play/Pause</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">Space</kbd>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Next Step</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">→</kbd>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Previous Step</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">←</kbd>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Reset</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">R</kbd>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Close Modal</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">Esc</kbd>
                                                            </div>
                                                            <div className="flex justify-between items-center">
                                                                <span className="text-gray-400">Toggle This</span>
                                                                <kbd className="px-2 py-1 bg-qcyan-500/20 rounded text-qcyan-500 font-mono">?</kbd>
                                                            </div>
                                                        </div>
                                                    </motion.div>
                                                )}
                                            </AnimatePresence>
                                        </div>
                                        <button
                                            onClick={onClose}
                                            className="p-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                                        >
                                            <X className="w-5 h-5 text-qcyan-500" />
                                        </button>
                                    </div>
                                </div>
                            </div>

                            {/* Main Content - Split View */}
                            <div className="flex-1 flex gap-4 p-4 overflow-hidden">
                                {/* Circuit Visualization - Left Side */}
                                <div className="flex-1 overflow-auto custom-scrollbar p-4 bg-black/20 rounded-xl border border-qcyan-500/20">
                                    <div className="inline-block min-w-full">
                                        <div className="flex gap-6">
                                            {/* Qubit Labels */}
                                            <div className="flex flex-col justify-around py-2">
                                                {Array.from({ length: numQubits }).map((_, qubitIndex) => (
                                                    <div key={`label-${qubitIndex}`} className="h-20 flex items-center">
                                                        <div className="px-4 py-2 rounded-lg bg-gradient-to-r from-qcyan-500 to-qgreen-500 text-black font-bold">
                                                            q{qubitIndex}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>

                                            {/* Circuit Grid */}
                                            <div className="flex-1">
                                                <div className="grid gap-0" style={{ gridTemplateColumns: `repeat(${maxStep + 1}, 120px)` }}>
                                                    {Array.from({ length: numQubits }).map((_, qubitIndex) =>
                                                        Array.from({ length: maxStep + 1 }).map((_, stepIndex) => {
                                                            const gate = sortedGates.find(
                                                                g => g.qubit === qubitIndex && g.step === stepIndex
                                                            );
                                                            const isVisible = stepIndex <= currentStep;
                                                            const isCurrent = stepIndex === currentStep;

                                                            return (
                                                                <div
                                                                    key={`cell-${qubitIndex}-${stepIndex}`}
                                                                    className={`
                                                                    relative h-20 border flex items-center justify-center
                                                                    ${isCurrent ? 'border-qgreen-500 bg-qgreen-500/10' : 'border-qcyan-500/20'}
                                                                `}
                                                                >
                                                                    {/* Qubit Wire */}
                                                                    <div className={`
                                                                    absolute left-0 right-0 h-1 pointer-events-none transition-all
                                                                    ${isVisible ? 'bg-qcyan-500' : 'bg-qcyan-500/30'}
                                                                `} />

                                                                    {/* Gate */}
                                                                    {gate && (
                                                                        <motion.div
                                                                            initial={{ scale: 0, rotate: -180, opacity: 0 }}
                                                                            animate={isVisible ? {
                                                                                scale: 1,
                                                                                rotate: 0,
                                                                                opacity: 1
                                                                            } : {
                                                                                scale: 0,
                                                                                rotate: -180,
                                                                                opacity: 0
                                                                            }}
                                                                            transition={{ duration: 0.5, type: "spring" }}
                                                                            className="relative z-10"
                                                                        >
                                                                            <div className={`
                                                                            w-16 h-16 rounded-xl ${gate.bgGradient} 
                                                                            flex items-center justify-center text-white 
                                                                            font-bold text-2xl shadow-lg border-2 border-white/20
                                                                            transition-all duration-300
                                                                            ${isCurrent && gate ? 'ring-4 ring-qgreen-500 shadow-[0_0_30px_rgba(0,255,163,0.6)] scale-110 border-qgreen-500' : ''}
                                                                        `}>
                                                                                {gate.name}
                                                                            </div>
                                                                            {isCurrent && gate && (
                                                                                <motion.div
                                                                                    className="absolute inset-0 rounded-xl bg-qgreen-500/20 pointer-events-none"
                                                                                    animate={{ opacity: [0.5, 0, 0.5] }}
                                                                                    transition={{ duration: 1.5, repeat: Infinity }}
                                                                                />
                                                                            )}
                                                                        </motion.div>
                                                                    )}
                                                                </div>
                                                            );
                                                        })
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Results Panel - Right Side */}
                                <div className="w-80 flex flex-col overflow-auto custom-scrollbar">
                                    <div className="flex flex-col gap-4 p-4">
                                        {/* Results Header */}
                                        <div className="glass-card border border-qcyan-500/30 p-3 bg-black/30">
                                            <div className="flex items-center gap-2 mb-2">
                                                <BarChart3 className="w-5 h-5 text-qcyan-500" />
                                                <h3 className="text-lg font-bold text-qcyan-500">Live Results</h3>
                                            </div>
                                            <p className="text-xs text-gray-400">
                                                After step {currentStep} of {maxStep}
                                            </p>
                                        </div>

                                        {/* Measurement Results */}
                                        {totalShots === 0 ? (
                                            <div className="flex-1 flex items-center justify-center glass-card border border-dashed border-qcyan-500/30 rounded-lg bg-black/20 p-6">
                                                <div className="text-center">
                                                    <BarChart3 className="w-12 h-12 mx-auto mb-3 text-qcyan-500/30" />
                                                    <p className="text-sm text-gray-500">Add gates to see results</p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="space-y-2">
                                                {Object.entries(currentResults.counts)
                                                    .sort(([a], [b]) => a.localeCompare(b))
                                                    .map(([state, count]) => {
                                                        const countNum = Number(count);
                                                        const probability = (countNum / totalShots) * 100;
                                                        const barWidth = (countNum / maxCount) * 100;

                                                        return (
                                                            <motion.div
                                                                key={state}
                                                                initial={{ opacity: 0, x: -20 }}
                                                                animate={{ opacity: 1, x: 0 }}
                                                                className="glass-card border border-qcyan-500/20 p-3 bg-black/30"
                                                            >
                                                                {/* State label */}
                                                                <div className="flex items-center justify-between mb-2">
                                                                    <span className="text-sm font-mono text-qcyan-500 font-bold">|{state}⟩</span>
                                                                    <span className="text-xs font-semibold text-qgreen-500">{probability.toFixed(1)}%</span>
                                                                </div>

                                                                {/* Bar */}
                                                                <div className="relative h-6 bg-black/50 rounded overflow-hidden border border-qcyan-500/20">
                                                                    <motion.div
                                                                        initial={{ width: 0 }}
                                                                        animate={{ width: `${barWidth}%` }}
                                                                        transition={{ duration: 0.5, ease: "easeOut" }}
                                                                        className="h-full bg-gradient-to-r from-qcyan-500 to-qgreen-500"
                                                                    >
                                                                        <motion.div
                                                                            className="absolute inset-0 bg-white/20"
                                                                            animate={{ opacity: [0.2, 0.4, 0.2] }}
                                                                            transition={{ duration: 2, repeat: Infinity }}
                                                                        />
                                                                    </motion.div>

                                                                    {/* Count label */}
                                                                    <div className="absolute inset-0 flex items-center justify-center">
                                                                        <span className="text-xs font-bold text-white drop-shadow-lg">
                                                                            {countNum}
                                                                        </span>
                                                                    </div>
                                                                </div>
                                                            </motion.div>
                                                        );
                                                    })}
                                            </div>
                                        )}

                                        {/* Stats */}
                                        {totalShots > 0 && (
                                            <div className="glass-card border border-qcyan-500/30 p-4 bg-black/30">
                                                <div className="space-y-2 text-sm">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">Total Shots</span>
                                                        <span className="font-bold text-qcyan-500">{totalShots}</span>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">States</span>
                                                        <span className="font-bold text-qgreen-500">
                                                            {Object.keys(currentResults.counts).length}
                                                        </span>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-gray-400">Gates Applied</span>
                                                        <span className="font-bold text-qorange-500">{visibleGates.length}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="p-6 border-t border-qcyan-500/20 bg-black/20">
                                <div className="flex items-center justify-between gap-4">
                                    {/* Progress */}
                                    <div className="flex-1">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="text-sm text-gray-400">
                                                Step {currentStep} of {maxStep}
                                            </span>
                                            <span className="text-sm font-bold text-qcyan-500">
                                                {maxStep > 0 ? Math.round((currentStep / maxStep) * 100) : 0}%
                                            </span>
                                        </div>
                                        <div className="h-2 bg-black/50 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: maxStep > 0 ? `${(currentStep / maxStep) * 100}%` : '0%' }}
                                                transition={{ duration: 0.3 }}
                                                className="h-full bg-gradient-to-r from-qcyan-500 to-qgreen-500"
                                            />
                                        </div>
                                    </div>

                                    {/* Playback Controls */}
                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={handleReset}
                                            className="p-3 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                                            disabled={currentStep === 0}
                                        >
                                            <RotateCcw className="w-5 h-5 text-qcyan-500" />
                                        </button>

                                        <button
                                            onClick={handlePrevious}
                                            className="p-3 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                                            disabled={currentStep === 0}
                                        >
                                            <ChevronRight className="w-5 h-5 text-qcyan-500 rotate-180" />
                                        </button>

                                        <button
                                            onClick={handlePlay}
                                            className="p-4 rounded-lg bg-gradient-to-r from-qcyan-500 to-qgreen-500 hover:from-qcyan-600 hover:to-qgreen-600 transition-all"
                                        >
                                            {isPlaying ? (
                                                <Pause className="w-6 h-6 text-black" />
                                            ) : (
                                                <Play className="w-6 h-6 text-black ml-0.5" />
                                            )}
                                        </button>

                                        <button
                                            onClick={handleNext}
                                            className="p-3 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                                            disabled={currentStep >= maxStep}
                                        >
                                            <ChevronRight className="w-5 h-5 text-qcyan-500" />
                                        </button>

                                        {/* Speed Control */}
                                        <div className="ml-4 flex items-center gap-2">
                                            <span className="text-xs text-gray-400">Speed:</span>
                                            <select
                                                value={speed}
                                                onChange={(e) => setSpeed(Number(e.target.value))}
                                                className="px-3 py-2 rounded-lg bg-qcyan-500/10 border border-qcyan-500/30 text-qcyan-500 text-sm"
                                            >
                                                <option value={2000}>0.5x</option>
                                                <option value={1000}>1x</option>
                                                <option value={500}>2x</option>
                                                <option value={250}>4x</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                {/* Current Gate Info - Enhanced */}
                                {currentStep <= maxStep && sortedGates.filter(g => g.step === currentStep).length > 0 && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10 }}
                                        animate={{ opacity: 1, y: 0 }}
                                        className="mt-4 p-4 rounded-lg bg-qgreen-500/10 border border-qgreen-500/30"
                                    >
                                        <div className="flex items-center justify-between mb-2">
                                            <h4 className="text-sm font-bold text-qgreen-500 flex items-center gap-2">
                                                <Zap className="w-4 h-4" />
                                                Current Operation
                                            </h4>
                                            <button
                                                onClick={() => setShowGateInfo(!showGateInfo)}
                                                className="p-1.5 rounded bg-qgreen-500/10 hover:bg-qgreen-500/20 transition-colors"
                                                title="Toggle gate details"
                                            >
                                                <Info className="w-4 h-4 text-qgreen-500" />
                                            </button>
                                        </div>

                                        <div className="space-y-3">
                                            {sortedGates.filter(g => g.step === currentStep).map((gate, idx) => {
                                                const gateInfo = GATE_INFO[gate.name];
                                                return (
                                                    <div key={idx} className="space-y-2">
                                                        <p className="text-sm text-gray-300">
                                                            <span className="font-bold text-white">{gate.name}</span> gate applied to{' '}
                                                            <span className="font-bold text-qcyan-500">qubit {gate.qubit}</span>
                                                        </p>

                                                        {showGateInfo && gateInfo && (
                                                            <motion.div
                                                                initial={{ opacity: 0, height: 0 }}
                                                                animate={{ opacity: 1, height: 'auto' }}
                                                                exit={{ opacity: 0, height: 0 }}
                                                                className="pl-4 border-l-2 border-qgreen-500/30 space-y-2"
                                                            >
                                                                <div>
                                                                    <p className="text-xs font-semibold text-qgreen-500 mb-1">Description:</p>
                                                                    <p className="text-xs text-gray-400">{gateInfo.description}</p>
                                                                </div>
                                                                <div>
                                                                    <p className="text-xs font-semibold text-qgreen-500 mb-1">Matrix:</p>
                                                                    <code className="text-xs text-qcyan-500 bg-black/40 px-2 py-1 rounded block font-mono">
                                                                        {gateInfo.matrix}
                                                                    </code>
                                                                </div>
                                                                <div>
                                                                    <p className="text-xs font-semibold text-qgreen-500 mb-1">Effect:</p>
                                                                    <p className="text-xs text-gray-400 font-mono">{gateInfo.effect}</p>
                                                                </div>
                                                            </motion.div>
                                                        )}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </motion.div>
                                )}
                            </div>

                            {/* Custom Scrollbar */}
                            <style jsx>{`
                                .custom-scrollbar::-webkit-scrollbar {
                                    width: 8px;
                                    height: 8px;
                                }
                                .custom-scrollbar::-webkit-scrollbar-track {
                                    background: rgba(0, 0, 0, 0.3);
                                    border-radius: 4px;
                                }
                                .custom-scrollbar::-webkit-scrollbar-thumb {
                                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.4), rgba(0, 255, 163, 0.4));
                                    border-radius: 4px;
                                }
                                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                                    background: linear-gradient(135deg, rgba(0, 217, 255, 0.7), rgba(0, 255, 163, 0.7));
                                }
                            `}</style>
                        </motion.div>
                    </div>
                </>
            )}
        </AnimatePresence>
    );
}
