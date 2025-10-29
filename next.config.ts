import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Only use basePath in production (when deployed with Nginx)
  basePath: process.env.NODE_ENV === 'production' ? '/llm-text-generator' : '',
  assetPrefix: process.env.NODE_ENV === 'production' ? '/llm-text-generator' : '',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
