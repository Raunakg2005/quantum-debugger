"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Cpu, Zap, Activity, CheckCircle2, Clock, Wifi } from "lucide-react";

interface HardwareProfile {
    id: string;
    name: string;
    provider: string;
    qubits: number;
    connectivity: string;
    fidelity: string;
    t1: string;
    t2: string;
    available: boolean;
    description: string;
    icon: string;
}

const HARDWARE_PROFILES: HardwareProfile[] = [
    {
        id: "ibm_perth",
        name: "IBM Perth",
        provider: "IBM Quantum",
        qubits: 7,
        connectivity: "Heavy-Hex",
        fidelity: "99.8%",
        t1: "100μs",
        t2: "80μs",
        available: true,
        description: "7-qubit superconducting quantum processor with heavy-hex topology",
        icon: "🔷"
    },
    {
        id: "ibm_lagos",
        name: "IBM Lagos",
        provider: "IBM Quantum",
        qubits: 7,
        connectivity: "Heavy-Hex",
        fidelity: "99.7%",
        t1: "95μs",
        t2: "75μs",
        available: true,
        description: "7-qubit processor optimized for QAOA algorithms",
        icon: "🔷"
    },
    {
        id: "google_sycamore",
        name: "Sycamore",
        provider: "Google Quantum AI",
        qubits: 53,
        connectivity: "2D Grid",
        fidelity: "99.6%",
        t1: "20μs",
        t2: "15μs",
        available: true,
        description: "53-qubit processor that achieved quantum supremacy",
        icon: "🔶"
    },
    {
        id: "ionq_aria",
        name: "IonQ Aria",
        provider: "IonQ",
        qubits: 25,
        connectivity: "All-to-All",
        fidelity: "99.9%",
        t1: "∞",
        t2: "10s",
        available: true,
        description: "25-qubit trapped ion system with all-to-all connectivity",
        icon: "⚛️"
    },
    {
        id: "rigetti_aspen",
        name: "Aspen-M-3",
        provider: "Rigetti Computing",
        qubits: 80,
        connectivity: "Octagonal",
        fidelity: "97.8%",
        t1: "40μs",
        t2: "30μs",
        available: true,
        description: "80-qubit superconducting processor with tunable couplers",
        icon: "🟣"
    },
    {
        id: "quantinuum_h2",
        name: "H2-1",
        provider: "Quantinuum",
        qubits: 32,
        connectivity: "All-to-All",
        fidelity: "99.95%",
        t1: "∞",
        t2: "100s",
        available: true,
        description: "32-qubit trapped ion quantum computer with record fidelity",
        icon: "💎"
    },
    {
        id: "aws_sv1",
        name: "SV1 Simulator",
        provider: "AWS Braket",
        qubits: 34,
        connectivity: "Full",
        fidelity: "100%",
        t1: "N/A",
        t2: "N/A",
        available: true,
        description: "High-performance state vector simulator",
        icon: "☁️"
    },
    {
        id: "azure_ionq",
        name: "Azure IonQ",
        provider: "Microsoft Azure",
        qubits: 11,
        connectivity: "All-to-All",
        fidelity: "99.5%",
        t1: "∞",
        t2: "5s",
        available: true,
        description: "Cloud-accessible trapped ion quantum computer",
        icon: "🔷"
    },
    {
        id: "xanadu_borealis",
        name: "Borealis",
        provider: "Xanadu",
        qubits: 216,
        connectivity: "Photonic",
        fidelity: "98%",
        t1: "N/A",
        t2: "N/A",
        available: true,
        description: "Photonic quantum computer for Gaussian Boson Sampling",
        icon: "💡"
    },
    {
        id: "pasqal_fresnel",
        name: "Fresnel",
        provider: "PASQAL",
        qubits: 100,
        connectivity: "Programmable",
        fidelity: "98.5%",
        t1: "100ms",
        t2: "50ms",
        available: true,
        description: "Neutral atom quantum processor with programmable geometry",
        icon: "⚡"
    },
    {
        id: "atom_computing",
        name: "Phoenix",
        provider: "Atom Computing",
        qubits: 100,
        connectivity: "2D Array",
        fidelity: "99.2%",
        t1: "10s",
        t2: "1s",
        available: true,
        description: "Neutral atom quantum computer with long coherence times",
        icon: "🔥"
    }
];

interface HardwareModalProps {
    isOpen: boolean;
    onClose: () => void;
    currentHardware: string;
    onSelect: (hardware: HardwareProfile) => void;
}

export default function HardwareModal({ isOpen, onClose, currentHardware, onSelect }: HardwareModalProps) {
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
                            className="glass-card border border-qcyan-500/30 rounded-2xl max-w-6xl w-full max-h-[90vh] overflow-hidden"
                        >
                            {/* Header */}
                            <div className="p-6 border-b border-qcyan-500/20 bg-gradient-to-r from-qcyan-500/10 to-qgreen-500/10">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h2 className="text-2xl font-bold text-qcyan-500 flex items-center gap-3">
                                            <Cpu className="w-7 h-7" />
                                            Quantum Hardware Selector
                                        </h2>
                                        <p className="text-sm text-gray-400 mt-1">
                                            Choose from 11 quantum computing platforms
                                        </p>
                                    </div>
                                    <button
                                        onClick={onClose}
                                        className="p-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                                    >
                                        <X className="w-5 h-5 text-qcyan-500" />
                                    </button>
                                </div>
                            </div>

                            {/* Content */}
                            <div className="p-6 overflow-y-auto max-h-[calc(90vh-140px)] custom-scrollbar">
                                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                                    {HARDWARE_PROFILES.map((hardware) => {
                                        const isSelected = hardware.name === currentHardware;
                                        
                                        return (
                                            <motion.div
                                                key={hardware.id}
                                                whileHover={{ scale: hardware.available ? 1.02 : 1 }}
                                                whileTap={{ scale: hardware.available ? 0.98 : 1 }}
                                                onClick={() => hardware.available && onSelect(hardware)}
                                                className={`
                                                    relative p-4 rounded-xl border-2 transition-all cursor-pointer
                                                    ${isSelected 
                                                        ? 'border-qgreen-500 bg-qgreen-500/10' 
                                                        : hardware.available
                                                            ? 'border-qcyan-500/30 bg-black/20 hover:border-qcyan-500/50 hover:bg-qcyan-500/5'
                                                            : 'border-gray-700/30 bg-black/10 opacity-60 cursor-not-allowed'
                                                    }
                                                `}
                                            >
                                                {/* Selected Indicator */}
                                                {isSelected && (
                                                    <div className="absolute top-2 right-2">
                                                        <CheckCircle2 className="w-5 h-5 text-qgreen-500" />
                                                    </div>
                                                )}

                                                {/* Status Badge */}
                                                <div className="absolute top-2 left-2">
                                                    <span className={`
                                                        px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1
                                                        ${hardware.available 
                                                            ? 'bg-qgreen-500/20 text-qgreen-500 border border-qgreen-500/30' 
                                                            : 'bg-gray-700/20 text-gray-400 border border-gray-700/30'
                                                        }
                                                    `}>
                                                        <Wifi className="w-3 h-3" />
                                                        {hardware.available ? 'Online' : 'Offline'}
                                                    </span>
                                                </div>

                                                {/* Icon */}
                                                <div className="text-4xl mb-4 mt-6 text-center">
                                                    {hardware.icon}
                                                </div>

                                                {/* Hardware Info */}
                                                <div className="text-center mb-3">
                                                    <h3 className="text-lg font-bold text-white mb-1">
                                                        {hardware.name}
                                                    </h3>
                                                    <p className="text-xs text-qcyan-500 font-medium">
                                                        {hardware.provider}
                                                    </p>
                                                </div>

                                                <p className="text-xs text-gray-400 mb-4 min-h-[40px]">
                                                    {hardware.description}
                                                </p>

                                                {/* Specs Grid */}
                                                <div className="space-y-2 pt-3 border-t border-qcyan-500/20">
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-gray-400 flex items-center gap-1">
                                                            <Cpu className="w-3 h-3" />
                                                            Qubits
                                                        </span>
                                                        <span className="font-bold text-qcyan-500">{hardware.qubits}</span>
                                                    </div>
                                                    
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-gray-400 flex items-center gap-1">
                                                            <Activity className="w-3 h-3" />
                                                            Fidelity
                                                        </span>
                                                        <span className="font-bold text-qgreen-500">{hardware.fidelity}</span>
                                                    </div>
                                                    
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-gray-400 flex items-center gap-1">
                                                            <Zap className="w-3 h-3" />
                                                            Topology
                                                        </span>
                                                        <span className="font-medium text-gray-300">{hardware.connectivity}</span>
                                                    </div>
                                                    
                                                    <div className="flex items-center justify-between text-xs">
                                                        <span className="text-gray-400 flex items-center gap-1">
                                                            <Clock className="w-3 h-3" />
                                                            T1 / T2
                                                        </span>
                                                        <span className="font-medium text-gray-300">{hardware.t1} / {hardware.t2}</span>
                                                    </div>
                                                </div>
                                            </motion.div>
                                        );
                                    })}
                                </div>
                            </div>

                            {/* Custom Scrollbar */}
                            <style jsx>{`
                                .custom-scrollbar::-webkit-scrollbar {
                                    width: 8px;
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
