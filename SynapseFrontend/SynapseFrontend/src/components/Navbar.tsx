import { Button } from "@/components/ui/button";
import { useAuth } from "@/hooks/use-auth";
import { motion } from "framer-motion";
import { Brain, Menu, User, X, Moon, Sun } from "lucide-react";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

export function Navbar() {
  const { isAuthenticated, user, signOut } = useAuth();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark">("light");

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

  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
    localStorage.setItem("theme", next);
  };

  const handleSignOut = async () => {
    await signOut();
    navigate("/");
  };

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      className="sticky top-0 z-50 border-b border-white/20 dark:border-white/10 backdrop-blur-xl backdrop-saturate-150 bg-transparent supports-[backdrop-filter]:bg-transparent shadow-none"
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center h-16 md:grid md:grid-cols-[auto_1fr_auto]">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <Brain className="h-8 w-8 text-primary" />
            <span className="text-xl font-bold tracking-tight">Synapse</span>
          </Link>

          {/* Center scrollable tabs (desktop) */}
          <div className="hidden md:flex justify-center">
            <div className="overflow-x-auto no-scrollbar max-w-3xl">
              <div className="flex gap-2 py-2 px-1">
                <a
                  href="/#top"
                  className="px-3 py-1.5 text-xs font-medium rounded-full border bg-white/40 dark:bg-white/10 backdrop-blur-md hover:bg-white/60 dark:hover:bg-white/20 transition-colors"
                >
                  Home
                </a>
                <a
                  href="/#why-synapse"
                  className="px-3 py-1.5 text-xs font-medium rounded-full border bg-white/40 dark:bg-white/10 backdrop-blur-md hover:bg-white/60 dark:hover:bg-white/20 transition-colors"
                >
                  Why Synapse
                </a>
                <a
                  href="/#how-it-works"
                  className="px-3 py-1.5 text-xs font-medium rounded-full border bg-white/40 dark:bg-white/10 backdrop-blur-md hover:bg-white/60 dark:hover:bg-white/20 transition-colors"
                >
                  How It Works
                </a>
                <a
                  href="/#story"
                  className="px-3 py-1.5 text-xs font-medium rounded-full border bg-white/40 dark:bg-white/10 backdrop-blur-md hover:bg-white/60 dark:hover:bg-white/20 transition-colors"
                >
                  Story
                </a>
              </div>
            </div>
          </div>

          {/* Desktop Navigation (right) */}
          <div className="hidden md:flex items-center gap-3">
            {/* Dark mode toggle (only one, extreme right next to avatar) */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="h-9 w-9 rounded-full bg-white/30 dark:bg-white/10 border border-white/30 dark:border-white/10 backdrop-blur-md shadow-md hover:bg-white/50 dark:hover:bg-white/20"
              title="Toggle theme"
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4 text-yellow-400" />
              ) : (
                <Moon className="h-4 w-4 text-indigo-600" />
              )}
            </Button>

            {isAuthenticated ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="h-9 px-2">
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
                className="h-9 w-9 rounded-full"
                title="Sign in"
              >
                <User className="h-4 w-4" />
              </Button>
            )}
          </div>

          {/* Mobile controls */}
          <div className="md:hidden flex items-center gap-1">
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              className="h-9 w-9 rounded-full bg-white/30 dark:bg-white/10 border border-white/30 dark:border-white/10 backdrop-blur-md shadow-md hover:bg-white/50 dark:hover:bg-white/20"
              title="Toggle theme"
            >
              {theme === "dark" ? (
                <Sun className="h-4 w-4 text-yellow-400" />
              ) : (
                <Moon className="h-4 w-4 text-indigo-600" />
              )}
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="h-9 w-9"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t bg-background/95 backdrop-blur-sm"
          >
            <div className="px-2 pt-2 pb-3 space-y-1">
              <a
                href="/#top"
                className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Home
              </a>
              <a
                href="/#why-synapse"
                className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Why Synapse
              </a>
              <a
                href="/#how-it-works"
                className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                How It Works
              </a>
              <a
                href="/#story"
                className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                onClick={() => setMobileMenuOpen(false)}
              >
                Story
              </a>

              {isAuthenticated ? (
                <>
                  <a
                    href="/dashboard"
                    className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Dashboard
                  </a>
                  <a
                    href="/portfolio"
                    className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    Portfolio
                  </a>
                  <Button
                    variant="ghost"
                    className="w-full justify-start"
                    onClick={async () => {
                      await signOut();
                      setMobileMenuOpen(false);
                      navigate("/");
                    }}
                  >
                    Sign Out
                  </Button>
                </>
              ) : (
                <a
                  href="/auth"
                  className="block px-3 py-2 text-base font-medium hover:text-primary transition-colors"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Sign In
                </a>
              )}
            </div>
          </motion.div>
        )}
      </div>
    </motion.nav>
  );
}