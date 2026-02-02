import { initializeApp } from "https://www.gstatic.com/firebasejs/9.4.0/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged,
  signOut,
} from "https://www.gstatic.com/firebasejs/9.4.0/firebase-auth.js";

// ----------------------
// 🔥 Firebase Config
// ----------------------
const firebaseConfig = {
  apiKey: "AIzaSyBoLsSmfgx3co6HOCWpEMY7lfWAgX-z5Z4",
  authDomain: "talkgenius-77644.firebaseapp.com",
  projectId: "talkgenius-77644",
  storageBucket: "talkgenius-77644.appspot.com",
  messagingSenderId: "639644293009",
  appId: "1:639644293009:web:f82cf6661d2f9f552f2c30",
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

// ----------------------------
// 🔹 DOM Elements
// ----------------------------
const loginForm = document.getElementById("login-form");
const signupForm = document.getElementById("signup-form");
const logoutButton = document.getElementById("logout-button");

// ----------------------------
// 🔹 Signup Handler
// ----------------------------
if (signupForm) {
  signupForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = document.querySelector(".up-email").value;
    const password = document.querySelector(".up-password").value;
    const confirmPassword = document.querySelector(
      ".up-confirm-password"
    ).value;

    // 🔹 Check if passwords match
    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    createUserWithEmailAndPassword(auth, email, password)
      .then(() => {
        // Redirect to login page instead of home
        window.location.href = "index.html";
      })
      .catch((error) => {
        alert(error.message);
        console.error(error);
      });
  });
}

// ----------------------------
// 🔹 Login Handler
// ----------------------------
if (loginForm) {
  loginForm.addEventListener("submit", (e) => {
    e.preventDefault();

    const email = document.querySelector(".in-email").value;
    const password = document.querySelector(".in-password").value;

    signInWithEmailAndPassword(auth, email, password)
      .then(() => {
        window.location.href = "home.html";
      })
      .catch((error) => {
        alert(error.message);
        console.error(error);
      });
  });
}

// ----------------------------
// 🔹 Logout Handler
// ----------------------------
if (logoutButton) {
  logoutButton.addEventListener("click", () => {
    signOut(auth)
      .then(() => {
        window.location.href = "index.html";
      })
      .catch((error) => {
        console.error("Sign out error:", error);
      });
  });
}

// ------------------------------------------------
// 🔥 FIXED AUTH STATE CHECK (NO MORE RELOAD LOOP)
// ------------------------------------------------
function checkAuth() {
  console.log("Checking authentication state...");

  onAuthStateChanged(auth, (user) => {
    const path = window.location.pathname;

    // Pages considered as login page:
    const onLoginPage =
      path.endsWith("index.html") ||
      path === "/" ||
      path === "" ||
      path.includes("index");

    // ----------------------------------------------
    // No user → allow login page, block all others
    // ----------------------------------------------
    if (!user && onLoginPage) {
      console.log("Not logged in — staying on login page");
      return;
    }

    if (!user && !onLoginPage) {
      console.log("Not logged in — redirect → index.html");
      window.location.href = "index.html";
      return;
    }

    // ----------------------------------------------
    // User logged in → block login page
    // ----------------------------------------------
    if (user && onLoginPage) {
      console.log("Logged in — redirect → home.html");
      window.location.href = "home.html";
      return;
    }

    console.log("User authenticated — staying on this page.");
  });
}

window.onload = checkAuth;
