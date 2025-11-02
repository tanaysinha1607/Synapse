import { useEffect, useRef } from "react";

function isTouchDevice() {
  return typeof window !== "undefined" && ("ontouchstart" in window || navigator.maxTouchPoints > 0);
}

export default function Cursor() {
  const dotRef = useRef<HTMLDivElement | null>(null);
  const ringRef = useRef<HTMLDivElement | null>(null);
  const rafRef = useRef<number | null>(null);

  useEffect(() => {
    if (isTouchDevice()) return;

    const dot = document.createElement("div");
    const ring = document.createElement("div");
    dotRef.current = dot;
    ringRef.current = ring;

    dot.className = "synapse-cursor-dot pointer-events-none";
    ring.className = "synapse-cursor-ring pointer-events-none";

    document.body.appendChild(ring);
    document.body.appendChild(dot);

    let x = window.innerWidth / 2;
    let y = window.innerHeight / 2;
    let rx = x;
    let ry = y;

    const lerp = (a: number, b: number, n: number) => a + (b - a) * n;

    const setPos = (el: HTMLDivElement, px: number, py: number, scale = 1) => {
      el.style.transform = `translate3d(${px}px, ${py}px, 0) scale(${scale})`;
    };

    const update = () => {
      rx = lerp(rx, x, 0.18);
      ry = lerp(ry, y, 0.18);
      if (dotRef.current) setPos(dotRef.current, x, y);
      if (ringRef.current) setPos(ringRef.current, rx, ry);
      rafRef.current = requestAnimationFrame(update);
    };
    rafRef.current = requestAnimationFrame(update);

    const onMove = (e: MouseEvent) => {
      x = e.clientX;
      y = e.clientY;

      const target = e.target as HTMLElement | null;
      const clickable =
        !!target &&
        (target.closest("a, button, [role='button'], .btn, .link, .clickable") ||
          target.tagName === "A" ||
          target.tagName === "BUTTON");

      if (ringRef.current) {
        ringRef.current.classList.toggle("is-clickable", !!clickable);
      }
    };

    const onDown = () => {
      ringRef.current?.classList.add("is-down");
      dotRef.current?.classList.add("is-down");
    };
    const onUp = () => {
      ringRef.current?.classList.remove("is-down");
      dotRef.current?.classList.remove("is-down");
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    window.addEventListener("mousedown", onDown);
    window.addEventListener("mouseup", onUp);

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mousedown", onDown);
      window.removeEventListener("mouseup", onUp);
      dot.remove();
      ring.remove();
    };
  }, []);

  return null;
}
