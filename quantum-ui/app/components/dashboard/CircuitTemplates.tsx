"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { FileCode, Sparkles, X, Zap } from "lucide-react";

export interface CircuitTemplate {
    id: string;
    name: string;
    description: string;
    category: 'basic' | 'intermediate' | 'advanced';
    gates: any[];
    qubits: number;
}

const templates: CircuitTemplate[] = [
    {
        id: "bell_state",
        name: "Bell State",
        description: "Create quantum entanglement between two qubits",
        category: "basic",
        qubits: 2,
        gates: [
            { id: "h-1", type: "h", name: "H", qubit: 0, step: 0, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { id: "cnot-1", type: "cnot", name: "●─", qubit: 0, step: 1, bgGradient: "bg-gradient-to-br from-pink-500 to-red-600" },
            { id: "cnot-2", type: "x", name: "X", qubit: 1, step: 1, bgGradient: "bg-gradient-to-br from-green-500 to-emerald-600" }
        ]
    },
    {
        id: "superposition",
        name: "Superposition",
        description: "Put all qubits in equal superposition",
        category: "basic",
        qubits: 3,
        gates: [
            { id: "h-1", type: "h", name: "H", qubit: 0, step: 0, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { id: "h-2", type: "h", name: "H", qubit: 1, step: 0, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { id: "h-3", type: "h", name: "H", qubit: 2, step: 0, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" }
        ]
    },
    {
        id: "ghz_state",
        name: "GHZ State",
        description: "Three-qubit entangled state",
        category: "intermediate",
        qubits: 3,
        gates: [
            { id: "h-1", type: "h", name: "H", qubit: 0, step: 0, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { id: "cnot-1", type: "cnot", name: "●─", qubit: 0, step: 1, bgGradient: "bg-gradient-to-br from-pink-500 to-red-600" },
            { id: "x-1", type: "x", name: "X", qubit: 1, step: 1, bgGradient: "bg-gradient-to-br from-green-500 to-emerald-600" },
            { id: "cnot-2", type: "cnot", name: "●─", qubit: 1, step: 2, bgGradient: "bg-gradient-to-br from-pink-500 to-red-600" },
            { id: "x-2", type: "x", name: "X", qubit: 2, step: 2, bgGradient: "bg-gradient-to-br from-green-500 to-emerald-600" }
        ]
    },
    {
        id: "deutsch",
        name: "Deutsch Algorithm",
        description: "Simple quantum algorithm demonstration",
        category: "intermediate",
        qubits: 2,
        gates: [
            { id: "x-1", type: "x", name: "X", qubit: 1, step: 0, bgGradient: "bg-gradient-to-br from-green-500 to-emerald-600" },
            { id: "h-1", type: "h", name: "H", qubit: 0, step: 1, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" },
            { id: "h-2", type: "h", name: "H", qubit: 1, step: 1, bgGradient: "bg-gradient-to-br from-blue-500 to-purple-600" }
        ]
    }
];

interface CircuitTemplatesProps {
    onSelect: (template: CircuitTemplate) => void;
}

export default function CircuitTemplates({ onSelect }: CircuitTemplatesProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [selectedCategory, setSelectedCategory] = useState<'all' | 'basic' | 'intermediate' | 'advanced'>('all');

    const filteredTemplates = selectedCategory === 'all'
        ? templates
        : templates.filter(t => t.category === selectedCategory);

    const handleSelect = (template: CircuitTemplate) => {
        onSelect(template);
        setIsOpen(false);
    };

    const categoryColors = {
        basic: 'text-qgreen-500 border-qgreen-500/30 bg-qgreen-500/10',
        intermediate: 'text-qcyan-500 border-qcyan-500/30 bg-qcyan-500/10',
        advanced: 'text-qpurple-500 border-qpurple-500/30 bg-qpurple-500/10'
    };

    return (
        <>
            {/* Trigger Button */}
            <button
                onClick={() => setIsOpen(true)}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qpurple-500/10 hover:bg-qpurple-500/20 border border-qpurple-500/30 text-qpurple-500 text-sm font-medium transition-colors"
            >
                <FileCode className="w-4 h-4" />
                Templates
            </button>

            {/* Modal */}
            {isOpen && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={() => setIsOpen(false)}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="glass-card border border-qpurple-500/30 rounded-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden flex flex-col"
                        onClick={(e) => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="p-6 border-b border-qpurple-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-3">
                                    <Sparkles className="w-6 h-6 text-qpurple-500" />
                                    <h2 className="text-2xl font-bold text-qpurple-500">Circuit Templates</h2>
                                </div>
                                <button
                                    onClick={() => setIsOpen(false)}
                                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                                >
                                    <X className="w-5 h-5 text-gray-400" />
                                </button>
                            </div>

                            {/* Category Filter */}
                            <div className="flex gap-2">
                                {(['all', 'basic', 'intermediate', 'advanced'] as const).map(category => (
                                    <button
                                        key={category}
                                        onClick={() => setSelectedCategory(category)}
                                        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${selectedCategory === category
                                                ? 'bg-qpurple-500/20 text-qpurple-500 border border-qpurple-500/50'
                                                : 'text-gray-400 hover:bg-white/5'
                                            }`}
                                    >
                                        {category.charAt(0).toUpperCase() + category.slice(1)}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Templates List */}
                        <div className="flex-1 overflow-y-auto p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                {filteredTemplates.map(template => (
                                    <motion.div
                                        key={template.id}
                                        whileHover={{ scale: 1.02 }}
                                        onClick={() => handleSelect(template)}
                                        className="glass-card p-4 border border-qcyan-500/20 hover:border-qcyan-500/50 rounded-xl cursor-pointer transition-all group"
                                    >
                                        <div className="flex items-start justify-between mb-2">
                                            <h3 className="font-bold text-white group-hover:text-qcyan-500 transition-colors">
                                                {template.name}
                                            </h3>
                                            <span className={`px-2 py-0.5 rounded-full text-xs font-medium border ${categoryColors[template.category]}`}>
                                                {template.category}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-400 mb-3">
                                            {template.description}
                                        </p>
                                        <div className="flex items-center gap-4 text-xs text-gray-500">
                                            <div className="flex items-center gap-1">
                                                <Zap className="w-3 h-3" />
                                                {template.qubits} qubits
                                            </div>
                                            <div className="flex items-center gap-1">
                                                <FileCode className="w-3 h-3" />
                                                {template.gates.length} gates
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                </div>
            )}
        </>
    );
}
