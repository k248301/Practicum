import { loadLayout } from "./core/layoutLoader.js";
import { setActiveNav } from "./core/nav.js";
import { initHeaderMenu } from "./ui/headerMenu.js";
import { initAuth } from "./core/auth.js";

/**
 * Initialize page - Entry point for all pages
 */
async function initPage() {
    try {
        console.log("Initializing page...");

        // Load header and footer
        await loadLayout();

        // Initialize header menu (mobile toggle)
        initHeaderMenu();

        // Set active navigation link
        setActiveNav();

        // Initialize authentication (logout button)
        initAuth();

        console.log("Page initialization complete");
    } catch (error) {
        console.error("Page initialization failed:", error);
        // Still show error but don't break the page
        const errorDiv = document.createElement("div");
        errorDiv.style.cssText =
            "background: #ffebee; color: #c62828; padding: 16px; margin: 16px; border-radius: 4px;";
        errorDiv.textContent =
            "Failed to load page components. Some features may not work correctly.";
        document.body.insertBefore(errorDiv, document.body.firstChild);
    }
}

// Initialize page when DOM is ready
if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initPage);
} else {
    initPage();
}
