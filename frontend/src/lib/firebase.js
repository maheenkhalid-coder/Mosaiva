import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: "mosaiva.firebaseapp.com",
  projectId: "mosaiva",
  storageBucket: "mosaiva.firebasestorage.app",
  messagingSenderId: "742159876588",
  appId: "1:742159876588:web:89de87a31ed6d1327380c9",
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({ prompt: "select_account" });