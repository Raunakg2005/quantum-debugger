"""Quick GPU Backend Test"""
from quantum_debugger.backends import get_backend, list_available_backends

print("="*60)
print("GPU BACKEND TEST")
print("="*60)

# Check available backends
backends = list_available_backends()
print("\nAvailable backends:")
for name, available in backends.items():
    status = "✓" if available else "✗"
    print(f"  {status} {name}")

# Test GPU backend
if backends.get('cupy', False):
    print("\n" + "-"*60)
    print("Testing GPU Backend...")
    print("-"*60)
    
    try:
        gpu = get_backend('gpu')
        print(f"✓ GPU Backend: {gpu.name}")
        print(f"✓ GPU Device: {gpu.device_id}")
        
        mem = gpu.memory_info()
        print(f"✓ GPU Memory: {mem['total_mb']:.0f}MB total")
        print(f"  Free: {mem['free_mb']:.0f}MB")
        print(f"  Used: {mem['used_mb']:.2f}MB")
        
        # Quick operation test
        a = gpu.eye(4)
        b = gpu.matmul(a, a)
        print(f"✓ Matrix operations working")
        
        print("\n🎉 GPU BACKEND READY!")
        
    except Exception as e:
        print(f"✗ GPU test failed: {e}")
else:
    print("\n⚠ CuPy not available - GPU backend not installed")

print("="*60)
