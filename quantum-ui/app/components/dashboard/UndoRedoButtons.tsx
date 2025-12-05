"use client";

import { Undo, Redo } from "lucide-react";

interface UndoRedoButtonsProps {
    onUndo: () => void;
    onRedo: () => void;
    canUndo: boolean;
    canRedo: boolean;
}

export default function UndoRedoButtons({ onUndo, onRedo, canUndo, canRedo }: UndoRedoButtonsProps) {
    return (
        <div className="flex gap-2">
            <button
                onClick={onUndo}
                disabled={!canUndo}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${canUndo
                        ? 'bg-qcyan-500/10 hover:bg-qcyan-500/20 border-qcyan-500/30 text-qcyan-500'
                        : 'bg-gray-500/10 border-gray-500/20 text-gray-500 cursor-not-allowed'
                    }`}
                title="Undo (Ctrl+Z)"
            >
                <Undo className="w-4 h-4" />
                Undo
            </button>
            <button
                onClick={onRedo}
                disabled={!canRedo}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${canRedo
                        ? 'bg-qcyan-500/10 hover:bg-qcyan-500/20 border-qcyan-500/30 text-qcyan-500'
                        : 'bg-gray-500/10 border-gray-500/20 text-gray-500 cursor-not-allowed'
                    }`}
                title="Redo (Ctrl+Y)"
            >
                <Redo className="w-4 h-4" />
                Redo
            </button>
        </div>
    );
}
