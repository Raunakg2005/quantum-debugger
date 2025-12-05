import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";

interface HoldButtonProps {
    holdProgress: number;
    onPointerDown: () => void;
    onPointerUp: () => void;
    onPointerLeave: () => void;
}

export default function HoldButton({ holdProgress, onPointerDown, onPointerUp, onPointerLeave }: HoldButtonProps) {
    return (
        <div className="relative inline-flex justify-center items-center">
            {/* Main Button */}
            <div
                onPointerDown={onPointerDown}
                onPointerUp={onPointerUp}
                onPointerLeave={onPointerLeave}
                className="relative w-48 h-48 md:w-64 md:h-64 rounded-full border-4 border-qcyan-500 flex items-center justify-center cursor-pointer select-none z-10"
                style={{
                    background: `conic-gradient(from 0deg, 
            rgba(0, 217, 255, 0.4) ${holdProgress}%, 
            transparent ${holdProgress}%)`,
                    boxShadow: `0 0 ${20 + holdProgress}px rgba(0, 217, 255, ${0.5 + holdProgress / 200})`,
                    touchAction: 'none',
                }}
            >
                {/* Inner Circle */}
                <div className="absolute inset-4 rounded-full bg-black border-2 border-qcyan-500/50 flex items-center justify-center pointer-events-none overflow-hidden">
                    <motion.div
                        className="absolute inset-0 opacity-30"
                        style={{
                            background: 'radial-gradient(circle, rgba(0, 217, 255, 0.3) 0%, transparent 70%)',
                        }}
                        animate={{
                            scale: [1, 1.5, 1],
                            opacity: [0.3, 0.6, 0.3],
                        }}
                        transition={{ duration: 2, repeat: Infinity }}
                    />

                    <motion.div
                        animate={{
                            scale: [1, 1.1, 1],
                            rotate: [0, 360],
                        }}
                        transition={{
                            scale: { duration: 2, repeat: Infinity },
                            rotate: { duration: 10, repeat: Infinity, ease: 'linear' },
                        }}
                    >
                        <Sparkles className="w-12 h-12 md:w-16 md:h-16 text-qcyan-500" />
                    </motion.div>
                </div>
            </div>

            {/* Progress Ring */}
            <svg className="absolute w-48 h-48 md:w-64 md:h-64 -rotate-90 pointer-events-none" viewBox="0 0 256 256">
                <circle
                    cx="128"
                    cy="128"
                    r="124"
                    stroke="rgba(0, 217, 255, 0.8)"
                    strokeWidth="6"
                    fill="none"
                    strokeDasharray={`${(holdProgress / 100) * 780} 780`}
                    strokeLinecap="round"
                    style={{
                        filter: 'drop-shadow(0 0 10px rgba(0, 217, 255, 0.8))',
                    }}
                />
            </svg>

            {/* Progress Percentage */}
            {holdProgress > 0 && holdProgress < 100 && (
                <motion.div
                    className="absolute -bottom-12 md:-bottom-10 flex flex-col items-center"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <p className="text-qcyan-500 text-xl md:text-2xl font-bold">
                        {Math.round(holdProgress)}%
                    </p>
                    <div className="w-24 md:w-32 h-1 bg-black border border-qcyan-500/30 rounded-full overflow-hidden mt-2">
                        <motion.div
                            className="h-full bg-gradient-to-r from-qcyan-500 to-qgreen-500"
                            style={{ width: `${holdProgress}%` }}
                        />
                    </div>
                </motion.div>
            )}
        </div>
    );
}
