import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

// `role` is optional: when set, logged-in users with a different role are sent
// back to the dashboard. This is only a UX convenience — the backend enforces
// roles itself (403), so hiding a page here is not what keeps data safe.
export default function ProtectedRoute({ role, children }) {
  const { token, user, restoring } = useAuth();
  // Still checking a saved token from a previous visit. Redirecting now would
  // bounce a logged-in user to /login on every refresh. This can take up to a
  // minute if the Render API is waking up from free-tier spin-down.
  if (restoring) {
    return (
      <div className="page">
        <p>Loading...</p>
      </div>
    );
  }
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  if (role && user.role !== role) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}
