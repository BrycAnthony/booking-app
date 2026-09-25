import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function DashboardPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <div className="page">
      <h1>Dashboard</h1>
      <p>Logged in as {user.email}</p>
      <p>Role: {user.role}</p>
      {user.role === "provider" && (
        <p>
          <Link to="/slots">Manage availability</Link>
        </p>
      )}
      {user.role === "client" && (
        <p>
          <Link to="/book">Book an appointment</Link>
        </p>
      )}
      <button type="button" onClick={handleLogout}>
        Log out
      </button>
    </div>
  );
}
