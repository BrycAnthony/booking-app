import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import * as api from "../lib/api.js";

// Timezone note: <input type="datetime-local"> produces a naive local time like
// "2026-10-01T09:00", and the DB column is a naive `timestamp`. We send and
// display those values as-is, so times are always in the provider's own local
// time. That's fine for a single-timezone app; supporting clients in other
// timezones would mean switching to `timestamptz` and converting to UTC.
function formatTime(value) {
  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function byStartTime(a, b) {
  return new Date(a.start_time) - new Date(b.start_time);
}

export default function SlotsPage() {
  const { token } = useAuth();

  const [slots, setSlots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState(null);

  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    api
      .fetchMySlots(token)
      .then(setSlots)
      .catch((err) => setLoadError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      // No client-side "end after start" check on purpose: the API validates it
      // and returns a readable message, which we show below the form.
      const slot = await api.createSlot(token, {
        start_time: startTime,
        end_time: endTime,
      });
      setSlots((prev) => [...prev, slot].sort(byStartTime));
      setStartTime("");
      setEndTime("");
    } catch (err) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page-wide">
      <h1>My availability</h1>

      <form onSubmit={handleSubmit}>
        <label>
          Start
          <input
            type="datetime-local"
            required
            value={startTime}
            onChange={(e) => setStartTime(e.target.value)}
          />
        </label>
        <label>
          End
          <input
            type="datetime-local"
            required
            value={endTime}
            onChange={(e) => setEndTime(e.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" disabled={submitting}>
          {submitting ? "Creating..." : "Create slot"}
        </button>
      </form>

      <h2>Your slots</h2>
      {loading && <p>Loading...</p>}
      {loadError && <p className="error">{loadError}</p>}
      {!loading && !loadError && slots.length === 0 && <p>No slots yet.</p>}
      {slots.length > 0 && (
        <ul className="slot-list">
          {slots.map((slot) => (
            <li key={slot.id}>
              {formatTime(slot.start_time)} – {formatTime(slot.end_time)}
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
