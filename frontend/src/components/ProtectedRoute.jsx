import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

// `role` is optional: when set, logged-in users with a different role are sent
// back to the dashboard. This is only a UX convenience — the backend enforces
// roles itself (403), so hiding a page here is not what keeps data safe.
export default function ProtectedRoute({ role, children }) {
  const { token, user } = useAuth();
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
