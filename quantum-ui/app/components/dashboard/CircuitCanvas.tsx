"use client";

import { motion } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { X } from "lucide-react";

interface Gate {
    id: string;
    type: string;
    name: string;
    qubit: number;
    step: number;
    bgGradient: string;
}

interface CircuitCanvasProps {
    qubits?: number;
    steps?: number;
    onGatesChange?: (gates: Gate[]) => void;
    initialGates?: Gate[];
}

export default function CircuitCanvas({ qubits = 3, steps = 8, onGatesChange, initialGates = [] }: CircuitCanvasProps) {
    const [hoveredCell, setHoveredCell] = useState<{ qubit: number; step: number } | null>(null);
    const [placedGates, setPlacedGates] = useState<Gate[]>(initialGates);
    const isLoadingRef = useRef(false);

    // Load initial gates when prop changes
    useEffect(() => {
        const currentGatesStr = JSON.stringify(placedGates);
        const initialGatesStr = JSON.stringify(initialGates);

        if (currentGatesStr !== initialGatesStr && !isLoadingRef.current) {
            isLoadingRef.current = true;
            setPlacedGates(initialGates);
            setTimeout(() => {
                isLoadingRef.current = false;
            }, 100);
        }
    }, [initialGates]); // Only initialGates, NOT placedGates

    // Notify parent when gates change
    useEffect(() => {
        if (onGatesChange && !isLoadingRef.current) {
            onGatesChange(placedGates);
        }
    }, [placedGates, onGatesChange]);

    const handleDragOver = (e: React.DragEvent, qubit: number, step: number) => {
        e.preventDefault();
        setHoveredCell({ qubit, step });
    };

    const handleDrop = (e: React.DragEvent, qubit: number, step: number) => {
        e.preventDefault();
        const gateData = e.dataTransfer.getData("gate");
        if (!gateData) return;

        const gate = JSON.parse(gateData);

        const existingGateIndex = placedGates.findIndex(
            g => g.qubit === qubit && g.step === step
        );

        const newGate: Gate = {
            id: `${gate.id}-${Date.now()}`,
            type: gate.id,
            name: gate.name,
            qubit,
            step,
            bgGradient: gate.bgGradient,
        };

        if (existingGateIndex >= 0) {
            const newGates = [...placedGates];
            newGates[existingGateIndex] = newGate;
            setPlacedGates(newGates);
        } else {
            setPlacedGates([...placedGates, newGate]);
        }

        setHoveredCell(null);
    };

    const removeGate = (gateId: string) => {
        setPlacedGates(placedGates.filter(g => g.id !== gateId));
    };

    const clearCircuit = () => {
        setPlacedGates([]);
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-card border border-qcyan-500/30 p-6 h-full flex flex-col"
        >
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h3 className="text-lg font-bold text-qcyan-500">Quantum Circuit</h3>
                    <p className="text-xs text-gray-400">Drag gates from the toolbox to build your circuit</p>
                </div>
                <div className="flex items-center gap-2">
                    <span className="px-2 py-1 rounded bg-qcyan-500/10 border border-qcyan-500/30 text-xs text-gray-400">
                        {qubits} Qubits
                    </span>
                    <span className="px-2 py-1 rounded bg-qgreen-500/10 border border-qgreen-500/30 text-xs text-gray-400">
                        {steps} Steps
                    </span>
                    {placedGates.length > 0 && (
                        <button
                            onClick={clearCircuit}
                            className="px-2 py-1 rounded bg-qorange-500/10 border border-qorange-500/30 text-xs text-qorange-500 hover:bg-qorange-500/20 transition-colors"
                        >
                            Clear All
                        </button>
                    )}
                </div>
            </div>

            {/* Circuit Grid */}
            <div className="flex-1 overflow-auto custom-scrollbar">
                <div className="inline-block min-w-full">
                    <div className="flex gap-4">
                        {/* Qubit Labels */}
                        <div className="flex flex-col justify-around">
                            {Array.from({ length: qubits }).map((_, qubitIndex) => (
                                <div key={`label-${qubitIndex}`} className="h-16 flex items-center justify-center">
                                    <div className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-qcyan-500 to-qgreen-500 text-black font-bold text-sm">
                                        q{qubitIndex}
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Grid with wires */}
                        <div className="flex-1">
                            <div className="grid gap-0" style={{ gridTemplateColumns: `repeat(${steps}, 1fr)` }}>
                                {Array.from({ length: qubits }).map((_, qubitIndex) =>
                                    Array.from({ length: steps }).map((_, stepIndex) => {
                                        const isHovered = hoveredCell?.qubit === qubitIndex && hoveredCell?.step === stepIndex;
                                        const placedGate = placedGates.find(g => g.qubit === qubitIndex && g.step === stepIndex);

                                        return (
                                            <motion.div
                                                key={`cell-${qubitIndex}-${stepIndex}`}
                                                className="relative h-16 border border-qcyan-500/10 flex items-center justify-center"
                                                onDragOver={(e) => handleDragOver(e, qubitIndex, stepIndex)}
                                                onDrop={(e) => handleDrop(e, qubitIndex, stepIndex)}
                                                onDragLeave={() => setHoveredCell(null)}
                                                whileHover={{ backgroundColor: placedGate ? undefined : "rgba(0, 217, 255, 0.05)" }}
                                            >
                                                {/* Qubit Wire */}
                                                <div className="absolute left-0 right-0 h-0.5 bg-qcyan-500/50 pointer-events-none" />

                                                {/* Drop Zone */}
                                                {isHovered && !placedGate && (
                                                    <motion.div
                                                        initial={{ scale: 0, opacity: 0 }}
                                                        animate={{ scale: 1, opacity: 1 }}
                                                        className="absolute inset-0 border-2 border-dashed border-qcyan-500 rounded bg-qcyan-500/10 z-10"
                                                    />
                                                )}

                                                {/* Placed Gate */}
                                                {placedGate ? (
                                                    <motion.div
                                                        initial={{ scale: 0, rotate: -180 }}
                                                        animate={{ scale: 1, rotate: 0 }}
                                                        className="relative group z-20"
                                                    >
                                                        <div className={`w-12 h-12 rounded-lg ${placedGate.bgGradient} flex items-center justify-center text-white font-bold text-xl shadow-lg border-2 border-white/20`}>
                                                            {placedGate.name}
                                                        </div>
                                                        <button
                                                            onClick={() => removeGate(placedGate.id)}
                                                            className="absolute -top-2 -right-2 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                                                        >
                                                            <X className="w-3 h-3 text-white" />
                                                        </button>
                                                    </motion.div>
                                                ) : (
                                                    <div className="text-qcyan-500/20 text-xs pointer-events-none z-10">
                                                        {isHovered && "Drop here"}
                                                    </div>
                                                )}
                                            </motion.div>
                                        );
                                    })
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Footer */}
            <div className="mt-4 pt-4 border-t border-qcyan-500/20 flex items-center justify-between text-xs text-gray-500">
                <span>Drag gates onto the circuit • Hover to remove</span>
                <span className="text-qcyan-500 font-medium">Total Gates: {placedGates.length}</span>
            </div>

            {/* Custom Scrollbar Styles */}
            <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.2);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(0, 217, 255, 0.3);
          border-radius: 3px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(0, 217, 255, 0.5);
        }
      `}</style>
        </motion.div>
    );
}
