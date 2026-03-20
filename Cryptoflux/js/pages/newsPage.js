import { newsService } from "../services/newsService.js";
import { showError, showSuccess, showWarning, showToast } from "../ui/toast.js";

/**
 * News Page Controller
 */
class NewsPage {
    constructor() {
        this.initialized = false;
    }

    /**
     * Initialize the news page
     */
    async initialize() {
        if (this.initialized) return;

        try {
            console.log("Initializing news page...");

            // Fetch and display news
            await this.loadNews();

            this.initialized = true;
            console.log("News page initialized successfully");
        } catch (error) {
            console.error("Failed to initialize news page:", error);
            showError("Failed to load news. Please refresh.");
        }
    }

    /**
     * Load and display news articles with retry logic
     */
    async loadNews(retryCount = 0) {
        const MAX_RETRIES = 3;
        const RETRY_DELAY = 2000;

        try {
            // Show skeleton loader on first attempt
            if (retryCount === 0) {
                this.showSkeletonLoader();
            }

            console.log(`Loading news (Attempt ${retryCount + 1})...`);
            const articles = await newsService.fetchNews();
            const filtered = newsService.filterValidArticles(articles);

            if (filtered.length === 0) {
                throw new Error("No valid news articles available");
            }

            // Display top news (main + side articles)
            this.displayTopNews(filtered.slice(0, 4));

            // Display slider articles
            this.displaySlider(filtered.slice(4));

            if (retryCount > 0) {
                showSuccess("News loaded successfully after retry");
            }
        } catch (error) {
            console.error(`News loading error (Attempt ${retryCount + 1}):`, error);

            if (retryCount < MAX_RETRIES) {
                const remaining = MAX_RETRIES - retryCount;
                showToast(`News load failed. Retrying in 3s... (${remaining} left)`, "warning", 2500);
                
                // Wait for retry delay
                await new Promise(r => setTimeout(r, RETRY_DELAY));
                return this.loadNews(retryCount + 1);
            }

            showError(error.message || "Failed to load news after multiple attempts");
            this.clearContainers(); // Clear skeleton if final attempt fails
        }
    }

    /**
     * Show skeleton loader placeholders
     */
    showSkeletonLoader() {
        const mainArticleEl = document.getElementById("mainArticle");
        const sideArticlesEl = document.getElementById("sideArticles");
        const slider = document.getElementById("slider");

        if (mainArticleEl) {
            mainArticleEl.innerHTML = `
                <div class="main-article">
                    <div class="skeleton skeleton-main"></div>
                    <div class="overlay">
                        <div class="skeleton skeleton-title"></div>
                        <div class="skeleton skeleton-text"></div>
                    </div>
                </div>
            `;
        }

        if (sideArticlesEl) {
            sideArticlesEl.innerHTML = Array(3).fill(0).map(() => `
                <div class="side-article">
                    <div class="skeleton" style="width: 100px; height: 80px;"></div>
                    <div class="content" style="flex: 1;">
                        <div class="skeleton skeleton-title" style="width: 80%;"></div>
                        <div class="skeleton skeleton-text" style="width: 60%; margin-top: 10px;"></div>
                    </div>
                </div>
            `).join("");
        }

        if (slider) {
            slider.innerHTML = Array(6).fill(0).map(() => `
                <div class="slide">
                    <div class="skeleton" style="height: 150px;"></div>
                    <div class="slide-content">
                        <div class="skeleton skeleton-title" style="width: 70%;"></div>
                        <div class="skeleton skeleton-text" style="width: 90%; margin-top: 10px;"></div>
                    </div>
                </div>
            `).join("");
        }
    }

    /**
     * Clear news containers (e.g., if loading fails completely)
     */
    clearContainers() {
        const els = ["mainArticle", "sideArticles", "slider"];
        els.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.innerHTML = "";
        });
    }

    /**
     * Display top news section
     * @param {Array} articles - Articles to display
     */
    displayTopNews(articles) {
        if (!articles || articles.length === 0) return;

        const main = articles[0];
        const sides = articles.slice(1);

        // Truncate main content
        let mainContent = main.content || "";
        if (mainContent.length > 150) {
            mainContent = mainContent.substring(0, 150) + "...";
        }

        const mainArticleEl = document.getElementById("mainArticle");
        if (mainArticleEl) {
            mainArticleEl.innerHTML = `
        <div onclick="window.open('${main.url}', '_blank')" style="cursor:pointer;">
          <img src="${main.urlToImage}" alt="Main Article">
          <div class="overlay">
            <h2>${main.title}</h2>
            <p>${mainContent}</p>
          </div>
        </div>
      `;
        }

        const sideArticlesEl = document.getElementById("sideArticles");
        if (sideArticlesEl) {
            sideArticlesEl.innerHTML = sides
                .map((a) => {
                    let sideContent = a.content || "";
                    if (sideContent.length > 80) {
                        sideContent = sideContent.substring(0, 80) + "...";
                    }

                    return `
            <div class="side-article" onclick="window.open('${a.url}', '_blank')" style="cursor:pointer;">
              <img src="${a.urlToImage}" alt="">
              <div class="content">
                <h4>${a.title}</h4>
                <p>${sideContent}</p>
              </div>
            </div>
          `;
                })
                .join("");
        }
    }

    /**
     * Display slider articles
     * @param {Array} articles - Articles to display
     */
    displaySlider(articles) {
        const slider = document.getElementById("slider");
        if (!slider) return;

        slider.innerHTML = articles
            .map((a) => {
                let content = a.content || "";
                if (content.length > 100) {
                    content = content.substring(0, 100) + "...";
                }

                return `
          <div class="slide" onclick="window.open('${a.url}', '_blank')" style="cursor:pointer;">
            <img src="${a.urlToImage}" alt="">
            <div class="slide-content">
              <h5>${a.title}</h5>
              <p>${content}</p>
            </div>
          </div>
        `;
            })
            .join("");
    }

    /**
     * Scroll slider
     * @param {number} direction - -1 for left, 1 for right
     */
    scrollSlider(direction) {
        const slider = document.getElementById("slider");
        if (!slider) return;

        const scrollAmount = 300 * direction;
        slider.scrollBy({ left: scrollAmount, behavior: "smooth" });
    }
}

// Make scrollSlider available globally for onclick handlers
window.scrollSlider = function (direction) {
    newsPage.scrollSlider(direction);
};

// Initialize page
const newsPage = new NewsPage();
newsPage.initialize();
