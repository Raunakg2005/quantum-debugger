"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import QuantumSpinner from "../components/ui/QuantumSpinner";
import QuantumError from "../components/ui/QuantumError";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function UIShowcase() {
    const [showError, setShowError] = useState(false);
    const [errorSeverity, setErrorSeverity] = useState<'warning' | 'error' | 'critical'>('error');

    return (
        <div className="min-h-screen p-8 space-y-12">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Link
                    href="/"
                    className="p-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 text-qcyan-500" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-qcyan-500">UI Polish Showcase</h1>
                    <p className="text-gray-400 text-sm">Quantum-themed UI components</p>
                </div>
            </div>

            {/* Loading Spinners */}
            <section className="space-y-6">
                <h2 className="text-2xl font-bold text-qgreen-500">Loading States</h2>

                <div className="glass-card p-8 border border-qcyan-500/20">
                    <h3 className="text-lg font-semibold text-white mb-6">Spinner Variants</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        <div className="glass-card p-6 border border-qcyan-500/10 flex flex-col items-center">
                            <h4 className="text-sm font-medium text-gray-400 mb-4">Orbital</h4>
                            <QuantumSpinner variant="orbital" size="lg" text="Simulating..." />
                        </div>
                        <div className="glass-card p-6 border border-qcyan-500/10 flex flex-col items-center">
                            <h4 className="text-sm font-medium text-gray-400 mb-4">Pulse</h4>
                            <QuantumSpinner variant="pulse" size="lg" text="Processing..." />
                        </div>
                        <div className="glass-card p-6 border border-qcyan-500/10 flex flex-col items-center">
                            <h4 className="text-sm font-medium text-gray-400 mb-4">Wave</h4>
                            <QuantumSpinner variant="wave" size="lg" text="Loading..." />
                        </div>
                    </div>
                </div>

                <div className="glass-card p-8 border border-qcyan-500/20">
                    <h3 className="text-lg font-semibold text-white mb-6">Spinner Sizes</h3>
                    <div className="flex items-center justify-around">
                        <div>
                            <p className="text-xs text-gray-400 mb-2 text-center">Small</p>
                            <QuantumSpinner variant="orbital" size="sm" />
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 mb-2 text-center">Medium</p>
                            <QuantumSpinner variant="orbital" size="md" />
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 mb-2 text-center">Large</p>
                            <QuantumSpinner variant="orbital" size="lg" />
                        </div>
                    </div>
                </div>
            </section>

            {/* Error States */}
            <section className="space-y-6">
                <h2 className="text-2xl font-bold text-qgreen-500">Error States</h2>

                <div className="glass-card p-8 border border-qcyan-500/20 space-y-4">
                    <h3 className="text-lg font-semibold text-white mb-6">Error Severity Levels</h3>

                    {/* Controls */}
                    <div className="flex items-center gap-4 mb-6">
                        <button
                            onClick={() => {
                                setErrorSeverity('warning');
                                setShowError(true);
                            }}
                            className="px-4 py-2 rounded-lg bg-orange-500/20 hover:bg-orange-500/30 text-orange-500 transition-colors"
                        >
                            Show Warning
                        </button>
                        <button
                            onClick={() => {
                                setErrorSeverity('error');
                                setShowError(true);
                            }}
                            className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-500 transition-colors"
                        >
                            Show Error
                        </button>
                        <button
                            onClick={() => {
                                setErrorSeverity('critical');
                                setShowError(true);
                            }}
                            className="px-4 py-2 rounded-lg bg-qpink-500/20 hover:bg-qpink-500/30 text-qpink-500 transition-colors"
                        >
                            Show Critical
                        </button>
                    </div>

                    {/* Error Display */}
                    <div className="min-h-[100px] flex items-center justify-center">
                        {showError && (
                            <QuantumError
                                severity={errorSeverity}
                                message={
                                    errorSeverity === 'warning'
                                        ? "Quantum state approaching decoherence threshold"
                                        : errorSeverity === 'error'
                                            ? "Circuit simulation failed - measurement collapse error"
                                            : "Critical quantum decoherence detected - system unstable"
                                }
                                details={errorSeverity === 'critical' ? "Error code: QE-2048" : undefined}
                                onRetry={() => console.log('Retrying...')}
                                onDismiss={() => setShowError(false)}
                            />
                        )}
                    </div>
                </div>

                {/* Example Errors */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <QuantumError
                        severity="warning"
                        message="High noise level detected"
                        details="T1 relaxation: 45μs"
                        onDismiss={() => { }}
                    />
                    <QuantumError
                        severity="error"
                        message="Gate fidelity below threshold"
                        onRetry={() => console.log('Retry')}
                        onDismiss={() => { }}
                    />
                    <QuantumError
                        severity="critical"
                        message="Quantum entanglement lost"
                        details="Decoherence rate: 99.8%"
                        onRetry={() => console.log('Retry')}
                        onDismiss={() => { }}
                    />
                </div>
            </section>

            {/* Glassmorphism Examples */}
            <section className="space-y-6">
                <h2 className="text-2xl font-bold text-qgreen-500">Glassmorphism Effects</h2>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="glass-card p-6 border border-qcyan-500/30"
                    >
                        <h4 className="text-lg font-bold text-qcyan-500 mb-2">Standard Glass</h4>
                        <p className="text-sm text-gray-400">Backdrop blur with semi-transparent background</p>
                    </motion.div>

                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="glass-card p-6 border-2 border-qgreen-500/30 shadow-quantum-glow-green"
                    >
                        <h4 className="text-lg font-bold text-qgreen-500 mb-2">With Glow</h4>
                        <p className="text-sm text-gray-400">Enhanced with quantum glow effect</p>
                    </motion.div>

                    <motion.div
                        whileHover={{ scale: 1.05 }}
                        className="glass-card p-6 border-2 border-qpink-500/30 bg-gradient-to-br from-qpink-500/10 to-qpurple-500/10"
                    >
                        <h4 className="text-lg font-bold text-qpink-500 mb-2">Gradient Glass</h4>
                        <p className="text-sm text-gray-400">Combined with gradient background</p>
                    </motion.div>
                </div>
            </section>

            {/* Responsive Design Info */}
            <section className="space-y-6">
                <h2 className="text-2xl font-bold text-qgreen-500">Responsive Design</h2>

                <div className="glass-card p-8 border border-qcyan-500/20">
                    <h3 className="text-lg font-semibold text-white mb-4">Breakpoints</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="p-4 rounded-lg bg-qcyan-500/10 border border-qcyan-500/20">
                            <p className="font-mono text-sm text-qcyan-500 mb-1">Mobile</p>
                            <p className="text-xs text-gray-400">320px - 767px</p>
                            <p className="text-xs text-gray-500 mt-2">Single column, stacked layout</p>
                        </div>
                        <div className="p-4 rounded-lg bg-qgreen-500/10 border border-qgreen-500/20">
                            <p className="font-mono text-sm text-qgreen-500 mb-1">Tablet</p>
                            <p className="text-xs text-gray-400">768px - 1023px</p>
                            <p className="text-xs text-gray-500 mt-2">2-column grid, optimized spacing</p>
                        </div>
                        <div className="p-4 rounded-lg bg-qpink-500/10 border border-qpink-500/20">
                            <p className="font-mono text-sm text-qpink-500 mb-1">Desktop</p>
                            <p className="text-xs text-gray-400">1024px+</p>
                            <p className="text-xs text-gray-500 mt-2">Full layout with sidebars</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
}
