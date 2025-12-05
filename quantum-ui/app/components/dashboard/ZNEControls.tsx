"use client";

import { useState } from "react";
import { Sparkles, Zap } from "lucide-react";
import { motion } from "framer-motion";

interface ZNEControlsProps {
    enabled: boolean;
    onToggle: (enabled: boolean) => void;
    scaleFactor: number;
    onScaleFactorChange: (value: number) => void;
    method: 'linear' | 'polynomial' | 'exponential';
    onMethodChange: (method: 'linear' | 'polynomial' | 'exponential') => void;
}

export default function ZNEControls({
    enabled,
    onToggle,
    scaleFactor,
    onScaleFactorChange,
    method,
    onMethodChange
}: ZNEControlsProps) {
    const [showPreview, setShowPreview] = useState(false);

    return (
        <div className="glass-card border border-qcyan-500/30 p-4 rounded-xl">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-qcyan-500" />
                    <h3 className="text-lg font-bold text-qcyan-500">Zero-Noise Extrapolation</h3>
                </div>

                {/* Toggle Switch */}
                <button
                    onClick={() => onToggle(!enabled)}
                    className={`relative w-14 h-7 rounded-full transition-all duration-300 ${enabled ? 'bg-qgreen-500/30' : 'bg-gray-500/20'
                        } border ${enabled ? 'border-qgreen-500/50' : 'border-gray-500/30'}`}
                >
                    <motion.div
                        className={`absolute top-1 h-5 w-5 rounded-full transition-all duration-300 ${enabled ? 'bg-qgreen-500 left-8' : 'bg-gray-500 left-1'
                            }`}
                        animate={enabled ? {
                            boxShadow: ['0 0 0px rgba(16, 185, 129, 0.5)', '0 0 15px rgba(16, 185, 129, 0.8)', '0 0 0px rgba(16, 185, 129, 0.5)']
                        } : {}}
                        transition={{ duration: 2, repeat: Infinity }}
                    />
                </button>
            </div>

            {enabled && (
                <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="space-y-4"
                >
                    {/* Method Selector */}
                    <div>
                        <label className="text-sm font-medium text-gray-400 mb-2 block">
                            Extrapolation Method
                        </label>
                        <select
                            value={method}
                            onChange={(e) => onMethodChange(e.target.value as any)}
                            className="w-full px-3 py-2 bg-black/50 border border-qcyan-500/30 rounded-lg text-white focus:outline-none focus:border-qcyan-500"
                        >
                            <option value="linear">Linear</option>
                            <option value="polynomial">Polynomial</option>
                            <option value="exponential">Exponential</option>
                        </select>
                    </div>

                    {/* Scale Factor Slider */}
                    <div>
                        <div className="flex items-center justify-between mb-2">
                            <label className="text-sm font-medium text-gray-400">
                                Scale Factor
                            </label>
                            <span className="text-sm font-bold text-qgreen-500">
                                {scaleFactor.toFixed(1)}x
                            </span>
                        </div>
                        <div className="relative">
                            <input
                                type="range"
                                min="1"
                                max="5"
                                step="0.1"
                                value={scaleFactor}
                                onChange={(e) => onScaleFactorChange(parseFloat(e.target.value))}
                                className="w-full h-2 bg-black/50 rounded-lg appearance-none cursor-pointer"
                                style={{
                                    background: `linear-gradient(to right, 
                                        rgba(16, 185, 129, 0.3) 0%,
                                        rgba(16, 185, 129, 0.3) ${((scaleFactor - 1) / 4) * 100}%, 
                                        rgba(0, 0, 0, 0.5) ${((scaleFactor - 1) / 4) * 100}%, 
                                        rgba(0, 0, 0, 0.5) 100%)`
                                }}
                            />
                            {/* Quantum glow effect */}
                            <motion.div
                                className="absolute top-0 h-2 rounded-lg pointer-events-none"
                                style={{
                                    left: 0,
                                    width: `${((scaleFactor - 1) / 4) * 100}%`,
                                    background: 'linear-gradient(to right, rgba(16, 185, 129, 0.5), rgba(16, 185, 129, 0.2))'
                                }}
                                animate={{
                                    opacity: [0.5, 0.8, 0.5]
                                }}
                                transition={{
                                    duration: 2,
                                    repeat: Infinity
                                }}
                            />
                        </div>
                    </div>

                    {/* Preview Toggle */}
                    <button
                        onClick={() => setShowPreview(!showPreview)}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 border border-qcyan-500/30 text-qcyan-500 text-sm font-medium transition-colors"
                    >
                        <Zap className="w-4 h-4" />
                        {showPreview ? 'Hide' : 'Show'} Improvement Preview
                    </button>

                    {showPreview && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="p-3 rounded-lg bg-qgreen-500/10 border border-qgreen-500/30"
                        >
                            <p className="text-xs text-gray-400 mb-2">Estimated Improvement:</p>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-300">Fidelity Boost</span>
                                <span className="text-lg font-bold text-qgreen-500">
                                    +{(scaleFactor * 2.5).toFixed(1)}%
                                </span>
                            </div>
                            <div className="flex items-center justify-between mt-1">
                                <span className="text-sm text-gray-300">Noise Reduction</span>
                                <span className="text-lg font-bold text-qcyan-500">
                                    {(scaleFactor * 8).toFixed(1)}%
                                </span>
                            </div>
                        </motion.div>
                    )}
                </motion.div>
            )}
        </div>
    );
}
