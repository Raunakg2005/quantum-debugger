"use client";

import { Download, FileJson, FileSpreadsheet } from "lucide-react";
import { exportResultsJSON, exportResultsCSV } from "../../utils/circuitStorage";

interface ExportButtonProps {
    results: { counts: { [key: string]: number } };
    circuitName?: string;
}

export default function ExportButton({ results, circuitName = 'circuit' }: ExportButtonProps) {
    const handleExportJSON = () => {
        exportResultsJSON(results, circuitName);
    };

    const handleExportCSV = () => {
        exportResultsCSV(results, circuitName);
    };

    const totalShots = Object.values(results.counts).reduce((a, b) => a + b, 0);

    if (totalShots === 0) return null;

    return (
        <div className="flex gap-2">
            <button
                onClick={handleExportJSON}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qcyan-500/10 hover:bg-qcyan-500/20 border border-qcyan-500/30 text-qcyan-500 text-xs font-medium transition-colors"
                title="Export as JSON"
            >
                <FileJson className="w-4 h-4" />
                JSON
            </button>
            <button
                onClick={handleExportCSV}
                className="flex items-center gap-2 px-3 py-2 rounded-lg bg-qgreen-500/10 hover:bg-qgreen-500/20 border border-qgreen-500/30 text-qgreen-500 text-xs font-medium transition-colors"
                title="Export as CSV"
            >
                <FileSpreadsheet className="w-4 h-4" />
                CSV
            </button>
        </div>
    );
}
