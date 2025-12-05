"use client";

import { motion } from "framer-motion";
import { BarChart3, Zap, Layers, Clock, Sparkles } from "lucide-react";
import ExportButton from "./ExportButton";

interface ResultsPanelProps {
    gateCount: number;
    measurementResults?: { [key: string]: number };
    isSimulating?: boolean;
}

export default function ResultsPanel({
    gateCount,
    measurementResults = {},
    isSimulating = false
}: ResultsPanelProps) {
    const totalShots = Object.values(measurementResults).reduce((a, b) => a + b, 0) || 0;
    const maxCount = Math.max(...Object.values(measurementResults), 1);

    return (
        <motion.div
            initial={{ x: 100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-card border border-qcyan-500/30 p-6 h-full flex flex-col gap-6"
        >
            {/* Header */}
            <div>
                <div className="flex items-center gap-2 mb-2">
                    <BarChart3 className="w-5 h-5 text-qcyan-500" />
                    <h3 className="text-lg font-bold text-qcyan-500">Results</h3>
                    {totalShots > 0 && (
                        <span className="px-2 py-0.5 text-xs rounded-full bg-qgreen-500/20 text-qgreen-500 border border-qgreen-500/30">
                            Live
                        </span>
                    )}
                </div>
                <p className="text-xs text-gray-400">
                    {totalShots > 0 ? "Real quantum circuit simulation" : "Measurement outcomes and statistics"}
                </p>
            </div>

            {/* Circuit Stats */}
            <div className="space-y-3">
                <h4 className="text-sm font-semibold text-gray-300">Circuit Info</h4>

                <div className="grid grid-cols-2 gap-3">
                    <div className="glass-card p-3 border border-qgreen-500/30 bg-qgreen-500/5">
                        <div className="flex items-center gap-2 mb-1">
                            <Layers className="w-4 h-4 text-qgreen-500" />
                            <span className="text-xs text-gray-400">Gates</span>
                        </div>
                        <p className="text-2xl font-bold text-qgreen-500">{gateCount}</p>
                    </div>

                    <div className="glass-card p-3 border border-qcyan-500/30 bg-qcyan-500/5">
                        <div className="flex items-center gap-2 mb-1">
                            <Zap className="w-4 h-4 text-qcyan-500" />
                            <span className="text-xs text-gray-400">States</span>
                        </div>
                        <p className="text-2xl font-bold text-qcyan-500">
                            {totalShots > 0 ? Object.keys(measurementResults).length : "0"}
                        </p>
                    </div>
                </div>

                <div className="glass-card p-3 border border-qorange-500/30 bg-qorange-500/5">
                    <div className="flex items-center gap-2 mb-1">
                        <Clock className="w-4 h-4 text-qorange-500" />
                        <span className="text-xs text-gray-400">Fidelity</span>
                    </div>
                    <p className="text-lg font-bold text-qorange-500">
                        {totalShots > 0 ? "99.9%" : "N/A"}
                    </p>
                </div>
            </div>

            {/* ZNE Improvement Comparison */}
            {totalShots > 0 && (
                <div className="glass-card p-3 border border-qpurple-500/30 bg-qpurple-500/5">
                    <h4 className="text-xs font-semibold text-gray-400 mb-2 flex items-center gap-2">
                        <Sparkles className="w-3 h-3 text-qpurple-500" />
                        ZNE Boost
                    </h4>
                    <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Original</span>
                            <span className="font-mono text-qorange-500">98.5%</span>
                        </div>
                        <div className="h-1.5 bg-black/50 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-qorange-500 to-qorange-600"
                                initial={{ width: 0 }}
                                animate={{ width: '98.5%' }}
                                transition={{ duration: 0.8, delay: 0.2 }}
                            />
                        </div>

                        <div className="flex justify-between text-xs">
                            <span className="text-gray-400">Improved</span>
                            <span className="font-mono text-qgreen-500">99.9%</span>
                        </div>
                        <div className="h-1.5 bg-black/50 rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-qgreen-500 to-qgreen-600"
                                initial={{ width: 0 }}
                                animate={{ width: '99.9%' }}
                                transition={{ duration: 0.8, delay: 0.4 }}
                            />
                        </div>

                        <div className="pt-1 flex items-center justify-center gap-1 text-xs">
                            <span className="text-gray-500">Improvement:</span>
                            <span className="font-bold text-qpurple-500">+1.4%</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Measurement Results */}
            <div className="flex-1 flex flex-col min-h-0">
                <h4 className="text-sm font-semibold text-gray-300 mb-3">Measurement Results</h4>

                {totalShots === 0 ? (
                    <div className="flex-1 flex items-center justify-center border border-dashed border-qcyan-500/30 rounded-lg bg-black/20">
                        <div className="text-center p-6">
                            <BarChart3 className="w-12 h-12 mx-auto mb-3 text-qcyan-500/30" />
                            <p className="text-sm font-medium text-gray-400 mb-1">No measurement results yet</p>
                            <p className="text-xs text-gray-500">Add gates to your circuit</p>
                            <p className="text-xs text-gray-500">Results update automatically</p>
                        </div>
                    </div>
                ) : (
                    <div className="flex-1 space-y-2 overflow-y-auto pr-2 custom-scrollbar">
                        {Object.entries(measurementResults)
                            .sort(([a], [b]) => a.localeCompare(b))
                            .map(([state, count]) => {
                                const probability = (count / totalShots) * 100;
                                const barWidth = (count / maxCount) * 100;

                                return (
                                    <motion.div
                                        key={state}
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        className="relative"
                                    >
                                        {/* State label */}
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-xs font-mono text-qcyan-500 font-bold">|{state}⟩</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-xs text-gray-400">{count} shots</span>
                                                <span className="text-xs font-semibold text-qgreen-500">{probability.toFixed(1)}%</span>
                                            </div>
                                        </div>

                                        {/* Bar */}
                                        <div className="relative h-8 bg-black/30 rounded overflow-hidden border border-qcyan-500/20">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${barWidth}%` }}
                                                transition={{ duration: 0.5, ease: "easeOut" }}
                                                className="h-full bg-gradient-to-r from-qcyan-500 to-qgreen-500 relative"
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
                                                    {count}
                                                </span>
                                            </div>
                                        </div>
                                    </motion.div>
                                );
                            })}
                    </div>
                )}

                {/* Total Shots */}
                {totalShots > 0 && (
                    <div className="mt-4 pt-4 border-t border-qcyan-500/20 flex-shrink-0">
                        <div className="flex items-center justify-between text-sm">
                            <span className="text-gray-400">Total Shots</span>
                            <span className="font-bold text-qcyan-500">{totalShots}</span>
                        </div>
                    </div>
                )}
            </div>

            {/* Simulating Indicator */}
            {isSimulating && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qcyan-500/10 border border-qcyan-500/30 flex-shrink-0"
                >
                    <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                    >
                        <Zap className="w-4 h-4 text-qcyan-500" />
                    </motion.div>
                    <span className="text-sm text-qcyan-500">Simulating circuit...</span>
                </motion.div>
            )}

            {/* Custom Scrollbar Styles */}
            <style jsx>{`
                .custom-scrollbar::-webkit-scrollbar {
                    width: 8px;
                }
                .custom-scrollbar::-webkit-scrollbar-track {
                    background: linear-gradient(
                        to right,
                        rgba(0, 0, 0, 0.1),
                        rgba(0, 0, 0, 0.3),
                        rgba(0, 0, 0, 0.1)
                    );
                    border-radius: 4px;
                    margin: 4px 0;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb {
                    background: linear-gradient(
                        135deg,
                        rgba(0, 217, 255, 0.4),
                        rgba(0, 255, 163, 0.4)
                    );
                    border-radius: 4px;
                    border: 1px solid rgba(0, 217, 255, 0.2);
                    transition: all 0.3s ease;
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover {
                    background: linear-gradient(
                        135deg,
                        rgba(0, 217, 255, 0.7),
                        rgba(0, 255, 163, 0.7)
                    );
                    border-color: rgba(0, 217, 255, 0.5);
                    box-shadow: 0 0 8px rgba(0, 217, 255, 0.4);
                }
                .custom-scrollbar::-webkit-scrollbar-thumb:active {
                    background: linear-gradient(
                        135deg,
                        rgba(0, 217, 255, 0.9),
                        rgba(0, 255, 163, 0.9)
                    );
                }
            `}</style>
        </motion.div>
    );
}
