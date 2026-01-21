"""
AWS Braket Backend

Interface to Amazon Braket quantum computing service

REQUIRES: AWS account and credentials (PAID SERVICE)
COST: $0.30 per task + $0.00035 per shot (approximate)

NO FREE TIER - charges apply for all usage

Usage:
    1. Set up AWS account
    2. Configure AWS credentials
    3. Budget accordingly (~$5-10 minimum for testing)
"""

import logging
from typing import Dict, List

from .base_backend import QuantumBackend

logger = logging.getLogger(__name__)

# Check if AWS Braket is available
try:
    import boto3
    from braket.aws import AwsDevice
    from braket.circuits import Circuit as BraketCircuit

    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    BraketCircuit = None
    logger.debug(
        "AWS Braket not available. Install with: pip install amazon-braket-sdk"
    )


class AWSBraketBackend(QuantumBackend):
    """
    Amazon Braket quantum backend.

    ⚠️ PAID SERVICE - Charges apply for all usage

    PRICING (approximate):
    - Per-task fee: $0.30
    - Per-shot fee: $0.00035
    - Example: 1000 shots = $0.30 + (1000 × $0.00035) = $0.65

    Available devices:
    - IonQ (11 qubits)
    - Rigetti (superconducting)
    - D-Wave (quantum annealer)
    - Simulators (cheaper: $0.075/minute)

    Examples:
        >>> # WARNING: This costs money!
        >>> backend = AWSBraketBackend()
        >>> backend.connect({
        ...     'aws_access_key': 'YOUR_KEY',
        ...     'aws_secret_key': 'YOUR_SECRET',
        ...     'region': 'us-east-1'
        ... })
        >>>
        >>> # This will charge your AWS account
        >>> counts = backend.execute(gates, n_shots=100)  # ~$0.33
    """

    def __init__(self):
        """Initialize AWS Braket backend."""
        super().__init__(name="aws_braket")

        if not AWS_AVAILABLE:
            raise ImportError(
                "AWS Braket SDK not installed. "
                "Install with: pip install amazon-braket-sdk"
            )

        self.session = None
        self.current_device = None
        self.is_available = AWS_AVAILABLE

    def connect(self, credentials: Dict[str, str]):
        """
        Connect to AWS Braket.

        Args:
            credentials: Must contain:
                - 'aws_access_key': AWS access key ID
                - 'aws_secret_key': AWS secret access key
                - 'region': AWS region (e.g., 'us-east-1')
                - 's3_bucket' (optional): S3 bucket for results

        Raises:
            ValueError: If required credentials missing
            Runtime Error: If connection fails
        """
        required = ["aws_access_key", "aws_secret_key", "region"]
        missing = [k for k in required if k not in credentials]

        if missing:
            raise ValueError(f"Missing required credentials: {missing}")

        try:
            # Create boto3 session
            self.session = boto3.Session(
                aws_access_key_id=credentials["aws_access_key"],
                aws_secret_access_key=credentials["aws_secret_key"],
                region_name=credentials["region"],
            )

            self.s3_bucket = credentials.get("s3_bucket")
            self.is_connected = True

            logger.info("Connected to AWS Braket successfully")
            logger.warning("⚠️  AWS Braket charges apply for all usage!")

        except Exception as e:
            raise RuntimeError(f"Failed to connect to AWS Braket: {e}")

    def execute(
        self,
        circuit_gates: List,
        n_shots: int = 100,  # Default lower to reduce costs
        device: str = "arn:aws:braket:::device/quantum-simulator/amazon/sv1",
    ) -> Dict[str, int]:
        """
        Execute circuit on AWS Braket.

        ⚠️ THIS COSTS MONEY!

        Args:
            circuit_gates: Circuit in quantum-debugger format
            n_shots: Number of shots (costs scale with this)
            device: Device ARN (default: free simulator)

        Returns:
            Measurement counts

        Cost estimate:
            Real hardware: $0.30 + (n_shots × $0.00035)
            Simulator: $0.075 per minute
        """
        if not self.is_connected:
            raise RuntimeError("Not connected. Call connect() first.")

        # Convert to Braket circuit
        circuit = self._convert_to_braket(circuit_gates)

        # Get device
        aws_device = AwsDevice(device, aws_session=self.session)

        # Estimate cost
        estimated_cost = 0.30 + (n_shots * 0.00035)
        logger.warning(
            f"⚠️  Executing on AWS Braket. " f"Estimated cost: ${estimated_cost:.2f}"
        )

        # Execute
        task = aws_device.run(
            circuit, shots=n_shots, s3_destination_folder=self.s3_bucket
        )
        result = task.result()

        # Convert measurements to counts
        counts = result.measurement_counts

        logger.info(f"Executed on {device}: {n_shots} shots")

        return counts

    def _convert_to_braket(self, circuit_gates: List):
        """Convert quantum-debugger format to Braket circuit."""
        # Determine number of qubits
        max_qubit = 0
        for gate in circuit_gates:
            if isinstance(gate, tuple) and len(gate) >= 2:
                qubits = gate[1]
                if isinstance(qubits, int):
                    max_qubit = max(max_qubit, qubits)
                elif isinstance(qubits, (tuple, list)):
                    max_qubit = max(max_qubit, max(qubits))

        circuit = BraketCircuit()

        for gate in circuit_gates:
            gate_name = gate[0]

            # Single qubit gates
            if len(gate) >= 2 and isinstance(gate[1], int):
                qubit = gate[1]
                params = gate[2:] if len(gate) > 2 else []

                if gate_name == "h":
                    circuit.h(qubit)
                elif gate_name == "x":
                    circuit.x(qubit)
                elif gate_name == "y":
                    circuit.y(qubit)
                elif gate_name == "z":
                    circuit.z(qubit)
                elif gate_name == "rx" and params:
                    circuit.rx(qubit, params[0])
                elif gate_name == "ry" and params:
                    circuit.ry(qubit, params[0])
                elif gate_name == "rz" and params:
                    circuit.rz(qubit, params[0])

            # Two qubit gates
            elif len(gate) >= 2 and isinstance(gate[1], (tuple, list)):
                qubits = gate[1]
                if len(qubits) == 2:
                    if gate_name in ["cnot", "cx"]:
                        circuit.cnot(qubits[0], qubits[1])
                    elif gate_name == "cz":
                        circuit.cz(qubits[0], qubits[1])

        return circuit

    def get_available_devices(self) -> List[str]:
        """Get list of available AWS Braket devices."""
        if not self.is_connected:
            raise RuntimeError("Not connected")

        # Common device ARNs
        return [
            "arn:aws:braket:::device/quantum-simulator/amazon/sv1",  # Simulator (cheaper)
            "arn:aws:braket:us-east-1::device/qpu/ionq/Harmony",  # IonQ
            "arn:aws:braket:us-west-1::device/qpu/rigetti/Aspen-M-3",  # Rigetti
        ]

    def get_device_info(self, device_arn: str) -> Dict:
        """Get information about AWS Braket device."""
        if not self.is_connected:
            raise RuntimeError("Not connected")

        device = AwsDevice(device_arn, aws_session=self.session)
        props = device.properties

        return {
            "name": device.name,
            "arn": device_arn,
            "type": device.type,
            "provider": props.provider.name if hasattr(props, "provider") else "AWS",
            "status": device.status,
        }

    def estimate_cost(self, n_shots: int, device_type: str = "qpu") -> Dict:
        """
        Estimate cost for execution.

        Args:
            n_shots: Number of shots
            device_type: 'qpu' or 'simulator'

        Returns:
            Cost breakdown
        """
        if device_type == "qpu":
            per_task = 0.30
            per_shot = 0.00035
            total = per_task + (n_shots * per_shot)

            return {
                "per_task_fee": per_task,
                "per_shot_fee": per_shot,
                "n_shots": n_shots,
                "total_cost_usd": round(total, 2),
                "note": "Real hardware - charges apply",
            }
        else:  # simulator
            minutes = 0.5  # Estimate
            per_minute = 0.075
            total = minutes * per_minute

            return {
                "per_minute_fee": per_minute,
                "estimated_minutes": minutes,
                "total_cost_usd": round(total, 2),
                "note": "Simulator - much cheaper than QPU",
            }


def is_aws_available() -> bool:
    """Check if AWS Braket backend is available."""
    return AWS_AVAILABLE
