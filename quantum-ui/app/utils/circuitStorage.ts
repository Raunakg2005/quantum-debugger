// Circuit storage utilities
export interface SavedCircuit {
    id: string;
    name: string;
    gates: any[];
    qubits: number;
    timestamp: number;
}

const STORAGE_KEY = 'quantum_circuits';

// Save circuit to localStorage
export function saveCircuit(name: string, gates: any[], qubits: number): string {
    const circuits = getSavedCircuits();
    const id = `circuit_${Date.now()}`;

    const newCircuit: SavedCircuit = {
        id,
        name,
        gates,
        qubits,
        timestamp: Date.now()
    };

    circuits.push(newCircuit);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(circuits));

    return id;
}

// Load circuit from localStorage
export function loadCircuit(id: string): SavedCircuit | null {
    const circuits = getSavedCircuits();
    return circuits.find(c => c.id === id) || null;
}

// Get all saved circuits
export function getSavedCircuits(): SavedCircuit[] {
    try {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : [];
    } catch {
        return [];
    }
}

// Delete a circuit
export function deleteCircuit(id: string): void {
    const circuits = getSavedCircuits().filter(c => c.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(circuits));
}

// Export results to JSON
export function exportResultsJSON(results: any, circuitName: string = 'circuit') {
    const dataStr = JSON.stringify(results, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    downloadFile(blob, `${circuitName}_results.json`);
}

// Export results to CSV
export function exportResultsCSV(results: { counts: { [key: string]: number } }, circuitName: string = 'circuit') {
    const totalShots = Object.values(results.counts).reduce((a, b) => a + b, 0);

    let csv = 'State,Count,Probability\n';
    Object.entries(results.counts)
        .sort(([a], [b]) => a.localeCompare(b))
        .forEach(([state, count]) => {
            const probability = ((count / totalShots) * 100).toFixed(2);
            csv += `|${state}⟩,${count},${probability}%\n`;
        });

    const blob = new Blob([csv], { type: 'text/csv' });
    downloadFile(blob, `${circuitName}_results.csv`);
}

// Helper to trigger download
function downloadFile(blob: Blob, filename: string) {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}
