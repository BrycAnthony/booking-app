import { createContext, useContext, useState } from "react";
import * as api from "../lib/api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  // Token and user live only in React state — never persisted to
  // localStorage/sessionStorage, so a page refresh clears the session.
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  async function login(email, password) {
    const { access_token } = await api.login({ email, password });
    // Fetch the profile before committing any state, so we never end up
    // with a token set but no user (e.g. if /users/me unexpectedly fails).
    const me = await api.fetchMe(access_token);
    setToken(access_token);
    setUser(me);
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
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
