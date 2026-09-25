import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import * as api from "../lib/api.js";

// Same helper as SlotsPage. Duplicated rather than shared because it's two
// lines used in two places; worth extracting if a third page needs it.
function formatTime(value) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatRange(slot) {
  return `${formatTime(slot.start_time)} – ${formatTime(slot.end_time)}`;
}

export default function BookPage() {
  const { token } = useAuth();

  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  // ID of the slot whose booking request is in flight, or null.
  const [bookingId, setBookingId] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  async function loadSlots() {
    setLoadError(null);
    try {
      setSlots(await api.fetchOpenSlots(token));
    } catch (err) {
      setLoadError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSlots();
  }, [token]);

  async function handleBook(slot) {
    setError(null);
    setSuccess(null);
    setBookingId(slot.id);
    try {
      await api.createBooking(token, slot.id);
      setSlots((prev) => prev.filter((s) => s.id !== slot.id));
      setSuccess(`Booked: ${formatRange(slot)}`);
    } catch (err) {
      if (err.status === 409) {
        // Another client booked this slot after our list loaded. The DB unique
        // constraint on bookings.slot_id rejected our insert, so reload the
        // list to drop the stale slot.
        setError("This slot was just booked by someone else.");
        await loadSlots();
      } else {
        setError(err.message);
      }
    } finally {
      setBookingId(null);
    }
  }

  return (
    <div className="page page-wide">
      <h1>Book an appointment</h1>

      {success && <p className="success">{success}</p>}
      {error && <p className="error">{error}</p>}

      {loading && <p>Loading...</p>}
      {loadError && <p className="error">{loadError}</p>}
      {!loading && !loadError && slots.length === 0 && (
        <p>No open slots right now.</p>
      )}
      {slots.length > 0 && (
        <ul className="slot-list">
          {slots.map((slot) => (
            <li key={slot.id} className="slot-row">
              <span>{formatRange(slot)}</span>
              <button
                type="button"
                className="button-small"
                disabled={bookingId !== null}
                onClick={() => handleBook(slot)}
              >
                {bookingId === slot.id ? "Booking..." : "Book"}
              </button>
            </li>
          ))}
        </ul>
      )}

      <p className="field-hint">
        <Link to="/my-bookings">My bookings</Link>
        {" · "}
        <Link to="/dashboard">Back to dashboard</Link>
      </p>
    </div>
  );
}
