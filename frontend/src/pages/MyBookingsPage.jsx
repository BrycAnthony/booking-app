import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import * as api from "../lib/api.js";

// Same helpers as BookPage/SlotsPage. Now used on three pages, so these are
// a good candidate to move into a shared lib/format.js.
function formatTime(value) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatRange(slot) {
  return `${formatTime(slot.start_time)} – ${formatTime(slot.end_time)}`;
}

export default function MyBookingsPage() {
  const { token } = useAuth();

  const [bookings, setBookings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  // ID of the booking whose cancel request is in flight, or null.
  const [cancellingId, setCancellingId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    api
      .fetchMyBookings(token)
      .then(setBookings)
      .catch((err) => setLoadError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleCancel(booking) {
    // Cancelling frees the slot for anyone else to book, so ask first.
    if (!window.confirm(`Cancel your booking for ${formatRange(booking.slot)}?`)) {
      return;
    }
    setError(null);
    setSuccess(null);
    setCancellingId(booking.id);
    try {
      await api.cancelBooking(token, booking.id);
      setBookings((prev) => prev.filter((b) => b.id !== booking.id));
      setSuccess(`Cancelled: ${formatRange(booking.slot)}`);
    } catch (err) {
      setError(err.message);
    } finally {
      setCancellingId(null);
    }
  }

  return (
    <div className="page page-wide">
      <h1>My bookings</h1>

      {success && <p className="success">{success}</p>}
      {error && <p className="error">{error}</p>}

      {loading && <p>Loading...</p>}
      {loadError && <p className="error">{loadError}</p>}
      {!loading && !loadError && bookings.length === 0 && (
        <p>
          You have no bookings. <Link to="/book">Book an appointment</Link>
        </p>
      )}
      {bookings.length > 0 && (
        <ul className="slot-list">
          {bookings.map((booking) => (
            <li key={booking.id} className="slot-row">
              <span>{formatRange(booking.slot)}</span>
              <button
                type="button"
                className="button-small"
                disabled={cancellingId !== null}
                onClick={() => handleCancel(booking)}
              >
                {cancellingId === booking.id ? "Cancelling..." : "Cancel"}
              </button>
            </li>
          ))}
        </ul>
      )}

      <p className="field-hint">
        <Link to="/dashboard">Back to dashboard</Link>
      </p>
    </div>
  );
}
