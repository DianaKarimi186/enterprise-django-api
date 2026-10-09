import { useEffect, useMemo, useState } from "react";
import {
  Activity, AlertTriangle, ArrowDownUp, Boxes, Check, ChevronDown, CircleHelp,
  ClipboardList, LayoutDashboard, LogOut, Menu, PackagePlus, Pencil, Plus,
  Search, ShieldCheck, Trash2, TrendingUp, X,
} from "lucide-react";
import { apiRequest, clearTokens, getAccessToken, getMetrics, listCategories, listProducts, login } from "./api.js";

const emptyForm = { name: "", category: "", price: "", stock: "", description: "" };
const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });
const number = new Intl.NumberFormat("en-US");

function LoginScreen({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(username.trim(), password);
      onLogin();
    } catch (err) {
      setError(err.message || "Sign in failed.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-shell">
      <section className="login-card">
        <div className="brand-mark"><Boxes size={25} /></div>
        <p className="eyebrow">ENTERPRISE OPERATIONS</p>
        <h1>Welcome back</h1>
        <p className="muted">Sign in to manage your inventory workspace.</p>
        <form className="login-form" onSubmit={submit}>
          <label>Username<input autoComplete="username" value={username} onChange={e => setUsername(e.target.value)} required placeholder="Enter your username" /></label>
          <label>Password<input type="password" autoComplete="current-password" value={password} onChange={e => setPassword(e.target.value)} required placeholder="Enter your password" /></label>
          {error && <div className="alert error">{error}</div>}
          <button className="primary-button full-button" disabled={busy}>{busy ? "Signing in…" : "Sign in"}<span>→</span></button>
        </form>
        <div className="login-security"><ShieldCheck size={16} /> Secure access powered by Django REST Framework</div>
      </section>
    </main>
  );
}

function MetricCard({ label, value, note, icon: Icon, tone, prefix }) {
  return (
    <article className="metric-card">
      <div className="metric-top"><span>{label}</span><span className={`metric-icon ${tone}`}><Icon size={18} /></span></div>
      <strong>{prefix || ""}{value}</strong>
      <p>{note}</p>
    </article>
  );
}

function ProductDialog({ initial, categories, onClose, onSave, busy, error }) {
  const [form, setForm] = useState(initial || emptyForm);
  const editing = Boolean(initial.id);
  function update(field, value) { setForm(current => ({ ...current, [field]: value })); }
  function submit(event) {
    event.preventDefault();
    onSave({ ...form, category: Number(form.category), price: String(form.price), stock: Number(form.stock) });
  }

  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={event => event.target === event.currentTarget && onClose()}>
      <section className="product-dialog" role="dialog" aria-modal="true" aria-labelledby="product-dialog-title">
        <div className="dialog-heading"><div><p className="eyebrow">{editing ? "INVENTORY ITEM" : "NEW RECORD"}</p><h2 id="product-dialog-title">{editing ? "Edit product" : "Add product"}</h2></div><button className="icon-button" onClick={onClose} aria-label="Close dialog"><X size={20} /></button></div>
        <form className="product-form" onSubmit={submit}>
          <label className="span-two">Product name<input value={form.name} onChange={e => update("name", e.target.value)} required maxLength={255} placeholder="e.g. Dell Latitude 5420" /></label>
          <label>Category<select value={form.category} onChange={e => update("category", e.target.value)} required><option value="">Select category</option>{categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}</select></label>
          <label>Unit price (USD)<input type="number" min="0.01" step="0.01" value={form.price} onChange={e => update("price", e.target.value)} required /></label>
          <label>Stock quantity<input type="number" min="0" step="1" value={form.stock} onChange={e => update("stock", e.target.value)} required /></label>
          <label className="span-two">Description<textarea rows="3" value={form.description || ""} onChange={e => update("description", e.target.value)} placeholder="Add a short product description" /></label>
          {error && <div className="alert error span-two">{error}</div>}
          <div className="dialog-actions span-two"><button type="button" className="secondary-button" onClick={onClose}>Cancel</button><button className="primary-button" disabled={busy}>{busy ? "Saving…" : editing ? "Save changes" : "Create product"}<Check size={16} /></button></div>
        </form>
      </section>
    </div>
  );
}

export default function App() {
  const [authenticated, setAuthenticated] = useState(Boolean(getAccessToken()));
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pageError, setPageError] = useState("");
  const [search, setSearch] = useState("");
  const [stockFilter, setStockFilter] = useState("all");
  const [dialog, setDialog] = useState(null);
  const [saving, setSaving] = useState(false);
  const [dialogError, setDialogError] = useState("");
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  async function loadData() {
    setLoading(true);
    setPageError("");
    try {
      const [productRows, categoryRows, dashboardMetrics] = await Promise.all([listProducts(), listCategories(), getMetrics()]);
      setProducts(productRows);
      setCategories(categoryRows);
      setMetrics(dashboardMetrics);
    } catch (err) {
      setPageError(err.message || "Could not load inventory data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    const unauthorized = () => setAuthenticated(false);
    window.addEventListener("inventory:unauthorized", unauthorized);
    return () => window.removeEventListener("inventory:unauthorized", unauthorized);
  }, []);

  useEffect(() => { if (authenticated) loadData(); }, [authenticated]);

  const filteredProducts = useMemo(() => {
    const query = search.trim().toLowerCase();
    return products.filter(product => {
      const matchesSearch = !query || [product.name, product.description, product.category_details?.name].some(value => String(value || "").toLowerCase().includes(query));
      const matchesStock = stockFilter === "all" || (stockFilter === "low" && product.stock > 0 && product.stock <= 5) || (stockFilter === "out" && product.stock === 0);
      return matchesSearch && matchesStock;
    });
  }, [products, search, stockFilter]);

  function logout() {
    clearTokens();
    setAuthenticated(false);
    setProducts([]);
    setMetrics(null);
  }

  async function saveProduct(payload) {
    setSaving(true);
    setDialogError("");
    try {
      if (dialog?.id) {
        await apiRequest(`/api/products/${dialog.id}/`, { method: "PATCH", body: JSON.stringify(payload) });
      } else {
        await apiRequest("/api/products/", { method: "POST", body: JSON.stringify(payload) });
      }
      setDialog(null);
      await loadData();
    } catch (err) {
      setDialogError(err.message || "Could not save product.");
    } finally {
      setSaving(false);
    }
  }

  async function deleteProduct(product) {
    if (!window.confirm(`Delete “${product.name}” from your inventory?`)) return;
    setPageError("");
    try {
      await apiRequest(`/api/products/${product.id}/`, { method: "DELETE" });
      await loadData();
    } catch (err) {
      setPageError(err.message || "Could not delete product.");
    }
  }

  if (!authenticated) return <LoginScreen onLogin={() => setAuthenticated(true)} />;

  return (
    <div className="app-shell">
      <aside className={`sidebar ${mobileNavOpen ? "sidebar-open" : ""}`}>
        <div className="brand-lockup"><div className="brand-mark small"><Boxes size={21} /></div><div><strong>Northstar</strong><span>INVENTORY CLOUD</span></div><button className="mobile-close icon-button" onClick={() => setMobileNavOpen(false)} aria-label="Close navigation"><X size={18} /></button></div>
        <p className="nav-caption">WORKSPACE</p>
        <nav className="main-nav"><a className="nav-link active" href="#overview" onClick={() => setMobileNavOpen(false)}><LayoutDashboard size={18} />Overview</a><a className="nav-link" href="#inventory" onClick={() => setMobileNavOpen(false)}><ClipboardList size={18} />Inventory<span className="nav-count">{products.length}</span></a></nav>
        <div className="sidebar-bottom"><div className="help-card"><span className="help-icon"><CircleHelp size={17} /></span><strong>Need a hand?</strong><p>Keep stock data accurate by updating items as they move.</p></div><div className="user-profile"><div className="avatar">IN</div><div className="user-details"><strong>Inventory team</strong><span>Workspace account</span></div><button className="icon-button logout-button" onClick={logout} title="Sign out" aria-label="Sign out"><LogOut size={17} /></button></div></div>
      </aside>
      {mobileNavOpen && <button className="nav-scrim" aria-label="Close navigation" onClick={() => setMobileNavOpen(false)} />}
      <main className="main-content" id="overview">
        <header className="topbar"><button className="mobile-menu icon-button" onClick={() => setMobileNavOpen(true)} aria-label="Open navigation"><Menu size={21} /></button><div className="breadcrumb">Workspace <span>/</span> <strong>Overview</strong></div><div className="topbar-right"><span className="live-dot" /> All systems operational <span className="topbar-divider" /><span className="today-label">Inventory management</span><button className="icon-button top-logout" onClick={logout} title="Sign out" aria-label="Sign out"><LogOut size={17} /></button></div></header>
        <div className="page-container">
          <section className="welcome-row"><div><p className="eyebrow">INVENTORY OVERVIEW</p><h1>Your inventory, at a glance.</h1><p className="muted">Track stock levels, monitor product value, and keep operations moving.</p></div><button className="primary-button add-button" onClick={() => { setDialog({ ...emptyForm }); setDialogError(""); }}><Plus size={18} /> Add product</button></section>
          {pageError && <div className="alert error page-alert"><AlertTriangle size={17} />{pageError}<button className="icon-button" onClick={() => setPageError("")} aria-label="Dismiss error"><X size={16} /></button></div>}
          <section className="metrics-grid" aria-label="Inventory metrics">
            <MetricCard label="Total products" value={number.format(metrics?.total_products ?? products.length)} note="Unique inventory items" icon={Boxes} tone="purple" />
            <MetricCard label="Units in stock" value={number.format(metrics?.total_stock ?? 0)} note="Across all your products" icon={PackagePlus} tone="blue" />
            <MetricCard label="Low stock alerts" value={number.format(metrics?.low_stock_count ?? 0)} note="Between 1 and 5 units" icon={AlertTriangle} tone="amber" />
            <MetricCard label="Inventory value" value={currency.format(Number(metrics?.total_inventory_value || 0))} note="Based on price × quantity" icon={TrendingUp} tone="green" />
          </section>
          <section className="inventory-section" id="inventory">
            <div className="section-heading"><div><h2>Product inventory</h2><p>Review and manage products assigned to your account.</p></div><button className="secondary-button refresh-button" onClick={loadData} disabled={loading}><Activity size={16} className={loading ? "spin" : ""} /> Refresh</button></div>
            <div className="table-toolbar"><label className="search-field"><Search size={17} /><input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search products or descriptions…" aria-label="Search products" /><kbd>⌕</kbd></label><label className="filter-select"><ArrowDownUp size={16} /><select value={stockFilter} onChange={e => setStockFilter(e.target.value)} aria-label="Filter stock"><option value="all">All stock levels</option><option value="low">Low stock</option><option value="out">Out of stock</option></select><ChevronDown size={15} /></label><span className="result-count">{filteredProducts.length} items</span></div>
            <div className="table-wrap"><table className="inventory-table"><thead><tr><th>Product</th><th>Category</th><th>Unit price</th><th>Stock level</th><th>Status</th><th><span className="sr-only">Actions</span></th></tr></thead><tbody>
              {loading && products.length === 0 ? <tr><td colSpan="6"><div className="table-state"><span className="loader" />Loading your inventory…</div></td></tr> : filteredProducts.length === 0 ? <tr><td colSpan="6"><div className="empty-state"><div className="empty-icon"><Boxes size={24} /></div><strong>{search || stockFilter !== "all" ? "No matching products" : "Your inventory is ready"}</strong><p>{search || stockFilter !== "all" ? "Try adjusting your search or stock filter." : "Add your first product to start tracking inventory."}</p>{!search && stockFilter === "all" && <button className="primary-button" onClick={() => { setDialog({ ...emptyForm }); setDialogError(""); }}><Plus size={16} /> Add your first product</button>}</div></td></tr> : filteredProducts.map(product => {
                const status = product.stock === 0 ? "out" : product.stock <= 5 ? "low" : "healthy";
                return <tr key={product.id}><td><div className="product-cell"><div className="product-thumb"><PackagePlus size={19} /></div><div><strong>{product.name}</strong><span>SKU-{String(product.id).padStart(5, "0")}</span></div></div></td><td><span className="category-pill">{product.category_details?.name || categories.find(c => c.id === product.category)?.name || "Uncategorized"}</span></td><td className="price-cell">{currency.format(Number(product.price || 0))}</td><td><div className="stock-cell"><strong>{number.format(product.stock)}</strong><div className="stock-track"><span className={status} style={{ width: `${Math.min(100, product.stock === 0 ? 0 : Math.max(8, product.stock * 4))}%` }} /></div></div></td><td><span className={`status-pill ${status}`}><span />{status === "healthy" ? "In stock" : status === "low" ? "Low stock" : "Out of stock"}</span></td><td><div className="row-actions"><button className="icon-button" title="Edit product" aria-label={`Edit ${product.name}`} onClick={() => { setDialog({ ...product, category: String(product.category) }); setDialogError(""); }}><Pencil size={16} /></button><button className="icon-button danger-action" title="Delete product" aria-label={`Delete ${product.name}`} onClick={() => deleteProduct(product)}><Trash2 size={16} /></button></div></td></tr>;
              })}
            </tbody></table></div>
            <footer className="table-footer"><span>Showing <strong>{filteredProducts.length}</strong> of <strong>{products.length}</strong> products</span><span className="footer-secure"><ShieldCheck size={15} /> Your inventory data is account-scoped</span></footer>
          </section>
          <footer className="page-footer"><span>Northstar Inventory <span>·</span> Enterprise operations</span><span>Built on Django REST Framework</span></footer>
        </div>
      </main>
      {dialog && <ProductDialog initial={dialog} categories={categories} onClose={() => setDialog(null)} onSave={saveProduct} busy={saving} error={dialogError} />}
    </div>
  );
}
