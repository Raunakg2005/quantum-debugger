"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";
import Navbar from "../components/dashboard/Navbar";
import GateToolbox from "../components/dashboard/GateToolbox";
import CircuitCanvas from "../components/dashboard/CircuitCanvas";
import ResultsPanel from "../components/dashboard/ResultsPanel";
import BlochSphere from "../components/dashboard/BlochSphere";
import HardwareModal from "../components/dashboard/HardwareModal";
import CircuitAnimationModal from "../components/dashboard/CircuitAnimationModal";
import ZNEControls from "../components/dashboard/ZNEControls";
import SaveLoadCircuit from "../components/dashboard/SaveLoadCircuit";
import UndoRedoButtons from "../components/dashboard/UndoRedoButtons";
import { simulateQuantumGates, simulateQuantumCircuit } from "../utils/quantumSimulator";
import { getCircuitHistory } from "../utils/circuitHistory";
import Tour, { useTour } from "../components/dashboard/Tour";
import CircuitTemplates, { CircuitTemplate } from "../components/dashboard/CircuitTemplates";

interface Gate {
    id: string;
    type: string;
    name: string;
    qubit: number;
    step: number;
    bgGradient: string;
}

export default function DashboardPage() {
    const [qubits] = useState(3);
    const [hardware, setHardware] = useState("IBM Perth");
    const [particles, setParticles] = useState<Array<{ left: string; top: string }>>([]);
    const [isHardwareModalOpen, setIsHardwareModalOpen] = useState(false);
    const [isAnimationModalOpen, setIsAnimationModalOpen] = useState(false);
    const [gateCount, setGateCount] = useState(0);
    const [isSimulating, setIsSimulating] = useState(false);
    const [measurementResults, setMeasurementResults] = useState<{ [key: string]: number }>({});
    // Initialize at |0⟩ state: theta=0 (north pole of Bloch sphere)
    const [quantumState, setQuantumState] = useState({ theta: 0, phi: 0 });
    const [currentGates, setCurrentGates] = useState<Gate[]>([]);
    const simulationTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    // ZNE state
    const [zneEnabled, setZneEnabled] = useState(false);
    const [scaleFactor, setScaleFactor] = useState(2.5);
    const [zneMethod, setZneMethod] = useState<'linear' | 'polynomial' | 'exponential'>('linear');

    // Circuit history for undo/redo
    const history = getCircuitHistory();
    const [canUndo, setCanUndo] = useState(false);
    const [canRedo, setCanRedo] = useState(false);

    // Tour state
    const { showTour, setShowTour } = useTour();

    // Debounced simulation to prevent lag on complex circuits
    const debouncedSimulation = useCallback((gates: Gate[]) => {
        if (simulationTimeoutRef.current) {
            clearTimeout(simulationTimeoutRef.current);
        }

        simulationTimeoutRef.current = setTimeout(() => {
            if (gates.length > 0) {
                const result = simulateQuantumCircuit(gates, qubits, 1000);
                setMeasurementResults(result.counts);
            }
        }, 250); // 250ms debounce for smooth performance
    }, [qubits]);

    // Cleanup timeout on unmount
    useEffect(() => {
        return () => {
            if (simulationTimeoutRef.current) {
                clearTimeout(simulationTimeoutRef.current);
            }
        };
    }, []);

    useEffect(() => {
        setParticles(
            Array.from({ length: 30 }, () => ({
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
            }))
        );
    }, []);

    const handleRun = (gates: Gate[]) => {
        setIsSimulating(true);

        setTimeout(() => {
            // Run real quantum simulation
            const result = simulateQuantumCircuit(gates, qubits, 1000);
            setMeasurementResults(result.counts);
            setIsSimulating(false);
        }, 800);
    };

    const handleReset = () => {
        setMeasurementResults({});
        setCurrentGates([]);
        history.clear();
        setCanUndo(false);
        setCanRedo(false);
    };

    const handleUndo = () => {
        const previousState = history.undo();
        if (previousState) {
            setCurrentGates(previousState);
            handleGatesChange(previousState);
        }
    };

    const handleRedo = () => {
        const nextState = history.redo();
        if (nextState) {
            setCurrentGates(nextState);
            handleGatesChange(nextState);
        }
    };

    const handleLoadCircuit = (gates: Gate[]) => {
        setCurrentGates(gates);
        handleGatesChange(gates);
    };

    const handleTemplateSelect = (template: CircuitTemplate) => {
        setCurrentGates(template.gates);
        handleGatesChange(template.gates);
    };

    const handleHardwareSelect = useCallback((hardwareProfile: any) => {
        setHardware(hardwareProfile.name);
        setIsHardwareModalOpen(false);
    }, []);

    const handleGatesChange = useCallback((gates: Gate[]) => {
        setCurrentGates(gates);
        setGateCount(gates.length);

        // Add to history
        history.push(gates);
        setCanUndo(history.canUndo());
        setCanRedo(history.canRedo());

        // Filter gates for qubit 0 (Bloch sphere visualization is for single qubit)
        const qubit0Gates = gates.filter(g => g.qubit === 0);

        // If no gates on qubit 0, reset to |0⟩ state
        if (qubit0Gates.length === 0) {
            setQuantumState({ theta: 0, phi: 0 });

            // Clear results if no gates at all
            if (gates.length === 0) {
                setMeasurementResults({});
            }
            return;
        }

        // Simulate quantum state evolution for Bloch sphere
        const state = simulateQuantumGates(qubit0Gates);
        setQuantumState({ theta: state.theta, phi: state.phi });

        // Auto-execute circuit for measurements (debounced)
        debouncedSimulation(gates);
    }, [debouncedSimulation]);

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="min-h-screen flex flex-col relative overflow-hidden"
        >
            {/* Animated Grid Background */}
            <div
                className="fixed inset-0 z-0"
                style={{
                    backgroundImage: `
            linear-gradient(rgba(0, 217, 255, 0.03) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 217, 255, 0.03) 1px, transparent 1px)
          `,
                    backgroundSize: "50px 50px",
                    animation: "gridMove 20s linear infinite",
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
            <div className="relative z-10 flex flex-col min-h-screen">
                {/* Navbar */}
                <Navbar
                    qubits={qubits}
                    hardware={hardware}
                    onRun={() => handleRun(currentGates)}
                    onReset={handleReset}
                    onOpenHardware={() => setIsHardwareModalOpen(true)}
                    onOpenAnimation={() => setIsAnimationModalOpen(true)}
                />

                {/* Toolbar - Save/Load and Undo/Redo */}
                <div className="px-4 pt-2 flex items-center gap-3 flex-wrap">
                    <SaveLoadCircuit
                        currentGates={currentGates}
                        currentQubits={qubits}
                        onLoad={handleLoadCircuit}
                    />
                    <CircuitTemplates onSelect={handleTemplateSelect} />
                    <UndoRedoButtons
                        onUndo={handleUndo}
                        onRedo={handleRedo}
                        canUndo={canUndo}
                        canRedo={canRedo}
                    />
                </div>

                {/* Main Content Area - Scrollable */}
                <div className="flex-1 overflow-y-auto overflow-x-hidden">
                    <div className="h-full p-2 sm:p-3 md:p-4">
                        {/* Desktop & Tablet: Grid Layout */}
                        <div className="hidden lg:grid lg:grid-cols-[minmax(180px,200px)_1fr] xl:grid-cols-[minmax(200px,220px)_1fr_minmax(260px,300px)] gap-3 h-full">
                            {/* Gate Toolbox */}
                            <div className="min-h-0">
                                <GateToolbox />
                            </div>

                            {/* Circuit Canvas & Bloch Sphere */}
                            <div className="min-h-0 flex flex-col gap-3">
                                <CircuitCanvas onGatesChange={handleGatesChange} initialGates={currentGates} />
                                <BlochSphere theta={quantumState.theta} phi={quantumState.phi} />
                            </div>

                            {/* Results Panel + ZNE - Hidden on lg, shown on xl+ */}
                            <div className="hidden xl:flex xl:flex-col xl:gap-3 min-h-0">
                                <div className="flex-1 min-h-0">
                                    <ResultsPanel
                                        gateCount={gateCount}
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

                        {/* Mobile & Small Tablet: Stacked Layout */}
                        <div className="lg:hidden flex flex-col gap-3 h-full">
                            {/* Gate Toolbox */}
                            <div className="h-64 flex-shrink-0">
                                <GateToolbox />
                            </div>

                            {/* Circuit Canvas */}
                            <div className="flex-1 min-h-[400px]">
                                <CircuitCanvas onGatesChange={handleGatesChange} initialGates={currentGates} />
                            </div>

                            {/* Bloch Sphere */}
                            <div className="h-96 flex-shrink-0">
                                <BlochSphere theta={quantumState.theta} phi={quantumState.phi} />
                            </div>

                            {/* Results Panel */}
                            <div className="h-80 flex-shrink-0">
                                <ResultsPanel
                                    gateCount={gateCount}
                                    measurementResults={measurementResults}
                                    isSimulating={isSimulating}
                                />
                            </div>
                        </div>

                        {/* Results Panel - Bottom for lg only */}
                        <div className="hidden lg:block xl:hidden mt-3">
                            <div className="h-64">
                                <ResultsPanel
                                    gateCount={gateCount}
                                    measurementResults={measurementResults}
                                    isSimulating={isSimulating}
                                />
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            {/* Modals */}
            <HardwareModal
                isOpen={isHardwareModalOpen}
                onClose={() => setIsHardwareModalOpen(false)}
                currentHardware={hardware}
                onSelect={handleHardwareSelect}
            />

            <CircuitAnimationModal
                isOpen={isAnimationModalOpen}
                onClose={() => setIsAnimationModalOpen(false)}
                gates={currentGates}
                numQubits={qubits}
            />

            {/* Tour */}
            {showTour && <Tour onComplete={() => setShowTour(false)} />}

            <style jsx>{`
        @keyframes gridMove {
          0% {
            transform: translate(0, 0);
          }
          100% {
            transform: translate(50px, 50px);
          }
        }
      `}</style>
        </motion.div>
    );
}
