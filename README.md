# AssetFlow 🚀

AssetFlow is a next-generation Enterprise Asset Management (EAM) and Predictive Maintenance platform. Originally prototyped as an Odoo module, this project has been completely rebuilt from the ground up as a high-performance, custom full-stack web application using **FastAPI** and **React**.

By leveraging AI-driven forecasting and a beautiful glassmorphism UI, AssetFlow helps organizations efficiently manage physical assets, inventory, shared resources, maintenance workflows, audits, and analytics from a centralized platform.

---

## 🛠️ Tech Stack

### Frontend
- **Framework**: React (Vite)
- **Routing**: React Router DOM
- **Styling**: Vanilla CSS (Premium Glassmorphism & Dark Mode)
- **Icons**: Lucide React
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (Easily swappable to PostgreSQL)
- **ORM**: SQLAlchemy
- **Authentication**: JWT (JSON Web Tokens) with `passlib` (bcrypt hashing)
- **Data Validation**: Pydantic

---

## ✨ Features

AssetFlow aims to provide organizations with a complete solution for:
- **Asset Registration & Lifecycle Management**: Complete inventory tracking with visual health score bars.
- **Department & Employee Management**: Role-based access control and organizational data.
- **Asset Allocation & Transfers**: Track where assets are and who is responsible for them.
- **Shared Resource Booking**: Book meeting rooms, specialized equipment, and facility resources.
- **Maintenance Management**: View, assign, and track maintenance workflows.
- **Audit Management**: Track physical audits of assets for compliance.
- **Activity Logging & Notifications**: Immutable system audit trails for all critical actions.
- **Predictive Maintenance**: Visual risk board mapping assets by their AI-calculated failure probability.
- **Inventory Demand Forecasting**: Track historical consumption and leverage SMA/EWMA algorithms to predict future parts demand.
- **Reports & Analytics**: Real-time aggregation of active assets, pending requests, and critical alerts.

---

## 🚀 Getting Started (Local Development)

To run AssetFlow locally, you need to start both the Python backend and the React frontend.

### 1. Start the Backend (FastAPI)

Open a terminal and navigate to the project root directory, then run:

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
*Note: The backend will run on `http://localhost:8000`. The first time it runs, it will auto-generate a massive database of 50+ realistic records for the dashboard.*

### 2. Start the Frontend (React)

Open a **second terminal window**, navigate to the project root directory, and run:

```bash
cd frontend
npm install
npm run dev
```
*Note: The frontend will run on `http://localhost:5173`. Open this URL in your browser to view the application.*

---

## 🌍 How to Deploy (Production)

AssetFlow's decoupled architecture makes it incredibly easy to deploy for free using modern serverless providers.

### 1. Deploying the Backend (Render)
We recommend deploying the FastAPI backend to [Render.com](https://render.com/) as a Web Service.
1. Create a free account on Render and link your GitHub repository.
2. Click **New +** -> **Web Service**.
3. Select your repository.
4. Set the **Root Directory** to `backend/`.
5. Set the **Build Command** to `pip install -r requirements.txt`.
6. Set the **Start Command** to `uvicorn main:app --host 0.0.0.0 --port $PORT`.
7. Click **Create Web Service**. 
8. *(Note: Render will give you a live URL like `https://assetflow-api.onrender.com`. Copy this URL!)*

### 2. Deploying the Frontend (Vercel)
We recommend deploying the React frontend to [Vercel](https://vercel.com/) for lightning-fast edge delivery.
1. Before deploying, open `frontend/src/App.jsx` and change `const API_BASE = 'http://localhost:8000/api';` to your new Render Backend URL (e.g., `const API_BASE = 'https://assetflow-api.onrender.com/api';`). Commit this change.
2. Create a free account on Vercel and link your GitHub repository.
3. Click **Add New Project**.
4. Import your AssetFlow repository.
5. Set the **Root Directory** to `frontend/`.
6. Vercel will automatically detect it is a Vite project and set the build command to `npm run build`.
7. Click **Deploy**.

Congratulations! Your Enterprise Asset Management system is now live on the internet!
