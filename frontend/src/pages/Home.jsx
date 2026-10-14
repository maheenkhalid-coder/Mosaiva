import { useEffect, useState } from "react";
import { signInWithPopup, signOut } from "firebase/auth";
import { FcGoogle } from "react-icons/fc";

import { auth, googleProvider } from "../lib/firebase";
import api from "../lib/axios";
import getCurrentUser from "../features/auth/getCurrentUser";


function toUiUser(data) {
  return {
    displayName: data.displayName ?? data.name,
    email: data.email,
    photoURL: data.photoURL ?? data.avatar,
    uid: data.uid ?? data.firebase_uid,
  };
}

function Home() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getCurrentUser()
        .then((data) => {
        console.log("Current user from session:", data);
        setUser(toUiUser(data));
        })
        .catch(() => setUser(null));
  }, []);

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const result = await signInWithPopup(auth, googleProvider);
      console.log("Firebase user:", result.user);

      const token = await result.user.getIdToken();
      const response = await api.post("/auth/login", { token });

      console.log("Backend user:", response.data);
      setUser(toUiUser(response.data));

    } catch (err) {
      console.error("Login failed:", err);
      setError("Could not sign in. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    setLoading(true);
    setError("");

    try {
      await api.post("/auth/logout");
      await signOut(auth);
      setUser(null);
    } catch (err) {
      console.error("Logout failed:", err);
      setError("Could not log out. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <section className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center shadow-xl">
        <h1 className="text-3xl font-bold">Welcome to Mosaiva</h1>

        {user ? (
          <>
            <p className="mt-3 text-slate-300">
              You’re signed in as {user.displayName || user.email}.
            </p>

            {user.photoURL && (
              <img
                src={user.photoURL}
                alt="Your profile"
                className="mx-auto mt-6 h-16 w-16 rounded-full"
              />
            )}

            <button
              type="button"
              onClick={handleLogout}
              disabled={loading}
              className="mt-6 w-full rounded-lg bg-slate-700 px-4 py-3 font-semibold hover:bg-slate-600 disabled:opacity-60"
            >
              {loading ? "Please wait..." : "Log out"}
            </button>
          </>
        ) : (
          <>
            <p className="mt-3 text-slate-300">
              Please log in to continue with the app
            </p>

            <button
              type="button"
              onClick={handleLogin}
              disabled={loading}
              className="mt-8 flex w-full items-center justify-center gap-3 rounded-lg bg-white px-4 py-3 font-semibold text-slate-900 hover:bg-slate-100 disabled:opacity-60"
            >
              <FcGoogle size={24} />
              {loading ? "Please wait..." : "Continue with Google"}
            </button>
          </>
        )}

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      </section>
    </main>
  );
}

export default Home;