// Circuit history management for undo/redo functionality
export interface CircuitHistoryState {
    gates: any[];
    timestamp: number;
}

const MAX_HISTORY = 50; // Limit to prevent memory issues

export class CircuitHistory {
    private history: CircuitHistoryState[] = [];
    private currentIndex: number = -1;

    // Add a new state to history
    push(gates: any[]): void {
        // Remove any "future" states if we're not at the end
        if (this.currentIndex < this.history.length - 1) {
            this.history = this.history.slice(0, this.currentIndex + 1);
        }

        // Add new state
        this.history.push({
            gates: JSON.parse(JSON.stringify(gates)), // Deep copy
            timestamp: Date.now()
        });

        // Limit history size
        if (this.history.length > MAX_HISTORY) {
            this.history.shift();
        } else {
            this.currentIndex++;
        }
    }

    // Undo to previous state
    undo(): any[] | null {
        if (!this.canUndo()) return null;

        this.currentIndex--;
        return JSON.parse(JSON.stringify(this.history[this.currentIndex].gates));
    }

    // Redo to next state
    redo(): any[] | null {
        if (!this.canRedo()) return null;

        this.currentIndex++;
        return JSON.parse(JSON.stringify(this.history[this.currentIndex].gates));
    }

    // Check if undo is possible
    canUndo(): boolean {
        return this.currentIndex > 0;
    }

    // Check if redo is possible
    canRedo(): boolean {
        return this.currentIndex < this.history.length - 1;
    }

    // Get current state
    current(): any[] | null {
        if (this.currentIndex < 0) return null;
        return JSON.parse(JSON.stringify(this.history[this.currentIndex].gates));
    }

    // Clear all history
    clear(): void {
        this.history = [];
        this.currentIndex = -1;
    }

    // Get history size
    size(): number {
        return this.history.length;
    }
}

// Create singleton instance
let historyInstance: CircuitHistory | null = null;

export function getCircuitHistory(): CircuitHistory {
    if (!historyInstance) {
        historyInstance = new CircuitHistory();
    }
    return historyInstance;
}
