# Computer Security - Final Project

In this project, we developed a web-based imaginary communications company called Comunication_LTD. This company markets Internet packages and has a database that includes, among other things, information about the company's customers, various packages, and the sectors to which it markets its products.

We used the following technologies in our project:
| Database  | Web framework | Virtualization | Template engine |
| :---:   | :---: | :---: | :---: |
| Microsoft SQL 2022 | Flask   | Docker   | Jinja2 |

* The UI used plain HTML and CSS (no CSS frameworks).

## Switch Between The Vulnerable And Safe Codes
This project has two branches. The first one has vulnerable code (for SQL injection and XSS attacks), and the second one is not vularable and shows the solutions to those attacks.

You can find both of those versions in this repo:

* Invulnerable/Safe Version - https://github.com/eranbabayov/final_course_project/tree/main

* Vulnerable/Unsafe Version - https://github.com/eranbabayov/final_course_project/tree/hacked_version
## Setup / Run
### Prerequisites

Docker and its [prerequisites](https://docs.docker.com/desktop/install/windows-install/#system-requirements) are installed and **running**
```bash
docker ps
```

### Setup / Run
> The setup of the program or re-running can be done automatically with the same command,`docker compose up`.

1. Change your desired password in the `.env` file. Make sure your password meets [Microsoft's Password Policy](https://learn.microsoft.com/en-us/sql/relational-databases/security/password-policy?view=sql-server-ver16#password-complexity).

2. Run the `docker-compose.yml` file with the following command:
```bash
docker compose up
```
