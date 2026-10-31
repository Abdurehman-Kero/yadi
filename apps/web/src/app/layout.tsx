import type { Metadata } from "next";
import Link from "next/link";
import { NavLinks } from "@/components/NavLinks";
import "./globals.css";

export const metadata: Metadata = {
  title: "Yadi",
  description: "Your personal assistant for planning the day",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <div className="app">
          <nav className="sidebar" aria-label="Main">
            <Link href="/" className="brand">
              <span className="brand-mark" aria-hidden="true">
                Y
              </span>
              Yadi
            </Link>
            <NavLinks />
          </nav>
          <main id="main" className="page">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
