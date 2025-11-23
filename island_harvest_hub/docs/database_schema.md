
# Island Harvest Hub AI Assistant Database Schema Design

This document outlines the database schema for the Island Harvest Hub AI Assistant. The schema is designed to support all the required functionalities, including customer management, supplier management, daily operations tracking, financial management, communication, document organization, and strategic planning. The database will be implemented using SQLite for simplicity and ease of deployment, with SQLAlchemy as the ORM.

## 1. Customer Management System

**Table: `customers`**

This table stores information about hotels and restaurants that are customers of Island Harvest Hub.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the customer            |
| `name`             | TEXT      | NOT NULL, UNIQUE    | Name of the hotel or restaurant               |
| `contact_person`   | TEXT      |                     | Main contact person at the customer           |
| `phone`            | TEXT      |                     | Phone number of the customer                  |
| `email`            | TEXT      |                     | Email address of the customer                 |
| `address`          | TEXT      |                     | Physical address of the customer              |
| `preferences`      | TEXT      |                     | JSON string of customer preferences (e.g., delivery times, product types) |
| `satisfaction_score`| INTEGER   |                     | Customer satisfaction score (e.g., 1-5)       |
| `feedback`         | TEXT      |                     | General feedback from the customer            |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `orders`**

This table tracks customer orders.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the order               |
| `customer_id`      | INTEGER   | NOT NULL, FOREIGN KEY (`customers.id`) | ID of the customer placing the order          |
| `order_date`       | DATETIME  | NOT NULL            | Date and time the order was placed            |
| `delivery_date`    | DATETIME  | NOT NULL            | Scheduled delivery date and time              |
| `status`           | TEXT      | NOT NULL            | Current status of the order (e.g., Pending, Confirmed, Delivered, Cancelled) |
| `total_amount`     | REAL      |                     | Total monetary amount of the order            |
| `notes`            | TEXT      |                     | Any special notes or instructions for the order |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `order_items`**

This table details the products within each order.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the order item          |
| `order_id`         | INTEGER   | NOT NULL, FOREIGN KEY (`orders.id`) | ID of the order this item belongs to          |
| `product_name`     | TEXT      | NOT NULL            | Name of the product ordered                   |
| `quantity`         | REAL      | NOT NULL            | Quantity of the product                       |
| `unit_price`       | REAL      | NOT NULL            | Price per unit of the product                 |
| `subtotal`         | REAL      |                     | Subtotal for this order item (quantity * unit_price) |

## 2. Supplier (Farmer) Management

**Table: `farmers`**

This table stores information about the local farmers.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the farmer              |
| `name`             | TEXT      | NOT NULL, UNIQUE    | Name of the farmer or farm                    |
| `contact_person`   | TEXT      |                     | Main contact person at the farm               |
| `phone`            | TEXT      |                     | Phone number of the farmer                    |
| `email`            | TEXT      |                     | Email address of the farmer                   |
| `address`          | TEXT      |                     | Physical address of the farm                  |
| `product_specialties`| TEXT      |                     | JSON string of product specialties (e.g., '{

["yam", "callaloo"]') |
| `pickup_schedule`  | TEXT      |                     | JSON string of preferred pickup times and days |
| `quality_records`  | TEXT      |                     | JSON string of quality control notes for products |
| `payment_history`  | TEXT      |                     | JSON string of payment dates and amounts      |
| `performance_notes`| TEXT      |                     | Notes on farmer performance                   |
| `training_needs`   | TEXT      |                     | Identified training needs for the farmer      |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `farmer_payments`**

This table tracks payments made to farmers.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the payment             |
| `farmer_id`        | INTEGER   | NOT NULL, FOREIGN KEY (`farmers.id`) | ID of the farmer receiving payment            |
| `payment_date`     | DATETIME  | NOT NULL            | Date the payment was made                     |
| `amount`           | REAL      | NOT NULL            | Amount paid                                   |
| `notes`            | TEXT      |                     | Any notes related to the payment              |

## 3. Daily Operations Tracking

**Table: `daily_logs`**

This table logs daily order fulfillment and operational activities.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the daily log entry     |
| `log_date`         | DATETIME  | NOT NULL, UNIQUE    | Date of the daily log                         |
| `orders_fulfilled` | INTEGER   |                     | Number of orders fulfilled on this day        |
| `quality_control_notes`| TEXT      |                     | Notes on quality control checks               |
| `temperature_logs` | TEXT      |                     | JSON string of temperature monitoring data    |
| `delivery_route_notes`| TEXT      |                     | Notes on delivery route optimization          |
| `issue_tracking`   | TEXT      |                     | JSON string of issues tracked and their resolution |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

## 4. Financial Management

**Table: `transactions`**

This table records all financial transactions (revenue and expenses).

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the transaction         |
| `date`             | DATETIME  | NOT NULL            | Date of the transaction                       |
| `type`             | TEXT      | NOT NULL            | Type of transaction (e.g., Revenue, Expense, Farmer Payment) |
| `description`      | TEXT      |                     | Description of the transaction                |
| `amount`           | REAL      | NOT NULL            | Amount of the transaction                     |
| `related_entity_id`| INTEGER   |                     | ID of related customer, farmer, or order      |
| `related_entity_type`| TEXT      |                     | Type of related entity (e.g., Customer, Farmer, Order) |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `invoices`**

This table stores customer invoicing details.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the invoice             |
| `customer_id`      | INTEGER   | NOT NULL, FOREIGN KEY (`customers.id`) | ID of the customer to whom the invoice is issued |
| `order_id`         | INTEGER   | NOT NULL, FOREIGN KEY (`orders.id`) | ID of the order associated with this invoice  |
| `invoice_date`     | DATETIME  | NOT NULL            | Date the invoice was issued                   |
| `due_date`         | DATETIME  | NOT NULL            | Date the invoice is due                       |
| `total_amount`     | REAL      | NOT NULL            | Total amount of the invoice                   |
| `status`           | TEXT      | NOT NULL            | Status of the invoice (e.g., Issued, Paid, Overdue) |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

## 5. Communication Hub

**Table: `message_templates`**

This table stores reusable message templates for WhatsApp and email.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the template            |
| `name`             | TEXT      | NOT NULL, UNIQUE    | Name of the template (e.g., Order Confirmation, Payment Reminder) |
| `type`             | TEXT      | NOT NULL            | Type of template (e.g., WhatsApp, Email)      |
| `subject`          | TEXT      |                     | Subject for email templates                   |
| `body`             | TEXT      | NOT NULL            | Content of the message template               |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `meetings`**

This table tracks scheduled meetings.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the meeting             |
| `title`            | TEXT      | NOT NULL            | Title of the meeting                          |
| `date_time`        | DATETIME  | NOT NULL            | Date and time of the meeting                  |
| `attendees`        | TEXT      |                     | JSON string of attendees (e.g., '{["Brian Miller", "Farmer John"]}') |
| `notes`            | TEXT      |                     | Meeting notes                                 |
| `reminders_sent`   | BOOLEAN   | DEFAULT FALSE       | Whether reminders have been sent              |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `follow_up_tasks`**

This table manages follow-up tasks.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the task                |
| `description`      | TEXT      | NOT NULL            | Description of the task                       |
| `due_date`         | DATETIME  |                     | Due date for the task                         |
| `status`           | TEXT      | NOT NULL            | Status of the task (e.g., Pending, Completed, Overdue) |
| `assigned_to`      | TEXT      |                     | Person assigned to the task                   |
| `related_entity_id`| INTEGER   |                     | ID of related customer, farmer, or order      |
| `related_entity_type`| TEXT      |                     | Type of related entity (e.g., Customer, Farmer, Order) |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

## 6. Document Organization

**Table: `documents`**

This table tracks generated and stored documents.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the document            |
| `name`             | TEXT      | NOT NULL            | Name of the document                          |
| `file_path`        | TEXT      | NOT NULL, UNIQUE    | Path to the stored document file              |
| `type`             | TEXT      |                     | Type of document (e.g., Invoice, Report, Contract) |
| `version`          | TEXT      |                     | Version of the document                       |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

## 7. Strategic Planning

**Table: `goals`**

This table tracks business goals and their progress.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the goal                |
| `name`             | TEXT      | NOT NULL            | Name of the goal (e.g., Onboard 25 Farmers)   |
| `description`      | TEXT      |                     | Detailed description of the goal              |
| `target_value`     | REAL      |                     | Numeric target for the goal                   |
| `current_value`    | REAL      | DEFAULT 0.0         | Current progress towards the goal             |
| `start_date`       | DATETIME  |                     | Date the goal was set                         |
| `end_date`         | DATETIME  |                     | Target completion date                        |
| `status`           | TEXT      | NOT NULL            | Status of the goal (e.g., In Progress, Achieved, On Hold) |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `performance_metrics`**

This table stores key performance indicators (KPIs).

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the metric              |
| `name`             | TEXT      | NOT NULL, UNIQUE    | Name of the metric (e.g., Customer Satisfaction, On-time Delivery Rate) |
| `value`            | REAL      | NOT NULL            | Current value of the metric                   |
| `date`             | DATETIME  | NOT NULL            | Date the metric was recorded                  |
| `notes`            | TEXT      |                     | Any notes or context for the metric           |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |

**Table: `partnerships`**

This table tracks potential and existing partnerships.

| Column Name        | Data Type | Constraints         | Description                                   |
|--------------------|-----------|---------------------|-----------------------------------------------|
| `id`               | INTEGER   | PRIMARY KEY, AUTOINC | Unique identifier for the partnership         |
| `name`             | TEXT      | NOT NULL            | Name of the partner                           |
| `type`             | TEXT      |                     | Type of partnership (e.g., Hotel, Restaurant, Farmer Co-op) |
| `contact_person`   | TEXT      |                     | Contact person for the partnership            |
| `status`           | TEXT      | NOT NULL            | Status of the partnership (e.g., Prospect, Initiated, Active, Completed) |
| `notes`            | TEXT      |                     | Notes on the partnership                      |
| `created_at`       | DATETIME  | DEFAULT CURRENT_TIMESTAMP | Timestamp of record creation                  |
| `updated_at`       | DATETIME  |                     | Timestamp of last record update               |


## Data Relationships

- `customers` to `orders`: One-to-many (one customer can have many orders)
- `orders` to `order_items`: One-to-many (one order can have many items)
- `farmers` to `farmer_payments`: One-to-many (one farmer can receive many payments)
- `customers` to `invoices`: One-to-many (one customer can have many invoices)
- `orders` to `invoices`: One-to-one (one order can have one invoice)
- `transactions` to `customers`, `farmers`, `orders`: Many-to-one (transactions can be related to various entities)
- `follow_up_tasks` to `customers`, `farmers`, `orders`: Many-to-one (tasks can be related to various entities)

## Future Considerations

- **User Management**: For multi-user access, a `users` table with roles and permissions would be necessary.
- **Authentication**: Implement secure user authentication (e.g., OAuth, JWT).
- **Logging**: More detailed logging for auditing and debugging purposes.
- **Caching**: For performance optimization, especially with large datasets.
- **API Integrations**: Deeper integration with WhatsApp Business API, email services (e.g., SendGrid, Mailgun), and potentially accounting software (e.g., QuickBooks API).

This schema provides a robust foundation for the Island Harvest Hub AI Assistant, allowing for efficient data management and supporting the various functionalities required by Brian Miller.


