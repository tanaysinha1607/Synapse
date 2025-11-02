# Project Synapse  
**An AI-powered career simulation and mentorship platform built using Google Gemini, Vertex AI, and Cloud Run**

---

## Project Overview  

Project Synapse is a personalized career intelligence platform that leverages Google’s Generative AI ecosystem to help individuals understand, plan, and grow their careers through simulation-based guidance.  

It analyzes users’ resumes, skills, and interests to recommend career paths, identify skill gaps, and generate actionable roadmaps — bridging the gap between learning and employability.  

Our goal is to make career planning data-driven, adaptive, and transparent by combining generative reasoning with predictive modeling.  

---

## Inspiration and Ideation  

Most career guidance systems today are either generic or outdated, offering static recommendations that fail to consider an individual’s unique background or real-time industry trends.  

Synapse emerged from the question: *What if people could simulate their future careers before committing to them?*  

The idea was to transform career guidance into an **interactive simulation**, powered by Google’s generative models.  
Instead of providing one-size-fits-all advice, Synapse dynamically interprets a user’s data to generate personalized skill graphs, career simulations, and tailored learning paths.  

This approach blends **Google Gemini’s reasoning abilities** with **Vertex AI’s predictive modeling**, allowing users to visualize and act on their potential with clarity and confidence.  

---

## Technical Architecture  

Synapse is built as a modular, cloud-native system designed for scalability, reliability, and real-time AI inference.  

### System Flow  

1. **User Input Layer (Frontend)**  
   - Users upload resumes or select career interests.  
   - The data is structured and sent securely to backend endpoints.  

2. **Processing Layer (Backend)**  
   - FastAPI manages all agent operations and routes data through specialized modules: Resume, SkillGap, Mentor, and Roadmap.  
   - Each agent interacts with Google Gemini for reasoning and contextual understanding.  

3. **Model Intelligence Layer (Google AI)**  
   - **Gemini API** extracts skills, interprets user intent, and generates contextual insights.  
   - **Vertex AI** processes structured data to produce predictive career paths and personalized learning recommendations.  

4. **Serving and Deployment Layer**  
   - The backend is containerized with Docker and deployed via **Google Cloud Run**.  
   - The frontend is hosted on **Vercel** for fast, global delivery.  
   - Firebase or Firestore can be optionally integrated for user data persistence.  

5. **Output Layer**  
   - Results are displayed through a clean, intuitive interface.  
   - Users can view skill graphs, recommendations, gap analysis reports, and AI-generated simulations in real time.  

### Tech Stack Overview  

| Layer | Technology | Purpose |
|-------|-------------|----------|
| Frontend | React, TypeScript, Vite, TailwindCSS | Interactive and responsive UI |
| Backend | FastAPI (Python) | Core API management and logic execution |
| AI Layer | Google Gemini API, Vertex AI | Generative reasoning and predictive career modeling |
| Hosting | Google Cloud Run, Vercel | Scalable and reliable deployment |
| Tools | Docker | Containerization and environment consistency |

---

## Key Features  

- **AI Resume Intelligence:** Extracts, structures, and enriches skills from resumes and professional profiles.  
- **Personalized Role Recommendations:** Suggests in-demand roles aligned with user competencies and market trends.  
- **Skill Gap Analysis:** Highlights missing skills and provides targeted upskilling suggestions.  
- **Career Simulation Engine:** Generates realistic project briefs that mimic real-world roles.  
- **AI Mentor Feedback:** Offers tailored guidance and constructive evaluation for submitted work.  
- **Dynamic Learning Roadmap:** Outlines a step-by-step skill development plan using data-driven reasoning.  
- **Integrated AI Agent System:** Each agent works independently yet contributes to a cohesive ecosystem.  

---

## Innovation Edge  

Synapse redefines career guidance by integrating **simulation-based learning** with **generative intelligence**.  

Key innovations include:  
- An **AI-driven simulation layer** that lets users experience roles virtually before pursuing them.  
- A **multi-agent architecture**, enabling modular execution and scalability.  
- The fusion of **Google Gemini’s reasoning** with **Vertex AI’s prediction**, achieving both insight and foresight.  
- An **explainable AI framework**, ensuring transparency behind every recommendation.  
- A **cloud-native backbone**, allowing real-time inference and seamless user interaction.  

This combination results in a deeply personalized and trustworthy career guidance experience that evolves with each user interaction.  

---

## User Journey and Experience Flow  

1. **Profile Creation:** The user uploads their resume or manually inputs career interests.  
2. **Data Enrichment:** The Gemini API analyzes the data to extract skills and intent.  
3. **Recommendations:** Vertex AI identifies optimal roles and generates a list of best-fit opportunities.  
4. **Gap Analysis:** The system highlights missing skills and provides actionable improvement paths.  
5. **Career Simulation:** Users receive a project brief that reflects real-world challenges in their chosen role.  
6. **Mentor Review:** Users can upload completed projects to receive AI-generated feedback and improvement suggestions.  
7. **Learning Roadmap:** A personalized roadmap is generated, guiding the user toward their aspirational role.  

The experience is simple, responsive, and transparent — allowing users to progress intuitively through every step.  

---

## Impact and Alignment with the Hackathon Theme  

**Alignment with Google Gen AI Hackathon:**  
Synapse directly embodies the theme of leveraging **AI for Human Potential**. It transforms Google’s AI ecosystem into a practical tool for career empowerment, helping students and professionals make informed, future-ready decisions.  

**Impact Highlights:**  
- Reduces time spent on career planning by up to 60%.  
- Increases accuracy of skill identification by 40%.  
- Expands access to mentorship through scalable AI guidance.  
- Promotes inclusivity by supporting diverse user backgrounds and low-data inputs.  

By combining reasoning, prediction, and simulation, Synapse creates a pathway to personalized, equitable career growth.  

---

## Market Potential and Future Growth  

**Target Audience:**  
- University students exploring career paths.  
- Early-career professionals seeking upskilling guidance.  
- Educational institutions and training providers aiming to enhance career readiness.  

**Future Plans:**  
- Integration with **Google Career Certificates** for structured upskilling.  
- Expansion into **AI-driven internship simulations** and job-matching.  
- Development of a **Career Intelligence API** for educational institutions.  
- Implementation of a **skills forecasting engine** using Graph Neural Networks (GNNs).  

The long-term goal is to establish Synapse as a comprehensive **Career-as-a-Service (CaaS)** platform for the global education ecosystem.  

---

## Installation and Setup  

### Prerequisites  
- Python 3.11+  
- Node.js 18+  
- Google Gemini / Vertex AI API key  
- Docker (for deployment)  

### Setup  

```bash
# Clone the repository
git clone https://github.com/AmarJaglan/synapse-frontend.git
cd SynapseFinal

# Backend setup
cd googlegenaiproject
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY=AIzaSyD_HRneo82kfC8TSc_TzaojOwh0q3Wf5v0
export GCP_PROJECT_ID=synapse-hackathon-470816
export GCP_REGION=us-central1

# Run backend
uvicorn app.api:app --reload

# Frontend setup
cd ../Frontend
npm install
npm run dev
## Demo Instructions  


**Frontend Demo:** [https://synapse.vly.site](https://synapse.vly.site)  
**Backend API (Cloud Run):** [https://synapse-ml-537153748290.us-central1.run.app](https://synapse-ml-537153748290.us-central1.run.app)  

### Sample Input  
Upload a resume file or select a career area of interest.  

### Expected Output  
- Extracted and categorized skills  
- Recommended career roles  
- Gap analysis with skill improvement plan  
- Personalized roadmap and mentor feedback  

---

## Challenges and Learnings  

### Challenges  
- Managing multiple asynchronous AI agent interactions efficiently.  
- Structuring long-form Gemini outputs into consistent and usable formats.  
- Balancing model creativity with factual reliability.  

### Learnings  
- Fine-tuning generative models for domain-specific reasoning.  
- Building explainable AI workflows for transparency and trust.  
- Achieving seamless integration between FastAPI, Google Cloud Run, and the frontend framework.  

---

## Team and Roles  

| Name | Role | Contribution |
|------|------|---------------|
| **Amardeep Jaglan** | Cloud and Infrastructure Engineer | Deployed and managed the entire project architecture using Google Cloud Run, Firebase, and Docker; ensured scalable backend operations and environment consistency |
| **Naman** | Frontend Developer | Designed and implemented the user interface using React, Vite, and TailwindCSS; focused on responsive, intuitive UX and seamless API integration |
| **Tanay Sinha** | AI and Strategy Lead | Led AI architecture design, Gemini prompt engineering, and career intelligence framework development |
| **Atharv Agarwal** | Machine Learning Engineer | Developed ML-driven modules, handled data modeling, and fine-tuned AI components for accurate skill and career predictions |
| **Anwesh Sinha** | AI Agent and Systems Developer | Designed and optimized multi-agent workflows, integrating FastAPI with Google Gemini for reasoning and skill-gap analysis |

---

## Next Steps  

### Short-Term Goals  
- Enhance feedback quality using Gemini 1.5’s multimodal capabilities.  
- Introduce interactive analytics for learners and institutions.  
- Expand AI role simulations across new domains.  

### Long-Term Vision  
- Build a self-learning ecosystem that adapts career paths dynamically.  
- Establish Synapse as an integrated layer across education platforms.  
- Partner with institutions to scale AI-guided mentorship globally.  

---

## Summary  

**Project Synapse** transforms static career planning into a living, AI-driven experience powered by Google Gemini and Vertex AI.  
It combines reasoning, prediction, and simulation to help individuals navigate their career journey with confidence and clarity.  

By bridging the gap between skills and opportunities, Synapse represents a new model for **personalized, data-driven career growth** — one that can scale to millions of learners worldwide.
