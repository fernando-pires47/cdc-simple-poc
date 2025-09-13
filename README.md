# CDC Boilerplate: PostgreSQL to MongoDB

This project demonstrates a Change Data Capture (CDC) pipeline from PostgreSQL to MongoDB using Debezium, Kafka, and a custom Python consumer.

## Architecture

1.  **PostgreSQL**: The source database with `users` and `products` tables.
2.  **Debezium (Kafka Connect)**: Monitors the PostgreSQL WAL (Write-Ahead Log) for changes in the `users` and `products` tables and publishes them to a Kafka topic. It's configured to handle `DECIMAL` types as `string` to avoid data corruption issues during serialization/deserialization.
3.  **Kafka**: The message broker that receives the change events from Debezium.
4.  **Consumer**: A Python application that consumes the change events from Kafka, formats them, and writes them to MongoDB.
5.  **MongoDB**: The destination database that stores the consolidated user information.

## Prerequisites

*   Docker
*   Docker Compose

## Runbook

1.  **Start the environment:**

    ```bash
    docker compose up -d
    ```

2.  **Verify the setup:**

    *   Check the logs of the services to ensure they are running correctly:

        ```bash
        docker compose logs -f
        ```

    *   Verify that the Debezium connector is registered:

        ```bash
        curl http://localhost:8083/connectors/postgres-connector
        ```

    *   Verify that the Kafka topics for `users` and `products` are created:

        ```bash
        docker compose exec kafka kafka-topics --bootstrap-server localhost:29092 --list
        ```

3.  **Test the CDC pipeline:**

    *   **Important:** Before running these tests, ensure your MongoDB is clean. If you have old data, stop the environment (`docker compose down`), remove volumes (`docker volume rm cdc_mongodb_data`), and then start the environment again (`docker compose up -d`).

    *   **Insert a new user:**

        Insert a new user into the `users` table in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "INSERT INTO users (name, email) VALUES ('John Doe', 'john.doe@example.com');"
        ```

        Verify the new user via the API:

        ```bash
        curl http://localhost:8001/users
        ```

        Expected output (may contain multiple entries if not starting with a clean MongoDB):
        ```json
        {"users": [{"_id": "<some_id>", "id": 1, "name": "John Doe", "email": "john.doe@example.com"}]}
        ```

    *   **Update a user:**

        Update the user's email in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "UPDATE users SET email = 'john.doe.new@example.com' WHERE name = 'John Doe';"
        ```

        Verify the updated user via the API:

        ```bash
        curl http://localhost:8001/users
        ```

        Expected output (email should be updated):
        ```json
        {"users": [{"_id": "<some_id>", "id": 1, "name": "John Doe", "email": "john.doe.new@example.com"}]}
        ```

    *   **Delete a user:**

        Delete the user from PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "DELETE FROM users WHERE name = 'John Doe';"
        ```

        Verify the user is deleted via the API:

        ```bash
        curl http://localhost:8001/users
        ```

        Expected output (empty array):
        ```json
        {"users": []}
        ```

    *   **Insert a new product:**

        Insert a new product into the `products` table in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "INSERT INTO products (name, price) VALUES ('Laptop', 1200.50);"
        ```

        Verify the new product via the API:

        ```bash
        curl http://localhost:8001/products
        ```

        Expected output:
        ```json
        {"products": [{"_id": "<some_id>", "id": 1, "name": "Laptop", "price": "1200.50"}]}
        ```

    *   **Update a product:**

        Update the product's price in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "UPDATE products SET price = 1500.75 WHERE name = 'Laptop';"
        ```

        Verify the updated product via the API:

        ```bash
        curl http://localhost:8001/products
        ```

        Expected output (price should be updated):
        ```json
        {"products": [{"_id": "<some_id>", "id": 1, "name": "Laptop", "price": "1500.75"}]}
        ```

    *   **Delete a product:**

        Delete the product from PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "DELETE FROM products WHERE name = 'Laptop';"
        ```

        Verify the product is deleted via the API:

        ```bash
        curl http://localhost:8001/products
        ```

        Expected output (empty array):
        ```json
        {"products": []}
        ```

4.  **Stop the environment:**

    ```bash
    docker compose down
    ```

5.  **Clean up the environment (optional, for a fresh start):**

    ```bash
    docker compose down -v
    ```

## Troubleshooting

If you are having issues with the CDC pipeline, here are some commands that can help you debug the problem:

*   **Check the logs of all the services:**

    ```bash
    docker compose logs -f
    ```

*   **Check the logs of a specific service:**

    ```bash
    docker compose logs <service_name>
    ```

*   **Check the status of the Debezium connector:**

    ```bash
    curl http://localhost:8083/connectors/postgres-connector/status
    ```

*   **Check the configuration of the Debezium connector:**

    ```bash
    curl http://localhost:8083/connectors/postgres-connector
    ```

*   **Delete the Debezium connector:**

    ```bash
    curl -X DELETE http://localhost:8083/connectors/postgres-connector
    ```

*   **Register the Debezium connector:**

    ```bash
    curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-postgres.json
    ```

*   **List the topics in Kafka:**

    ```bash
    docker compose exec kafka kafka-topics --bootstrap-server localhost:29092 --list
    ```

*   **Consume messages from a Kafka topic:**

    ```bash
    docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:29092 --topic <topic_name> --from-beginning
    ```
