## Running the Project

1. **Install dependencies:**
   ```console
   pip install flask
   pip install requests
   ```
2. **Run the Flask app:**
   ```console
   Open a new console --> : run python app.py
   Open another console --> : run supplier.py
   
   ```
3. **Open your browser:**
   ```console
   http://127.0.0.1:5000  -->store manager dashboard
   http://127.0.0.1:5001  -->supplier dashboard
   ```

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


## Usage Instructions (Store Manager Dashboard)
- Use the **Shelf Simulator** buttons to simulate sales and observe automatic restock request creation.

- Approve or reject restock requests in the **Manager Dashboard**. Approvals are blocked if supplier inventory is depleted.

- Monitor environmental alerts and report issues, which will simulate automatic sensor correction.

- Visualize sales trends in the sales chart.

- Check analytics for overall system status including total, pending, approved, and rejected requests.


---
## Usage Instructions (Supplier Dashboard)
- Requests from the store manager will be displayed in the requests table with their status
- Each supply requests can be accepted or rejected, using the action buttons in last colum
- If a request is accepted you will see the status change until it is dispatched (latest stage)

**This project is part of the Industrial Software Master’s course and is intended for educational and demonstration purposes.**

