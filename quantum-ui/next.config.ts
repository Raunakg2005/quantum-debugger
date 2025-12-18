import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Base path for deploying alongside another application
  basePath: process.env.NEXT_PUBLIC_BASE_PATH || '',
  
  // Asset prefix for proper asset loading
  assetPrefix: process.env.NEXT_PUBLIC_BASE_PATH || '',
  
  // Enable standalone output for Docker optimization
  output: 'standalone',
  
  // Disable telemetry in production
  productionBrowserSourceMaps: false,
  
  // Image optimization
  images: {
    unoptimized: true, // For Docker deployment
  },
  
  // Trailing slash for consistent routing
  trailingSlash: true,
};

export default nextConfig;
