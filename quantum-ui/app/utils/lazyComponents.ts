'use client';

// Lazy-loaded components for better performance
import dynamic from 'next/dynamic';

// Lazy load heavy modals to reduce initial bundle size
export const LazyCircuitAnimationModal = dynamic(
    () => import('../components/dashboard/CircuitAnimationModal'),
    {
        ssr: false
    }
);

export const LazyHardwareModal = dynamic(
    () => import('../components/dashboard/HardwareModal'),
    {
        ssr: false
    }
);

// Note: BlochSphereVisualization should be imported directly where needed
// as it's already used in the main dashboard

// Lazy load Three.js only when needed
export const loadThree = async () => {
    const THREE = await import('three');
    return THREE;
};
