"use node";

import { action } from "./_generated/server";
import { v } from "convex/values";

function titleCase(input: string) {
  const cleaned = input.replace(/[-_]+/g, " ").replace(/\s+/g, " ").trim();
  return cleaned
    .split(" ")
    .filter(Boolean)
    .map(s => s.charAt(0).toUpperCase() + s.slice(1).toLowerCase())
    .join(" ");
}

export const validateLinkedinUrl = action({
  args: {
    url: v.string(),
  },
  handler: async (ctx, args) => {
    const url = args.url.trim();

    // Basic sanity
    let parsed: URL;
    try {
      parsed = new URL(url);
    } catch {
      return { valid: false, reason: "Please enter a valid URL." as const };
    }

    // Host and path validation for LinkedIn profiles
    const hostnameOk = /(^|\.)linkedin\.com$/i.test(parsed.hostname);
    const path = parsed.pathname.replace(/\/+$/, ""); // trim trailing slash
    // Accept common profile paths, primary focus on /in/
    const profileMatch = /^\/in\/[A-Za-z0-9\-%_.]+$/i.test(path);

    if (!hostnameOk || !profileMatch) {
      return {
        valid: false,
        reason:
          "That doesn't look like a valid LinkedIn profile URL. Please use a link like https://www.linkedin.com/in/your-handle" as const,
      };
    }

    // Try to fetch page to get a better name (may fail due to LinkedIn restrictions)
    let extractedName: string | null = null;
    try {
      const res = await fetch(url, {
        method: "GET",
        redirect: "follow",
        headers: {
          "User-Agent":
            "Mozilla/5.0 (compatible; SynapseBot/1.0; +https://example.com/bot)",
          Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        },
      });

      if (res.ok) {
        const html = await res.text();
        // Try og:title first
        const og = html.match(
          /<meta\s+property=["']og:title["']\s+content=["']([^"']+)["'][^>]*>/i,
        );
        if (og?.[1]) {
          // Often contains "Name - Title | LinkedIn"
          extractedName = og[1].split("-")[0].split("|")[0].trim();
        }
        if (!extractedName) {
          // Fallback to <title>
          const t = html.match(/<title[^>]*>([^<]+)<\/title>/i);
          if (t?.[1]) {
            extractedName = t[1].split("-")[0].split("|")[0].trim();
          }
        }
      }
    } catch {
      // ignore network/LinkedIn block issues and fall back
    }

    // Fallback: derive from last path segment
    if (!extractedName) {
      const segment = path.split("/").pop() ?? "";
      extractedName = titleCase(decodeURIComponent(segment));
    }

    if (!extractedName) {
      return {
        valid: false,
        reason:
          "We couldn't extract a name from that profile. Please double-check your URL." as const,
      };
    }

    return {
      valid: true as const,
      name: extractedName,
    };
  },
});
