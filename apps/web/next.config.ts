import type { NextConfig } from "next";

// The browser only ever talks to this app's origin; /api/* is forwarded to FastAPI.
// Same-origin means session cookies need no CORS and are simpler to protect (ADR-001).
const apiUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
