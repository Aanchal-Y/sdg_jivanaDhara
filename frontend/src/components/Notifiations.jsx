import React from "react";
import { useAppContext } from "../context/AppContext";

export default function Notifications() {
  const { state } = useAppContext();

  return (
    <div className="fixed top-4 right-4 space-y-2">
      {state.notifications.map((notif, idx) => (
        <div
          key={idx}
          className={`p-3 rounded-lg shadow-md ${
            notif.type === "success" ? "bg-green-500/80" : "bg-red-500/80"
          } text-white`}
        >
          {notif.message}
        </div>
      ))}
    </div>
  );
}
