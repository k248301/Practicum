import { DOM_IDS } from "./constants.js";

// Note: This file expects firebase to be initialized in firebase-script.js
// We import auth from there when available

/**
 * Initialize authentication (logout button)
 */
export function initAuth() {
  const logoutBtn = document.getElementById(DOM_IDS.LOGOUT_BUTTON);

  if (!logoutBtn) {
    console.warn("Logout button not found");
    return;
  }

  logoutBtn.addEventListener("click", async () => {
    try {
      // Access firebase auth from global scope if available
      if (window.auth) {
        await window.auth.signOut();
      }
      window.location.href = "index.html";
    } catch (error) {
      console.error("Logout failed:", error);
      // Still redirect on error
      window.location.href = "index.html";
    }
  });
}
