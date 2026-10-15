import { useEffect, useState } from "react";
import { signInWithPopup } from "firebase/auth";
import { FcGoogle } from "react-icons/fc";
import { useDispatch, useSelector } from "react-redux";

import { auth, googleProvider } from "../lib/firebase";
import api from "../lib/axios";
import getCurrentUser from "../features/auth/getCurrentUser";
import { setUserData, clearUserData } from "../redux/userSlice";

function toUiUser(data) {
  return {
    displayName: data.displayName ?? data.name,
    email: data.email,
    photoURL: data.photoURL ?? data.avatar,
    uid: data.uid ?? data.firebase_uid,
  };
}

function Home() {
  const dispatch = useDispatch();
  const userData = useSelector((state) => state.user.userData);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    getCurrentUser()
      .then((data) => dispatch(setUserData(toUiUser(data))))
      .catch(() => dispatch(clearUserData()))
      .finally(() => setCheckingSession(false));
  }, [dispatch]);

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      const response = await api.post("/auth/login", { token });

      dispatch(setUserData(toUiUser(response.data)));
    } catch (err) {
      console.error("Login failed:", err.response?.status, err.response?.data);
      setError(
        err.response?.data?.detail || "Could not sign in. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  if (checkingSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-slate-300">
        
      </main>
    );
  }

  if (userData) {
    return <main className="min-h-screen bg-black" />;
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-white">
      <section className="w-full max-w-md rounded-2xl border border-slate-800 bg-slate-900 p-8 text-center shadow-xl">
        <h1 className="text-3xl font-bold">Welcome to Mosaiva</h1>
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

        {error && <p className="mt-4 text-sm text-red-400">{error}</p>}
      </section>
    </main>
  );
}

export default Home;