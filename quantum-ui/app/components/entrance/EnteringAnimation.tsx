import { motion } from "framer-motion";

export default function EnteringAnimation() {
    return (
        <div>
            <motion.h2
                className="text-2xl sm:text-3xl md:text-4xl lg:text-6xl font-bold bg-gradient-to-r from-qcyan-500 via-qgreen-500 to-qorange-500 bg-clip-text text-transparent px-4"
                style={{ backgroundSize: "200% 100%" }}
                animate={{
                    backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                }}
                transition={{ duration: 2, repeat: Infinity }}
            >
                ENTERING QUANTUM WORLD
            </motion.h2>
            <div className="mt-6 md:mt-8 flex justify-center space-x-2 md:space-x-3">
                {[0, 1, 2, 3, 4].map((i) => (
                    <motion.div
                        key={i}
                        className="w-2 h-2 md:w-3 md:h-3 bg-qcyan-500 rounded-full"
                        animate={{
                            scale: [1, 2, 1],
                            opacity: [1, 0.3, 1],
                        }}
                        transition={{
                            duration: 1.5,
                            repeat: Infinity,
                            delay: i * 0.2,
                        }}
                    />
                ))}
            </div>
        </div>
    );
}
