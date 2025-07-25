# Smart Shelf Replenishment System with Environmental Monitoring

## Overview
This project implements a **Smart Shelf Replenishment System** built with **Flask** (Python backend) and a dynamic frontend using JavaScript and Chart.js.  
It simulates inventory management, restock request workflows, sales tracking, and environmental monitoring for perishable products in a retail setting.

---

## Features (MORE TO BE ADDED BY AHMED)

- **Multi-product inventory tracking:** Each product maintains independent stock, restock thresholds, and sales counters.  
- **Supplier inventory and restock requests:** Automatic restock requests generated when stock drops below thresholds, accounting for supplier availability. Partial restocks supported.  
- **Manager Dashboard:** Interactive list of restock requests with LIFO order, enabling approval/rejection. Approval is disabled when supplier stock is insufficient, with explanatory messages.  
- **Environmental monitoring:** Periodic simulation of temperature and humidity sensors for both shelf and inventory storage, with alerts on unsafe conditions.  
- **Sales simulation:** Simulate sales per product, with real-time updates to stock, sales statistics, and supplier requests.  
- **Data visualization:** Bar chart showing units sold per product using Chart.js.  
- **Configurable safety thresholds:** Safe temperature and humidity ranges can be updated for each product.

---

## Technical Details

- **Backend:**  
  - Flask REST API endpoints for stock management, restock requests, analytics, sensor data, and configuration.  
  - Background thread simulating sensor data fluctuations with random but realistic deviations.  
  - Intelligent restock logic preventing stock underrun and managing partial restock scenarios.  

- **Frontend:**  
  - HTML + CSS UI with separate cards for:  
    - Current Shelf Stock  
    - Supplier Inventory  
    - Pending Supplier Requests  
    - Sales and Analytics  
  - Manager Dashboard displays restock requests newest-first (LIFO) with actionable buttons.  
  - Chart.js integrated to plot sales per product.  
  - Error handling and user prompts for request rejection reasons.  

---

## Running the Project

1. **Install dependencies:**
   ```console
   pip install flask
   ```
3. **Run the Flask app:**
   ```console
   python app.py
   ```
5. **Open your browser:**
   ```console
   Visit http://127.0.0.1:5000 to interact with the system.
   ```
## Usage Instructions

- Use the **Shelf Simulator** buttons to simulate sales and observe automatic restock request creation.

- Approve or reject restock requests in the **Manager Dashboard**. Approvals are blocked if supplier inventory is depleted.

- Monitor environmental alerts and report issues, which will simulate automatic sensor correction.

- Visualize sales trends in the sales chart.

- Check analytics for overall system status including total, pending, approved, and rejected requests.

---

## Project Scope & Learning Goals

This project showcases key industrial software concepts:

- Real-time inventory and order management with asynchronous updates.

- Integration of IoT-like environmental sensor simulation and monitoring.

- Practical UI/UX for operations managers to oversee stock and supplier interactions.

- Handling of partial fulfillment and supplier constraints in inventory replenishment.

- Use of RESTful APIs to support interactive frontend dashboards.

---

## Future Work Ideas

- Persistent data storage (database integration).

- User authentication and role-based access control.

- More detailed environmental analytics and historical trends.

- Alerts via email or messaging services.

- Expand to support more complex supplier and shipment workflows.

---

**This project is part of the Industrial Software Master’s course and is intended for educational and demonstration purposes.**

