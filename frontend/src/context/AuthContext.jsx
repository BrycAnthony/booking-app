import { createContext, useContext, useEffect, useState } from "react";
import * as api from "../lib/api.js";

const AuthContext = createContext(null);

// The JWT is saved to localStorage so a page refresh keeps you logged in.
// Tradeoff: any script running on this page (e.g. via an XSS bug) could read
// it. The safer alternative, an httpOnly cookie, doesn't work reliably here:
// the frontend (vercel.app) and API (onrender.com) are different sites, and
// browsers increasingly block cross-site cookies. Tokens expire after 30
// minutes (ACCESS_TOKEN_EXPIRE_MINUTES), which limits the damage if one leaks.
const TOKEN_KEY = "booking_app_token";

// localStorage can throw (e.g. blocked storage in some private-browsing
// modes), so every access is wrapped — the app then just behaves like it did
// before persistence: logged out after a refresh.
function readStoredToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

function writeStoredToken(token) {
  try {
    if (token) {
      localStorage.setItem(TOKEN_KEY, token);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  } catch {
    // Ignore — persistence is a convenience, not a requirement.
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);
  // True while we check a saved token on first load. Protected pages wait on
  // this instead of redirecting to /login before the check finishes.
  const [restoring, setRestoring] = useState(() => readStoredToken() !== null);

  useEffect(() => {
    const saved = readStoredToken();
    if (!saved) {
      return;
    }
    // Only the token is saved, not the user: re-fetching /users/me confirms the
    // token is still valid and picks up the current role from the database.
    api
      .fetchMe(saved)
      .then((me) => {
        setToken(saved);
        setUser(me);
      })
      .catch((err) => {
        // 401 means expired or invalid, so forget it. Other failures (e.g. the
        // API is cold-starting or unreachable) keep it so a later refresh can
        // retry; the user just sees the login page for now.
        if (err.status === 401) {
          writeStoredToken(null);
        }
      })
      .finally(() => setRestoring(false));
  }, []);

  async function login(email, password) {
    const { access_token } = await api.login({ email, password });
    // Fetch the profile before committing any state, so we never end up
    // with a token set but no user (e.g. if /users/me unexpectedly fails).
    const me = await api.fetchMe(access_token);
    writeStoredToken(access_token);
    setToken(access_token);
    setUser(me);
  }

  function logout() {
    writeStoredToken(null);
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, restoring, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (ctx === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}
