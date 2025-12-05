// Quantum Circuit Simulator with Complex Number Support

interface Complex {
    real: number;
    imag: number;
}

interface Gate {
    id: string;
    type: string;
    name: string;
    qubit: number;
    step: number;
    bgGradient: string;
}

// Complex number operations
function complexMultiply(a: Complex, b: Complex): Complex {
    return {
        real: a.real * b.real - a.imag * b.imag,
        imag: a.real * b.imag + a.imag * b.real
    };
}

function complexAdd(a: Complex, b: Complex): Complex {
    return {
        real: a.real + b.real,
        imag: a.imag + b.imag
    };
}

function complexMagnitudeSquared(c: Complex): number {
    return c.real * c.real + c.imag * c.imag;
}

// Get 2x2 gate matrix for single-qubit gates
function getGateMatrix(gateName: string): Complex[][] {
    const sqrt2 = Math.sqrt(2);
    
    switch (gateName) {
        case 'H': // Hadamard
            return [
                [{ real: 1/sqrt2, imag: 0 }, { real: 1/sqrt2, imag: 0 }],
                [{ real: 1/sqrt2, imag: 0 }, { real: -1/sqrt2, imag: 0 }]
            ];
        case 'X': // Pauli-X (NOT)
            return [
                [{ real: 0, imag: 0 }, { real: 1, imag: 0 }],
                [{ real: 1, imag: 0 }, { real: 0, imag: 0 }]
            ];
        case 'Y': // Pauli-Y
            return [
                [{ real: 0, imag: 0 }, { real: 0, imag: -1 }],
                [{ real: 0, imag: 1 }, { real: 0, imag: 0 }]
            ];
        case 'Z': // Pauli-Z
            return [
                [{ real: 1, imag: 0 }, { real: 0, imag: 0 }],
                [{ real: 0, imag: 0 }, { real: -1, imag: 0 }]
            ];
        case 'T': // T gate (π/4 phase)
            return [
                [{ real: 1, imag: 0 }, { real: 0, imag: 0 }],
                [{ real: 0, imag: 0 }, { real: Math.cos(Math.PI/4), imag: Math.sin(Math.PI/4) }]
            ];
        case 'S': // S gate (π/2 phase)
            return [
                [{ real: 1, imag: 0 }, { real: 0, imag: 0 }],
                [{ real: 0, imag: 0 }, { real: 0, imag: 1 }]
            ];
        default:
            // Identity
            return [
                [{ real: 1, imag: 0 }, { real: 0, imag: 0 }],
                [{ real: 0, imag: 0 }, { real: 1, imag: 0 }]
            ];
    }
}

// Apply a single-qubit gate to the state vector
function applyMultiQubitGate(stateVector: Complex[], gate: Gate, numQubits: number): Complex[] {
    const newState = [...stateVector];
    const matrix = getGateMatrix(gate.name);
    const qubitIndex = gate.qubit;
    const numStates = 1 << numQubits;
    const qubitMask = 1 << qubitIndex;

    for (let i = 0; i < numStates; i++) {
        if ((i & qubitMask) === 0) {
            const i0 = i;
            const i1 = i | qubitMask;
            
            const amp0 = stateVector[i0];
            const amp1 = stateVector[i1];
            
            newState[i0] = complexAdd(
                complexMultiply(matrix[0][0], amp0),
                complexMultiply(matrix[0][1], amp1)
            );
            newState[i1] = complexAdd(
                complexMultiply(matrix[1][0], amp0),
                complexMultiply(matrix[1][1], amp1)
            );
        }
    }
    
    return newState;
}

// Simulate the full quantum circuit
export function simulateQuantumCircuit(gates: Gate[], numQubits: number = 3, shots: number = 1000) {
    if (gates.length === 0) {
        return { counts: {}, probabilities: {} };
    }

    const numStates = 1 << numQubits;
    
    // Initialize state vector to |000...0⟩
    let stateVector: Complex[] = Array(numStates).fill(null).map(() => ({ real: 0, imag: 0 }));
    stateVector[0] = { real: 1, imag: 0 };

    // Apply gates in order (sorted by step)
    const sortedGates = [...gates].sort((a, b) => a.step - b.step);
    
    for (const gate of sortedGates) {
        if (gate.name === 'M') continue; // Skip measurement gates
        if (gate.name === 'CNOT') continue; // Skip multi-qubit gates for now
        
        stateVector = applyMultiQubitGate(stateVector, gate, numQubits);
    }

    // Calculate probabilities
    const probabilities: { [key: string]: number } = {};
    for (let i = 0; i < numStates; i++) {
        const prob = complexMagnitudeSquared(stateVector[i]);
        if (prob > 1e-10) { // Only include non-negligible probabilities
            const state = i.toString(2).padStart(numQubits, '0');
            probabilities[state] = prob;
        }
    }

    // Sample measurements according to probabilities
    const counts: { [key: string]: number } = {};
    for (let shot = 0; shot < shots; shot++) {
        const rand = Math.random();
        let cumProb = 0;
        
        for (const [state, prob] of Object.entries(probabilities)) {
            cumProb += prob;
            if (rand <= cumProb) {
                counts[state] = (counts[state] || 0) + 1;
                break;
            }
        }
    }

    return { counts, probabilities };
}

// Simulate quantum gates for Bloch sphere visualization (single qubit)
export function simulateQuantumGates(gates: Gate[]): { theta: number; phi: number } {
    if (gates.length === 0) {
        return { theta: 0, phi: 0 }; // |0⟩ state at north pole
    }

    // Initialize to |0⟩
    let state: Complex[] = [
        { real: 1, imag: 0 }, // |0⟩ amplitude
        { real: 0, imag: 0 }  // |1⟩ amplitude
    ];

    // Apply gates in sequence
    const sortedGates = [...gates].sort((a, b) => a.step - b.step);
    
    for (const gate of sortedGates) {
        if (gate.name === 'M') continue;
        
        const matrix = getGateMatrix(gate.name);
        const newState = [
            complexAdd(
                complexMultiply(matrix[0][0], state[0]),
                complexMultiply(matrix[0][1], state[1])
            ),
            complexAdd(
                complexMultiply(matrix[1][0], state[0]),
                complexMultiply(matrix[1][1], state[1])
            )
        ];
        state = newState;
    }

    // Convert to Bloch sphere coordinates
    const alpha = state[0];
    const beta = state[1];
    
    // Calculate theta (polar angle)
    const theta = 2 * Math.acos(Math.min(1, Math.max(-1, Math.sqrt(complexMagnitudeSquared(alpha)))));
    
    // Calculate phi (azimuthal angle)
    let phi = Math.atan2(beta.imag, beta.real) - Math.atan2(alpha.imag, alpha.real);
    
    // Normalize phi to [0, 2π]
    while (phi < 0) phi += 2 * Math.PI;
    while (phi >= 2 * Math.PI) phi -= 2 * Math.PI;
    
    return { theta, phi };
}
