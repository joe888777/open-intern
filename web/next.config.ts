import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  reactCompiler: true,
  async rewrites() {
    return [
      {
        source: "/api/dashboard/:path*",
        destination: "http://localhost:8000/api/dashboard/:path*",
      },
    ];
  },
};

export default nextConfig;
