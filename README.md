# Cocktail Advisor Chat

## Overview

The **Cocktail Advisor Chat** is a Python-based chat application that integrates an LLM (via LangChain) and a vector database (FAISS) to create a Retrieval-Augmented Generation (RAG) system. This application allows users to ask cocktail-related questions, provide preferences, and receive personalized recommendations based on their input.

---

## Time Spent on Task

**4-5 Hours**

---

## Features

1. **Knowledge Base:**
   - Retrieves relevant cocktail information from the dataset.
   - Supports questions such as:
     - *What are the 5 cocktails containing lemon?*
     - *What are the 5 non-alcoholic cocktails containing sugar?*

2. **Preference Handling:**
   - Dynamically updates user preferences (e.g., favorite ingredients or cocktails).
   - Stores preferences persistently in FAISS.

3. **Personalized Recommendations:**
   - Suggests cocktails tailored to user preferences.
   - Answers queries like:
     - *Recommend 5 cocktails that contain my favorite ingredients.*
     - *Recommend a cocktail similar to "Hot Creamy Bush".*

4. **Deployment-Ready:**
   - Dockerized for ease of deployment and portability.

---

## Results

The **Cocktail Advisor Chat** was tested with a variety of questions. Below are the results:

### Knowledge Base Testing

1. **What are the 5 cocktails containing lemon?**
   - Example output:
     - *Lady Love Fizz* (Ingredients: Gin, Lemon juice, Egg white).
     - *Sazerac* (Ingredients: Lemon peel, Bourbon).

2. **What are the 5 non-alcoholic cocktails containing sugar?**
   - Example output:
     - *Lemon Soda Fizz* (Ingredients: Lemon juice, sugar, club soda).
     - *Virgin Mojito* (Ingredients: Lime juice, sugar, mint leaves).

3. **What are my favorite ingredients?**
   - Example output:
     - Ingredients: Soda, Lemon.
     - Cocktails: *Cocktail with Rum and Lime*.

---

### Advisor Testing

1. **Recommend 5 cocktails that contain my favorite ingredients.**
   - Example output:
     - *Rum Cooler*: Combines rum, lemon-lime soda, and lemon.
     - *Gin and Soda*: Soda water, gin, and lime.

2. **Recommend a cocktail similar to “Hot Creamy Bush.”**
   - Example output:
     - *Imperial Cocktail*: Lime juice, Gin, Aperol.
     - *English Rose Cocktail*: Lemon juice, Gin, Grenadine.

3. **Additional advisor queries:**
   - *Cocktail with rum and lime* updated preferences and provided immediate recommendations.
   - Questions mixing ingredients and advice produced relevant results.

---

## Thought Process

1. **Design:**
   - Used FastAPI for a lightweight backend.
   - Integrated LangChain to leverage LLM for parsing and generating responses.
   - Connected a cocktail dataset to FAISS for fast vector-based searches.

2. **Preference Handling:**
   - Implemented user preference extraction using LangChain’s JSON parser.
   - Stored preferences persistently in FAISS to ensure continuity between sessions.

3. **Personalization:**
   - Combined user preferences with retrieved cocktail data to tailor responses.

4. **Deployment:**
   - Dockerized the application and created a Makefile for streamlined development and deployment.



## How to Run the Application

1. **Clone the Repository:**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```
2. **Build and run using docker:**
```bash
  docker build --build-arg OPENAI_API_KEY=sk-ваш-ключ -t cocktail-advisor .
  docker run -d -p 8000:8000 cocktail-advisor
3. **Access the Chat:**

Open your browser and navigate to http://127.0.0.1:8000
4. **Stop and Remove container**
```bash
docker stop cocktail-advisor-container
docker rm cocktail-advisor-container

```

## Future Improvements

- **Authentication:**  
  Add user accounts to separate preferences for multiple users.

- **UI Enhancements:**  
  Create a rich front-end with ingredient selection or dropdowns for queries.

- **External Data Integration:**  
  Use APIs like CocktailDB for real-time data updates.