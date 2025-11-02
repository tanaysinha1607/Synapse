import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { motion } from "framer-motion";
import { Menu, User, X } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

function SynapseMark({ className = "" }: { className?: string }) {
  // Minimal AI + growth glyph: connected nodes + upward arrow with gradient stroke
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      aria-hidden="true"
      role="img"
      fill="none"
    >
      <defs>
        <linearGradient id="synapseGrad" x1="0" y1="24" x2="24" y2="0" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="hsl(260 90% 60%)" />
          <stop offset="50%" stopColor="hsl(290 90% 60%)" />
          <stop offset="100%" stopColor="hsl(210 90% 60%)" />
        </linearGradient>
      </defs>
      {/* Neural nodes */}
      <circle cx="6" cy="12" r="1.4" stroke="url(#synapseGrad)" strokeWidth="1.5" />
      <circle cx="12" cy="7" r="1.4" stroke="url(#synapseGrad)" strokeWidth="1.5" />
      <circle cx="12" cy="17" r="1.4" stroke="url(#synapseGrad)" strokeWidth="1.5" />
      <circle cx="18" cy="12" r="1.4" stroke="url(#synapseGrad)" strokeWidth="1.5" />
      {/* Connections */}
      <path d="M7.4 11.2 L10.6 8.2" stroke="url(#synapseGrad)" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M7.4 12.8 L10.6 15.8" stroke="url(#synapseGrad)" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M13.4 8.8 L16.6 11.8" stroke="url(#synapseGrad)" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M13.4 15.2 L16.6 12.2" stroke="url(#synapseGrad)" strokeWidth="1.5" strokeLinecap="round" />
      {/* Upward growth arrow */}
      <path
        d="M5 17 L11 11 L13.5 13.5 L19 8"
        stroke="url(#synapseGrad)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d="M17.5 8 H19 V9.5"
        stroke="url(#synapseGrad)"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function Navbar() {
  const { isAuthenticated, user, signOut } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [scrolled, setScrolled] = useState(false);
  const [hue, setHue] = useState(265);

  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark =
      typeof window !== "undefined" &&
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches;

    const initial = stored === "dark" || (!stored && prefersDark) ? "dark" : "light";
    setTheme(initial);
    document.documentElement.classList.toggle("dark", initial === "dark");
  }, []);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const id = setInterval(() => {
      setHue((h) => (h + 1) % 360);
    }, 40);
    return () => clearInterval(id);
  }, []);

  const smoothScrollToId = (hash: string) => {
    const id = hash.replace("#", "");
    const el = document.getElementById(id);
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - 100; // offset for fixed navbar
    window.scrollTo({ top: y, behavior: "smooth" });
  };

  const handleAnchorClick = (
    e: React.MouseEvent<HTMLAnchorElement, MouseEvent>,
    href: string
  ) => {
    if (!href.startsWith("/#")) return;

    const pathname =
      typeof window !== "undefined" ? window.location.pathname : "/";

    // If we're not on the landing page, navigate to the anchor on "/"
    if (pathname !== "/") {
      e.preventDefault();
      navigate(href);
      return;
    }

    // On the landing page, smooth scroll
    e.preventDefault();
    smoothScrollToId(href.slice(2));
  };

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="fixed inset-x-0 top-0 z-50 bg-transparent"
    >
      <div
        className={[
          "pointer-events-none px-8 sm:px-12 lg:px-20",
          "mt-10",
        ].join(" ")}
      >
        <div
          className={[
            "pointer-events-auto mx-auto max-w-6xl",
            "rounded-full",
            "backdrop-blur-xl backdrop-saturate-150",
            "bg-white/30 dark:bg-white/10",
            "shadow-lg shadow-black/10 dark:shadow-black/40",
            "transition-all duration-300",
            scrolled ? "scale-[0.98] backdrop-blur-2xl" : "",
            "border",
            "relative overflow-visible",
          ].join(" ")}
          style={{
            borderWidth: 1.5,
            borderColor: `hsl(${hue} 90% ${theme === "dark" ? "55%" : "60%"})`,
          }}
        >
          {/* Multicolor diffused glow ring (subtle, animated by hue) */}
          <div
            aria-hidden
            className="pointer-events-none absolute -inset-4 rounded-full opacity-70"
            style={{
              background: `
                conic-gradient(
                  from ${hue}deg,
                  hsla(${hue}, 92%, 68%, 0.28),
                  hsla(${(hue + 30) % 360}, 92%, 67%, 0.24),
                  hsla(${(hue + 60) % 360}, 92%, 66%, 0.22),
                  hsla(${(hue + 90) % 360}, 92%, 65%, 0.26),
                  hsla(${(hue + 120) % 360}, 92%, 66%, 0.24),
                  hsla(${(hue + 150) % 360}, 92%, 67%, 0.20),
                  hsla(${(hue + 180) % 360}, 92%, 68%, 0.22),
                  hsla(${(hue + 210) % 360}, 92%, 67%, 0.20),
                  hsla(${(hue + 240) % 360}, 92%, 66%, 0.22),
                  hsla(${(hue + 270) % 360}, 92%, 65%, 0.24),
                  hsla(${(hue + 300) % 360}, 92%, 66%, 0.26),
                  hsla(${(hue + 330) % 360}, 92%, 67%, 0.24),
                  hsla(${hue}, 92%, 68%, 0.28)
                )
              `,
              filter: "blur(28px)",
              maskImage:
                "radial-gradient(closest-side, rgba(0,0,0,0) 60%, rgba(0,0,0,0.65) 74%, rgba(0,0,0,1) 100%)",
              WebkitMaskImage:
                "radial-gradient(closest-side, rgba(0,0,0,0) 60%, rgba(0,0,0,0.65) 74%, rgba(0,0,0,1) 100%)",
            } as React.CSSProperties}
          />

          {/* Extra soft outer halo for depth and diffusion */}
          <div
            aria-hidden
            className="pointer-events-none absolute -inset-8 rounded-[999px] opacity-50"
            style={{
              background: `
                conic-gradient(
                  from ${(hue + 15) % 360}deg,
                  hsla(${(hue + 10) % 360}, 90%, 70%, 0.14),
                  hsla(${(hue + 50) % 360}, 90%, 72%, 0.10),
                  hsla(${(hue + 95) % 360}, 90%, 74%, 0.12),
                  hsla(${(hue + 140) % 360}, 90%, 72%, 0.10),
                  hsla(${(hue + 185) % 360}, 90%, 70%, 0.12),
                  hsla(${(hue + 230) % 360}, 90%, 72%, 0.10),
                  hsla(${(hue + 275) % 360}, 90%, 74%, 0.12),
                  hsla(${(hue + 320) % 360}, 90%, 72%, 0.10),
                  hsla(${(hue + 360) % 360}, 90%, 70%, 0.14)
                )
              `,
              filter: "blur(40px)",
              maskImage:
                "radial-gradient(closest-side, rgba(0,0,0,0) 52%, rgba(0,0,0,0.6) 72%, rgba(0,0,0,1) 100%)",
              WebkitMaskImage:
                "radial-gradient(closest-side, rgba(0,0,0,0) 52%, rgba(0,0,0,0.6) 72%, rgba(0,0,0,1) 100%)",
            } as React.CSSProperties}
          />

          {/* Inner subtle halo just around the border for depth */}
          <div
            aria-hidden
            className="pointer-events-none absolute inset-0 rounded-full"
            style={{
              boxShadow:
                "0 0 22px rgba(255,255,255,0.10), inset 0 0 0 1px rgba(255,255,255,0.18)",
              background: `
                conic-gradient(
                  from ${hue}deg,
                  hsla(${hue}, 92%, 72%, 0.42),
                  hsla(${(hue + 45) % 360}, 92%, 71%, 0.34),
                  hsla(${(hue + 90) % 360}, 92%, 70%, 0.30),
                  hsla(${(hue + 135) % 360}, 92%, 71%, 0.32),
                  hsla(${(hue + 180) % 360}, 92%, 72%, 0.34),
                  hsla(${(hue + 225) % 360}, 92%, 71%, 0.30),
                  hsla(${(hue + 270) % 360}, 92%, 70%, 0.34),
                  hsla(${(hue + 315) % 360}, 92%, 71%, 0.36),
                  hsla(${hue}, 92%, 72%, 0.42)
                )
              `,
              padding: "1px",
              WebkitMask:
                "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
              WebkitMaskComposite: "xor",
              maskComposite: "exclude",
            } as React.CSSProperties}
          />

          <div className="px-4 sm:px-5">
            <div className="h-14 flex items-center justify-between">
              {/* Left: Logo + Text */}
              <Link to="/" className="flex items-center gap-2" onClick={(e) => {
                e.preventDefault();
                navigate("/");
              }}>
                <SynapseMark className="h-6 w-6" />
                <span className="text-lg font-semibold tracking-tight">Synapse</span>
              </Link>

              {/* Right: Nav items + controls (desktop) */}
              <div className="hidden md:flex items-center gap-4">
                <nav className="flex items-center gap-1">
                  {[
                    { label: "Home", href: "/#top" },
                    { label: "Why Synapse", href: "/#why-synapse" },
                    { label: "How It Works", href: "/#how-it-works" },
                    { label: "Story", href: "/#story" },
                  ].map((item) => (
                    <a
                      key={item.label}
                      href={item.href}
                      onClick={(e) => handleAnchorClick(e, item.href)}
                      className="px-3 py-1.5 text-sm font-medium rounded-full text-foreground/90 hover:text-foreground transition group"
                    >
                      <span className="inline-block group-hover:scale-[1.02] transition">
                        {item.label}
                      </span>
                      <span className="block h-[2px] w-0 group-hover:w-full transition-all duration-300 rounded bg-primary/70 mt-1 mx-auto" />
                    </a>
                  ))}
                </nav>

                {/* Separate pill for profile on extreme right */}
                <div className="flex items-center gap-1 rounded-full bg-white/30 dark:bg-white/10 border border-white/30 dark:border-white/10 backdrop-blur-xl px-1.5 py-1 shadow-lg shadow-black/5">
                  {isAuthenticated ? (
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="h-8 px-2 rounded-full bg-transparent">
                          <Avatar className="h-7 w-7">
                            <AvatarImage src={user?.image ?? ""} alt={user?.name ?? "Profile"} />
                            <AvatarFallback className="text-xs">
                              {(user?.name?.[0] ?? "U").toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end" className="w-44">
                        <DropdownMenuItem onClick={() => navigate("/dashboard")}>
                          Dashboard
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => navigate("/portfolio")}>
                          Portfolio
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive focus:text-destructive"
                          onClick={async () => {
                            await signOut();
                            navigate("/");
                          }}
                        >
                          Sign Out
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  ) : (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => navigate("/auth")}
                      className="h-8 w-8 rounded-full"
                      title="Sign in"
                    >
                      <User className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </div>

              {/* Mobile controls inside pill */}
              <div className="md:hidden flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                  className="h-9 w-9 rounded-full"
                  title="Menu"
                >
                  {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
                </Button>
              </div>
            </div>
          </div>

          {/* Mobile slide-out panel */}
          {mobileMenuOpen && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="md:hidden border-t border-white/20 dark:border-white/10 bg-background/90 backdrop-blur-sm rounded-b-full"
            >
              <div className="px-4 pt-2 pb-4 space-y-1">
                <a
                  href="/#top"
                  className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                  onClick={(e) => {
                    setMobileMenuOpen(false);
                    handleAnchorClick(e, "/#top");
                  }}
                >
                  Home
                </a>
                <a
                  href="/#why-synapse"
                  className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                  onClick={(e) => {
                    setMobileMenuOpen(false);
                    handleAnchorClick(e, "/#why-synapse");
                  }}
                >
                  Why Synapse
                </a>
                <a
                  href="/#how-it-works"
                  className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                  onClick={(e) => {
                    setMobileMenuOpen(false);
                    handleAnchorClick(e, "/#how-it-works");
                  }}
                >
                  How It Works
                </a>
                <a
                  href="/#story"
                  className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                  onClick={(e) => {
                    setMobileMenuOpen(false);
                    handleAnchorClick(e, "/#story");
                  }}
                >
                  Story
                </a>

                {isAuthenticated ? (
                  <>
                    <a
                      href="/dashboard"
                      className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                      onClick={(e) => {
                        e.preventDefault();
                        setMobileMenuOpen(false);
                        navigate("/dashboard");
                      }}
                    >
                      Dashboard
                    </a>
                    <a
                      href="/portfolio"
                      className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                      onClick={(e) => {
                        e.preventDefault();
                        setMobileMenuOpen(false);
                        navigate("/portfolio");
                      }}
                    >
                      Portfolio
                    </a>
                    <Button
                      variant="ghost"
                      className="w-full justify-start"
                      onClick={async () => {
                        setMobileMenuOpen(false);
                        await signOut();
                        navigate("/");
                      }}
                    >
                      Sign Out
                    </Button>
                  </>
                ) : (
                  <a
                    href="/auth"
                    className="block px-3 py-2 text-base font-medium hover:text-primary transition"
                    onClick={(e) => {
                      e.preventDefault();
                      setMobileMenuOpen(false);
                      navigate("/auth");
                    }}
                  >
                    Sign In
                  </a>
                )}
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </motion.nav>
  );
}