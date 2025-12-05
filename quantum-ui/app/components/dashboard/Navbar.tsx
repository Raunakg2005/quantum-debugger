import { motion } from "framer-motion";
import { Zap, Cpu, Play, RotateCcw, Settings, Film } from "lucide-react";

interface NavbarProps {
    qubits: number;
    hardware: string;
    onRun: () => void;
    onReset: () => void;
    onOpenHardware?: () => void;
    onOpenAnimation?: () => void;
}

export default function Navbar({ qubits, hardware, onRun, onReset, onOpenHardware, onOpenAnimation }: NavbarProps) {
    return (
        <motion.nav
            initial={{ y: -100 }}
            animate={{ y: 0 }}
            transition={{ duration: 0.5, type: "spring" }}
            className="glass-card border-b border-qcyan-500/30 p-3 md:p-4 flex items-center justify-between gap-2 md:gap-4"
        >
            {/* Logo - Always visible */}
            <div className="flex items-center gap-2 md:gap-3 min-w-0">
                <motion.div
                    className="w-8 h-8 md:w-10 md:h-10 rounded-lg bg-gradient-to-br from-qcyan-500 to-qgreen-500 flex items-center justify-center flex-shrink-0"
                    whileHover={{ scale: 1.05, rotate: 5 }}
                >
                    <Zap className="w-4 h-4 md:w-6 md:h-6 text-black" />
                </motion.div>
                <div className="min-w-0">
                    <h1 className="text-sm md:text-xl font-bold bg-gradient-to-r from-qcyan-500 to-qgreen-500 bg-clip-text text-transparent truncate">
                        QuantumDebugger
                    </h1>
                    <p className="text-[10px] md:text-xs text-gray-500 hidden sm:block">Circuit Builder</p>
                </div>
            </div>

            {/* Stats - Hidden on small screens */}
            <div className="hidden lg:flex items-center gap-3 xl:gap-6">
                <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-qcyan-500/30 bg-qcyan-500/5">
                    <Cpu className="w-4 h-4 text-qcyan-500" />
                    <span className="text-sm text-gray-300">{qubits} Qubits</span>
                </div>
                <button
                    onClick={onOpenHardware}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-qgreen-500/30 bg-qgreen-500/5 hover:bg-qgreen-500/10 transition-colors"
                >
                    <div className="w-2 h-2 rounded-full bg-qgreen-500 animate-pulse" />
                    <span className="text-sm text-gray-300">{hardware}</span>
                    <Settings className="w-3 h-3 text-qgreen-500" />
                </button>
            </div>

            {/* Actions - Compact on mobile */}
            <div className="flex items-center gap-2 md:gap-3 flex-shrink-0">
                <motion.button
                    onClick={onOpenAnimation}
                    className="px-2 md:px-3 py-1.5 md:py-2 rounded-lg border border-purple-500/30 bg-purple-500/5 text-purple-500 flex items-center gap-1 md:gap-2 text-xs md:text-sm font-medium hidden sm:flex"
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                >
                    <Film className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden md:inline">Animate</span>
                </motion.button>
                <motion.button
                    onClick={onReset}
                    className="px-2 md:px-4 py-1.5 md:py-2 rounded-lg border border-qorange-500/30 bg-qorange-500/5 text-qorange-500 flex items-center gap-1 md:gap-2 text-xs md:text-sm font-medium"
                    whileHover={{ scale: 1.05, boxShadow: "0 0 20px rgba(255, 107, 53, 0.3)" }}
                    whileTap={{ scale: 0.95 }}
                >
                    <RotateCcw className="w-3 h-3 md:w-4 md:h-4" />
                    <span className="hidden sm:inline">Reset</span>
                </motion.button>
                <motion.button
                    onClick={onRun}
                    className="px-2 md:px-4 py-1.5 md:py-2 rounded-lg bg-gradient-to-r from-qcyan-600 to-qgreen-600 text-black flex items-center gap-1 md:gap-2 text-xs md:text-sm font-bold shadow-neon-cyan"
                    whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 217, 255, 0.6)" }}
                    whileTap={{ scale: 0.95 }}
                >
                    <Play className="w-3 h-3 md:w-4 md:h-4" />
                    <span>Run</span>
                </motion.button>
            </div>
        </motion.nav>
    );
}
