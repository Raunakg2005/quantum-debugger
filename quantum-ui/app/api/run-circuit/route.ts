import { NextRequest, NextResponse } from 'next/server';
import { spawn } from 'child_process';
import path from 'path';

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { num_qubits, gates, shots = 1000 } = body;

        // Call Python script
        const result = await runPythonScript({
            command: 'simulate',
            num_qubits,
            gates,
            shots
        });

        return NextResponse.json(result);
    } catch (error: any) {
        return NextResponse.json(
            { error: error.message || 'Failed to run circuit' },
            { status: 500 }
        );
    }
}

function runPythonScript(input: any): Promise<any> {
    return new Promise((resolve, reject) => {
        const pythonPath = 'python'; // or 'python3' on Unix
        const scriptPath = path.join(process.cwd(), 'python', 'quantum_runner.py');

        const python = spawn(pythonPath, [scriptPath, JSON.stringify(input)]);

        let output = '';
        let errorOutput = '';

        python.stdout.on('data', (data) => {
            output += data.toString();
        });

        python.stderr.on('data', (data) => {
            errorOutput += data.toString();
        });

        python.on('close', (code) => {
            if (code !== 0) {
                reject(new Error(`Python script failed: ${errorOutput}`));
                return;
            }

            try {
                const result = JSON.parse(output);
                if (result.error) {
                    reject(new Error(result.error));
                } else {
                    resolve(result);
                }
            } catch (err) {
                reject(new Error(`Failed to parse Python output: ${output}`));
            }
        });
    });
}
