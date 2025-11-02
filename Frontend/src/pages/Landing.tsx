import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { useAuth } from "@/hooks/use-auth";
import { motion } from "framer-motion";
import {
  ArrowRight,
  Brain,
  Rocket,
  Users,
  Lightbulb,
  Gamepad2,
  FolderKanban,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Link } from "react-router";
import { useEffect, useState, useRef } from "react";
import BackgroundAurora from "@/components/BackgroundAurora";

export default function Landing() {
  const { isAuthenticated, user } = useAuth();

  const [hue, setHue] = useState(265);
  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const [active, setActive] = useState(0);

  // Smooth scroll helper for the hero CTA to the "How It Works" section
  const scrollToHowItWorks = () => {
    const el = document.getElementById("how-it-works");
    if (!el) return;
    const y = el.getBoundingClientRect().top + window.scrollY - 90; // account for fixed navbar
    window.scrollTo({ top: y, behavior: "smooth" });
  };

  useEffect(() => {
    const id = setInterval(() => setHue((h) => (h + 1) % 360), 40);
    return () => clearInterval(id);
  }, []);

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;

    const onWheel = (e: WheelEvent) => {
      // Convert vertical scroll into horizontal motion
      if (Math.abs(e.deltaY) > Math.abs(e.deltaX)) {
        el.scrollLeft += e.deltaY;
        e.preventDefault();
      }
    };
    const onScroll = () => {
      const cards = Array.from(el.querySelectorAll("[data-story-card]")) as HTMLElement[];
      if (cards.length === 0) return;
      const { left, width } = el.getBoundingClientRect();
      const center = left + width / 2;
      let bestIdx = 0;
      let bestDist = Infinity;
      cards.forEach((c, i) => {
        const r = c.getBoundingClientRect();
        const cCenter = r.left + r.width / 2;
        const dist = Math.abs(cCenter - center);
        if (dist < bestDist) {
          bestDist = dist;
          bestIdx = i;
        }
      });
      setActive(bestIdx);
    };

    el.addEventListener("wheel", onWheel, { passive: false });
    el.addEventListener("scroll", onScroll, { passive: true });
    // initial compute
    onScroll();

    return () => {
      el.removeEventListener("wheel", onWheel as any);
      el.removeEventListener("scroll", onScroll as any);
    };
  }, []);

  const stories = [
    {
      name: "Aarav",
      quote: `“I wasn't sure if data science was really for me. Through Synapse, I got hands-on with real-world challenges and discovered how much I enjoy solving problems with data. I built projects that now live in my portfolio and gave me the confidence to apply for roles I once thought were out of reach."`,
      tagline: "From uncertain to unstoppable — with proof of skills that matter.",
    },
    {
      name: "Meera",
      quote: `“I felt like I was going in circles, applying to jobs without really knowing if they were the right fit. Synapse let me simulate marketing roles, test my skills, and see where I truly thrive. For the first time, I had clarity and a path that actually excites me."`,
      tagline: "From directionless to driven — and a career path with clarity.",
    },
    {
      name: "Rohan",
      quote: `"Breaking into tech felt overwhelming with so many roles I didn't fully understand. Synapse gave me a safe space to explore UX design and product management through simulations. I gained confidence, learned by doing, and built a portfolio that finally speaks for me."`,
      tagline: "From overwhelmed to confident — with a portfolio that opens doors.",
    },
    {
      name: "Priya",
      quote: `"Switching careers felt daunting until I tried Synapse. The simulations helped me test roles, fill gaps, and build a portfolio that truly reflects my abilities. I finally know where I want to go — and how to get there."`,
      tagline: "From unsure to intentional — with clarity and momentum.",
    },
  ];

  const scrollByCards = (dir: -1 | 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    const card = el.querySelector("[data-story-card]") as HTMLElement | null;
    const step = card ? card.offsetWidth + 24 : el.clientWidth * 0.8;
    el.scrollTo({ left: el.scrollLeft + dir * step, behavior: "smooth" });
  };

  const scrollToIndex = (idx: number) => {
    const el = scrollerRef.current;
    if (!el) return;
    const cards = el.querySelectorAll("[data-story-card]") as NodeListOf<HTMLElement>;
    const target = cards[idx];
    if (!target) return;
    el.scrollTo({ left: target.offsetLeft - 12, behavior: "smooth" });
  };

  return (
    <div className={`min-h-screen relative overflow-x-hidden`}>
      <div className="relative z-20">
        {/* Hero Section */}
        <section className="pt-56 md:pt-64 pb-10 md:pb-14 px-4 sm:px-6 lg:px-8 relative overflow-hidden text-center min-h-[70vh] grid place-items-center">
          <span id="top" className="absolute -top-24" />
          <div className="max-w-4xl mx-auto grid grid-cols-1 gap-10 items-center justify-items-center justify-center">
            {/* Left: Text */}
            <div>
              <motion.h1
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 }}
                className="text-5xl md:text-7xl font-extrabold leading-[1.05] tracking-tight mb-4 text-center text-white -mt-3"
              >
                Your{" "}
                <motion.span
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.15 }}
                  className="text-white"
                >
                  Career
                </motion.span>
                {", "}
                <motion.span
                  initial={{ opacity: 1, y: 0 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{}}
                  className="text-white opacity-100"
                >
                  Simulated
                </motion.span>
                .
              </motion.h1>

              <motion.p
                initial={{ opacity: 0, y: 18 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.12 }}
                className="text-lg md:text-xl text-white max-w-2xl mb-3 mx-auto font-semibold"
                style={{
                  textShadow: `
                    0 0 10px hsl(${hue} 90% 70% / 0.35),
                    0 0 22px hsl(${(hue + 60) % 360} 90% 70% / 0.25),
                    0 0 36px hsl(${(hue + 120) % 360} 90% 72% / 0.20)
                  `,
                }}
              >
                From lost to confident — test-drive your dream career with AI.
              </motion.p>

              <motion.p
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.18 }}
                className="text-base md:text-lg text-muted-foreground max-w-2xl mb-8 mx-auto"
              >
                Experience your future career through hands-on simulations. Discover your
                strengths, explore trajectories, and build a portfolio that proves it.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 14 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.24 }}
                className="flex flex-col sm:flex-row gap-4 items-center justify-center"
              >
                {isAuthenticated ? (
                  <Button
                    asChild
                    variant="ghost"
                    size="lg"
                    className="relative overflow-hidden text-base md:text-lg px-8 py-6 rounded-xl border border-white/20 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md text-foreground/90 shadow-[inset_0_1px_0_rgba(255,255,255,0.25)] transition-all hover:from-white/20 hover:to-white/10 hover:scale-[1.02] focus-visible:ring-2 focus-visible:ring-white/40 w-full sm:w-auto"
                  >
                    <Link to="/dashboard">
                      {user?.onboardingCompleted ? "Dashboard" : "Complete Setup"}
                      <ArrowRight className="ml-2 h-5 w-5" />
                    </Link>
                  </Button>
                ) : (
                  <>
                    <Button
                      asChild
                      variant="ghost"
                      size="lg"
                      className="relative overflow-hidden text-base md:text-lg px-8 py-6 rounded-xl border border-white/20 bg-gradient-to-br from-white/10 to-white/5 backdrop-blur-md text-foreground/90 shadow-[inset_0_1px_0_rgba(255,255,255,0.25)] transition-all hover:from-white/20 hover:to-white/10 hover:scale-[1.02] focus-visible:ring-2 focus-visible:ring-white/40 w-full sm:w-auto"
                    >
                      <Link to="/auth">
                        Get Started Free
                        <ArrowRight className="ml-2 h-5 w-5" />
                      </Link>
                    </Button>
                    <Button
                      variant="outline"
                      size="lg"
                      onClick={scrollToHowItWorks}
                      className="text-base md:text-lg px-8 py-6 hover:bg-indigo-50 hover:text-indigo-700 w-full sm:w-auto"
                    >
                      See How It Works
                    </Button>
                  </>
                )}
              </motion.div>
            </div>

            {/* Right: Hero Visual - simplify to a clean, neutral card without background blobs/overlays */}
            {/* Removed empty right-side container to keep hero fully centered */}
          </div>
        </section>

        {/* Why Synapse */}
        <section className="py-12 md:py-16 px-4 sm:px-6 lg:px-8">
          <span id="why-synapse" className="block -mt-16 pt-16" />
          <div className="max-w-5xl mx-auto">
            {/* Scroll-reveal header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">Why Synapse?</h2>
              <p className="text-muted-foreground text-lg mt-3">
                Three simple reasons to start today
              </p>
            </motion.div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
              {[
                {
                  title: "Discover",
                  Icon: Lightbulb,
                  desc: "Uncover your strengths with AI-powered skill analysis.",
                },
                {
                  title: "Simulate",
                  Icon: Gamepad2,
                  desc: "Test-drive careers through micro-internships that feel real.",
                },
                {
                  title: "Build Portfolio",
                  Icon: FolderKanban,
                  desc: "Showcase your work and unlock opportunities with confidence.",
                },
              ].map((item, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 16 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: 0.05 * i }}
                  // Outer container: no fill, just glow; the gradient border is drawn via a masked overlay below
                  className="group relative rounded-2xl will-change-transform hover:-translate-y-1.5"
                  style={{
                    boxShadow: `
                      0 0 22px hsl(${hue} 90% 68% / 0.28),
                      0 0 44px hsl(${(hue + 60) % 360} 90% 70% / 0.22),
                      0 0 68px hsl(${(hue + 120) % 360} 90% 72% / 0.18)
                    `,
                  }}
                >
                  {/* Masked gradient border layer: renders ONLY the outline, no interior fill */}
                  <div
                    aria-hidden
                    className="pointer-events-none absolute inset-0 rounded-[1rem]"
                    style={{
                      padding: "2px",
                      background: `
                        conic-gradient(
                          from 0deg,
                          hsl(${hue} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 40) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 80) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 120) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 160) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 200) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 240) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 280) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${(hue + 320) % 360} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"}),
                          hsl(${hue} 90% ${document.documentElement.classList.contains("dark") ? "60%" : "65%"})
                        )
                      `,
                      WebkitMask:
                        "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                      WebkitMaskComposite: "xor",
                      maskComposite: "exclude",
                      borderRadius: "1rem",
                    } as React.CSSProperties}
                  />
                  {/* Inner panel: transparent glass with subtle inner ring; no color fill */}
                  <div className="relative rounded-[1rem] p-8 min-h-48 md:min-h-56 bg-transparent backdrop-blur-xl ring-1 ring-white/40 dark:ring-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.18)]">
                    <div className="text-3xl">
                      <item.Icon className="h-8 w-8 text-white/90" strokeWidth={2.5} />
                    </div>
                    <h3 className="mt-3 text-xl font-semibold">{item.title}</h3>
                    <p className="text-muted-foreground mt-2">{item.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section id="how-it-works" className="py-16 md:py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto relative">
            {/* Subtle controlled glow following the roadmap line */}
            <div
              aria-hidden
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(1200px 240px at 50% 10%, rgba(99,102,241,0.18), rgba(56,189,248,0.12) 40%, rgba(0,0,0,0) 70%)",
                filter: "blur(10px)",
              }}
            />

            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="text-center mb-12 relative z-10"
            >
              <h2 className="text-3xl md:text-4xl font-bold tracking-tight">How It Works</h2>
              <p className="text-muted-foreground text-lg mt-3">
                A clean, modern path from curious to confident
              </p>
            </motion.div>

            {/* Roadmap wrapper limits the vertical line from step 1 to 5 */}
            <div className="relative">
              {/* Central animated roadmap line (bounded by steps) */}
              <div className="pointer-events-none absolute top-0 bottom-0 left-1/2 -translate-x-1/2 w-[2px] overflow-hidden rounded-full">
                <motion.div
                  initial={{ scaleY: 0 }}
                  whileInView={{ scaleY: 1 }}
                  viewport={{ once: true, margin: "-100px" }}
                  transition={{ duration: 0.9, ease: "easeOut" }}
                  className="origin-top h-full w-full bg-gradient-to-b from-indigo-400/40 via-blue-400/40 to-fuchsia-400/40"
                />
              </div>

              {/* Roadmap steps */}
              <ol className="space-y-10 md:space-y-14 relative z-10">
                {[
                  { title: "Onboarding", desc: "Connect LinkedIn, upload your resume, and record a short intro to personalize your experience.", Icon: Users },
                  { title: "Skill Graph", desc: "View your AI-generated strengths map and understand your unique profile.", Icon: Brain },
                  { title: "Career Path", desc: "Explore trajectories with match scores, growth trends, and required skills.", Icon: ArrowRight },
                  { title: "Micro‑Internship", desc: "Work on realistic projects with guidance and feedback to learn by doing.", Icon: Gamepad2 },
                  { title: "Portfolio", desc: "Publish your wins and showcase your simulated experience with confidence.", Icon: FolderKanban },
                ].map((step, i) => {
                  const isLeft = i % 2 === 0;
                  return (
                    <motion.li
                      key={i}
                      initial={{ opacity: 0, x: isLeft ? -24 : 24, y: 18 }}
                      whileInView={{ opacity: 1, x: 0, y: 0 }}
                      viewport={{ once: true, margin: "-100px" }}
                      transition={{ duration: 0.55, ease: "easeOut", delay: i * 0.04 }}
                      className="relative"
                    >
                      {/* Per-step number badge on roadmap line */}
                      <div className="absolute left-1/2 -translate-x-1/2 -top-2 md:top-1/2 md:-translate-y-1/2">
                        <div
                          className="h-9 w-9 rounded-full grid place-items-center text-white font-bold shadow-[0_8px_30px_rgba(99,102,241,0.35)] ring-1 ring-white/30"
                          style={{
                            background:
                              "linear-gradient(135deg, rgba(99,102,241,0.96), rgba(56,189,248,0.9))",
                            boxShadow:
                              "0 0 18px rgba(99,102,241,0.35), 0 0 36px rgba(56,189,248,0.25)",
                          }}
                        >
                          {i + 1}
                        </div>
                      </div>

                      {/* Connector from line to card */}
                      <div
                        className={`hidden md:block absolute top-1/2 -translate-y-1/2 ${isLeft ? "left-1/2 -translate-x-full" : "left-1/2"} `}
                      >
                        <div
                          className={`h-[2px] ${isLeft ? "w-24" : "w-24"} rounded-full`}
                          style={{
                            background:
                              "linear-gradient(90deg, rgba(99,102,241,0.45), rgba(56,189,248,0.45))",
                            boxShadow:
                              "0 0 10px rgba(99,102,241,0.35), 0 0 18px rgba(56,189,248,0.25)",
                          }}
                        />
                      </div>

                      {/* Card wrapper alternating sides */}
                      <div
                        className={`md:flex ${isLeft ? "md:justify-start" : "md:justify-end"} md:pl-0`}
                      >
                        <div className="relative">
                          {/* Hover glow outline via masked gradient */}
                          <div
                            aria-hidden
                            className="pointer-events-none absolute inset-0 rounded-xl opacity-0 md:group-hover:opacity-100 transition-opacity"
                            style={{
                              padding: "2px",
                              background:
                                "conic-gradient(from 0deg, rgba(99,102,241,0.9), rgba(56,189,248,0.9), rgba(236,72,153,0.9), rgba(99,102,241,0.9))",
                              WebkitMask:
                                "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                              WebkitMaskComposite: "xor",
                              maskComposite: "exclude",
                              borderRadius: "0.75rem",
                            } as React.CSSProperties}
                          />
                          {/* Card */}
                          <div className="group relative w-full md:max-w-[480px] rounded-xl p-6 md:p-7 bg-white/10 dark:bg-white/5 backdrop-blur-xl ring-1 ring-white/25 dark:ring-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.18),0_8px_30px_rgba(0,0,0,0.15)] transition-all duration-300 will-change-transform hover:scale-[1.02]">
                            <div className="flex items-start gap-4">
                              <div className="shrink-0 h-12 w-12 rounded-xl bg-white/20 dark:bg-white/10 backdrop-blur-md grid place-items-center ring-1 ring-white/30 dark:ring-white/10 shadow-[inset_0_1px_0_rgba(255,255,255,0.22)]">
                                <step.Icon className="h-6 w-6 text-white/90" strokeWidth={2.4} />
                              </div>
                              <div>
                                <h4 className="text-lg md:text-xl font-semibold">{step.title}</h4>
                                <p className="text-sm md:text-base text-muted-foreground mt-1">
                                  {step.desc}
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </motion.li>
                  );
                })}
              </ol>
            </div>
          </div>
        </section>

        {/* STORIES: horizontal perspective scroller */}
        <section className="py-16 md:py-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 18 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.5 }}
              className="text-center mb-8"
            >
              <h3 className="text-3xl md:text-4xl font-bold tracking-tight">Stories</h3>
              <p className="text-muted-foreground text-lg mt-3">
                Real journeys from exploration to confidence
              </p>
            </motion.div>

            <div className="relative">
              {/* Subtle glow behind active card */}
              <div
                aria-hidden
                className="pointer-events-none absolute inset-0 -z-10"
                style={{
                  background:
                    "radial-gradient(600px 160px at 50% 60%, rgba(99,102,241,0.25), rgba(56,189,248,0.18) 40%, rgba(0,0,0,0) 70%)",
                  filter: "blur(10px)",
                }}
              />

              {/* Arrow controls (desktop only) */}
              <div className="hidden md:flex items-center justify-between absolute left-0 right-0 top-1/2 -translate-y-1/2 h-[300px] pointer-events-none px-2">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => scrollByCards(-1)}
                  className="pointer-events-auto h-10 w-10 rounded-full bg-background/60 backdrop-blur-md border-white/20"
                >
                  <ChevronLeft className="h-5 w-5" />
                </Button>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => scrollByCards(1)}
                  className="pointer-events-auto h-10 w-10 rounded-full bg-background/60 backdrop-blur-md border-white/20"
                >
                  <ChevronRight className="h-5 w-5" />
                </Button>
              </div>

              {/* Horizontal scroller with snap; vertical wheel mapped to horizontal */}
              <div
                ref={scrollerRef}
                className="no-scrollbar relative overflow-x-auto overflow-y-hidden snap-x snap-mandatory flex gap-6 md:gap-8 px-1 md:px-2 py-2"
                style={{ scrollBehavior: "smooth" }}
              >
                {stories.map((s, i) => (
                  <motion.div
                    key={i}
                    data-story-card
                    initial={{ opacity: 0, y: 18 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.45, delay: 0.05 * i }}
                    className="snap-center shrink-0 w-[88%] sm:w-[78%] md:w-[520px] lg:w-[560px]"
                  >
                    {/* Outline glow via masked gradient on hover */}
                    <div
                      aria-hidden
                      className="pointer-events-none absolute -inset-[1px] rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                      style={{
                        padding: "2px",
                        background:
                          "conic-gradient(from 0deg, rgba(99,102,241,0.9), rgba(56,189,248,0.9), rgba(236,72,153,0.9), rgba(99,102,241,0.9))",
                        WebkitMask:
                          "linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0)",
                        WebkitMaskComposite: "xor",
                        maskComposite: "exclude",
                        borderRadius: "1rem",
                      } as React.CSSProperties}
                    />
                    {/* Card */}
                    <div
                      className={[
                        "group relative rounded-2xl p-6 md:p-8",
                        "bg-white/10 dark:bg-white/5 backdrop-blur-xl ring-1 ring-white/25 dark:ring-white/10",
                        "shadow-[inset_0_1px_0_rgba(255,255,255,0.18),0_8px_30px_rgba(0,0,0,0.15)]",
                        "transition-transform duration-300",
                        // Consistent height and perspective effect
                        "min-h-[260px] md:min-h-[280px] flex flex-col",
                        i === active ? "scale-[1.02]" : "scale-[0.98] opacity-90 md:blur-[0.25px]",
                      ].join(" ")}
                      style={{
                        backgroundImage:
                          "linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02))",
                      }}
                    >
                      <div className="flex items-center gap-3 mb-2">
                        <div className="h-10 w-10 rounded-xl bg-white/15 grid place-items-center ring-1 ring-white/20">
                          <Users className="h-5 w-5 text-white/90" />
                        </div>
                        <h4 className="text-xl md:text-2xl font-semibold">
                          {s.name}'s Story
                        </h4>
                      </div>
                      <p className="italic text-muted-foreground">
                        {s.quote}
                      </p>
                      <div className="mt-4 font-semibold">
                        {s.tagline}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Dots pagination */}
              <div className="mt-5 flex items-center justify-center gap-2">
                {stories.map((_, i) => (
                  <button
                    key={i}
                    aria-label={`Go to story ${i + 1}`}
                    onClick={() => scrollToIndex(i)}
                    className={[
                      "h-2.5 rounded-full transition-all",
                      i === active ? "w-6 bg-white/90" : "w-2.5 bg-white/50 hover:bg-white/70",
                    ].join(" ")}
                  />
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-8 relative overflow-hidden">
          <div>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
              <div className="text-center">
                <h4 className="text-2xl font-semibold">
                  Don't just plan your career.{" "}
                  <span className="animate-pulse">
                    Simulate it.
                  </span>
                </h4>
                <div className="mt-6 flex flex-wrap gap-3 justify-center">
                  {[
                    { label: "Privacy", href: "#" },
                    { label: "Terms", href: "#" },
                    { label: "Contact", href: "#" },
                    { label: "GitHub", href: "https://github.com/namaninnovates" },
                  ].map((link, i) => (
                    <a
                      key={i}
                      href={link.href}
                      className="px-4 py-2 rounded-full bg-white/10 hover:bg-white/20 transition text-sm transform will-change-transform hover:rotate-2 hover:scale-105"
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
                {!isAuthenticated && (
                  <div className="mt-8">
                    <Button asChild size="lg">
                      <Link to="/auth">
                        Get Started
                        <ArrowRight className="ml-2 h-5 w-5" />
                      </Link>
                    </Button>
                  </div>
                )}
                <div className="mt-4 text-sm text-muted-foreground">Created with ❤️ by namaninnovates</div>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}