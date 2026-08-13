import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  basePath: "/xjockiemusic",
  trailingSlash: true,
  images: { unoptimized: true },
};

export default nextConfig;
