// ===== Finance Tracker — Storage Module =====
// All localStorage utility functions for transactions and settings.

// ───── Transactions ─────

function getTransactions() {
  return JSON.parse(localStorage.getItem("ft_transactions") || "[]");
}

function addTransaction(tx) {
  const transactions = getTransactions();
  tx.id = Date.now().toString() + Math.random().toString(36).substring(2, 6);
  transactions.push(tx);
  localStorage.setItem("ft_transactions", JSON.stringify(transactions));
  return tx;
}

function deleteTransaction(id) {
  const transactions = getTransactions().filter((t) => t.id !== id);
  localStorage.setItem("ft_transactions", JSON.stringify(transactions));
}

function clearTransactions() {
  localStorage.removeItem("ft_transactions");
}

// ───── Computed Values ─────

function getBalance() {
  return getTotalIncome() - getTotalExpenses();
}

function getTotalIncome() {
  return getTransactions()
    .filter((t) => t.type === "income")
    .reduce((sum, t) => sum + Number(t.amount), 0);
}

function getTotalExpenses() {
  return getTransactions()
    .filter((t) => t.type === "expense")
    .reduce((sum, t) => sum + Number(t.amount), 0);
}

function getCategoryTotals() {
  return getTransactions()
    .filter((t) => t.type === "expense")
    .reduce((acc, t) => {
      const cat = t.category || "Other";
      acc[cat] = (acc[cat] || 0) + Number(t.amount);
      return acc;
    }, {});
}

// ───── Settings ─────

function getSettings() {
  const defaults = { budget: 5000, currency: "₹", darkMode: true };
  const saved = JSON.parse(localStorage.getItem("ft_settings") || "null");
  return saved ? { ...defaults, ...saved } : defaults;
}

function saveSettings(settings) {
  localStorage.setItem("ft_settings", JSON.stringify(settings));
}

// ───── Theme Initialization ─────
// Call this on every page to apply the saved theme
function initTheme() {
  const settings = getSettings();
  if (!settings.darkMode) {
    document.documentElement.setAttribute("data-theme", "light");
  } else {
    document.documentElement.removeAttribute("data-theme");
  }
}

// ───── Currency Formatter ─────
function formatCurrency(amount) {
  const settings = getSettings();
  const symbol = settings.currency || "₹";
  return `${symbol}${Number(amount).toLocaleString("en-IN")}`;
}

// Auto-init theme on load
document.addEventListener("DOMContentLoaded", initTheme);
