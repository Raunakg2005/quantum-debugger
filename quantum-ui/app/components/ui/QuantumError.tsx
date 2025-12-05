"use client";

import { motion, AnimatePresence } from "framer-motion";
import { AlertTriangle, XCircle, AlertCircle, X, RotateCcw } from "lucide-react";
import { useState, useEffect } from "react";

interface QuantumErrorProps {
    severity?: 'warning' | 'error' | 'critical';
    message: string;
    details?: string;
    onRetry?: () => void;
    onDismiss?: () => void;
    autoDismiss?: boolean;
    autoDismissDelay?: number;
}

export default function QuantumError({
    severity = 'error',
    message,
    details,
    onRetry,
    onDismiss,
    autoDismiss = false,
    autoDismissDelay = 5000
}: QuantumErrorProps) {
    const [isVisible, setIsVisible] = useState(true);

    // Auto-dismiss logic
    useEffect(() => {
        if (autoDismiss && onDismiss) {
            const timer = setTimeout(() => {
                handleDismiss();
            }, autoDismissDelay);
            return () => clearTimeout(timer);
        }
    }, [autoDismiss, onDismiss, autoDismissDelay]);

    const handleDismiss = () => {
        setIsVisible(false);
        setTimeout(() => {
            onDismiss?.();
        }, 300);
    };

    const severityConfig = {
        warning: {
            icon: AlertTriangle,
            color: 'orange-500',
            bg: 'bg-orange-500/10',
            border: 'border-orange-500/30',
            glow: 'shadow-[0_0_20px_rgba(251,146,60,0.3)]',
            title: 'Quantum Warning'
        },
        error: {
            icon: XCircle,
            color: 'red-500',
            bg: 'bg-red-500/10',
            border: 'border-red-500/30',
            glow: 'shadow-[0_0_20px_rgba(239,68,68,0.3)]',
            title: 'Quantum Error'
        },
        critical: {
            icon: AlertCircle,
            color: 'qpink-500',
            bg: 'bg-qpink-500/10',
            border: 'border-qpink-500/30',
            glow: 'shadow-[0_0_20px_rgba(236,72,153,0.4)]',
            title: 'Critical Decoherence'
        }
    };

    const config = severityConfig[severity];
    const Icon = config.icon;

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0, y: -20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.95 }}
                    className={`glass-card border ${config.border} ${config.bg} ${config.glow} p-4 rounded-xl max-w-md`}
                >
                    <div className="flex items-start gap-4">
                        {/* Animated Icon */}
                        <motion.div
                            animate={{
                                scale: [1, 1.1, 1],
                                rotate: severity === 'critical' ? [0, -5, 5, -5, 0] : 0
                            }}
                            transition={{
                                duration: severity === 'critical' ? 0.5 : 2,
                                repeat: Infinity,
                                repeatDelay: severity === 'critical' ? 0 : 1
                            }}
                        >
                            <Icon className={`w-6 h-6 text-${config.color}`} />
                        </motion.div>

                        {/* Content */}
                        <div className="flex-1">
                            <h3 className={`text-sm font-bold text-${config.color} mb-1`}>
                                {config.title}
                            </h3>
                            <p className="text-sm text-gray-300 mb-2">
                                {message}
                            </p>
                            {details && (
                                <p className="text-xs text-gray-500 font-mono mb-3">
                                    {details}
                                </p>
                            )}

                            {/* Actions */}
                            <div className="flex items-center gap-2">
                                {onRetry && (
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={onRetry}
                                        className={`px-3 py-1.5 rounded-lg bg-${config.color}/20 hover:bg-${config.color}/30 text-${config.color} text-xs font-medium flex items-center gap-2 transition-colors`}
                                    >
                                        <RotateCcw className="w-3 h-3" />
                                        Retry
                                    </motion.button>
                                )}
                                {onDismiss && (
                                    <motion.button
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.95 }}
                                        onClick={handleDismiss}
                                        className="px-3 py-1.5 rounded-lg bg-gray-500/20 hover:bg-gray-500/30 text-gray-400 text-xs font-medium transition-colors"
                                    >
                                        Dismiss
                                    </motion.button>
                                )}
                            </div>
                        </div>

                        {/* Close button */}
                        {onDismiss && (
                            <button
                                onClick={handleDismiss}
                                className="p-1 rounded hover:bg-white/5 transition-colors"
                            >
                                <X className="w-4 h-4 text-gray-500" />
                            </button>
                        )}
                    </div>

                    {/* Quantum glitch effect for critical errors */}
                    {severity === 'critical' && (
                        <motion.div
                            className="absolute inset-0 rounded-xl pointer-events-none overflow-hidden"
                            animate={{
                                opacity: [0, 0.1, 0]
                            }}
                            transition={{
                                duration: 0.2,
                                repeat: Infinity,
                                repeatDelay: 2
                            }}
                        >
                            <div className="absolute inset-0 bg-qpink-500/20" />
                        </motion.div>
                    )}
                </motion.div>
            )}
        </AnimatePresence>
    );
}
