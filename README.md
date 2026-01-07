# FedEx Smart DCA Manager 🚀

**Team Name:** SolveX  
**Event:** FedEx SMART Hackathon 2026 (IIT Madras)

## Problem Statement
Right now, assigning debt cases to collection agencies is done manually using Excel. It takes a lot of time to figure out which agency should get which case. We wanted to automate this process to make it faster and smarter.

## Our Solution
We built a web portal where the admin can upload a CSV file of all the debt cases. Our system automatically reads the file, calculates a "priority score" for each case, and assigns them to agencies based on their performance rating.

## How the Algorithm Works 🧠
We didn't just assign cases randomly. We used some basic DSA logic here:

1.  **Priority Scoring:** We calculate a score for every case using:  
    `Score = Amount * Days_Overdue`
2.  **Sorting:** We sort all the cases from highest score to lowest.
3.  **Weighted Allocation:** This is the main logic. instead of giving everyone equal work, we calculate capacity based on the agency's rating.
    * *Example:* A 9.5 rated agency gets more cases than a 5.5 rated agency.
    * The best agency also gets the "hardest" (highest score) cases first.

## Project Structure
* `app.py`: Main backend code (Flask). Contains the algorithm and routes.
* `templates/dashboard.html`: The frontend UI.
* `uploads/`: Folder where the CSV files are saved temporarily.

## Tech Stack
* **Language:** Python
* **Web Framework:** Flask
* **Data Handling:** Pandas (for reading the CSV)
* **Frontend:** HTML, Bootstrap

## How to Run This
1.  Make sure you have Python installed.
2.  Install the required libraries:
    ```bash
    pip install flask pandas
    ```
3.  Run the application:
    ```bash
    python app.py
    ```
4.  Open your browser and go to `http://127.0.0.1:5000`