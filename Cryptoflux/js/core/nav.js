/**
 * Set the active navigation link based on current page
 */
export function setActiveNav() {
    const currentPage = document.body.dataset.page;

    if (!currentPage) {
        console.warn("No data-page attribute found on body");
        return;
    }

    document.querySelectorAll(".nav-links a").forEach((link) => {
        if (link.dataset.page === currentPage) {
            link.classList.add("active");
        } else {
            link.classList.remove("active");
        }
    });
}
