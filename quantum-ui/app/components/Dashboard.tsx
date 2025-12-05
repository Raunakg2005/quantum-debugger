"use client";

import { motion } from "framer-motion";
import { Zap, Rocket, BarChart3, Atom, Sparkles, ArrowRight } from "lucide-react";
import { useState, useEffect } from "react";
import Navbar from "./dashboard/Navbar";
import GateToolbox from "./dashboard/GateToolbox";
import CircuitCanvas from "./dashboard/CircuitCanvas";
import ResultsPanel from "./dashboard/ResultsPanel";
import BlochSphere from "./dashboard/BlochSphere";
import SaveLoadCircuit from "./dashboard/SaveLoadCircuit";
import UndoRedoButtons from "./dashboard/UndoRedoButtons";
import ZNEControls from "./dashboard/ZNEControls";
import { getCircuitHistory } from "../utils/circuitHistory";
import { simulateQuantumCircuit } from "../utils/quantumSimulator";

export default function Dashboard({ particles }: { particles: Array<{ left: string; top: string }> }) {
    const [qubits] = useState(3);
    const [hardware] = useState("IBM Quantum");
    const [placedGates, setPlacedGates] = useState<any[]>([]);
    const [measurementResults, setMeasurementResults] = useState({});
    const [isSimulating, setIsSimulating] = useState(false);

    //ZNE state
    const [zneEnabled, setZneEnabled] = useState(false);
    const [scaleFactor, setScaleFactor] = useState(2.5);
    const [zneMethod, setZneMethod] = useState<'linear' | 'polynomial' | 'exponential'>('linear');

    // Circuit history for undo/redo
    const history = getCircuitHistory();
    const [canUndo, setCanUndo] = useState(false);
    const [canRedo, setCanRedo] = useState(false);

    // Update undo/redo state
    useEffect(() => {
        setCanUndo(history.canUndo());
        setCanRedo(history.canRedo());
    }, [placedGates, history]);

    const handleGatesChange = (gates: any[]) => {
        setPlacedGates(gates);
        // Add to history
        history.push(gates);
        setCanUndo(history.canUndo());
        setCanRedo(history.canRedo());
    };

    const handleRun = () => {
        setIsSimulating(true);
        setTimeout(() => {
            const results = simulateQuantumCircuit(placedGates, qubits);
            setMeasurementResults(results.counts || {});
            setIsSimulating(false);
        }, 500);
    };

    const handleReset = () => {
        setPlacedGates([]);
        setMeasurementResults({});
        history.clear();
        setCanUndo(false);
        setCanRedo(false);
    };

    const handleUndo = () => {
        const previousState = history.undo();
        if (previousState) {
            setPlacedGates(previousState);
            setCanUndo(history.canUndo());
            setCanRedo(history.canRedo());
        }
    };

    const handleRedo = () => {
        const nextState = history.redo();
        if (nextState) {
            setPlacedGates(nextState);
            setCanUndo(history.canUndo());
            setCanRedo(history.canRedo());
        }
    };

    const handleLoadCircuit = (gates: any[]) => {
        setPlacedGates(gates);
        history.push(gates);
        setCanUndo(history.canUndo());
        setCanRedo(history.canRedo());
    };

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 1 }}
            className="min-h-screen flex flex-col relative overflow-hidden"
        >
            {/* Animated Grid Background */}
            <div className="fixed inset-0 z-0"
                style={{
                    backgroundImage: `
            linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px)
          `,
                    backgroundSize: '50px 50px',
                    animation: 'gridMove 20s linear infinite',
                }}
            />

            {/* Particles */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none z-0">
                {particles.map((particle, i) => (
                    <motion.div
                        key={i}
                        className="particle"
                        style={{ left: particle.left, top: particle.top }}
                        animate={{
                            y: [0, -100, 0],
                            opacity: [0.3, 1, 0.3],
                        }}
                        transition={{
                            duration: 6 + Math.random() * 4,
                            repeat: Infinity,
                            delay: Math.random() * 5,
                        }}
                    />
                ))}
            </div>

            {/* Main Content */}
            <div className="relative z-10 flex flex-col h-screen">
                {/* Navbar */}
                <Navbar
                    qubits={qubits}
                    hardware={hardware}
                    onRun={handleRun}
                    onReset={handleReset}
                />

                {/* Toolbar - Save/Load and Undo/Redo */}
                <div className="px-4 pt-2 flex items-center gap-3 flex-wrap">
                    <SaveLoadCircuit
                        currentGates={placedGates}
                        currentQubits={qubits}
                        onLoad={handleLoadCircuit}
                    />
                    <UndoRedoButtons
                        onUndo={handleUndo}
                        onRedo={handleRedo}
                        canUndo={canUndo}
                        canRedo={canRedo}
                    />
                </div>

                {/* Main Grid */}
                <div className="flex-1 grid grid-cols-1 lg:grid-cols-[280px_1fr_350px] gap-4 p-4 overflow-hidden">
                    {/* Gate Toolbox */}
                    <GateToolbox />

                    {/* Circuit Canvas + Bloch Sphere */}
                    <div className="flex flex-col gap-4 min-h-0">
                        <div className="flex-1 min-h-0">
                            <CircuitCanvas onGatesChange={handleGatesChange} />
                        </div>
                        <div className="h-[300px]">
                            <BlochSphere theta={Math.PI / 2} phi={0} />
                        </div>
                    </div>

                    {/* Right Sidebar - Results + ZNE Controls */}
                    <div className="flex flex-col gap-4 min-h-0">
                        <div className="flex-1 min-h-0">
                            <ResultsPanel
                                gateCount={placedGates.length}
                                measurementResults={measurementResults}
                                isSimulating={isSimulating}
                            />
                        </div>
                        <ZNEControls
                            enabled={zneEnabled}
                            onToggle={setZneEnabled}
                            scaleFactor={scaleFactor}
                            onScaleFactorChange={setScaleFactor}
                            method={zneMethod}
                            onMethodChange={setZneMethod}
                        />
                    </div>
                </div>
            </div>

            <style jsx>{`
        @keyframes gridMove {
          0% { transform: translate(0, 0); }
          100% { transform: translate(50px, 50px); }
        }
      `}</style>
        </motion.div>
    );
}
