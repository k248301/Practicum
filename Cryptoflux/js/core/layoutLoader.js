import { DOM_IDS } from "./constants.js";

/**
 * Load header and footer components into the page
 * @returns {Promise<void>}
 */
export async function loadLayout() {
    try {
        // Load header
        const headerHTML = await fetchComponent("components/header.html");
        const headerElement = document.getElementById(DOM_IDS.HEADER);
        if (headerElement) {
            headerElement.innerHTML = headerHTML;
        } else {
            console.warn("Header element not found");
        }

        // Load footer
        const footerHTML = await fetchComponent("components/footer.html");
        const footerElement = document.getElementById(DOM_IDS.FOOTER);
        if (footerElement) {
            footerElement.innerHTML = footerHTML;
        } else {
            console.warn("Footer element not found");
        }
    } catch (error) {
        console.error("Failed to load layout components:", error);
        throw error;
    }
}

/**
 * Fetch a component HTML file
 * @param {string} path - Path to the component file
 * @returns {Promise<string>}
 */
async function fetchComponent(path) {
    try {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.text();
    } catch (error) {
        console.error(`Failed to fetch component: ${path}`, error);
        throw error;
    }
}
