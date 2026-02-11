import { DOM_IDS } from "../core/constants.js";

/**
 * Initialize mobile menu functionality
 */
export function initHeaderMenu() {
  const menuBtn = document.getElementById(DOM_IDS.MENU_TOGGLE);
  const navLinks = document.querySelector(".nav-links");

  if (!menuBtn || !navLinks) {
    console.warn("Menu toggle or nav-links not found");
    return;
  }

  menuBtn.addEventListener("click", () => {
    navLinks.classList.toggle("show");
  });
}
