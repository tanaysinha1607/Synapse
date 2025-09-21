// src/hooks/use-auth.ts
import { useEffect, useState } from "react";

export function useAuth() {
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(true); // Assume logged in
  const [user, setUser] = useState<{ id: string; name: string } | null>({
    id: "demo-user",
    name: "Amardeep",
  });

  useEffect(() => {
    // In future: fetch real auth status from backend
    // For now: mock auth is always ready
    setIsLoading(false);
  }, []);

  function signIn() {
    // TODO: Hook up to backend /auth later
    setIsAuthenticated(true);
    setUser({ id: "demo-user", name: "Amardeep" });
  }

  function signOut() {
    setIsAuthenticated(false);
    setUser(null);
  }

  return {
    isLoading,
    isAuthenticated,
    user,
    signIn,
    signOut,
  };
}
