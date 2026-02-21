# ==========================================================
# 🎓 AI Internship Recommendation System (Flask Version + Readiness Score)
# ==========================================================

from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import sqlite3
from sentence_transformers import SentenceTransformer, util
from deep_translator import GoogleTranslator
import docx2txt
import PyPDF2
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# ⚙ Setup
# ==========================================================
app = Flask(__name__)
app.secret_key = "supersecretkey"

# 🧠 Load Sentence Transformer Model
model = SentenceTransformer('all-MiniLM-L6-v2')

# 🗄 Database Setup
conn = sqlite3.connect('internship_profiles.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS profiles
             (name TEXT, email TEXT, skills TEXT, education TEXT, experience TEXT)''')
conn.commit()

# 🎓 Internship Dataset
internships = [
  {
    "title": "Frontend Developer",
    "category": "Technology & Computer Science",
    "description": "Work with React, Angular, Vue.js technologies to build user interfaces and web applications with salary range ₹4-15 LPA."
  },
  {
    "title": "Backend Developer", 
    "category": "Technology & Computer Science",
    "description": "Develop server-side applications using Node.js, Python, Java with salary range ₹5-18 LPA."
  },
  {
    "title": "Full Stack Developer",
    "category": "Technology & Computer Science", 
    "description": "Build complete web solutions covering both frontend and backend development with salary range ₹6-25 LPA."
  },
  {
    "title": "Mobile App Developer",
    "category": "Technology & Computer Science",
    "description": "Create iOS and Android applications with salary range ₹5-20 LPA."
  },
  {
    "title": "Game Developer",
    "category": "Technology & Computer Science",
    "description": "Develop games using Unity and Unreal Engine with salary range ₹4-18 LPA."
  },
  {
    "title": "DevOps Engineer",
    "category": "Technology & Computer Science",
    "description": "Manage CI/CD pipelines and cloud infrastructure with salary range ₹7-30 LPA."
  },
  {
    "title": "Software Architect",
    "category": "Technology & Computer Science",
    "description": "Design and plan software system architecture with salary range ₹15-50 LPA."
  },
  {
    "title": "Data Scientist",
    "category": "AI / ML",
    "description": "Work on machine learning algorithms, analytics, and data insights with salary range ₹8-35 LPA."
  },
  {
    "title": "Data Analyst",
    "category": "AI / ML",
    "description": "Analyze business data and create intelligence reports with salary range ₹4-15 LPA."
  },
  {
    "title": "Machine Learning Engineer",
    "category": "AI / ML",
    "description": "Build and deploy AI models and machine learning systems with salary range ₹10-40 LPA."
  },
  {
    "title": "AI Research Scientist",
    "category": "AI / ML",
    "description": "Conduct advanced AI research and development with salary range ₹15-60 LPA."
  },
  {
    "title": "Data Engineer",
    "category": "AI / ML",
    "description": "Build ETL pipelines and data infrastructure with salary range ₹7-25 LPA."
  },
  {
    "title": "Business Intelligence Analyst",
    "category": "AI / ML",
    "description": "Create business insights using Tableau, Power BI tools with salary range ₹5-18 LPA."
  },
  {
    "title": "Security Analyst",
    "category": "Cybersecurity",
    "description": "Monitor and detect security threats with salary range ₹5-20 LPA."
  },
  {
    "title": "Ethical Hacker",
    "category": "Cybersecurity",
    "description": "Perform penetration testing and security assessments with salary range ₹6-25 LPA."
  },
  {
    "title": "Security Architect",
    "category": "Cybersecurity",
    "description": "Design infrastructure security systems with salary range ₹12-40 LPA."
  },
  {
    "title": "Cybersecurity Consultant",
    "category": "Cybersecurity",
    "description": "Provide security advisory and consulting services with salary range ₹10-35 LPA."
  },
  {
    "title": "SOC Analyst",
    "category": "Cybersecurity",
    "description": "Monitor security operations center activities with salary range ₹4-15 LPA."
  },
  {
    "title": "Cloud Architect",
    "category": "Cloud & Infrastructure",
    "description": "Design cloud solutions on AWS, Azure, GCP platforms with salary range ₹10-40 LPA."
  },
  {
    "title": "Cloud Engineer",
    "category": "Cloud & Infrastructure",
    "description": "Implement and manage cloud infrastructure with salary range ₹7-25 LPA."
  },
  {
    "title": "Network Engineer",
    "category": "Cloud & Infrastructure",
    "description": "Design and maintain network infrastructure with salary range ₹5-18 LPA."
  },
  {
    "title": "System Administrator",
    "category": "Cloud & Infrastructure",
    "description": "Manage server systems and infrastructure with salary range ₹4-12 LPA."
  },
  {
    "title": "Site Reliability Engineer",
    "category": "Cloud & Infrastructure",
    "description": "Ensure system stability and reliability with salary range ₹8-30 LPA."
  },
  {
    "title": "Blockchain Developer",
    "category": "Emerging Tech",
    "description": "Develop Web3 and cryptocurrency applications with salary range ₹8-35 LPA."
  },
  {
    "title": "IoT Engineer",
    "category": "Emerging Tech",
    "description": "Work on smart devices and Internet of Things with salary range ₹6-22 LPA."
  },
  {
    "title": "AR/VR Developer",
    "category": "Emerging Tech",
    "description": "Create immersive augmented and virtual reality experiences with salary range ₹7-25 LPA."
  },
  {
    "title": "Quantum Computing Specialist",
    "category": "Emerging Tech",
    "description": "Work on next-generation quantum computing systems with salary range ₹15-50 LPA."
  },
  {
    "title": "Robotics Engineer",
    "category": "Emerging Tech",
    "description": "Design and build automation and robotic systems with salary range ₹7-28 LPA."
  },
  {
    "title": "Design Engineer",
    "category": "Mechanical Engineering",
    "description": "Work on CAD and product design with salary range ₹4-15 LPA."
  },
  {
    "title": "Production Engineer",
    "category": "Mechanical Engineering",
    "description": "Manage manufacturing processes and production with salary range ₹4-12 LPA."
  },
  {
    "title": "Quality Engineer",
    "category": "Mechanical Engineering",
    "description": "Ensure quality assurance and quality control with salary range ₹4-14 LPA."
  },
  {
    "title": "HVAC Engineer",
    "category": "Mechanical Engineering",
    "description": "Design and maintain climate control systems with salary range ₹4-15 LPA."
  },
  {
    "title": "Automobile Engineer",
    "category": "Mechanical Engineering",
    "description": "Work on vehicle design and automotive systems with salary range ₹5-18 LPA."
  },
  {
    "title": "Aerospace Engineer",
    "category": "Mechanical Engineering",
    "description": "Design aircraft and aerospace systems with salary range ₹7-25 LPA."
  },
  {
    "title": "R&D Engineer",
    "category": "Mechanical Engineering",
    "description": "Conduct research and innovation in engineering with salary range ₹6-20 LPA."
  },
  {
    "title": "Maintenance Engineer",
    "category": "Mechanical Engineering",
    "description": "Maintain and service equipment and machinery with salary range ₹4-12 LPA."
  },
  {
    "title": "CAE Analyst",
    "category": "Mechanical Engineering",
    "description": "Perform computer-aided engineering simulation with salary range ₹5-18 LPA."
  },
  {
    "title": "Structural Engineer",
    "category": "Civil Engineering",
    "description": "Design building structures and infrastructure with salary range ₹4-18 LPA."
  },
  {
    "title": "Construction Manager",
    "category": "Civil Engineering",
    "description": "Manage construction sites and project execution with salary range ₹5-20 LPA."
  },
  {
    "title": "Urban Planner",
    "category": "Civil Engineering",
    "description": "Plan city development and urban infrastructure with salary range ₹5-16 LPA."
  },
  {
    "title": "Transportation Engineer",
    "category": "Civil Engineering",
    "description": "Design transportation infrastructure systems with salary range ₹5-18 LPA."
  },
  {
    "title": "Water Resources Engineer",
    "category": "Civil Engineering",
    "description": "Work on hydrology and water management systems with salary range ₹4-15 LPA."
  },
  {
    "title": "Geotechnical Engineer",
    "category": "Civil Engineering",
    "description": "Study soil mechanics and foundation engineering with salary range ₹5-16 LPA."
  },
  {
    "title": "Quantity Surveyor",
    "category": "Civil Engineering",
    "description": "Estimate costs and manage construction budgets with salary range ₹4-14 LPA."
  },
  {
    "title": "Site Engineer",
    "category": "Civil Engineering",
    "description": "Supervise project execution on construction sites with salary range ₹3-10 LPA."
  },
  {
    "title": "Environmental Engineer",
    "category": "Civil Engineering",
    "description": "Work on sustainability and environmental protection with salary range ₹5-17 LPA."
  },
  {
    "title": "Project Manager",
    "category": "Civil Engineering",
    "description": "Manage construction projects and teams with salary range ₹8-30 LPA."
  },
  {
    "title": "Power Systems Engineer",
    "category": "Electrical Engineering",
    "description": "Work on electrical grid management and power systems with salary range ₹5-18 LPA."
  },
  {
    "title": "Control Systems Engineer",
    "category": "Electrical Engineering",
    "description": "Design automation and control systems with salary range ₹5-17 LPA."
  },
  {
    "title": "Electrical Design Engineer",
    "category": "Electrical Engineering",
    "description": "Design electrical circuits and systems with salary range ₹4-15 LPA."
  },
  {
    "title": "Instrumentation Engineer",
    "category": "Electrical Engineering",
    "description": "Work with sensors and measurement systems with salary range ₹5-16 LPA."
  },
  {
    "title": "Energy Consultant",
    "category": "Electrical Engineering",
    "description": "Provide renewable energy solutions and consulting with salary range ₹6-20 LPA."
  },
  {
    "title": "General Physician",
    "category": "Medical & Healthcare",
    "description": "Provide primary healthcare and medical treatment with salary range ₹6-25 LPA."
  },
  {
    "title": "Surgeon",
    "category": "Medical & Healthcare",
    "description": "Perform surgical procedures across various specialties with salary range ₹15-80 LPA."
  },
  {
    "title": "Cardiologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in heart and cardiovascular diseases with salary range ₹20 LPA-1 Cr+."
  },
  {
    "title": "Neurologist",
    "category": "Medical & Healthcare",
    "description": "Treat brain and nervous system disorders with salary range ₹18-80 LPA."
  },
  {
    "title": "Dermatologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in skin conditions and treatments with salary range ₹15-60 LPA."
  },
  {
    "title": "Orthopedic Surgeon",
    "category": "Medical & Healthcare",
    "description": "Specialize in bone and joint surgery with salary range ₹18-80 LPA."
  },
  {
    "title": "Pediatrician",
    "category": "Medical & Healthcare",
    "description": "Provide healthcare for children and infants with salary range ₹12-50 LPA."
  },
  {
    "title": "Gynecologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in women's health and reproductive medicine with salary range ₹15-70 LPA."
  },
  {
    "title": "Psychiatrist",
    "category": "Medical & Healthcare",
    "description": "Provide mental health treatment and therapy with salary range ₹12-60 LPA."
  },
  {
    "title": "Radiologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in medical imaging and diagnostics with salary range ₹15-70 LPA."
  },
  {
    "title": "Anesthesiologist",
    "category": "Medical & Healthcare",
    "description": "Provide anesthesia for surgical procedures with salary range ₹18-80 LPA."
  },
  {
    "title": "Oncologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in cancer treatment and care with salary range ₹20 LPA-1 Cr+."
  },
  {
    "title": "Pathologist",
    "category": "Medical & Healthcare",
    "description": "Perform laboratory diagnostics and disease analysis with salary range ₹12-50 LPA."
  },
  {
    "title": "Emergency Medicine Doctor",
    "category": "Medical & Healthcare",
    "description": "Provide emergency room medical care with salary range ₹12-40 LPA."
  },
  {
    "title": "ENT Specialist",
    "category": "Medical & Healthcare",
    "description": "Treat ear, nose, and throat conditions with salary range ₹15-60 LPA."
  },
  {
    "title": "Ophthalmologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in eye care and vision treatment with salary range ₹15-70 LPA."
  },
  {
    "title": "Endocrinologist",
    "category": "Medical & Healthcare",
    "description": "Treat hormone and endocrine system disorders with salary range ₹15-60 LPA."
  },
  {
    "title": "Nephrologist",
    "category": "Medical & Healthcare",
    "description": "Specialize in kidney diseases and treatment with salary range ₹15-65 LPA."
  },
  {
    "title": "Dentist",
    "category": "Medical & Healthcare",
    "description": "Provide oral health care and dental treatment with salary range ₹5-40 LPA."
  },
  {
    "title": "Pharmacist",
    "category": "Medical & Healthcare",
    "description": "Dispense medications and provide pharmaceutical expertise with salary range ₹3-12 LPA."
  },
  {
    "title": "Physiotherapist",
    "category": "Medical & Healthcare",
    "description": "Provide physical therapy and rehabilitation with salary range ₹3-15 LPA."
  },
  {
    "title": "Occupational Therapist",
    "category": "Medical & Healthcare",
    "description": "Help patients with rehabilitation and daily activities with salary range ₹3-12 LPA."
  },
  {
    "title": "Speech Therapist",
    "category": "Medical & Healthcare",
    "description": "Treat communication and speech disorders with salary range ₹3-10 LPA."
  },
  {
    "title": "Nutritionist",
    "category": "Medical & Healthcare",
    "description": "Provide dietary planning and nutrition counseling with salary range ₹3-15 LPA."
  },
  {
    "title": "Clinical Psychologist",
    "category": "Medical & Healthcare",
    "description": "Provide mental health therapy and counseling with salary range ₹4-20 LPA."
  },
  {
    "title": "Medical Lab Technologist",
    "category": "Medical & Healthcare",
    "description": "Perform laboratory testing and medical diagnostics with salary range ₹3-10 LPA."
  },
  {
    "title": "Radiographer",
    "category": "Medical & Healthcare",
    "description": "Operate medical imaging equipment with salary range ₹3-12 LPA."
  },
  {
    "title": "Optometrist",
    "category": "Medical & Healthcare",
    "description": "Provide vision care and eye examinations with salary range ₹3-12 LPA."
  },
  {
    "title": "Registered Nurse",
    "category": "Medical & Healthcare",
    "description": "Provide patient care and medical assistance with salary range ₹3-12 LPA."
  },
  {
    "title": "ICU Nurse",
    "category": "Medical & Healthcare",
    "description": "Provide critical care nursing in intensive care units with salary range ₹4-15 LPA."
  },
  {
    "title": "Business Development Manager",
    "category": "Business & Management",
    "description": "Develop growth strategies and expand business opportunities with salary range ₹6-25 LPA."
  },
  {
    "title": "Operations Manager",
    "category": "Business & Management",
    "description": "Manage business processes and operational efficiency with salary range ₹6-22 LPA."
  },
  {
    "title": "Product Manager",
    "category": "Business & Management",
    "description": "Develop product strategy and manage product lifecycle with salary range ₹10-45 LPA."
  },
  {
    "title": "General Manager",
    "category": "Business & Management",
    "description": "Oversee overall business operations and management with salary range ₹10-40 LPA."
  },
  {
    "title": "Chief Operating Officer",
    "category": "Business & Management",
    "description": "Lead company operations and strategic execution with salary range ₹25 LPA-2 Cr+."
  },
  {
    "title": "Chief Executive Officer",
    "category": "Business & Management",
    "description": "Lead entire company and make strategic decisions with salary range ₹30-5 Cr+."
  },
  {
    "title": "Strategy Consultant",
    "category": "Business & Management",
    "description": "Provide business strategy and consulting services with salary range ₹10-50 LPA."
  },
  {
    "title": "Management Consultant",
    "category": "Business & Management",
    "description": "Advise companies on management and operational improvements with salary range ₹8-40 LPA."
  },
  {
    "title": "Business Analyst",
    "category": "Business & Management",
    "description": "Analyze business processes and recommend improvements with salary range ₹5-20 LPA."
  },
  {
    "title": "HR Manager",
    "category": "Human Resources",
    "description": "Manage people operations and human resources with salary range ₹6-25 LPA."
  },
  {
    "title": "Recruitment Specialist",
    "category": "Human Resources",
    "description": "Handle talent acquisition and hiring processes with salary range ₹4-15 LPA."
  },
  {
    "title": "Training & Development Manager",
    "category": "Human Resources",
    "description": "Design and deliver employee learning programs with salary range ₹5-20 LPA."
  },
  {
    "title": "Compensation & Benefits Manager",
    "category": "Human Resources",
    "description": "Manage employee compensation and payroll systems with salary range ₹6-22 LPA."
  },
  {
    "title": "HR Business Partner",
    "category": "Human Resources",
    "description": "Provide strategic HR support to business units with salary range ₹8-30 LPA."
  },
  {
    "title": "Chartered Accountant",
    "category": "Finance & Accounting",
    "description": "Provide financial expertise and accounting services with salary range ₹8-50 LPA."
  },
  {
    "title": "Cost Accountant",
    "category": "Finance & Accounting",
    "description": "Manage cost accounting and financial analysis with salary range ₹6-30 LPA."
  },
  {
    "title": "Company Secretary",
    "category": "Finance & Accounting",
    "description": "Ensure regulatory compliance and corporate governance with salary range ₹6-35 LPA."
  },
  {
    "title": "Accountant",
    "category": "Finance & Accounting",
    "description": "Maintain financial records and accounting processes with salary range ₹3-12 LPA."
  },
  {
    "title": "Auditor",
    "category": "Finance & Accounting",
    "description": "Conduct financial audits and compliance reviews with salary range ₹5-25 LPA."
  },
  {
    "title": "Internal Auditor",
    "category": "Finance & Accounting",
    "description": "Perform risk assessment and internal controls review with salary range ₹5-20 LPA."
  },
  {
    "title": "Tax Consultant",
    "category": "Finance & Accounting",
    "description": "Provide tax planning and compliance services with salary range ₹5-30 LPA."
  },
  {
    "title": "Forensic Accountant",
    "category": "Finance & Accounting",
    "description": "Investigate financial fraud and conduct forensic analysis with salary range ₹6-28 LPA."
  },
  {
    "title": "Financial Controller",
    "category": "Finance & Accounting",
    "description": "Oversee accounting operations and financial reporting with salary range ₹12-45 LPA."
  },
  {
    "title": "Chief Financial Officer",
    "category": "Finance & Accounting",
    "description": "Lead financial strategy and company finances with salary range ₹25 LPA-2 Cr+."
  },
  {
    "title": "Investment Banker",
    "category": "Investment & Banking",
    "description": "Handle mergers, acquisitions, and IPO transactions with salary range ₹10-80 LPA."
  },
  {
    "title": "Equity Research Analyst",
    "category": "Investment & Banking",
    "description": "Analyze stocks and provide investment recommendations with salary range ₹6-35 LPA."
  },
  {
    "title": "Portfolio Manager",
    "category": "Investment & Banking",
    "description": "Manage investment portfolios and asset allocation with salary range ₹10-60 LPA."
  },
  {
    "title": "Financial Analyst",
    "category": "Investment & Banking",
    "description": "Analyze financial data and create investment plans with salary range ₹5-22 LPA."
  },
  {
    "title": "Credit Analyst",
    "category": "Investment & Banking",
    "description": "Assess loan applications and credit risk with salary range ₹4-16 LPA."
  },
  {
    "title": "Treasury Manager",
    "category": "Investment & Banking",
    "description": "Manage cash flow and treasury operations with salary range ₹7-28 LPA."
  },
  {
    "title": "Wealth Manager",
    "category": "Investment & Banking",
    "description": "Provide financial advisory to high net worth individuals with salary range ₹8-50 LPA."
  },
  {
    "title": "Private Banker",
    "category": "Investment & Banking",
    "description": "Provide personalized banking services to wealthy clients with salary range ₹6-30 LPA."
  },
  {
    "title": "Branch Manager",
    "category": "Investment & Banking",
    "description": "Manage bank branch operations and customer service with salary range ₹5-20 LPA."
  },
  {
    "title": "Relationship Manager",
    "category": "Investment & Banking",
    "description": "Manage client relationships and banking services with salary range ₹4-18 LPA."
  },
  {
    "title": "Graphic Designer",
    "category": "Creative & Design",
    "description": "Create visual communication and graphic design solutions with salary range ₹3-15 LPA."
  },
  {
    "title": "UI/UX Designer",
    "category": "Creative & Design",
    "description": "Design user experiences and interfaces for digital products with salary range ₹5-25 LPA."
  },
  {
    "title": "Product Designer",
    "category": "Creative & Design",
    "description": "Design digital products and user-centered solutions with salary range ₹6-28 LPA."
  },
  {
    "title": "Brand Designer",
    "category": "Creative & Design",
    "description": "Create brand identity and visual branding systems with salary range ₹5-22 LPA."
  },
  {
    "title": "Illustrator",
    "category": "Creative & Design",
    "description": "Create digital and traditional artwork and illustrations with salary range ₹3-18 LPA."
  },
  {
    "title": "Motion Graphics Designer",
    "category": "Creative & Design",
    "description": "Create animated graphics and motion design with salary range ₹4-20 LPA."
  },
  {
    "title": "3D Designer",
    "category": "Creative & Design",
    "description": "Create 3D models and visualizations with salary range ₹5-22 LPA."
  },
  {
    "title": "Art Director",
    "category": "Creative & Design",
    "description": "Lead creative teams and visual design projects with salary range ₹8-35 LPA."
  },
  {
    "title": "Creative Director",
    "category": "Creative & Design",
    "description": "Develop creative strategy and lead design teams with salary range ₹12-60 LPA."
  },
  {
    "title": "Architect",
    "category": "Architecture & Interior",
    "description": "Design buildings and architectural structures with salary range ₹4-25 LPA."
  },
  {
    "title": "Landscape Architect",
    "category": "Architecture & Interior",
    "description": "Design outdoor spaces and landscape environments with salary range ₹4-20 LPA."
  },
  {
    "title": "Interior Designer",
    "category": "Architecture & Interior",
    "description": "Design interior spaces and environments with salary range ₹3-18 LPA."
  },
  {
    "title": "Urban Designer",
    "category": "Architecture & Interior",
    "description": "Plan and design urban environments and city spaces with salary range ₹5-22 LPA."
  },
  {
    "title": "3D Visualizer",
    "category": "Architecture & Interior",
    "description": "Create architectural renderings and 3D visualizations with salary range ₹4-16 LPA."
  },
  {
    "title": "Fashion Designer",
    "category": "Fashion & Textiles",
    "description": "Design clothing and fashion collections with salary range ₹3-30 LPA."
  },
  {
    "title": "Textile Designer",
    "category": "Fashion & Textiles",
    "description": "Design fabrics and textile patterns with salary range ₹3-15 LPA."
  },
  {
    "title": "Fashion Stylist",
    "category": "Fashion & Textiles",
    "description": "Provide personal styling and fashion consulting with salary range ₹3-20 LPA."
  },
  {
    "title": "Fashion Merchandiser",
    "category": "Fashion & Textiles",
    "description": "Develop retail strategy for fashion products with salary range ₹4-18 LPA."
  },
  {
    "title": "Photographer",
    "category": "Photography & Video",
    "description": "Capture photographs across various specialties and events with salary range ₹3-30 LPA."
  },
  {
    "title": "Videographer",
    "category": "Photography & Video",
    "description": "Create video content and film production with salary range ₹4-25 LPA."
  },
  {
    "title": "Video Editor",
    "category": "Photography & Video",
    "description": "Edit and post-process video content with salary range ₹3-18 LPA."
  },
  {
    "title": "Cinematographer",
    "category": "Photography & Video",
    "description": "Handle camera work and visual storytelling with salary range ₹5-40 LPA."
  },
  {
    "title": "Content Creator",
    "category": "Photography & Video",
    "description": "Create digital content across multiple platforms with salary range ₹2-50 LPA."
  },
  {
    "title": "Journalist",
    "category": "Media & Communication",
    "description": "Report news and conduct investigative journalism with salary range ₹3-20 LPA."
  },
  {
    "title": "News Anchor",
    "category": "Media & Communication",
    "description": "Present news on television and broadcast media with salary range ₹5-50 LPA."
  },
  {
    "title": "Editor",
    "category": "Media & Communication",
    "description": "Edit content for publications and media outlets with salary range ₹4-25 LPA."
  },
  {
    "title": "Content Writer",
    "category": "Media & Communication",
    "description": "Write web content and marketing materials with salary range ₹3-12 LPA."
  },
  {
    "title": "Copywriter",
    "category": "Media & Communication",
    "description": "Write advertising copy and marketing content with salary range ₹4-20 LPA."
  },
  {
    "title": "Technical Writer",
    "category": "Media & Communication",
    "description": "Create technical documentation and manuals with salary range ₹4-18 LPA."
  },
  {
    "title": "PR Manager",
    "category": "Media & Communication",
    "description": "Manage public relations and media communications with salary range ₹5-25 LPA."
  },
  {
    "title": "Social Media Manager",
    "category": "Media & Communication",
    "description": "Develop and execute social media strategies with salary range ₹4-20 LPA."
  },
  {
    "title": "Primary School Teacher",
    "category": "Education & Research",
    "description": "Teach elementary education and early childhood development with salary range ₹3-10 LPA."
  },
  {
    "title": "Secondary School Teacher",
    "category": "Education & Research",
    "description": "Teach middle school subjects and curriculum with salary range ₹3-12 LPA."
  },
  {
    "title": "High School Teacher",
    "category": "Education & Research",
    "description": "Teach senior classes and prepare students for higher education with salary range ₹4-15 LPA."
  },
  {
    "title": "College Lecturer",
    "category": "Education & Research",
    "description": "Teach undergraduate courses and conduct academic research with salary range ₹4-18 LPA."
  },
  {
    "title": "Assistant Professor",
    "category": "Education & Research",
    "description": "Conduct university teaching and academic research with salary range ₹6-25 LPA."
  },
  {
    "title": "Associate Professor",
    "category": "Education & Research",
    "description": "Lead academic programs and advanced research with salary range ₹8-35 LPA."
  },
  {
    "title": "Professor",
    "category": "Education & Research",
    "description": "Lead academic departments and conduct high-level research with salary range ₹10-50 LPA."
  },
  {
    "title": "Research Scientist",
    "category": "Education & Research",
    "description": "Conduct scientific research and development with salary range ₹6-35 LPA."
  },
  {
    "title": "Advocate",
    "category": "Legal & Government",
    "description": "Practice law and provide legal representation with salary range ₹5 LPA-1 Cr+."
  },
  {
    "title": "Corporate Lawyer",
    "category": "Legal & Government",
    "description": "Handle business law and corporate legal matters with salary range ₹8-80 LPA."
  },
  {
    "title": "Criminal Lawyer",
    "category": "Legal & Government",
    "description": "Defend clients in criminal cases and litigation with salary range ₹6 LPA-1 Cr+."
  },
  {
    "title": "Civil Lawyer",
    "category": "Legal & Government",
    "description": "Handle civil litigation and legal disputes with salary range ₹5-60 LPA."
  },
  {
    "title": "Judge",
    "category": "Legal & Government",
    "description": "Preside over court proceedings and legal decisions with salary range ₹10-50 LPA."
  },
  {
    "title": "IAS Officer",
    "category": "Legal & Government",
    "description": "Serve in administrative positions in government with salary range ₹8-25 LPA + perks."
  },
  {
    "title": "IPS Officer",
    "category": "Legal & Government",
    "description": "Lead police services and law enforcement with salary range ₹8-25 LPA + perks."
  },
  {
    "title": "IFS Officer",
    "category": "Legal & Government",
    "description": "Represent India in foreign diplomatic services with salary range ₹8-25 LPA + perks."
  },
  {
    "title": "Agricultural Scientist",
    "category": "Agriculture & Environmental",
    "description": "Conduct research in agriculture and crop science with salary range ₹5-20 LPA."
  },
  {
    "title": "Agronomist",
    "category": "Agriculture & Environmental",
    "description": "Manage crop production and agricultural practices with salary range ₹4-16 LPA."
  },
  {
    "title": "Environmental Scientist",
    "category": "Agriculture & Environmental",
    "description": "Study environmental issues and conduct research with salary range ₹5-20 LPA."
  },
  {
    "title": "Environmental Consultant",
    "category": "Agriculture & Environmental",
    "description": "Provide environmental advisory and consulting services with salary range ₹5-22 LPA."
  },
  {
    "title": "Wildlife Biologist",
    "category": "Agriculture & Environmental",
    "description": "Study and conserve wildlife and animal habitats with salary range ₹4-16 LPA."
  },
  {
    "title": "Veterinarian",
    "category": "Agriculture & Environmental",
    "description": "Provide medical care for animals and livestock with salary range ₹5-30 LPA."
  },
  {
    "title": "Electrician",
    "category": "Skilled Trades & Manufacturing",
    "description": "Install and repair electrical systems and wiring with salary range ₹3-10 LPA."
  },
  {
    "title": "Plumber",
    "category": "Skilled Trades & Manufacturing",
    "description": "Install and maintain plumbing systems with salary range ₹3-10 LPA."
  },
  {
    "title": "Carpenter",
    "category": "Skilled Trades & Manufacturing",
    "description": "Work with wood and create furniture and structures with salary range ₹3-12 LPA."
  },
  {
    "title": "Welder",
    "category": "Skilled Trades & Manufacturing",
    "description": "Join metals and perform welding operations with salary range ₹3-12 LPA."
  },
  {
    "title": "Auto Mechanic",
    "category": "Skilled Trades & Manufacturing",
    "description": "Repair and maintain vehicles and automotive systems with salary range ₹3-12 LPA."
  },
  {
    "title": "Production Supervisor",
    "category": "Skilled Trades & Manufacturing",
    "description": "Supervise manufacturing operations and production lines with salary range ₹4-15 LPA."
  },
  {
    "title": "Quality Control Inspector",
    "category": "Skilled Trades & Manufacturing",
    "description": "Ensure product quality and manufacturing standards with salary range ₹3-12 LPA."
  },
  {
    "title": "Machine Operator",
    "category": "Skilled Trades & Manufacturing",
    "description": "Operate CNC machines and manufacturing equipment with salary range ₹3-10 LPA."
  },
  {
    "title": "Sales Executive",
    "category": "Sales & Marketing",
    "description": "Sell products and services to customers with salary range ₹3-15 LPA."
  },
  {
    "title": "Business Development Executive",
    "category": "Sales & Marketing",
    "description": "Develop new business opportunities and client relationships with salary range ₹4-18 LPA."
  },
  {
    "title": "Account Manager",
    "category": "Sales & Marketing",
    "description": "Manage client accounts and customer relationships with salary range ₹5-22 LPA."
  },
  {
    "title": "Sales Manager",
    "category": "Sales & Marketing",
    "description": "Lead sales teams and achieve revenue targets with salary range ₹6-28 LPA."
  },
  {
    "title": "Marketing Executive",
    "category": "Sales & Marketing",
    "description": "Execute marketing campaigns and promotional activities with salary range ₹4-15 LPA."
  },
  {
    "title": "Digital Marketing Manager",
    "category": "Sales & Marketing",
    "description": "Manage online marketing and digital advertising with salary range ₹6-28 LPA."
  },
  {
    "title": "SEO Specialist",
    "category": "Sales & Marketing",
    "description": "Optimize websites for search engines and organic traffic with salary range ₹4-18 LPA."
  },
  {
    "title": "Social Media Marketing Manager",
    "category": "Sales & Marketing",
    "description": "Develop social media strategies and manage online presence with salary range ₹5-22 LPA."
  },
  {
    "title": "Brand Manager",
    "category": "Sales & Marketing",
    "description": "Develop brand strategy and manage brand positioning with salary range ₹7-30 LPA."
  },
  {
    "title": "Hotel Manager",
    "category": "Hospitality & Tourism",
    "description": "Manage hotel operations and guest services with salary range ₹5-25 LPA."
  },
  {
    "title": "Chef",
    "category": "Hospitality & Tourism",
    "description": "Prepare culinary dishes and manage kitchen operations with salary range ₹4-25 LPA."
  },
  {
    "title": "Restaurant Manager",
    "category": "Hospitality & Tourism",
    "description": "Manage restaurant operations and customer service with salary range ₹4-18 LPA."
  },
  {
    "title": "Travel Agent",
    "category": "Hospitality & Tourism",
    "description": "Plan travel itineraries and provide travel services with salary range ₹3-12 LPA."
  },
  {
    "title": "Tour Manager",
    "category": "Hospitality & Tourism",
    "description": "Organize and manage tour operations and travel groups with salary range ₹3-15 LPA."
  },
  {
    "title": "Event Manager",
    "category": "Hospitality & Tourism",
    "description": "Plan and execute events and special occasions with salary range ₹5-25 LPA."
  },
  {
    "title": "Professional Athlete",
    "category": "Sports & Fitness",
    "description": "Compete in various sports at professional level with salary range ₹5 Lakh-50 Cr+."
  },
  {
    "title": "Sports Coach",
    "category": "Sports & Fitness",
    "description": "Train athletes and develop sports skills with salary range ₹3-25 LPA."
  },
  {
    "title": "Fitness Trainer",
    "category": "Sports & Fitness",
    "description": "Provide personal training and fitness guidance with salary range ₹3-15 LPA."
  },
  {
    "title": "Yoga Instructor",
    "category": "Sports & Fitness",
    "description": "Teach yoga and mindfulness practices with salary range ₹3-12 LPA."
  },
  {
    "title": "Sports Nutritionist",
    "category": "Sports & Fitness",
    "description": "Provide dietary guidance for athletic performance with salary range ₹4-18 LPA."
  },
  {
    "title": "Social Worker",
    "category": "Social Services & NGO",
    "description": "Provide community service and social support with salary range ₹3-12 LPA."
  },
  {
    "title": "NGO Manager",
    "category": "Social Services & NGO",
    "description": "Manage non-profit organizations and social programs with salary range ₹4-18 LPA."
  },
  {
    "title": "Community Development Officer",
    "category": "Social Services & NGO",
    "description": "Implement social development programs in communities with salary range ₹4-14 LPA."
  },
  {
    "title": "Career Counselor",
    "category": "Social Services & NGO",
    "description": "Provide career guidance and counseling services with salary range ₹4-15 LPA."
  },
  {
    "title": "Prompt Engineer",
    "category": "Emerging & Future Careers",
    "description": "Optimize AI prompts and language model interactions with salary range ₹8-35 LPA."
  },
  {
    "title": "AI Ethics Specialist",
    "category": "Emerging & Future Careers",
    "description": "Ensure responsible AI development and ethical guidelines with salary range ₹10-40 LPA."
  },
  {
    "title": "Conversational AI Designer",
    "category": "Emerging & Future Careers",
    "description": "Design chatbots and conversational AI systems with salary range ₹7-28 LPA."
  },
  {
    "title": "Computer Vision Engineer",
    "category": "Emerging & Future Careers",
    "description": "Develop image recognition and computer vision AI with salary range ₹10-40 LPA."
  },
  {
    "title": "NLP Engineer",
    "category": "Emerging & Future Careers",
    "description": "Work on natural language processing and AI language systems with salary range ₹10-40 LPA."
  },
  {
    "title": "Sustainability Manager",
    "category": "Emerging & Future Careers",
    "description": "Implement green operations and sustainability practices with salary range ₹7-30 LPA."
  },
  {
    "title": "Carbon Accountant",
    "category": "Emerging & Future Careers",
    "description": "Measure and manage carbon footprint for organizations with salary range ₹6-25 LPA."
  },
  {
    "title": "Web3 Developer",
    "category": "Emerging & Future Careers",
    "description": "Build decentralized applications and blockchain solutions with salary range ₹10-45 LPA."
  },
  {
    "title": "Metaverse Architect",
    "category": "Emerging & Future Careers",
    "description": "Design virtual worlds and metaverse experiences with salary range ₹10-40 LPA."
  },
  {
    "title": "Drone Pilot",
    "category": "Emerging & Future Careers",
    "description": "Operate unmanned aircraft for various applications with salary range ₹4-18 LPA."
  },
  {
    "title": "3D Printing Specialist",
    "category": "Emerging & Future Careers",
    "description": "Work with additive manufacturing and 3D printing technology with salary range ₹5-22 LPA."
  },
  {
    "title": "Telemedicine Coordinator",
    "category": "Emerging & Future Careers",
    "description": "Manage remote healthcare services and digital health with salary range ₹5-20 LPA."
  },
  {
    "title": "Health Informatics Specialist",
    "category": "Emerging & Future Careers",
    "description": "Manage medical data and healthcare information systems with salary range ₹6-25 LPA."
  }
]
intern_df = pd.DataFrame(internships)

# ==========================================================
# 🔧 Helper Functions
# ==========================================================
def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.filename.split('.')[-1].lower()
    if file_type == "pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return "".join(page.extract_text() for page in reader.pages)
    elif file_type == "docx":
        return docx2txt.process(uploaded_file)
    elif file_type == "txt":
        return uploaded_file.read().decode("utf-8")
    return ""

def detect_and_translate_to_english(text, lang_choice):
    if lang_choice == "English": return text
    elif lang_choice == "Hindi": return GoogleTranslator(source='hi', target='en').translate(text)
    elif lang_choice == "Odia": return GoogleTranslator(source='or', target='en').translate(text)
    return text

def translate_from_english(text, lang_choice):
    if lang_choice == "English": return text
    elif lang_choice == "Hindi": return GoogleTranslator(source='en', target='hi').translate(text)
    elif lang_choice == "Odia": return GoogleTranslator(source='en', target='or').translate(text)
    return text

def extract_skills(text):
    keywords = ['python','java','c++','machine learning','deep learning','ai','data science','flask','django',
                'html','css','javascript','react','node','sql','aws','azure','docker','kubernetes','cybersecurity',
                'iot','arduino','raspberry pi','cloud','tensorflow','pytorch','nlp','big data']
    text = text.lower()
    return list(set([kw for kw in keywords if kw in text]))

def store_profile(name, email, skills, education, experience):
    c.execute("INSERT INTO profiles VALUES (?, ?, ?, ?, ?)", (name, email, skills, education, experience))
    conn.commit()

def calculate_readiness_score(user_skills):
    # Example: readiness = (matched skills / total skills) * 100
    total_skills = 26  # Total number of skills in keywords list
    matched = len(user_skills)
    return int((matched / total_skills) * 100)

def get_internship_recommendations(user_text, domain_filter=None):
    user_skills = extract_skills(user_text)
    df = intern_df.copy()
    if domain_filter and domain_filter != "All":
        df = df[df['category'] == domain_filter]

    embeddings_interns = model.encode(df['description'].tolist(), convert_to_tensor=True)
    embedding_user = model.encode(user_text, convert_to_tensor=True)
    cosine_scores = util.cos_sim(embedding_user, embeddings_interns)[0].cpu().tolist()

    keyword_scores = []
    for desc in df['description']:
        desc_lower = desc.lower()
        match_count = sum(1 for s in user_skills if s in desc_lower)
        keyword_scores.append(match_count / (len(user_skills) + 1e-6))

    final_scores = [(0.7 * cosine_scores[i]) + (0.3 * keyword_scores[i]) for i in range(len(cosine_scores))]
    df['similarity'] = final_scores
    df = df.sort_values(by='similarity', ascending=False).head(5)
    return df, user_skills

# ==========================================================
# 🌐 Routes
# ==========================================================
@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = None
    chart_html = None
    detected_skills = None
    readiness_score = None
    readiness_chart = None

    if request.method == "POST":
        lang_choice = request.form.get("language")
        domain_filter = request.form.get("domain")

        name = request.form.get("name")
        email = request.form.get("email")
        skills = request.form.get("skills")
        education = request.form.get("education")
        experience = request.form.get("experience")

        uploaded_file = request.files.get("resume")
        resume_text = ""

        if uploaded_file and uploaded_file.filename != "":
            resume_text = extract_text_from_file(uploaded_file)

        user_text = resume_text or f"{skills} {education} {experience}"
        if not user_text.strip():
            flash("⚠ Please upload a resume or fill out your profile.", "danger")
            return redirect(url_for("home"))

        # Save profile
        if name and email:
            store_profile(name, email, skills, education, experience)

        # Translate + Recommend
        user_text_en = detect_and_translate_to_english(user_text, lang_choice)
        recommendations, detected_skills = get_internship_recommendations(user_text_en, domain_filter)

        # Translate results to chosen language
        recommendations['title'] = [translate_from_english(t, lang_choice) for t in recommendations['title']]
        recommendations['description'] = [translate_from_english(d, lang_choice) for d in recommendations['description']]

        # 🎯 Readiness Score
        readiness_score = calculate_readiness_score(detected_skills)

        # 📊 Readiness Gauge Chart
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=readiness_score,
            title={'text': "Profile Readiness (%)"},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': "green"},
                   'steps': [
                       {'range': [0, 40], 'color': "red"},
                       {'range': [40, 70], 'color': "yellow"},
                       {'range': [70, 100], 'color': "lightgreen"}
                   ]}
        ))
        readiness_chart = gauge_fig.to_html(full_html=False)

        # 📈 Internship Recommendation Chart
        fig = px.bar(
            recommendations, x='title', y='similarity', color='category',
            text=[f"{round(v*100, 2)}%" for v in recommendations['similarity']],
            title="Top Matches (AI Similarity)"
        )
        fig.update_traces(textposition='outside')
        fig.update_layout(yaxis_range=[0, 1], template='plotly_white')
        chart_html = fig.to_html(full_html=False)

        if recommendations is not None and recommendations.empty:
            recommendations = None

    return render_template("index.html",
                           recommendations=recommendations,
                           chart_html=chart_html,
                           detected_skills=detected_skills,
                           readiness_score=readiness_score,
                           readiness_chart=readiness_chart)

# ==========================================================
# 🚀 Run App
# ==========================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)