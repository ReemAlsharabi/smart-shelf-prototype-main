let products = {};
let supplierStockData = {};
let pendingSupplier = {};
let salesChartInstance = null;

function fetchStock() {
  fetch('/stock')
    .then(res => res.json())
    .then(data => {
      products = data;
      renderStock();
      renderSales();
      renderSalesGraph();
    })
    .catch(err => console.error("Stock fetch error:", err));
}

function fetchAnalytics() {
  fetch('/analytics')
    .then(res => res.json())
    .then(data => {
      pendingSupplier = data.pending_supplier || {};
      supplierStockData = data.supplier || {};

      const stats = `
        <strong>Total Requests:</strong> ${data.total} |
        <strong>Pending:</strong> ${data.pending} |
        <strong>Approved:</strong> ${data.approved} |
        <strong>Rejected:</strong> ${data.rejected}
      `;
      document.getElementById("stats").innerHTML = stats;

      renderStock();
      renderAlerts(data.alerts || {});
    })
    .catch(err => {
      console.error("Analytics fetch error:", err);
      document.getElementById("stats").innerText = "⚠️ Failed to load stats";
    });
}

function renderAlerts(alerts) {
  const container = document.getElementById("alerts");
  container.innerHTML = "";

  for (const product in alerts) {
    const list = alerts[product];
    if (list.length > 0) {
      const div = document.createElement("div");
      div.innerHTML = `
        <strong>${product} Alerts:</strong>
        <ul>${list.map(msg => `<li>${msg}</li>`).join('')}</ul>
        <button onclick="reportIssue('${product}')">📢 Report Environmental Issue</button>
      `;
      div.style.color = "red";
      container.appendChild(div);
    }
  }
}

function reportIssue(product) {
  fetch('/report-environment', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product })
  })
    .then(res => res.json())
    .then(data => {
      alert(data.message);
      fetchAnalytics(); // Refresh alerts after delay
    })
    .catch(err => console.error("Failed to report issue:", err));
}

function renderStock() {
  const container = document.getElementById("stockContainer");
  container.innerHTML = '';

  for (const [product, info] of Object.entries(products)) {
    const sensors = info.sensors || {};
    const shelf = sensors.shelf || {};
    const inventory = sensors.inventory || {};
    const supplierAvailable = supplierStockData[product] ?? 0;
    const pendingQty = pendingSupplier[product] || 0;

    const div = document.createElement('div');
    div.innerHTML = `
      <h3>${product}</h3>
      <div class="stock-cards">
        <div class="stock-card"><strong>Shelf Stock:</strong><br> ${info.stock}</div>
        <div class="stock-card"><strong>Supplier Inventory:</strong><br> ${supplierAvailable} units</div>
        <div class="stock-card"><strong>Pending Requests:</strong><br> ${pendingQty} units</div>
        <div class="stock-card"><strong>Shelf Temp:</strong><br> ${shelf.temp ?? 'N/A'} °C</div>
        <div class="stock-card"><strong>Shelf Humidity:</strong><br> ${shelf.humidity ?? 'N/A'} %</div>
        <div class="stock-card"><strong>Inventory Temp:</strong><br> ${inventory.temp ?? 'N/A'} °C</div>
        <div class="stock-card"><strong>Inventory Humidity:</strong><br> ${inventory.humidity ?? 'N/A'} %</div>
      </div>
      <button id="btn-${product}" ${info.stock <= 0 ? 'disabled' : ''} onclick="simulateSale('${product}')">
        ${info.stock <= 0 ? 'Out of Stock' : 'Simulate Sale (-1)'}
      </button>
    `;
    container.appendChild(div);
  }
}

function renderSales() {
  const container = document.getElementById("salesContainer");
  container.innerHTML = '';

  for (const [product, info] of Object.entries(products)) {
    const div = document.createElement('div');
    div.innerHTML = `
      <h3>${product}</h3>
      <p>Units Sold: <span id="sales-${product}">${info.sales}</span></p>
    `;
    container.appendChild(div);
  }
}

function renderSalesGraph() {
  const ctx = document.getElementById('salesChart').getContext('2d');
  const labels = Object.keys(products);
  const salesData = labels.map(p => products[p].sales);

  if (salesChartInstance) salesChartInstance.destroy();

  salesChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Units Sold',
        data: salesData,
        backgroundColor: 'rgba(54, 162, 235, 0.7)'
      }]
    },
    options: {
      responsive: true,
      scales: {
        y: { beginAtZero: true }
      }
    }
  });
}

function simulateSale(product) {
  if (!products[product] || products[product].stock <= 0) return;

  const newStock = products[product].stock - 1;
  fetch('/stock', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ product, stock: newStock })
  })
    .then(() => {
      fetchStock();
      fetchRequests();
      fetchAnalytics();
    })
    .catch(err => console.error("Sale simulation error:", err));
}

function fetchRequests() {
  fetch('/requests')
    .then(res => res.json())
    .then(data => renderRequests(data))
    .catch(err => console.error("Failed to load requests:", err));
}

function renderRequests(requests) {
  const list = document.getElementById("requestList");
  list.innerHTML = "";

  requests.slice().reverse().forEach(req => {
    const canApprove = req.status === "Pending" &&
                       !(req.comment || "").includes("Skipped") &&
                       supplierStockData[req.product] > 0;

    const li = document.createElement("li");
    li.innerHTML = `
      <strong>Request #${req.id}</strong> – ${req.product} (${req.quantity})<br>
      Status: <em>${req.status}</em> at ${new Date(req.timestamp).toLocaleString()}<br>
      ${req.comment ? `<em>Comment:</em> ${req.comment}<br>` : ""}
      ${canApprove ? `
        <button onclick="updateRequest(${req.id}, 'approve')">Approve</button>
        <button onclick="updateRequest(${req.id}, 'reject')">Reject</button>
      ` : ""}
    `;
    list.appendChild(li);
  });
}

function updateRequest(id, action) {
  const comment = action === 'reject' ? prompt("Enter rejection reason:") : "";

  fetch('/requests', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id, action, comment })
  })
    .then(() => {
      fetchRequests();
      fetchAnalytics();
      fetchStock();
    });
}

// INIT
fetchStock();
fetchRequests();
fetchAnalytics();
