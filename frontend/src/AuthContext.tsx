import { createContext, useContext, useState, type ReactNode } from "react";
import { loginWithGoogle as apiLoginWithGoogle, logout as apiLogout, currentUser } from "@/lib/api";

type User = { id: string; name: string; email: string };

type AuthState = {
  user: User | null;
  loading: boolean;
  error: string | null;
  loginWithGoogle: (credential: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(currentUser());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function loginWithGoogle(credential: string) {
    setLoading(true);
    setError(null);
    try {
      const u = await apiLoginWithGoogle(credential);
      setUser(u);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not sign in with Google");
      throw e;
    } finally {
      setLoading(false);
    }
  }

  function logout() {
    apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, loginWithGoogle, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
