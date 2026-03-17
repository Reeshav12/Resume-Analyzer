from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Literal
from urllib import error as urllib_error
from urllib import request as urllib_request

from pydantic import BaseModel, Field

from .config import settings


# Skills list drives both keyword detection and the learning-plan suggestions.
# Keep these names human-readable because we display them to users.
SKILLS: list[str] = [
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",
    "TypeScript",
    "HTML",
    "CSS",
    "Tailwind CSS",
    "React",
    "Redux",
    "Next.js",
    "Node.js",
    "Express.js",
    "GraphQL",
    "FastAPI",
    "Django",
    "Flask",
    "REST APIs",
    "SQL",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Git",
    "Linux",
    "Docker",
    "Kubernetes",
    "Terraform",
    "CI/CD",
    "Jenkins",
    "Nginx",
    "Cloud Computing",
    "AWS",
    "Azure",
    "GCP",
    "Data Science",
    "Machine Learning",
    "NLP",
    "Computer Vision",
    "Deep Learning",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Tableau",
    "Power BI",
    "Hadoop",
    "Spark",
    "Airflow",
    "ETL",
    "BigQuery",
    "Cyber Security",
    "Network Security",
    "Penetration Testing",
    "Wireshark",
    "Metasploit",
    "Nmap",
    "Embedded Systems",
    "AutoCAD",
    "Selenium",
    "Playwright",
    "PyTest",
    "JUnit",
]


LEARNING_RESOURCES: dict[str, list[dict[str, str]]] = {
    "Python": [
        {"title": "Python for Everybody (Coursera)", "url": "https://www.coursera.org/specializations/python"},
        {"title": "Python Tutorial (official docs)", "url": "https://docs.python.org/3/tutorial/"},
        {"title": "Scientific Computing with Python (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/"},
        {"title": "Python Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=rfscVS0vtbw"},
    ],
    "Java": [
        {"title": "Java Programming (Mooc.fi)", "url": "https://java-programming.mooc.fi/"},
        {"title": "Java Tutorials (Oracle)", "url": "https://docs.oracle.com/javase/tutorial/"},
        {"title": "Java Course (Codecademy)", "url": "https://www.codecademy.com/learn/learn-java"},
        {"title": "Java Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=GoXwIVyNvX0"},
    ],
    "C": [
        {"title": "C Programming (Learn-C)", "url": "https://www.learn-c.org/"},
        {"title": "C Reference (cppreference)", "url": "https://en.cppreference.com/w/c"},
    ],
    "C++": [
        {"title": "C++ Tutorial (LearnCpp)", "url": "https://www.learncpp.com/"},
        {"title": "C++ Reference (cppreference)", "url": "https://en.cppreference.com/w/cpp"},
    ],
    "JavaScript": [
        {"title": "JavaScript Guide (MDN)", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"},
        {"title": "JavaScript Algorithms and Data Structures (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/"},
        {"title": "JavaScript (Codecademy)", "url": "https://www.codecademy.com/learn/introduction-to-javascript"},
        {"title": "JavaScript Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=PkZNo7MFNFg"},
    ],
    "TypeScript": [
        {"title": "TypeScript Handbook (Microsoft)", "url": "https://www.typescriptlang.org/docs/handbook/intro.html"},
        {"title": "TypeScript for JavaScript Programmers", "url": "https://www.typescriptlang.org/docs/handbook/typescript-in-5-minutes.html"},
        {"title": "TypeScript Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=30LWjhZzg4s"},
    ],
    "HTML": [
        {"title": "HTML (MDN)", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML"},
        {"title": "Responsive Web Design (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
    ],
    "CSS": [
        {"title": "CSS (MDN)", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS"},
        {"title": "Responsive Web Design (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/"},
    ],
    "React": [
        {"title": "React Learn (official)", "url": "https://react.dev/learn"},
        {"title": "Full Stack Open: React", "url": "https://fullstackopen.com/en/"},
        {"title": "React Course (Scrimba)", "url": "https://scrimba.com/learn/learnreact"},
        {"title": "React Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=bMknfKXIFA8"},
    ],
    "Tailwind CSS": [
        {"title": "Tailwind CSS Docs (official)", "url": "https://tailwindcss.com/docs"},
        {"title": "Tailwind CSS Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=ft30zcMlFao"},
    ],
    "Redux": [
        {"title": "Redux Essentials (Redux Toolkit)", "url": "https://redux.js.org/tutorials/essentials/part-1-overview-concepts"},
        {"title": "Redux Toolkit Crash Course (YouTube)", "url": "https://www.youtube.com/watch?v=9zySeP5vH9c"},
    ],
    "Next.js": [
        {"title": "Next.js Learn (official)", "url": "https://nextjs.org/learn"},
        {"title": "Next.js Docs: App Router", "url": "https://nextjs.org/docs/app"},
        {"title": "Next.js Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=ZVnjOPwW4ZA"},
    ],
    "Node.js": [
        {"title": "Node.js Learn (official)", "url": "https://nodejs.org/en/learn"},
        {"title": "Node.js Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=Oe421EPjeBE"},
    ],
    "Express.js": [
        {"title": "Express Guide (official)", "url": "https://expressjs.com/en/guide/routing.html"},
        {"title": "Express.js Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=L72fhGm1tfE"},
    ],
    "GraphQL": [
        {"title": "GraphQL Learn (official)", "url": "https://graphql.org/learn/"},
        {"title": "GraphQL Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=ed8SzALpx1Q"},
    ],
    "FastAPI": [
        {"title": "FastAPI Tutorial (official)", "url": "https://fastapi.tiangolo.com/tutorial/"},
        {"title": "FastAPI Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=0sOvCWFmrtA"},
    ],
    "Django": [
        {"title": "Django Documentation (official)", "url": "https://docs.djangoproject.com/en/stable/"},
        {"title": "Django for Beginners (Mozilla)", "url": "https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django"},
        {"title": "Django Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=F5mRW0jo-U4"},
    ],
    "Flask": [
        {"title": "Flask Quickstart (official)", "url": "https://flask.palletsprojects.com/en/stable/quickstart/"},
        {"title": "Flask Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=Z1RJmh_OqeA"},
    ],
    "REST APIs": [
        {"title": "REST API Tutorial (MDN)", "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Client-side_web_APIs/Introduction"},
        {"title": "REST API Best Practices (Microsoft Learn)", "url": "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design"},
        {"title": "REST API Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=qbLc5a9jdXo"},
    ],
    "SQL": [
        {"title": "SQLBolt", "url": "https://sqlbolt.com/"},
        {"title": "SQL (Khan Academy)", "url": "https://www.khanacademy.org/computing/computer-programming/sql"},
        {"title": "Learn SQL (Codecademy)", "url": "https://www.codecademy.com/learn/learn-sql"},
        {"title": "SQL Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY"},
    ],
    "PostgreSQL": [
        {"title": "PostgreSQL Tutorial (official)", "url": "https://www.postgresql.org/docs/current/tutorial.html"},
        {"title": "SQLBolt", "url": "https://sqlbolt.com/"},
        {"title": "PostgreSQL Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=qw--VYLpxG4"},
    ],
    "MySQL": [
        {"title": "MySQL Tutorial (official)", "url": "https://dev.mysql.com/doc/refman/8.0/en/tutorial.html"},
        {"title": "SQLBolt", "url": "https://sqlbolt.com/"},
        {"title": "MySQL Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=7S_tz1z_5bA"},
    ],
    "MongoDB": [
        {"title": "MongoDB University", "url": "https://learn.mongodb.com/"},
        {"title": "MongoDB Manual", "url": "https://www.mongodb.com/docs/manual/"},
    ],
    "Git": [
        {"title": "Pro Git (book)", "url": "https://git-scm.com/book/en/v2"},
        {"title": "GitHub Skills", "url": "https://skills.github.com/"},
        {"title": "Learn Git and GitHub (Coursera)", "url": "https://www.coursera.org/learn/introduction-git-github"},
    ],
    "Linux": [
        {"title": "Linux Journey", "url": "https://linuxjourney.com/"},
        {"title": "The Linux Command Line (book)", "url": "https://linuxcommand.org/tlcl.php"},
        {"title": "Linux for Beginners (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=sWbUDq4S6Y8"},
    ],
    "Docker": [
        {"title": "Docker Get Started (official)", "url": "https://docs.docker.com/get-started/"},
        {"title": "Docker for Beginners (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=fqMOX6JJhGo"},
    ],
    "Kubernetes": [
        {"title": "Kubernetes Basics (official)", "url": "https://kubernetes.io/docs/tutorials/kubernetes-basics/"},
        {"title": "Kubernetes (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=d6WC5n9G_sM"},
    ],
    "Terraform": [
        {"title": "Terraform Learn (HashiCorp)", "url": "https://developer.hashicorp.com/terraform/tutorials"},
        {"title": "Terraform Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=SLB_c_ayRMo"},
    ],
    "CI/CD": [
        {"title": "CI/CD Concepts (Atlassian)", "url": "https://www.atlassian.com/continuous-delivery/ci-vs-ci-vs-cd"},
        {"title": "CI/CD Pipeline Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=Gg4bLk8cGNo"},
    ],
    "Jenkins": [
        {"title": "Jenkins User Documentation (official)", "url": "https://www.jenkins.io/doc/"},
        {"title": "Jenkins Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=6YZvp2GwT0A"},
    ],
    "Nginx": [
        {"title": "NGINX Beginner's Guide (official docs)", "url": "https://nginx.org/en/docs/beginners_guide.html"},
        {"title": "NGINX Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=9t9Mp0BGnyI"},
    ],
    "Cloud Computing": [
        {"title": "Google Cloud Skills Boost", "url": "https://www.cloudskillsboost.google/"},
        {"title": "AWS Skill Builder", "url": "https://skillbuilder.aws/"},
        {"title": "Microsoft Learn: Azure", "url": "https://learn.microsoft.com/en-us/training/azure/"},
        {"title": "Cloud Computing Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=2LaAJq1lB1Q"},
    ],
    "AWS": [
        {"title": "AWS Skill Builder", "url": "https://skillbuilder.aws/"},
        {"title": "AWS Cloud Practitioner Essentials (digital)", "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials"},
        {"title": "AWS Cloud Practitioner Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=SOTamWNgDKc"},
    ],
    "Azure": [
        {"title": "Microsoft Learn: Azure Fundamentals", "url": "https://learn.microsoft.com/en-us/training/paths/azure-fundamentals/"},
        {"title": "Azure Fundamentals Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=NKEFWyqJ5XA"},
    ],
    "GCP": [
        {"title": "Google Cloud Skills Boost", "url": "https://www.cloudskillsboost.google/"},
        {"title": "Google Cloud: Training", "url": "https://cloud.google.com/training"},
        {"title": "Google Cloud Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=jpno8FSqpc8"},
    ],
    "Data Science": [
        {"title": "Data Science (Kaggle Learn)", "url": "https://www.kaggle.com/learn"},
        {"title": "Data Science: Foundations (Coursera)", "url": "https://www.coursera.org/specializations/jhu-data-science"},
    ],
    "Machine Learning": [
        {"title": "Machine Learning (Coursera)", "url": "https://www.coursera.org/learn/machine-learning"},
        {"title": "Intro to Machine Learning (Kaggle)", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
        {"title": "Machine Learning Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=NWONeJKn6kc"},
    ],
    "NLP": [
        {"title": "NLP Course (Hugging Face)", "url": "https://huggingface.co/learn/nlp-course/chapter1/1"},
        {"title": "NLP with Python Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=X2vAabgKiuM"},
    ],
    "Computer Vision": [
        {"title": "OpenCV Tutorials (official)", "url": "https://docs.opencv.org/4.x/d9/df8/tutorial_root.html"},
        {"title": "Computer Vision Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=O5xeyoRL95U"},
    ],
    "Deep Learning": [
        {"title": "Deep Learning Specialization (Coursera)", "url": "https://www.coursera.org/specializations/deep-learning"},
        {"title": "Deep Learning (fast.ai)", "url": "https://course.fast.ai/"},
        {"title": "Deep Learning Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=VyWAvY2CF9c"},
    ],
    "TensorFlow": [
        {"title": "TensorFlow Tutorials (official)", "url": "https://www.tensorflow.org/tutorials"},
        {"title": "Intro to TensorFlow for AI (Coursera)", "url": "https://www.coursera.org/learn/introduction-tensorflow"},
    ],
    "PyTorch": [
        {"title": "PyTorch Tutorials (official)", "url": "https://pytorch.org/tutorials/"},
        {"title": "Deep Learning with PyTorch (Udacity)", "url": "https://www.udacity.com/course/deep-learning-pytorch--ud188"},
    ],
    "Pandas": [
        {"title": "Pandas Getting Started (official)", "url": "https://pandas.pydata.org/docs/getting_started/index.html"},
        {"title": "Data Analysis with Python (freeCodeCamp)", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/"},
        {"title": "Pandas Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=vmEHCJofslg"},
    ],
    "NumPy": [
        {"title": "NumPy Quickstart (official)", "url": "https://numpy.org/doc/stable/user/quickstart.html"},
        {"title": "NumPy Tutorial (Kaggle)", "url": "https://www.kaggle.com/learn/pandas"},
        {"title": "NumPy Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=QUT1VHiLmmI"},
    ],
    "Scikit-learn": [
        {"title": "scikit-learn Tutorials (official)", "url": "https://scikit-learn.org/stable/tutorial/index.html"},
        {"title": "Machine Learning (Kaggle)", "url": "https://www.kaggle.com/learn/intro-to-machine-learning"},
    ],
    "Tableau": [
        {"title": "Tableau Training Videos", "url": "https://www.tableau.com/learn/training"},
        {"title": "Data Visualization with Tableau (Coursera)", "url": "https://www.coursera.org/learn/data-visualization-tableau"},
        {"title": "Tableau Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=TPMlZxRRaBQ"},
    ],
    "Power BI": [
        {"title": "Microsoft Learn: Power BI", "url": "https://learn.microsoft.com/en-us/training/powerplatform/power-bi/"},
        {"title": "Getting Started with Power BI", "url": "https://learn.microsoft.com/en-us/power-bi/fundamentals/"},
        {"title": "Power BI Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=AGrl-H87pRU"},
    ],
    "Hadoop": [
        {"title": "Apache Hadoop (official docs)", "url": "https://hadoop.apache.org/docs/"},
        {"title": "Hadoop Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=1vbXmCrkT3Y"},
    ],
    "Spark": [
        {"title": "Apache Spark (official docs)", "url": "https://spark.apache.org/docs/latest/"},
        {"title": "Apache Spark Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=_C8kWso4ne4"},
    ],
    "Airflow": [
        {"title": "Apache Airflow (official docs)", "url": "https://airflow.apache.org/docs/"},
        {"title": "Airflow Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=K9AnJ9_ZAXE"},
    ],
    "ETL": [
        {"title": "ETL Concepts (AWS)", "url": "https://aws.amazon.com/what-is/etl/"},
        {"title": "ETL and Data Pipelines (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=3pZCP0z_7YQ"},
    ],
    "BigQuery": [
        {"title": "BigQuery Documentation (Google)", "url": "https://cloud.google.com/bigquery/docs"},
        {"title": "BigQuery Full Course (YouTube)", "url": "https://www.youtube.com/watch?v=3G8wqZV0fWk"},
    ],
    "Cyber Security": [
        {"title": "Cybersecurity Specialization (Coursera)", "url": "https://www.coursera.org/specializations/cyber-security"},
        {"title": "TryHackMe (hands-on)", "url": "https://tryhackme.com/"},
        {"title": "OWASP Top 10", "url": "https://owasp.org/www-project-top-ten/"},
        {"title": "Cybersecurity Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=U_P23SqJaDc"},
    ],
    "Network Security": [
        {"title": "Network Security (Coursera)", "url": "https://www.coursera.org/learn/network-security"},
        {"title": "Cisco Networking Academy", "url": "https://www.netacad.com/"},
    ],
    "Penetration Testing": [
        {"title": "Penetration Testing (TryHackMe paths)", "url": "https://tryhackme.com/paths"},
        {"title": "Kali Linux Revealed (book)", "url": "https://kali.training/"},
        {"title": "Penetration Testing Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=3Kq1MIfTWCE"},
    ],
    "Wireshark": [
        {"title": "Wireshark Documentation (official)", "url": "https://www.wireshark.org/docs/"},
        {"title": "Wireshark Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=lb1Dw0elw0Q"},
    ],
    "Metasploit": [
        {"title": "Metasploit Unleashed (Offensive Security)", "url": "https://www.offensive-security.com/metasploit-unleashed/"},
        {"title": "Metasploit Tutorial (YouTube)", "url": "https://www.youtube.com/watch?v=8lR27r8Y_ik"},
    ],
    "Nmap": [
        {"title": "Nmap Reference Guide (official)", "url": "https://nmap.org/book/man.html"},
        {"title": "Nmap Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=4t4kBkMsDbQ"},
    ],
    "Embedded Systems": [
        {"title": "Embedded Systems (Coursera)", "url": "https://www.coursera.org/learn/intro-embedded-systems"},
        {"title": "Embedded Systems (edX)", "url": "https://www.edx.org/learn/embedded-systems"},
        {"title": "Embedded Systems Full Course (YouTube)", "url": "https://www.youtube.com/watch?v=3oFqGQ9qP2M"},
    ],
    "AutoCAD": [
        {"title": "AutoCAD (Autodesk Learning)", "url": "https://www.autodesk.com/learn"},
        {"title": "AutoCAD Course (Udemy)", "url": "https://www.udemy.com/course/autocad-course/"},
        {"title": "AutoCAD Full Course (YouTube)", "url": "https://www.youtube.com/watch?v=VYbVhPrq1nM"},
    ],
    "Selenium": [
        {"title": "Selenium Documentation (official)", "url": "https://www.selenium.dev/documentation/"},
        {"title": "Selenium Full Course (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=j7VZsCCnptM"},
    ],
    "Playwright": [
        {"title": "Playwright Docs (official)", "url": "https://playwright.dev/docs/intro"},
        {"title": "Playwright Full Course (YouTube)", "url": "https://www.youtube.com/watch?v=H2-5ecFwHHQ"},
    ],
    "PyTest": [
        {"title": "pytest Documentation (official)", "url": "https://docs.pytest.org/en/stable/"},
        {"title": "pytest Tutorial (freeCodeCamp YouTube)", "url": "https://www.youtube.com/watch?v=cHYq1MRoyI0"},
    ],
    "JUnit": [
        {"title": "JUnit 5 User Guide (official)", "url": "https://junit.org/junit5/docs/current/user-guide/"},
        {"title": "JUnit Full Course (YouTube)", "url": "https://www.youtube.com/watch?v=flpmSXVTqBI"},
    ],
}


ROLE_CATALOG: dict[str, list[dict[str, str]]] = {
    "Software Development": [
        {
            "name": "Software Engineer",
            "description": "Design, develop, and maintain software applications using Python, Java, C++, Git, SQL, MongoDB, HTML, CSS, JavaScript, and software testing fundamentals.",
        },
        {
            "name": "Frontend Developer",
            "description": "Build responsive user interfaces using HTML, CSS, JavaScript, React, TypeScript, accessibility best practices, performance optimization, and API integration.",
        },
        {
            "name": "Backend Developer",
            "description": "Develop secure backend services using Python or Java, REST APIs, SQL, PostgreSQL, authentication, testing, cloud deployment, caching, and system integration.",
        },
        {
            "name": "Full Stack Developer",
            "description": "Work across frontend and backend using React, JavaScript, TypeScript, Python, SQL, REST APIs, Git, testing, and deployment workflows to deliver full product features.",
        },
        {
            "name": "React Developer",
            "description": "Build modern web interfaces using React, JavaScript, TypeScript, Redux, CSS, Tailwind CSS, performance optimization, and API integration.",
        },
        {
            "name": "Next.js Developer",
            "description": "Build SEO-friendly web apps using React, Next.js, TypeScript, Tailwind CSS, routing, data fetching, and deployment workflows.",
        },
        {
            "name": "Node.js Developer",
            "description": "Develop backend services using Node.js, Express.js, REST APIs, PostgreSQL, MongoDB, authentication, testing, and deployment.",
        },
        {
            "name": "Python Backend Developer",
            "description": "Build backend services using Python, FastAPI, Django, Flask, REST APIs, SQL, PostgreSQL, authentication, testing, and cloud deployment.",
        },
        {
            "name": "API Developer",
            "description": "Design and implement REST APIs and GraphQL services with authentication, validation, SQL databases, documentation, and reliable integrations.",
        },
        {
            "name": "Mobile App Developer",
            "description": "Build mobile products with strong UI development, API integration, state management, testing, app performance, and release workflows.",
        },
    ],
    "Data and AI": [
        {
            "name": "Data Scientist",
            "description": "Develop and optimize machine learning models and analyze large datasets using Python, SQL, Tableau, Power BI, TensorFlow, Hadoop, Spark, and statistical analysis.",
        },
        {
            "name": "AI/ML Engineer",
            "description": "Build and deploy AI models using TensorFlow, PyTorch, Python, NLP, Computer Vision, Deep Learning, model tuning, and data preprocessing.",
        },
        {
            "name": "Machine Learning Engineer",
            "description": "Train and deploy Machine Learning models using Python, Scikit-learn, TensorFlow, PyTorch, Pandas, NumPy, model evaluation, and production-ready APIs.",
        },
        {
            "name": "Data Analyst",
            "description": "Analyze datasets using SQL, Python, Pandas, Tableau, Power BI, dashboards, reporting, and clear business communication.",
        },
        {
            "name": "Data Engineer",
            "description": "Build ETL data pipelines using Python, SQL, Airflow, Spark, Hadoop, BigQuery, data quality checks, and performance optimization.",
        },
        {
            "name": "BI Analyst",
            "description": "Build dashboards and reporting systems using SQL, Tableau, Power BI, metrics definition, stakeholder reporting, and clean data modeling.",
        },
    ],
    "Cloud, DevOps and Security": [
        {
            "name": "DevOps Engineer",
            "description": "Automate infrastructure and delivery pipelines using Git, Linux, Docker, Kubernetes, Terraform, CI/CD, monitoring, and incident response workflows.",
        },
        {
            "name": "Cloud Engineer",
            "description": "Design and manage cloud systems using AWS, Azure, GCP, Cloud Computing, Python, automation, security controls, CI/CD, and scalable deployment practices.",
        },
        {
            "name": "Site Reliability Engineer",
            "description": "Operate reliable services using Linux, Docker, Kubernetes, Terraform, CI/CD, monitoring, performance troubleshooting, and incident response.",
        },
        {
            "name": "Cloud DevOps Engineer",
            "description": "Automate cloud infrastructure using AWS, Azure, GCP, Docker, Kubernetes, Terraform, Jenkins, CI/CD, and secure deployment practices.",
        },
        {
            "name": "Cyber Security Engineer",
            "description": "Implement firewalls, conduct vulnerability assessments, secure networks, and apply penetration testing, Network Security, Wireshark, Metasploit, Nmap, and Cyber Security fundamentals.",
        },
        {
            "name": "Security Analyst",
            "description": "Monitor and investigate security events using Wireshark, Nmap, Network Security, vulnerability assessments, and basic penetration testing techniques.",
        },
        {
            "name": "Database Administrator",
            "description": "Maintain PostgreSQL and MySQL databases, tune SQL queries, manage backups, monitoring, access controls, and production database performance.",
        },
        {
            "name": "Network Engineer",
            "description": "Design and troubleshoot networks using Network Security principles, Wireshark, Nmap, Linux, monitoring, and reliable connectivity practices.",
        },
    ],
    "Product, Design and Quality": [
        {
            "name": "Business Analyst",
            "description": "Translate business needs into product and reporting requirements using SQL, Tableau, Power BI, stakeholder communication, documentation, and process improvement.",
        },
        {
            "name": "Product Manager",
            "description": "Define product strategy, prioritize features, analyze feedback, communicate roadmaps, and collaborate closely with engineering, design, analytics, and go-to-market teams.",
        },
        {
            "name": "UI/UX Designer",
            "description": "Design intuitive digital experiences using user research, wireframes, prototypes, accessibility principles, design systems, and strong visual hierarchy.",
        },
        {
            "name": "QA Engineer",
            "description": "Create and execute test plans, verify fixes, track bugs, test APIs, and improve software quality using collaboration and testing frameworks.",
        },
        {
            "name": "QA Automation Engineer",
            "description": "Build automated tests using Selenium, Playwright, PyTest, JUnit, CI/CD pipelines, defect reporting, and regression coverage.",
        },
    ],
    "Core Engineering": [
        {
            "name": "Mechanical Engineer",
            "description": "Design mechanical systems with CAD and AutoCAD, simulate performance, support manufacturing, and apply thermodynamics, fluid mechanics, and material science.",
        },
        {
            "name": "Electrical Engineer",
            "description": "Work on circuit design, power systems, microcontrollers, simulation software, and electrical safety standards for reliable hardware systems.",
        },
        {
            "name": "Civil Engineer",
            "description": "Plan and design infrastructure projects using AutoCAD, structural analysis, geotechnical engineering, and building code compliance.",
        },
        {
            "name": "Electronics Engineer",
            "description": "Design embedded systems with microcontrollers, develop firmware in C and C++, and test circuits using electronics engineering tools.",
        },
        {
            "name": "Chemical Engineer",
            "description": "Optimize chemical production, manage process safety, improve reactions, and apply process engineering fundamentals in industrial systems.",
        },
        {
            "name": "Aerospace Engineer",
            "description": "Design aircraft or spacecraft, simulate aerodynamics, test propulsion systems, and apply strong foundations in control systems and materials.",
        },
        {
            "name": "Embedded Software Engineer",
            "description": "Develop firmware in C and C++ for Embedded Systems, work with microcontrollers, debugging, hardware-software integration, and low-level testing.",
        },
    ],
    "Finance and Banking": [
        {
            "name": "Financial Analyst",
            "description": "Analyze financial data, build forecasting models, prepare reports, and support investment or business decisions using Excel-style analysis, SQL, dashboards, and financial modeling.",
        },
        {
            "name": "Investment Analyst",
            "description": "Evaluate companies, markets, and portfolios using financial statements, valuation models, market research, risk analysis, and presentation of investment recommendations.",
        },
        {
            "name": "Accountant",
            "description": "Prepare financial records, reconciliations, tax-related documents, compliance reports, and month-end close activities with strong accounting principles and attention to detail.",
        },
        {
            "name": "Auditor",
            "description": "Review financial controls, check compliance, analyze transactions, document findings, and support internal or external audits with strong risk and reporting discipline.",
        },
        {
            "name": "Risk Analyst",
            "description": "Assess operational, financial, or market risk using reporting, statistical analysis, documentation, controls evaluation, and stakeholder communication.",
        },
        {
            "name": "FinTech Product Analyst",
            "description": "Support digital finance products through metrics analysis, SQL, dashboards, customer behavior analysis, compliance awareness, and collaboration across product and engineering teams.",
        },
    ],
    "Healthcare and Medical": [
        {
            "name": "Medical Officer",
            "description": "Provide clinical assessment, diagnosis, treatment planning, patient care coordination, medical documentation, and collaboration with multidisciplinary healthcare teams.",
        },
        {
            "name": "Registered Nurse",
            "description": "Deliver patient care, monitor vitals, administer treatments, maintain records, support recovery, and communicate clearly with patients, families, and physicians.",
        },
        {
            "name": "Pharmacist",
            "description": "Dispense medications, review prescriptions, counsel patients, ensure dosage safety, maintain compliance, and support medication management workflows.",
        },
        {
            "name": "Medical Lab Technician",
            "description": "Conduct laboratory testing, prepare samples, maintain equipment quality standards, document results, and support diagnostic workflows with accuracy and compliance.",
        },
        {
            "name": "Healthcare Data Analyst",
            "description": "Analyze healthcare datasets, build reporting dashboards, track patient or operational metrics, support quality improvement, and communicate insights to clinical or hospital teams.",
        },
        {
            "name": "Hospital Administrator",
            "description": "Coordinate hospital operations, staffing, patient service workflows, compliance processes, reporting, and cross-functional communication to improve care delivery.",
        },
    ],
    "Marketing and Sales": [
        {
            "name": "Marketing Analyst",
            "description": "Analyze campaign performance, customer segments, funnel metrics, and reporting dashboards to guide brand, growth, and product marketing decisions.",
        },
        {
            "name": "Digital Marketing Specialist",
            "description": "Plan and optimize digital campaigns across SEO, content, email, paid media, analytics dashboards, and audience targeting strategies.",
        },
        {
            "name": "Content Strategist",
            "description": "Create and manage content plans, editorial calendars, messaging frameworks, audience research, and performance reporting across digital channels.",
        },
        {
            "name": "Sales Executive",
            "description": "Generate leads, manage client relationships, present offerings, track pipeline progress, negotiate deals, and support revenue growth with strong communication skills.",
        },
        {
            "name": "Business Development Executive",
            "description": "Identify partnerships, qualify opportunities, support proposals, manage outreach, and convert market insights into new business growth.",
        },
    ],
    "Operations and Supply Chain": [
        {
            "name": "Operations Manager",
            "description": "Improve business operations, monitor KPIs, coordinate teams, streamline workflows, manage reporting, and support process efficiency across departments.",
        },
        {
            "name": "Supply Chain Analyst",
            "description": "Track inventory, logistics, procurement, and demand metrics using reporting, forecasting, process analysis, and stakeholder coordination.",
        },
        {
            "name": "Procurement Specialist",
            "description": "Manage vendor sourcing, purchase processes, cost analysis, contract coordination, inventory planning, and procurement compliance.",
        },
        {
            "name": "Logistics Coordinator",
            "description": "Coordinate shipments, warehouse flows, vendor communication, scheduling, documentation, and operational reporting for reliable delivery performance.",
        },
    ],
    "Education and Research": [
        {
            "name": "Lecturer",
            "description": "Teach subject matter clearly, prepare course materials, assess students, support academic outcomes, and contribute to curriculum improvement.",
        },
        {
            "name": "Research Assistant",
            "description": "Support research projects through literature review, data collection, analysis, documentation, report writing, and collaboration with faculty or research leads.",
        },
        {
            "name": "Academic Coordinator",
            "description": "Coordinate academic schedules, student support, documentation, faculty communication, reporting, and quality improvement across education programs.",
        },
        {
            "name": "Instructional Designer",
            "description": "Design learning experiences, digital course materials, assessments, learner journeys, and structured educational content with measurable outcomes.",
        },
    ],
}


JOB_DESCRIPTIONS = {
    role["name"]: role["description"]
    for sector_roles in ROLE_CATALOG.values()
    for role in sector_roles
}


SKILL_LOOKUP = {skill.lower(): skill for skill in SKILLS}
SKILL_PATTERN = re.compile(
    r"(?<![A-Za-z])(" + "|".join(re.escape(skill) for skill in sorted(SKILLS, key=len, reverse=True)) + r")(?![A-Za-z])",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class AnalysisResult:
    details: dict[str, str]
    match_score: float
    ats_score: float
    matched_skills: list[str]
    missing_skills: list[str]
    expected_skills: list[str]
    ai_summary: str
    ai_strengths: list[str]
    ai_risks: list[str]
    ai_next_steps: list[str]
    match_explanation: str
    section_insights: list[dict[str, object]]
    learning_plan: list[dict[str, object]]


class LlmSectionInsight(BaseModel):
    section: str
    score: int = Field(ge=0, le=100)
    tone: Literal["good", "warn", "bad"] = "warn"
    actions: list[str] = Field(default_factory=list)


class LlmResumeAnalysis(BaseModel):
    name: str = "Not found"
    email: str = "Not found"
    phone: str = "Not found"
    skills: list[str] = Field(default_factory=list)
    summary: str = "Not found"
    projects: str = "Not found"
    education: str = "Not found"
    experience: str = "Not found"
    match_score: float = Field(ge=0, le=100)
    ats_score: float = Field(ge=0, le=100)
    expected_skills: list[str] = Field(default_factory=list)
    matched_skills: list[str] = Field(default_factory=list)
    missing_skills: list[str] = Field(default_factory=list)
    match_explanation: str = ""
    ai_summary: str = ""
    ai_strengths: list[str] = Field(default_factory=list)
    ai_risks: list[str] = Field(default_factory=list)
    ai_next_steps: list[str] = Field(default_factory=list)
    section_insights: list[LlmSectionInsight] = Field(default_factory=list)


def extract_skills(text: str) -> list[str]:
    detected: dict[str, str] = {}
    for match in SKILL_PATTERN.finditer(text):
        key = match.group(1).lower()
        detected.setdefault(key, SKILL_LOOKUP[key])
    return list(detected.values())


def _truncate(value: str, limit: int) -> str:
    text = (value or "").strip()
    if not text:
        return "Not found"
    return text[:limit]


def _normalize_skill_list(skills: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for skill in skills:
        item = (skill or "").strip()
        if not item:
            continue
        key = item.lower()
        display = SKILL_LOOKUP.get(key, item)
        if display.lower() in seen:
            continue
        seen.add(display.lower())
        normalized.append(display)
    return normalized


def _normalize_detail(value: str, fallback: str = "Not found") -> str:
    text = (value or "").strip()
    return text if text else fallback


def _stringify_llm_value(value: Any, limit: int, fallback: str = "Not found") -> str:
    if value is None:
        return fallback
    if isinstance(value, str):
        return _truncate(value, limit)
    if isinstance(value, list):
        lines: list[str] = []
        for item in value:
            if isinstance(item, str):
                text = item.strip()
                if text:
                    lines.append(text)
                continue
            if isinstance(item, dict):
                parts = [str(v).strip() for v in item.values() if str(v).strip()]
                if parts:
                    lines.append(" | ".join(parts))
        return _truncate("\n".join(lines), limit) if lines else fallback
    if isinstance(value, dict):
        parts = [f"{k}: {v}".strip() for k, v in value.items() if str(v).strip()]
        return _truncate("\n".join(parts), limit) if parts else fallback
    return _truncate(str(value), limit)


def _normalize_section_insights(items: list[Any]) -> list[LlmSectionInsight]:
    normalized: list[LlmSectionInsight] = []
    default_sections = [
        "Summary",
        "Skills",
        "Projects/Experience",
        "ATS Formatting",
        "Role Alignment",
    ]
    for idx, item in enumerate(items):
        if isinstance(item, LlmSectionInsight):
            normalized.append(item)
            continue
        if isinstance(item, dict):
            try:
                normalized.append(LlmSectionInsight.model_validate(item))
                continue
            except Exception:
                pass
            actions_value = item.get("actions", [])
            if isinstance(actions_value, str):
                actions = [actions_value]
            elif isinstance(actions_value, list):
                actions = [str(x).strip() for x in actions_value if str(x).strip()]
            else:
                actions = []
            normalized.append(
                LlmSectionInsight(
                    section=str(item.get("section") or default_sections[min(idx, len(default_sections) - 1)]),
                    score=int(item.get("score") or 65),
                    tone=str(item.get("tone") or "warn"),
                    actions=actions[:4],
                )
            )
            continue
        if isinstance(item, str) and item.strip():
            normalized.append(
                LlmSectionInsight(
                    section=default_sections[min(idx, len(default_sections) - 1)],
                    score=65,
                    tone="warn",
                    actions=[item.strip()],
                )
            )
    return normalized


def extract_contact(text: str) -> tuple[str, str]:
    email_pattern = r"[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_pattern = r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}"
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    return (emails[0] if emails else "Not found", phones[0] if phones else "Not found")


def extract_name_from_top(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title_words = {
        "engineer",
        "developer",
        "intern",
        "analyst",
        "designer",
        "manager",
        "student",
        "resume",
        "curriculum",
        "vitae",
        "cv",
        "portfolio",
        "linkedin",
        "github",
    }
    best_candidate = None
    best_score = -10_000

    for idx, raw in enumerate(lines[:20]):
        first_line = raw.splitlines()[0].strip()
        primary_segment = re.split(r"\s*[|•·]\s*", first_line)[0].strip()

        # Common pattern: "Name - Role Title"
        if " - " in primary_segment:
            lhs, rhs = primary_segment.split(" - ", 1)
            rhs_l = rhs.lower()
            if any(word in rhs_l for word in title_words):
                primary_segment = lhs.strip()

        candidate = " ".join(primary_segment.split())
        if not candidate or len(candidate) > 50:
            continue
        if "@" in candidate or "http" in candidate or any(char.isdigit() for char in candidate):
            continue

        cleaned = re.sub(r"[^A-Za-z.\-\s]", "", candidate).strip()
        parts = [part for part in cleaned.split() if part]
        if not (1 <= len(parts) <= 4):
            continue
        if len(parts) == 1 and len(parts[0]) < 3:
            continue
        if any(part.lower() in SKILL_LOOKUP for part in parts):
            continue
        if any(part.lower() in title_words for part in parts):
            continue
        if not all(re.fullmatch(r"[A-Za-z][A-Za-z.\-]*", part) for part in parts):
            continue

        score = 100 - idx * 6
        if 2 <= len(parts) <= 3:
            score += 12
        if candidate.isupper():
            score += 3
        if candidate.istitle():
            score += 4
        if any(len(part) == 1 for part in parts):
            score -= 4

        if score > best_score:
            best_score = score
            best_candidate = candidate

    if best_candidate:
        return best_candidate
    return "Not found"


def expected_skills_for_role(job_desc: str) -> list[str]:
    return [skill for skill in SKILLS if re.search(rf"\b{re.escape(skill)}\b", job_desc, re.IGNORECASE)]


def _parse_sections(text: str) -> dict[str, str]:
    """
    Very lightweight "ATS style" section parsing based on common headings.
    We only need enough structure to give actionable feedback.
    """
    header_map: dict[str, list[str]] = {
        "Summary": ["summary", "professional summary", "objective", "about"],
        "Skills": ["skills", "technical skills", "skills & tools", "tools"],
        "Projects": ["projects", "project", "project experience"],
        "Experience": ["experience", "work experience", "employment", "internship", "internships"],
        "Education": ["education", "academics"],
        "Certifications": ["certifications", "certificates"],
        "Achievements": ["achievements", "awards", "honors"],
    }

    def normalize_header(line: str) -> str:
        return re.sub(r"[^a-z&\s]", "", (line or "").strip().lower()).strip()

    sections: dict[str, list[str]] = {}
    current = None
    for raw in text.splitlines():
        line = (raw or "").strip()
        if not line:
            continue
        norm = normalize_header(line)
        matched = None
        for canonical, variants in header_map.items():
            if norm in variants:
                matched = canonical
                break
        if matched:
            current = matched
            sections.setdefault(current, [])
            continue
        if current is None:
            continue
        sections[current].append(line)

    return {k: "\n".join(v).strip() for k, v in sections.items() if "\n".join(v).strip()}


def _learning_plan(missing_skills: list[str]) -> list[dict[str, object]]:
    plan: list[dict[str, object]] = []
    for skill in missing_skills[:10]:
        resources = LEARNING_RESOURCES.get(skill) or []
        if not resources:
            # Still return something so the UI can show the missing skill.
            resources = [{"title": "Search for a beginner course + build a mini project", "url": "https://www.google.com/"}]
        plan.append({"skill": skill, "resources": resources})
    return plan


def _section_insights(
    selected_role: str,
    details: dict[str, str],
    extracted_text: str,
    expected: list[str],
    matched: list[str],
    missing: list[str],
    sections: dict[str, str],
) -> list[dict[str, object]]:
    insights: list[dict[str, object]] = []

    def tone_for(score: int) -> str:
        if score >= 80:
            return "good"
        if score >= 55:
            return "warn"
        return "bad"

    # Contact
    contact_score = 100
    actions: list[str] = []
    if details.get("Name") in {None, "", "Not found"}:
        contact_score -= 30
        actions.append("Put your full name as the first line, large font, no extra words like 'Resume'.")
    if details.get("Email") in {None, "", "Not found"}:
        contact_score -= 35
        actions.append("Add a professional email address in the header.")
    if details.get("Phone") in {None, "", "Not found"}:
        contact_score -= 25
        actions.append("Add a phone number in the header.")
    if "linkedin" not in extracted_text.lower():
        actions.append("Add a LinkedIn URL (and GitHub/portfolio if relevant).")
    insights.append(
        {
            "section": "Contact",
            "score": max(contact_score, 0),
            "tone": tone_for(max(contact_score, 0)),
            "actions": actions[:4],
        }
    )

    # Summary
    summary_text = sections.get("Summary", "")
    summary_score = 65 if summary_text else 35
    summary_actions: list[str] = []
    if not summary_text:
        summary_actions.append("Add a 2-3 line Summary tailored to the selected role.")
    if missing:
        summary_actions.append(f"Include 2-4 role keywords naturally (ex: {', '.join(missing[:4])}).")
    summary_actions.append("Use one line for impact: years/projects, domain, and strongest stack.")
    insights.append(
        {
            "section": "Summary",
            "score": summary_score,
            "tone": tone_for(summary_score),
            "actions": summary_actions[:4],
        }
    )

    # Skills
    skills_text = details.get("Skills", "") or ""
    skill_count = 0 if skills_text in {"Not found", ""} else len([x for x in skills_text.split(",") if x.strip()])
    skills_score = min(40 + skill_count * 4, 90)
    skills_actions: list[str] = []
    if missing:
        skills_actions.append(f"Add missing keywords only if you can back them up: {', '.join(missing[:8])}.")
    skills_actions.append("Group skills by category (Languages, Frameworks, Databases, Tools) for ATS readability.")
    if skill_count < 6:
        skills_actions.append("Increase skill coverage by listing the exact tools you used in projects.")
    insights.append(
        {
            "section": "Skills",
            "score": int(skills_score),
            "tone": tone_for(int(skills_score)),
            "actions": skills_actions[:4],
        }
    )

    # Projects / Experience
    exp_text = sections.get("Experience", "") or sections.get("Projects", "") or ""
    has_bullets = any(line.strip().startswith(("-", "•")) for line in exp_text.splitlines())
    has_metrics = bool(re.search(r"\b(\d+%|\d+\+|\d+\s*(users|ms|s|sec|requests|reqs|x))\b", exp_text.lower()))
    proj_score = 45
    proj_actions: list[str] = []
    if exp_text:
        proj_score += 25
    if has_bullets:
        proj_score += 15
    if has_metrics:
        proj_score += 15
    if not exp_text:
        proj_actions.append("Add a Projects section (2-3 projects) if you have limited experience.")
    if not has_bullets:
        proj_actions.append("Use bullet points, not paragraphs. Start bullets with action verbs.")
    if not has_metrics:
        proj_actions.append("Add measurable impact: latency, accuracy, users, cost, time saved, or throughput.")
    if missing:
        proj_actions.append(f"Add 1 bullet proving {missing[0]} with a concrete feature/result.")
    insights.append(
        {
            "section": "Projects/Experience",
            "score": min(proj_score, 100),
            "tone": tone_for(min(proj_score, 100)),
            "actions": proj_actions[:4],
        }
    )

    # Formatting
    lower = extracted_text.lower()
    headings_present = sum(1 for h in ["summary", "skills", "projects", "experience", "education"] if h in lower)
    fmt_score = 55 + headings_present * 8
    fmt_actions: list[str] = []
    if headings_present < 3:
        fmt_actions.append("Add clear headings: Summary, Skills, Projects, Experience, Education.")
    if "|" in extracted_text:
        fmt_actions.append("Avoid tables/columns when possible; ATS often reads them poorly.")
    fmt_actions.append("Keep to 1 page (freshers) or 1-2 pages (experienced), consistent spacing, simple fonts.")
    insights.append(
        {
            "section": "ATS Formatting",
            "score": int(min(fmt_score, 100)),
            "tone": tone_for(int(min(fmt_score, 100))),
            "actions": fmt_actions[:4],
        }
    )

    # Role focus
    expected_count = max(len(expected), 1)
    role_score = int((len(matched) / expected_count) * 100)
    role_actions: list[str] = []
    if missing:
        role_actions.append(f"Prioritize adding evidence for top missing keywords: {', '.join(missing[:6])}.")
    role_actions.append(f"Mirror job-description wording for {selected_role} in Summary and project bullets.")
    role_actions.append("Add 1 'Relevant Coursework / Certifications' line if it directly supports the role.")
    insights.append(
        {
            "section": "Role Alignment",
            "score": role_score,
            "tone": tone_for(role_score),
            "actions": role_actions[:4],
        }
    )

    return insights


def keyword_match_score(job_desc: str, resume_text: str) -> float:
    job_terms = {match.group(1).lower() for match in SKILL_PATTERN.finditer(job_desc)}
    resume_terms = {match.group(1).lower() for match in SKILL_PATTERN.finditer(resume_text)}
    if not job_terms:
        return 0.0
    overlap = len(job_terms & resume_terms) / len(job_terms)
    return overlap * 100.0


def compute_ats_score(details: dict[str, str], extracted_text: str, matched_skills: list[str], missing_skills: list[str]) -> float:
    score = 0.0
    if details.get("Name") and details["Name"] != "Not found":
        score += 8
    if details.get("Email") and details["Email"] != "Not found":
        score += 10
    if details.get("Phone") and details["Phone"] != "Not found":
        score += 10
    if details.get("Education") and details["Education"] != "Not found":
        score += 8
    if details.get("Experience") and details["Experience"] != "Not found":
        score += 8

    expected_count = max(len(matched_skills) + len(missing_skills), 1)
    score += (len(matched_skills) / expected_count) * 36

    word_count = len(extracted_text.split())
    if word_count >= 250:
        score += 10
    elif word_count >= 120:
        score += 6
    elif word_count >= 60:
        score += 3

    resume_lower = extracted_text.lower()
    section_hits = sum(1 for section in ["experience", "education", "skills", "project", "summary"] if section in resume_lower)
    score += min(section_hits * 2, 10)
    return round(min(score, 100.0), 2)


def heuristic_ai_analysis(selected_role: str, match_score: float, ats_score: float, matched_skills: list[str], missing_skills: list[str], details: dict[str, str]) -> tuple[str, list[str], list[str], list[str]]:
    strengths: list[str] = []
    risks: list[str] = []
    next_steps: list[str] = []

    if details.get("Email") != "Not found" and details.get("Phone") != "Not found":
        strengths.append("Contact information is complete and ATS-friendly.")
    else:
        risks.append("Contact information looks incomplete; add email and phone in the header.")

    if matched_skills:
        strengths.append(f"Skills aligned with {selected_role}: {', '.join(matched_skills[:6])}.")
    else:
        risks.append(f"Limited skill overlap detected for {selected_role}.")

    if missing_skills:
        risks.append(f"Missing role keywords: {', '.join(missing_skills[:6])}.")
        next_steps.append(f"Add project bullets demonstrating {', '.join(missing_skills[:4])}.")

    if match_score >= 75:
        strengths.append("Role-fit score is strong based on detected keywords.")
    elif match_score >= 55:
        next_steps.append("Tailor summary and project bullets to match the job description wording.")
    else:
        risks.append("Resume wording is not aligned enough with the selected role.")
        next_steps.append("Rewrite 2-3 project bullets to include role keywords and measurable impact.")

    if ats_score < 60:
        next_steps.append("Improve ATS structure with clear headings: Summary, Skills, Projects, Experience, Education.")
    elif ats_score >= 80:
        strengths.append("ATS structure looks strong for early-career screening.")

    summary = f"Estimated {match_score:.1f}% role match and {ats_score:.1f}% ATS score for {selected_role}."
    return summary, strengths[:4], risks[:4], next_steps[:4]


def _call_ollama_analysis(resume_text: str, selected_role: str, job_desc: str, expected: list[str]) -> LlmResumeAnalysis:
    if not settings.ollama_api_key:
        raise RuntimeError("OLLAMA_API_KEY is not set. Add it before calling /analyze.")

    schema = LlmResumeAnalysis.model_json_schema()
    prompt = f"""
You are an ATS resume parser and evaluator.

Target role: {selected_role}
Job description:
{job_desc}

Expected role skills:
{", ".join(expected) if expected else "None provided"}

Known global skills vocabulary:
{", ".join(SKILLS)}

Instructions:
- Read the resume text carefully.
- Extract the candidate's details and section summaries.
- Return JSON only that matches the provided schema.
- Use "Not found" for missing scalar fields.
- Keep section text concise and factual.
- Keep lists short, specific, and non-duplicated.
- `match_score` and `ats_score` must be numbers from 0 to 100.
- `matched_skills`, `missing_skills`, and `expected_skills` should focus on the target role.
- `section_insights` should contain practical ATS improvement actions.

Resume text:
{resume_text[:18000]}
""".strip()

    payload = {
        "model": settings.ollama_model,
        "stream": False,
        "format": schema,
        "messages": [
            {
                "role": "system",
                "content": "You produce strict JSON that matches the supplied schema exactly.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    request = urllib_request.Request(
        f"{settings.ollama_base_url}/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {settings.ollama_api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(request, timeout=settings.ollama_timeout_seconds) as response:
            raw = response.read().decode("utf-8")
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise ValueError(f"Ollama API error {exc.code}: {body or exc.reason}") from exc
    except urllib_error.URLError as exc:
        raise ValueError(f"Unable to reach Ollama API: {exc.reason}") from exc

    try:
        parsed = json.loads(raw)
        content = parsed["message"]["content"]
        if not isinstance(content, dict):
            content = json.loads(content)
        content["projects"] = _stringify_llm_value(content.get("projects"), 900)
        content["education"] = _stringify_llm_value(content.get("education"), 700)
        content["experience"] = _stringify_llm_value(content.get("experience"), 900)
        content["summary"] = _stringify_llm_value(content.get("summary"), 600)
        content["section_insights"] = [item.model_dump() for item in _normalize_section_insights(content.get("section_insights", []))]
        return LlmResumeAnalysis.model_validate(content)
    except (KeyError, TypeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("Ollama API returned an unexpected response.") from exc


def _merge_analysis_with_fallback(
    llm: LlmResumeAnalysis,
    resume_text: str,
    selected_role: str,
    job_desc: str,
    expected: list[str],
) -> AnalysisResult:
    heuristic_skills = extract_skills(resume_text)
    merged_skills = _normalize_skill_list(list(llm.skills) + heuristic_skills)
    sections = _parse_sections(resume_text)
    extracted_email, extracted_phone = extract_contact(resume_text)

    details = {
        "Name": _normalize_detail(llm.name if llm.name != "Not found" else extract_name_from_top(resume_text)),
        "Email": _normalize_detail(llm.email if llm.email != "Not found" else extracted_email),
        "Phone": _normalize_detail(llm.phone if llm.phone != "Not found" else extracted_phone),
        "Skills": ", ".join(merged_skills) if merged_skills else "Not found",
        "Summary": _stringify_llm_value(llm.summary if llm.summary != "Not found" else sections.get("Summary", ""), 600),
        "Projects": _stringify_llm_value(llm.projects if llm.projects != "Not found" else sections.get("Projects", ""), 900),
        "Education": _stringify_llm_value(llm.education if llm.education != "Not found" else sections.get("Education", ""), 700),
        "Experience": _stringify_llm_value(llm.experience if llm.experience != "Not found" else sections.get("Experience", ""), 900),
    }

    actual_lookup = {skill.lower() for skill in merged_skills}
    matched = [skill for skill in expected if skill.lower() in actual_lookup]
    missing = [skill for skill in expected if skill.lower() not in actual_lookup]

    local_match_score = round(keyword_match_score(job_desc, resume_text), 2)
    local_ats_score = compute_ats_score(details, resume_text, matched, missing)

    ai_summary, strengths, risks, next_steps = heuristic_ai_analysis(
        selected_role, local_match_score, local_ats_score, matched, missing, details
    )
    match_explanation = (
        llm.match_explanation.strip()
        or f"Match is based on target-role evidence found in the resume for {selected_role}."
    )

    section_insights = _normalize_section_insights(llm.section_insights) or [
        LlmSectionInsight.model_validate(item)
        for item in _section_insights(selected_role, details, resume_text, expected, matched, missing, sections)
    ]

    return AnalysisResult(
        details=details,
        match_score=round((float(llm.match_score) + local_match_score) / 2, 2),
        ats_score=round((float(llm.ats_score) + local_ats_score) / 2, 2),
        matched_skills=matched,
        missing_skills=missing,
        expected_skills=expected,
        ai_summary=llm.ai_summary.strip() or ai_summary,
        ai_strengths=(llm.ai_strengths or strengths)[:4],
        ai_risks=(llm.ai_risks or risks)[:4],
        ai_next_steps=(llm.ai_next_steps or next_steps)[:4],
        match_explanation=match_explanation,
        section_insights=[item.model_dump() for item in section_insights[:6]],
        learning_plan=_learning_plan(missing),
    )


def analyze_resume(resume_text: str, selected_role: str) -> AnalysisResult:
    job_desc = JOB_DESCRIPTIONS.get(selected_role) or JOB_DESCRIPTIONS["Software Engineer"]
    expected = expected_skills_for_role(job_desc)
    llm = _call_ollama_analysis(resume_text, selected_role, job_desc, expected)
    return _merge_analysis_with_fallback(llm, resume_text, selected_role, job_desc, expected)
