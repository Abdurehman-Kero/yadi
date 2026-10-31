"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useUnreadCount } from "@/features/notifications/useUnreadCount";

const LINKS = [
  {
    href: "/",
    label: "Today",
    icon: "M12 3v2m0 14v2M5 5l1.5 1.5m11 11L19 19M3 12h2m14 0h2M5 19l1.5-1.5m11-11L19 5M16 12a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z",
  },
  {
    href: "/schedule",
    label: "Schedule",
    icon: "M8 3v3m8-3v3M4 9h16M5 5h14a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Z",
  },
  {
    href: "/tasks",
    label: "Tasks",
    icon: "M9 6h11M9 12h11M9 18h11M4 6l1 1 1.5-2M4 12l1 1 1.5-2M4 18l1 1 1.5-2",
  },
  {
    href: "/notifications",
    label: "Notifications",
    icon: "M6 9a6 6 0 1 1 12 0c0 6 2.5 7 2.5 7h-17S6 15 6 9Zm4 10a2 2 0 0 0 4 0",
  },
  { href: "/settings", label: "Settings", icon: "M4 7h9m4 0h3M4 17h3m4 0h9M15 5v4M9 15v4" },
];

export function NavLinks() {
  const pathname = usePathname();
  const unread = useUnreadCount();
  return (
    <ul className="nav-links">
      {LINKS.map((link) => (
        <li key={link.href}>
          <Link
            className="nav-link"
            href={link.href}
            aria-current={pathname === link.href ? "page" : undefined}
          >
            <svg
              className="icon"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.75"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden="true"
            >
              <path d={link.icon} />
            </svg>
            {link.label}
            {link.href === "/notifications" && unread > 0 && (
              <span className="nav-count">
                {unread}
                <span className="visually-hidden"> unread</span>
              </span>
            )}
          </Link>
        </li>
      ))}
    </ul>
  );
}
