"use client";

import { useState } from "react";
import { Save, FolderOpen, Trash2 } from "lucide-react";
import { saveCircuit, getSavedCircuits, loadCircuit, deleteCircuit, SavedCircuit } from "../../utils/circuitStorage";

interface SaveLoadCircuitProps {
    currentGates: any[];
    currentQubits: number;
    onLoad: (gates: any[]) => void;
}

export default function SaveLoadCircuit({ currentGates, currentQubits, onLoad }: SaveLoadCircuitProps) {
    const [showSaveDialog, setShowSaveDialog] = useState(false);
    const [showLoadDialog, setShowLoadDialog] = useState(false);
    const [circuitName, setCircuitName] = useState("");
    const [savedCircuits, setSavedCircuits] = useState<SavedCircuit[]>([]);
    const [deleteConfirm, setDeleteConfirm] = useState<{ id: string; name: string } | null>(null);

    const handleSave = () => {
        if (!circuitName.trim()) {
            alert("Please enter a circuit name");
            return;
        }

        saveCircuit(circuitName, currentGates, currentQubits);
        setCircuitName("");
        setShowSaveDialog(false);
        alert(`Circuit "${circuitName}" saved successfully!`);
    };

    const handleShowLoad = () => {
        setSavedCircuits(getSavedCircuits());
        setShowLoadDialog(true);
    };

    const handleLoad = (circuit: SavedCircuit) => {
        onLoad(circuit.gates);
        setShowLoadDialog(false);
    };

    const handleDeleteClick = (circuit: SavedCircuit, e: React.MouseEvent) => {
        e.stopPropagation();
        setDeleteConfirm({ id: circuit.id, name: circuit.name });
    };

    const confirmDelete = () => {
        if (deleteConfirm) {
            deleteCircuit(deleteConfirm.id);
            setSavedCircuits(getSavedCircuits());
            setDeleteConfirm(null);
        }
    };

    const cancelDelete = () => {
        setDeleteConfirm(null);
    };

    return (
        <>
            {/* Action Buttons */}
            <div className="flex gap-2">
                <button
                    onClick={() => setShowSaveDialog(true)}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qgreen-500/10 hover:bg-qgreen-500/20 border border-qgreen-500/30 text-qgreen-500 text-sm font-medium transition-colors"
                    disabled={currentGates.length === 0}
                >
                    <Save className="w-4 h-4" />
                    Save
                </button>
                <button
                    onClick={handleShowLoad}
                    className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 border border-qcyan-500/30 text-qcyan-500 text-sm font-medium transition-colors"
                >
                    <FolderOpen className="w-4 h-4" />
                    Load
                </button>
            </div>

            {/* Save Dialog */}
            {showSaveDialog && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={() => setShowSaveDialog(false)}>
                    <div className="glass-card border border-qgreen-500/30 p-6 rounded-2xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                        <h3 className="text-xl font-bold text-qgreen-500 mb-4">Save Circuit</h3>
                        <input
                            type="text"
                            value={circuitName}
                            onChange={(e) => setCircuitName(e.target.value)}
                            placeholder="Enter circuit name..."
                            className="w-full px-4 py-2 bg-black/50 border border-qgreen-500/30 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-qgreen-500 mb-4"
                            autoFocus
                            onKeyDown={(e) => e.key === 'Enter' && handleSave()}
                        />
                        <p className="text-xs text-gray-400 mb-4">
                            {currentGates.length} gate(s), {currentQubits} qubit(s)
                        </p>
                        <div className="flex gap-2 justify-end">
                            <button
                                onClick={() => setShowSaveDialog(false)}
                                className="px-4 py-2 rounded-lg bg-gray-500/20 hover:bg-gray-500/30 text-gray-400 text-sm transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                className="px-4 py-2 rounded-lg bg-qgreen-500/20 hover:bg-qgreen-500/30 text-qgreen-500 border border-qgreen-500/30 text-sm font-medium transition-colors"
                            >
                                Save Circuit
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Load Dialog */}
            {showLoadDialog && (
                <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50" onClick={() => setShowLoadDialog(false)}>
                    <div className="glass-card border border-qcyan-500/30 p-6 rounded-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col" onClick={(e) => e.stopPropagation()}>
                        <h3 className="text-xl font-bold text-qcyan-500 mb-4">Load Circuit</h3>

                        {savedCircuits.length === 0 ? (
                            <p className="text-gray-400 text-center py-8">No saved circuits found</p>
                        ) : (
                            <div className="overflow-y-auto space-y-2 flex-1">
                                {savedCircuits.map((circuit) => (
                                    <div
                                        key={circuit.id}
                                        className="glass-card p-4 border border-qcyan-500/20 hover:border-qcyan-500/50 rounded-lg transition-all group"
                                    >
                                        <div className="flex items-start justify-between gap-3">
                                            <div
                                                className="flex-1 cursor-pointer"
                                                onClick={() => handleLoad(circuit)}
                                            >
                                                <h4 className="font-bold text-white group-hover:text-qcyan-500 transition-colors">
                                                    {circuit.name}
                                                </h4>
                                                <p className="text-xs text-gray-400 mt-1">
                                                    {circuit.gates.length} gates · {circuit.qubits} qubits
                                                </p>
                                                <p className="text-xs text-gray-500 mt-1">
                                                    {new Date(circuit.timestamp).toLocaleString()}
                                                </p>
                                            </div>
                                            <button
                                                onClick={(e) => handleDeleteClick(circuit, e)}
                                                className="p-2 rounded-lg bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 text-red-500 transition-all flex-shrink-0"
                                                title="Delete circuit"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}

                        <button
                            onClick={() => setShowLoadDialog(false)}
                            className="mt-4 px-4 py-2 rounded-lg bg-gray-500/20 hover:bg-gray-500/30 text-gray-400 text-sm transition-colors"
                        >
                            Close
                        </button>
                    </div>
                </div>
            )}

            {/* Delete Confirmation Modal */}
            {deleteConfirm && (
                <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-[60]" onClick={cancelDelete}>
                    <div className="glass-card border-2 border-red-500/50 p-6 rounded-2xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
                        <h3 className="text-xl font-bold text-red-500 mb-2">Delete Circuit</h3>
                        <p className="text-gray-300 mb-6">
                            Are you sure you want to delete <span className="font-bold text-white">"{deleteConfirm.name}"</span>? This action cannot be undone.
                        </p>
                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={cancelDelete}
                                className="px-4 py-2 rounded-lg bg-gray-500/20 hover:bg-gray-500/30 text-gray-400 text-sm transition-colors"
                            >
                                Cancel
                            </button>
                            <button
                                onClick={confirmDelete}
                                className="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white border border-red-500 text-sm font-medium transition-colors"
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
