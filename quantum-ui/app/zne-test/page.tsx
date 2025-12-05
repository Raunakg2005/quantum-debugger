"use client";

import { useState } from "react";
import ZNEControls from "../components/dashboard/ZNEControls";
import { ArrowLeft } from "lucide-react";
import Link from "next/link";

export default function ZNETestPage() {
    const [zneEnabled, setZneEnabled] = useState(false);
    const [scaleFactor, setScaleFactor] = useState(2.5);
    const [method, setMethod] = useState<'linear' | 'polynomial' | 'exponential'>('linear');

    return (
        <div className="min-h-screen p-8">
            {/* Header */}
            <div className="flex items-center gap-4 mb-8">
                <Link
                    href="/"
                    className="p-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 transition-colors"
                >
                    <ArrowLeft className="w-5 h-5 text-qcyan-500" />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-qcyan-500">ZNE Controls Test</h1>
                    <p className="text-gray-400 text-sm">Zero-Noise Extrapolation Settings</p>
                </div>
            </div>

            <div className="max-w-2xl mx-auto space-y-6">
                {/* ZNE Controls Component */}
                <ZNEControls
                    enabled={zneEnabled}
                    onToggle={setZneEnabled}
                    scaleFactor={scaleFactor}
                    onScaleFactorChange={setScaleFactor}
                    method={method}
                    onMethodChange={setMethod}
                />

                {/* Current State Display */}
                <div className="glass-card border border-qcyan-500/30 p-6 rounded-xl">
                    <h2 className="text-xl font-bold text-white mb-4">Current Settings</h2>
                    <div className="space-y-2">
                        <div className="flex justify-between">
                            <span className="text-gray-400">Enabled:</span>
                            <span className={`font-bold ${zneEnabled ? 'text-qgreen-500' : 'text-gray-500'}`}>
                                {zneEnabled ? 'YES' : 'NO'}
                            </span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Method:</span>
                            <span className="font-mono text-qcyan-500">{method}</span>
                        </div>
                        <div className="flex justify-between">
                            <span className="text-gray-400">Scale Factor:</span>
                            <span className="font-mono text-qgreen-500">{scaleFactor.toFixed(1)}x</span>
                        </div>
                    </div>
                </div>

                {/* Instructions */}
                <div className="glass-card border border-purple-500/30 p-6 rounded-xl bg-purple-500/5">
                    <h3 className="text-lg font-bold text-purple-500 mb-3">How to Test:</h3>
                    <ul className="space-y-2 text-sm text-gray-300">
                        <li className="flex items-start gap-2">
                            <span className="text-qcyan-500">1.</span>
                            <span>Toggle the ZNE switch to enable/disable - watch the quantum glow animation</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-qcyan-500">2.</span>
                            <span>When enabled, select different extrapolation methods from the dropdown</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-qcyan-500">3.</span>
                            <span>Drag the scale factor slider (1-5x) and watch the quantum glow track the value</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-qcyan-500">4.</span>
                            <span>Click "Show Improvement Preview" to see estimated fidelity boost and noise reduction</span>
                        </li>
                        <li className="flex items-start gap-2">
                            <span className="text-qcyan-500">5.</span>
                            <span>Check the "Current Settings" panel below to verify state updates</span>
                        </li>
                    </ul>
                </div>

                {/* Code Example */}
                <div className="glass-card border border-qorange-500/30 p-6 rounded-xl bg-qorange-500/5">
                    <h3 className="text-lg font-bold text-qorange-500 mb-3">Usage Example:</h3>
                    <pre className="text-xs text-gray-300 overflow-x-auto">
                        {`import ZNEControls from '@/components/dashboard/ZNEControls';

const [enabled, setEnabled] = useState(false);
const [scaleFactor, setScaleFactor] = useState(2.5);
const [method, setMethod] = useState('linear');

<ZNEControls
  enabled={enabled}
  onToggle={setEnabled}
  scaleFactor={scaleFactor}
  onScaleFactorChange={setScaleFactor}
  method={method}
  onMethodChange={setMethod}
/>`}
                    </pre>
                </div>
            </div>
        </div>
    );
}
