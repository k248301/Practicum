import { newsService } from "../services/newsService.js";
import { showError, showSuccess } from "../ui/toast.js";

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
     * Load and display news articles
     */
    async loadNews() {
        try {
            const articles = await newsService.fetchNews();
            const filtered = newsService.filterValidArticles(articles);

            if (filtered.length === 0) {
                showError("No news articles available");
                return;
            }

            // Display top news (main + side articles)
            this.displayTopNews(filtered.slice(0, 4));

            // Display slider articles
            this.displaySlider(filtered.slice(4));

            showSuccess("News loaded successfully");
        } catch (error) {
            showError(error.message || "Failed to load news");
            console.error("News loading error:", error);
        }
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
