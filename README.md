# Overview

GraphQL is a powerful query language and runtime for APIs, developed by Facebook, that allows clients to request exactly the data they need — nothing more, nothing less. Unlike REST APIs, which return fixed data structures, GraphQL gives clients the flexibility to shape the response format.

We will explore the foundations of GraphQL, understand its advantages over REST, and learn how to implement GraphQL in Django using libraries like `graphene-django`.

---

## Learning Objectives

By the end of this module, learners will be able to:

- Explain what GraphQL is and how it differs from REST.
- Describe the key components of a GraphQL schema (types, queries, mutations).
- Set up and configure GraphQL in a Django project using `graphene-django`.
- Build GraphQL queries and mutations to fetch and manipulate data.
- Use tools like GraphiQL or Insomnia to interact with GraphQL endpoints.
- Follow best practices to design scalable and secure GraphQL APIs.

---

## Learning Outcomes

After completing this lesson, learners should be able to:

- Implement GraphQL APIs in Django applications.
- Write custom queries and mutations using `graphene`.
- Integrate Django models into GraphQL schemas.
- Optimize performance and security in GraphQL endpoints.
- Explain when to use GraphQL instead of REST in real-world projects.

---

## Key Concepts

- **GraphQL vs REST**: Unlike REST which has multiple endpoints, GraphQL uses a single endpoint for all operations.
- **Schema**: Defines how clients can access the data. Includes Types, Queries, and Mutations.
- **Resolvers**: Functions that fetch data for a particular query or mutation.
- **Graphene-Django**: A Python library that integrates GraphQL into Django seamlessly.

---

## Best Practices for Using GraphQL with Django

| Area           | Best Practice                                                                     |
| -------------- | --------------------------------------------------------------------------------- |
| Schema Design  | Keep schema clean and modular. Define reusable types and use clear naming.        |
| Security       | Implement authentication and authorization in resolvers. Avoid exposing all data. |
| Error Handling | Use custom error messages and handle exceptions gracefully in resolvers.          |
| Pagination     | Implement pagination on large query sets to improve performance.                  |
| N+1 Problem    | Use tools like `DjangoSelectRelatedField` or `graphene-django-optimizer`.         |
| Testing        | Write unit tests for your queries and mutations to ensure correctness.            |
| Documentation  | Use GraphiQL for automatic schema documentation and make it available to clients. |

---

## Tools & Libraries

- **graphene-django**: Main library to integrate GraphQL in Django
- **GraphiQL**: Browser-based UI for testing GraphQL APIs
- **Django ORM**: Connect your models directly to GraphQL types
- **Insomnia/Postman**: Useful for testing APIs including GraphQL

---

## Real-World Use Cases

- Airbnb-style applications with flexible data querying
- Dashboards that need precise, real-time data
- Mobile apps with limited bandwidth and specific data needs

# Task Scheduling in Django

## Overview

**Cron** is a time-based task scheduler in Unix-like systems, commonly used to automate repetitive jobs like backups, notifications, and system maintenance.

In the context of **Django applications**, task scheduling can be integrated at multiple levels — from basic system cron jobs executing Django management commands to advanced asynchronous scheduling with tools like **Celery** and **django-celery-beat**.

This module explores the various methods of scheduling and automating tasks in Django. Learners will gain hands-on experience using **system crontabs**, **django-cron**, and **Celery** to implement reliable and maintainable background processes.

---

## Learning Objectives

By the end of this module, learners will be able to:

- Explain what cron jobs are and their role in task automation.
- Write and schedule cron jobs using the system crontab.
- Implement recurring tasks using **django-cron** in Django projects.
- Configure and use **Celery** for asynchronous and periodic task scheduling.
- Understand the strengths and limitations of each approach.
- Apply best practices for debugging and managing automated tasks.

---

## Learning Outcomes

After completing this lesson, learners should be able to:

- Schedule and manage cron jobs using `crontab`.
- Create custom Django management commands for scheduled tasks.
- Use **django-cron** to define and run cron jobs within the Django ecosystem.
- Set up **Celery** with **django-celery-beat** for scalable, distributed task scheduling.
- Monitor, debug, and secure scheduled processes in production.

---

## Key Concepts

| Concept                  | Description                                                              |
| ------------------------ | ------------------------------------------------------------------------ |
| **Crontab Syntax**       | Defines when a command should be run, using 5 time fields and a command. |
| **System Cron + Django** | Uses native system scheduling to run Django commands on a schedule.      |
| **django-cron**          | A library to define scheduled jobs inside Django apps.                   |
| **Celery & Celery Beat** | An asynchronous task queue with support for periodic execution.          |
| **Log Management**       | Redirection of task output to logs for easier monitoring and debugging.  |

---

## Best Practices for Using Crons in Django

| Area               | Best Practice                                                           |
| ------------------ | ----------------------------------------------------------------------- |
| **Scheduling**     | Use absolute paths in cron jobs to avoid environment-related issues.    |
| **Debugging**      | Redirect output (`>> /log/path.log 2>&1`) to capture logs for each job. |
| **Frequency**      | Avoid frequent jobs that can strain the system; batch where possible.   |
| **Access Control** | Use `cron.allow` and `cron.deny` for user-level access restrictions.    |
| **Celery Tasks**   | Keep them **idempotent** to prevent errors on retries.                  |
| **Monitoring**     | Use admin dashboards or custom alerts for task failures in production.  |

---

## Tools & Libraries

- **cron (crontab):** Native job scheduler on Unix systems
- **django-cron:** Schedule and manage cron jobs within Django
- **Celery:** Distributed task queue for asynchronous and periodic jobs
- **django-celery-beat:** Scheduler for managing periodic Celery tasks via Django Admin
- **Supervisord/Systemd:** Tools to keep Celery workers alive

---

## Real-World Use Cases

- Automatically clearing expired sessions or tokens in a Django app.
- Generating daily reports or email digests for users.
- Archiving logs or cleaning up old database records.
- Asynchronously sending notifications and webhooks at scheduled intervals.
- Running intensive background tasks during off-peak hours.
