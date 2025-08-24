import React from "react";
import { useGoogleLogin } from "@react-oauth/google";
import axios from "axios";
import { useAppContext } from "../context/AppContext";

export default function Navbar() {
  const { state, dispatch } = useAppContext();

  const login = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        const res = await axios.post("http://localhost:5000/api/auth/google", {
          token: tokenResponse.credential || tokenResponse.access_token
        });

        dispatch({ type: "LOGIN", payload: res.data });
        dispatch({ type: "ADD_NOTIFICATION", payload: { type: "success", message: "Login successful!" } });
      } catch (err) {
        dispatch({ type: "ADD_NOTIFICATION", payload: { type: "error", message: "Login failed" } });
      }
    }
  });

  return (
    <nav className="flex justify-between items-center p-4 bg-gray-900 text-white">
      <h1 className="text-xl font-bold">SDG Impact Platform</h1>
      {state.user ? (
        <span>Welcome, {state.user.name}</span>
      ) : (
        <button onClick={() => login()} className="bg-blue-500 px-4 py-2 rounded-lg">
          Sign in with Google
        </button>
      )}
    </nav>
  );
}
