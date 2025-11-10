# Excel Data Processing Web App

This project is a web-based utility designed to automate the processing and cleaning of Excel sales and receipt data from multiple branches. It provides a unified interface to handle different processing logic for each branch, streamlining data management tasks.

The application is containerized using Docker and consists of two main services:
1.  A **Sales Processor** (built with Django) for handling sales data.
2.  A **Receipt Processor** (built with Flask) for handling receipt and payment data.

An Nginx reverse proxy manages traffic between the two services, providing a seamless user experience.

## Features

-   **Multi-Branch Support:** Custom processing logic for different branches (Aluva, Kalamassery, Vedimara, Choondy).
-   **Sales Data Processing:** Cleans, restructures, and categorizes sales data based on treatment types.
-   **Receipt Data Processing:** Cleans and categorizes receipt data, handling different payment methods.
-   **Dockerized Environment:** Uses `docker-compose` to simplify setup and ensure a consistent environment.
-   **Unified Interface:** A single entry point and integrated navigation between the two processing applications.

## Prerequisites

Before you begin, ensure you have Docker and `docker-compose` installed on your system. The easiest way to get both is by installing [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Getting Started

To get a local copy up and running, follow these simple steps.

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/muhammedraihan007/excel-web-app.git
    ```

2.  **Navigate to the project directory:**
    ```sh
    cd excel-web-app/unified_project
    ```

3.  **Build and run the application:**
    ```sh
    docker-compose up --build
    ```
    This command will build the Docker images for all services and start the application. Wait for the process to complete. You will see log output from the `nginx`, `django-app`, and `flask-app` services.

## Usage

Once the application is running, you can access it in your web browser:

-   **Main Entry Point:** [http://localhost/django/processor/](http://localhost/django/processor/)

From the main page, you can upload sales data for processing. Use the "Receipt Processing" button to navigate to the receipt processing application. The navigation bar provides links to switch between the "Sales Process" and "Receipt Processing" sections.
