import { motion } from "framer-motion";

const GATES = [
    {
        id: "h",
        name: "H",
        description: "Hadamard Gate",
        bgGradient: "bg-gradient-to-br from-qcyan-500 to-qcyan-600",
        borderColor: "border-qcyan-500/30",
        bgColor: "bg-qcyan-500/5"
    },
    {
        id: "x",
        name: "X",
        description: "Pauli-X (NOT)",
        bgGradient: "bg-gradient-to-br from-qgreen-500 to-qgreen-600",
        borderColor: "border-qgreen-500/30",
        bgColor: "bg-qgreen-500/5"
    },
    {
        id: "y",
        name: "Y",
        description: "Pauli-Y Gate",
        bgGradient: "bg-gradient-to-br from-qorange-500 to-qorange-600",
        borderColor: "border-qorange-500/30",
        bgColor: "bg-qorange-500/5"
    },
    {
        id: "z",
        name: "Z",
        description: "Pauli-Z Gate",
        bgGradient: "bg-gradient-to-br from-qcyan-500 to-qcyan-600",
        borderColor: "border-qcyan-500/30",
        bgColor: "bg-qcyan-500/5"
    },
    {
        id: "t",
        name: "T",
        description: "T Gate (π/8)",
        bgGradient: "bg-gradient-to-br from-purple-500 to-purple-600",
        borderColor: "border-purple-500/30",
        bgColor: "bg-purple-500/5"
    },
    {
        id: "s",
        name: "S",
        description: "S Gate (Phase)",
        bgGradient: "bg-gradient-to-br from-pink-500 to-pink-600",
        borderColor: "border-pink-500/30",
        bgColor: "bg-pink-500/5"
    },
    {
        id: "cnot",
        name: "CX",
        description: "CNOT Gate",
        bgGradient: "bg-gradient-to-br from-qgreen-500 to-qgreen-600",
        borderColor: "border-qgreen-500/30",
        bgColor: "bg-qgreen-500/5"
    },
    {
        id: "m",
        name: "📊",
        description: "Measurement",
        bgGradient: "bg-gradient-to-br from-qorange-500 to-qorange-600",
        borderColor: "border-qorange-500/30",
        bgColor: "bg-qorange-500/5"
    },
];

export default function GateToolbox() {
    const handleDragStart = (e: React.DragEvent<HTMLDivElement>, gate: typeof GATES[0]) => {
        e.dataTransfer.setData("gate", JSON.stringify(gate));
        e.dataTransfer.effectAllowed = "copy";
    };

    return (
        <motion.div
            initial={{ x: -100, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="glass-card border border-qcyan-500/30 p-4 h-full overflow-y-auto custom-scrollbar"
        >
            <h3 className="text-lg font-bold text-qcyan-500 mb-4">Gate Toolbox</h3>

            <div className="space-y-3">
                {GATES.map((gate, index) => (
                    <div
                        key={gate.id}
                        draggable
                        onDragStart={(e) => handleDragStart(e, gate)}
                        className={`p-3 rounded-lg border ${gate.borderColor} ${gate.bgColor} cursor-grab active:cursor-grabbing`}
                    >
                        <motion.div
                            initial={{ x: -50, opacity: 0 }}
                            animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: index * 0.1 }}
                            whileHover={{
                                scale: 1.05,
                            }}
                            whileTap={{ scale: 0.95 }}
                            className="flex items-center gap-3"
                        >
                            <div className={`w-12 h-12 rounded-lg ${gate.bgGradient} flex items-center justify-center text-white font-bold text-xl shadow-lg`}>
                                {gate.name}
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-200">{gate.description}</p>
                            </div>
                        </motion.div>
                    </div>
                ))}
            </div>

            {/* Custom Scrollbar Styles */}
            <style jsx>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
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
