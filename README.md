# INTERN PATH AI
**A Smart Internship Guidance and Readiness System**

---

## Introduction

Students struggle significantly in identifying, filtering, and applying to internships that match their skills and interests. Existing platforms provide listings but lack personalization, guidance, and contextual recommendations.

This project aims to build an intelligent internship discovery platform that:
- Scrapes internship data from multiple online sources
- Extracts and normalizes relevant information such as skills, location, stipend, etc.
- Builds a searchable database of internships
- Integrates an NLP-based chatbot to assist users with personalized recommendations and queries

---

## Problem Statement

Most students struggle to find internships aligned with their skills because platforms lack clarity on requirements, provide no meaningful feedback after rejection, and do nothing to improve weak resumes or guide skill development.

---

## Gap Identified

Existing internship/job platforms (e.g. LinkedIn, Naukri, Internshala) provide listings but lack:
- **Centralized Aggregation**: No unified platform that combines data from multiple sources
- **Intelligent Filtering**: Basic search only; no semantic skill-based filtering
- **Personalized Recommendations**: No matching based on user skills or profile
- **Conversational Assistance**: No chatbot to guide users interactively
- **NLP-driven Insights**: No extraction of required skills and eligibility via NLP

This gap indicates the need for a centralized, intelligent, user-adaptive system.

---

## Proposed Solution

The proposed solution is an AI-assisted Internship Recommendation System that:
- Scrapes internship listings from multiple online sources
- Pre-processes and normalizes job descriptions
- Performs skill extraction using Natural Language Processing
- Utilizes a database to store structured internship data
- Provides a chatbot interface to query internships conversationally
- Recommends internships based on user skills and interest
- Supports filters like remote/on-site, stipend range, and domain

**Key innovation**: Integration of web scraping, NLP, and conversational AI for internship discovery.

---

## Module Description

The system consists of the following major modules:

### 1. Web Scraping Module
- Extracts internship data using BeautifulSoup / Selenium / Playwright
- Handles dynamic content and pagination

### 2. Data Normalization & Storage Module
- Cleans and structures scraped data
- Stores data in PostgreSQL / MongoDB

### 3. NLP Skill Extraction Module
- Extracts skills and entities using spaCy / BERT
- Identifies domain, duration, and requirements

### 4. User Profile & Matching Module
- Collects user skills, interests, and preferences
- Performs semantic matching and ranks internships

### 5. Chatbot Query Module
- NLP-based chatbot for internship queries
- Supports intent classification and entity extraction

### 6. User Interface Module
- Web-based interface for chatbot interaction
- Displays internship details and application links

---

## Software Requirement Specification

### User Interface

#### Student Dashboard
- Profile creation (skills, semester, projects)
- Internship recommendations with reasons
- Internship Readiness Score display

#### Internship Listing Page
- Scraped internships from multiple platforms
- Filter by skills, domain, location, type

#### Chatbot Interface
- Text-based conversational UI
- Answers internship-related queries

#### Fake Internship Checker Page
- Input internship URL
- Displays risk level (Low / Medium / High)

#### Resume Quality Assessment Page
- Resume upload (PDF/DOC) with validation
- Resume Quality Score (0–100) display
- Section-wise assessment (Skills, Projects, Education, Formatting)
- Actionable suggestions to improve resume quality

**UI Characteristics**:
- Responsive design (mobile + desktop)
- Simple navigation

---

## Software and Hardware Requirements

### Software Requirements
- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **Web Scraping**: BeautifulSoup / Requests
- **NLP Libraries**: spaCy / NLTK
- **Database**: PostgreSQL
- **OS**: Windows / Linux
- **Other dependencies**: Web driver for scraping (if dynamic)

### Hardware Requirements
- **Processor**: Intel i3 or above
- **RAM**: Minimum 4 GB
- **Storage**: 10 GB free disk
- **Internet**: Required (for scraping & APIs)

---

## Functional Requirements

### 1. User Registration & Profile Management
Users can enter:
- Skills
- Semester
- Projects
- Experience (optional)

### 2. Internship Data Collection
System scrapes internship data from:
- Company websites
- Internship portals

Extracts:
- Role
- Required skills
- Company details

### 3. Internship Recommendation System
- Matches user skills with internship requirements
- Calculates skill match percentage
- Displays reason for recommendation

### 4. Internship Readiness Score
System calculates score based on:
- Skill match
- Projects
- Resume keywords
- Experience (optional)

Displays:
- Score out of 100
- Recommendation message

### 5. NLP Chatbot
Chatbot answers:
- Internship guidance queries
- Skill improvement suggestions

Uses:
- Keyword extraction
- Intent classification
- Rule-based responses

### 6. Fake Internship Detection
User provides internship link. System checks:
- Domain credibility
- Payment-related keywords
- Contact authenticity
- Displays risk level

---

## Database Requirements

### Tables Required:

#### 1. Users
- user_id (PK)
- Name
- Semester
- Skills
- Projects
- Experience

#### 2. Internships
- internship_id (PK)
- Title
- Company
- skills_required
- source_url

#### 3. Recommendations
- recommendation_id (PK)
- user_id (FK)
- internship_id (FK)
- skill_match_percentage

#### 4. Skill_Gaps
- gap_id (PK)
- user_id (FK)
- missing_skills

#### 5. Fake_Internship_Check
- check_id (PK)
- internship_url
- risk_level
- reason

---

## Non-Functional Requirements

### Performance
- System should respond within 2–3 seconds
- Scraping tasks run asynchronously

### Security
- No sensitive user data exposed
- Input validation for URLs
- Protection against malicious links

### Scalability
- Can handle increasing number of users
- Internship sources can be extended

### Reliability
- Accurate recommendations based on real data
- Rule-based logic ensures predictable results

### Usability
- Easy to use for non-technical students
- Clear explanations and guidance

---

## Conclusion

- The project successfully provides a smart internship guidance platform for students
- Real internship data is collected using web scraping, ensuring relevant and up-to-date opportunities
- The system recommends internships based on skills, semester, and readiness level
- An Internship Readiness Score helps students evaluate their preparation before applying
- The NLP-based chatbot assists students with internship-related queries
- The fake internship detection feature helps users identify potentially fraudulent opportunities
- A rule-based approach ensures transparency and easy implementation
- The system reduces unnecessary rejections and supports better career planning

---

## References

1. https://ieeexplore.ieee.org/document/10923842/
2. https://ieeexplore.ieee.org/document/10544738
