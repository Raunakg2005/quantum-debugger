"""
Tests for GPU utilities
"""

import pytest
import numpy as np

from quantum_debugger.gpu import (
    MultiGPUManager,
    MixedPrecisionTrainer,
    GPUMemoryManager,
)


class TestMultiGPUManager:
    """Test multi-GPU management"""

    def test_initialization(self):
        """Test MultiGPUManager initialization"""
        manager = MultiGPUManager(gpu_ids=[])
        assert manager.n_gpus == 0

    def test_gpu_detection(self):
        """Test GPU detection"""
        manager = MultiGPUManager()
        gpus = manager.get_available_gpus()
        assert isinstance(gpus, list)

    def test_synchronize(self):
        """Test GPU synchronization"""
        manager = MultiGPUManager()
        # Should not raise
        manager.synchronize()


class TestMixedPrecisionTrainer:
    """Test mixed precision training"""

    def test_initialization(self):
        """Test trainer initialization"""

        class DummyModel:
            _parameters = np.random.randn(10)

        trainer = MixedPrecisionTrainer(DummyModel(), precision="fp16")
        assert trainer.enabled == True
        assert trainer.precision == "fp16"

    def test_fp16_conversion(self):
        """Test FP16 conversion"""

        class DummyModel:
            _parameters = np.random.randn(10)

        trainer = MixedPrecisionTrainer(DummyModel(), precision="fp16")
        arr = np.array([1.0, 2.0, 3.0])
        half = trainer.to_half(arr)
        assert half.dtype == np.float16

    def test_fp32_conversion(self):
        """Test FP32 conversion"""

        class DummyModel:
            _parameters = np.random.randn(10)

        trainer = MixedPrecisionTrainer(DummyModel())
        arr = np.array([1.0, 2.0, 3.0], dtype=np.float16)
        full = trainer.to_float(arr)
        assert full.dtype == np.float32

    def test_loss_scaling(self):
        """Test loss scaling"""

        class DummyModel:
            _parameters = np.random.randn(10)

        trainer = MixedPrecisionTrainer(DummyModel(), precision="fp16")
        loss = 0.5
        scaled = trainer.scale_loss(loss)
        assert scaled == loss * trainer.loss_scale

    def test_gradient_check(self):
        """Test gradient overflow check"""

        class DummyModel:
            _parameters = np.random.randn(10)

        trainer = MixedPrecisionTrainer(DummyModel())

        # Valid gradients
        valid_grads = np.array([0.1, 0.2, 0.3])
        assert trainer.check_gradients(valid_grads) == True

        # Invalid gradients
        invalid_grads = np.array([np.inf, 0.2, 0.3])
        assert trainer.check_gradients(invalid_grads) == False


class TestGPUMemoryManager:
    """Test GPU memory management"""

    def test_initialization(self):
        """Test memory manager initialization"""
        manager = GPUMemoryManager()
        assert manager.gradient_checkpointing_enabled == False

    def test_gradient_checkpointing(self):
        """Test gradient checkpointing enable/disable"""
        manager = GPUMemoryManager()

        class DummyModel:
            pass

        model = DummyModel()
        manager.enable_gradient_checkpointing(model)
        assert model._use_checkpointing == True

        manager.disable_gradient_checkpointing(model)
        assert model._use_checkpointing == False

    def test_memory_stats(self):
        """Test memory statistics retrieval"""
        manager = GPUMemoryManager()
        stats = manager.get_memory_stats()

        assert "used_mb" in stats
        assert "total_mb" in stats
        assert "free_mb" in stats
        assert "utilization" in stats

    def test_clear_cache(self):
        """Test cache clearing"""
        manager = GPUMemoryManager()
        # Should not raise
        manager.clear_cache()

    def test_get_recommendations(self):
        """Test memory recommendations"""
        manager = GPUMemoryManager()
        recs = manager.get_recommendations()
        assert isinstance(recs, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
