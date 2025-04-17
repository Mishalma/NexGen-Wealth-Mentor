
# 🚀 NexGen Wealth Mentor  
**Reimagining Personal Finance through AI, 3D, and Immersive Design**

**NexGen Wealth Mentor** is not just another finance tracker — it's your **AI-powered financial companion**, wrapped in a visually stunning, futuristic experience. Blending the power of intelligent algorithms with immersive 3D design, NexGen guides you to financial freedom in a way that’s intuitive, interactive, and downright fun.

> _"Imagine your finances in 3D, your goals visualized in motion, and your AI mentor glowing with guidance — welcome to the next generation of wealth management."_

---

## 🧭 Table of Contents  
- [✨ Overview](#-overview)  
- [🚀 Features](#-features)  
- [⚙️ Tech Stack](#-tech-stack)  
- [📁 Project Structure](#-project-structure)  
- [🛠️ Setup Instructions](#-setup-instructions)  
- [🧪 Usage](#-usage)  
- [🖼️ Screenshots](#-screenshots)  
- [🤝 Contributing](#-contributing)  
- [📜 License](#-license)  
- [🌟 Acknowledgements](#-acknowledgements)  

---

## ✨ Overview  

**NexGen Wealth Mentor** is envisioned as:  
> _“A living, breathing AI finance coach residing inside your device.”_

It transforms traditional financial management into an engaging, gamified, and cinematic experience with:

- 🧊 **Interactive 3D Dashboards** featuring modular Finance Cubes.  
- 🧠 **Conversational AI** inside a chat bubble UI.  
- 🪩 **Holographic Orb Guide** that reacts to your financial queries.  
- 🎯 **Gamified Goal Planning** with drag-and-drop modules.  
- 🔐 **Secure Login System** using Flask-Login & hashed credentials.  

Inspired by icons like **Apple Vision Pro**, **Tesla Model 3**, **Notion**, and **Cyberpunk 2077**, the interface combines **neo-morphism**, **glassmorphism**, and **animated depth** for a visually rich experience. 💡

> 💰 Currency Format: INR (₹)  
> 🧠 Powered by Google’s Agent Development Kit for intelligent financial analysis.

---

## 🚀 Features

### 🎨 Futuristic UI & Animations
- 3D Finance Cubes & radial charts via **Three.js** and **Plotly**  
- Neo-morphic & glassmorphic aesthetics with a cosmic color palette  
- Animated transitions, glowing effects, and parallax scrolling via **GSAP**

### 🔧 Interactive Elements
- Drag-and-drop goal planning (with **Interact.js**)  
- Hologram Orb & Chatbot that simulates financial coaching  
- Smart financial cards that respond dynamically to insights

### 🧮 Financial Intelligence Tools
- Budget breakdowns with real-time insights  
- Savings & emergency fund recommendations  
- Debt reduction strategies (Avalanche & Snowball methods)  
- Goal planning timelines with animated progress indicators

### 🔐 Authentication & Security
- User login & registration with **Flask-Login**  
- Passwords hashed using **Werkzeug**  
- All routes protected to ensure user data privacy

### 📱 Fully Responsive Design
- Tailwind-powered adaptive layout  
- Smooth sidebar toggle for mobile devices

---

## ⚙️ Tech Stack

- **Backend:** Flask, Flask-Login, SQLAlchemy  
- **Frontend:** Three.js, GSAP, Tailwind CSS, Interact.js, Plotly  
- **Database:** SQLite  
- **AI Integration:** Google ADK, Python, pandas  
- **Security:** Werkzeug, .env file for API keys  

---

## 📁 Project Structure

```
nexgen-wealth-mentor/
│
├── app.py                 # Main Flask app
├── finance_advisor.py     # Google ADK-powered financial logic
├── database.py            # SQLAlchemy database model
│
├── templates/             # HTML Templates
│   ├── base.html
│   ├── dashboard.html
│   ├── input.html
│   ├── results.html
│   ├── chat.html
│   ├── goals.html
│   └── login/register/about.html
│
├── static/
│   ├── css/styles.css     # Styling with glassmorphism + neon touches
│   ├── js/scripts.js      # 3D, animation, and drag-drop logic
│   └── data/expense_template.csv
│
├── .env                   # Google API Key
├── requirements.txt       # Python dependencies
└── finance.db             # SQLite database
```

---

## 🛠️ Setup Instructions

### 🔑 Prerequisites
- Python 3.8+  
- pip  
- Git  
- Google API Key (for ADK)  

### ⚙️ Steps

```bash
# 1. Clone the Repository
git clone https://github.com/your-username/nexgen-wealth-mentor.git
cd nexgen-wealth-mentor

# 2. Create & Activate Virtual Environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install Required Packages
pip install -r requirements.txt

# 4. Set Environment Variables
touch .env
echo "GOOGLE_API_KEY=your-google-api-key" >> .env

# 5. Initialize Database
python -c "from database import Base, engine; Base.metadata.create_all(engine)"

# 6. Run the App
python app.py
```

Access it at **[http://localhost:5000](http://localhost:5000)**

---

## 🧪 Usage

- 🔐 Register at `/register` → Login at `/login`  
- 💼 Input income/expenses at `/input`  
- 📊 Visualize analysis at `/results`  
- 🗣️ Talk to AI mentor at `/chat`  
- 🎯 Plan your dreams at `/goals`  
- 📥 Download template at `/download_template`  

---


## 🤝 Contributing

We welcome contributions from all future-thinkers.  
To contribute:

```bash
# Fork & clone
git checkout -b feature/your-feature
git commit -m "Add awesome feature"
git push origin feature/your-feature
```

Then open a **pull request** with a clear description.  
> Ensure your code follows **PEP 8** and includes tests if possible.  

---

## 📜 License

This project is licensed under the **MIT License**.  
See the [`LICENSE`](./LICENSE) file for full details.

---

## 🌟 Acknowledgements

- **xAI** – For the spark of AI inspiration  
- **Google ADK** – Financial analysis backbone  
- **Three.js** – Mind-blowing 3D rendering  
- **Tailwind CSS** – Rapid, clean styling  
- **Inspiration:** Apple Vision Pro, Tesla Model 3, Notion, Cyberpunk 2077  

---

## 🧠 Let’s Build the Future of Finance  
Have an idea, suggestion, or feature request?  
Open an [issue](https://github.com/your-username/nexgen-wealth-mentor/issues) or connect with us.

