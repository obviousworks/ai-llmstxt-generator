import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  basePath: '/llm-text-generator',
  assetPrefix: '/llm-text-generator',
  images: {
    unoptimized: true,
  },
};

export default nextConfig;
