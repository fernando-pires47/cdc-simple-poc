# CDC Boilerplate: PostgreSQL to Elasticsearch

This project demonstrates a Change Data Capture (CDC) pipeline from PostgreSQL to MongoDB using Debezium, Kafka, and a custom Python consumer.

## Architecture

1.  **PostgreSQL**: The source database with `users` and `products` tables.
2.  **Debezium (Kafka Connect)**: Monitors the PostgreSQL WAL (Write-Ahead Log) for changes in the `users` and `products` tables and publishes them to a Kafka topic.
3.  **Kafka**: The message broker that receives the change events from Debezium.
4.  **Elasticsearch Sink Connector (Kafka Connect)**: Consumes the change events from Kafka and writes them to Elasticsearch.
5.  **Elasticsearch**: The destination database that stores the consolidated user and product information.
6.  **Kibana**: A visualization tool for Elasticsearch.
7.  **API**: A FastAPI application that exposes `/users` and `/products` endpoints to retrieve data from Elasticsearch.
8.  **Consumer**: A Python application that consumes the change events from Kafka and caches them in Redis.

## Prerequisites

*   Docker
*   Docker Compose

## Runbook

1.  **Start the environment:**

    ```bash
    docker compose up -d --build
    ```

2.  **Verify the setup:**

    *   Check the logs of the services to ensure they are running correctly:

        ```bash
        docker compose logs -f
        ```

    *   Verify that the Debezium and Elasticsearch connectors are registered:

        ```bash
        curl http://localhost:8083/connectors
        ```

    *   Verify that the Kafka topics for `users` and `products` are created:

        ```bash
        docker compose exec kafka kafka-topics --bootstrap-server localhost:29092 --list
        ```

3.  **Test the CDC pipeline:**

    *   **Insert a new user:**

        Insert a new user into the `users` table in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "INSERT INTO users (name, email) VALUES ('John Doe', 'john.doe@example.com');"
        ```

        Verify the new user via the API and Redis cache:

        ```bash
        curl http://localhost:8001/users
        curl http://localhost:8001/check-redis/user/1
        ```

    *   **Update a user:**

        Update the user's email in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "UPDATE users SET email = 'john.doe.new@example.com' WHERE name = 'John Doe';"
        ```

        Verify the updated user via the API and Redis cache:

        ```bash
        curl http://localhost:8001/users
        curl http://localhost:8001/check-redis/user/1
        ```

    *   **Delete a user:**

        Delete the user from PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "DELETE FROM users WHERE name = 'John Doe';"
        ```

        Verify the user is deleted via the API and removed from Redis:

        ```bash
        curl http://localhost:8001/users
        curl http://localhost:8001/check-redis/user/1
        ```

    *   **Insert a new product:**

        Insert a new product into the `products` table in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "INSERT INTO products (name, price) VALUES ('Laptop', 1200.50);"
        ```

        Verify the new product via the API and Redis cache:

        ```bash
        curl http://localhost:8001/products
        curl http://localhost:8001/check-redis/product/1
        ```

    *   **Update a product (optional):**

        Update the product price in PostgreSQL:

        ```bash
        docker compose exec -T postgres2 psql -U user -d cdc_db -c "UPDATE products SET price = 999.99 WHERE name = 'Laptop';"
        ```

        Verify the updated product via the API and Redis cache:

        ```bash
        curl http://localhost:8001/products
        curl http://localhost:8001/check-redis/product/1
        ```

    *   **Check Elasticsearch:**

        You can check the data in Elasticsearch using Kibana at `http://localhost:5601`.

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

*   **Check the status of the connectors:**

    ```bash
    curl http://localhost:8083/connectors
    ```

*   **List the topics in Kafka:**

    ```bash
    docker compose exec kafka kafka-topics --bootstrap-server localhost:29092 --list
    ```

*   **Consume messages from a Kafka topic:**

    ```bash
    docker compose exec kafka kafka-console-consumer --bootstrap-server localhost:29092 --topic <topic_name> --from-beginning
    ```

## License

MIT License
