import { CHART_COLORS, TIMEFRAME } from "../core/constants.js";
import { profitHistoryStore } from "../store/profitHistoryStore.js";

/**
 * Profit Chart - Manages Chart.js instances for profit visualization
 */
class ProfitChart {
  constructor() {
    this.chartInstance = null;
    this.currentTicket = null;
    this.currentTimeframe = TIMEFRAME.ALL;
  }

  /**
   * Create a new chart instance
   * @param {string} canvasId - Canvas element ID
   * @param {string} ticket - Trade ticket
   */
  createChart(canvasId, ticket) {
    this.currentTicket = ticket;

    const canvas = document.getElementById(canvasId);
    if (!canvas) {
      console.error(`Canvas ${canvasId} not found`);
      return;
    }

    const ctx = canvas.getContext("2d");

    // Destroy existing chart if any
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }

    this.chartInstance = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          {
            label: "Profit",
            data: [],
            borderColor: CHART_COLORS.PROFIT,
            borderWidth: 2,
            fill: false,
            tension: 0.1,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        plugins: {
          legend: {
            display: true,
            position: "top",
          },
          tooltip: {
            enabled: true,
            mode: "index",
            intersect: false,
          },
          zoom: {
            pan: {
              enabled: true,
              mode: "x",
            },
            zoom: {
              wheel: {
                enabled: true,
              },
              pinch: {
                enabled: true,
              },
              mode: "x",
            },
          },
        },
        scales: {
          x: {
            title: {
              display: true,
              text: "Time",
            },
            ticks: {
              maxRotation: 45,
              minRotation: 0,
            },
          },
          y: {
            title: {
              display: true,
              text: "Profit",
            },
            beginAtZero: true,
          },
        },
      },
    });

    // Initial update
    this.updateChart(ticket, this.currentTimeframe);

    // Subscribe to profit updates
    profitHistoryStore.subscribe(ticket, () => {
      this.updateChart(ticket, this.currentTimeframe);
    });
  }

  /**
   * Update chart with new data
   * @param {string} ticket - Trade ticket
   * @param {number} timeframe - Timeframe in minutes (0 = all)
   */
  updateChart(ticket, timeframe = TIMEFRAME.ALL) {
    if (!this.chartInstance) {
      console.warn("Chart not initialized");
      return;
    }

    this.currentTimeframe = timeframe;

    const history = profitHistoryStore.getHistory(ticket, timeframe);

    this.chartInstance.data.labels = history.map((point) =>
      point.time.toLocaleTimeString(),
    );
    this.chartInstance.data.datasets[0].data = history.map(
      (point) => point.profit,
    );

    this.chartInstance.update("none"); // No animation for performance
  }

  /**
   * Set timeframe and update chart
   * @param {number} minutes - Timeframe in minutes
   */
  setTimeframe(minutes) {
    if (this.currentTicket) {
      this.updateChart(this.currentTicket, minutes);
    }
  }

  /**
   * Destroy chart instance
   */
  destroy() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
      this.chartInstance = null;
    }
    this.currentTicket = null;
  }
}

// Export singleton instance
export const profitChart = new ProfitChart();
