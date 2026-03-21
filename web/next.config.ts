import type { NextConfig } from "next";

const apiUrl = process.env.API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  reactCompiler: true,
  output: "standalone",
  async rewrites() {
    return [
      {
        source: "/api/dashboard/:path*",
        destination: `${apiUrl}/api/dashboard/:path*`,
      },
    ];
  },
};

export default nextConfig;
