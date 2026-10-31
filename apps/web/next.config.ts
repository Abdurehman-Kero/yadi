import type { NextConfig } from "next";

// The browser only ever talks to this app's origin; /api/* is forwarded to FastAPI.
// Same-origin means session cookies need no CORS and are simpler to protect (ADR-001).
const apiUrl = process.env.API_INTERNAL_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Browser tests build elsewhere, so they can run while `npm run dev` is open.
  distDir: process.env.NEXT_DIST_DIR ?? ".next",
  // Dev-only: this project uses 127.0.0.1 because localhost stalls on IPv6 here (KI-007).
  allowedDevOrigins: ["127.0.0.1"],
  // AI requests can take up to two 25-second attempts; the default proxy limit is 30 seconds.
  experimental: { proxyTimeout: 60_000 },
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${apiUrl}/api/:path*` }];
  },
};

export default nextConfig;
