<p align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/6295/6295417.png" width="100" />
</p>
<p align="center">
    <h1 align="center">FULL_YEAR_PROJECT</h1>
</p>
<p align="center">
    <em>Securing Success: Challenge, Learn, Conquer!</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="license">
	<img src="https://img.shields.io/github/languages/top/eranbabayov/full_year_project?style=flat&color=0080ff" alt="repo-top-language">
	<img src="https://img.shields.io/github/languages/count/eranbabayov/full_year_project?style=flat&color=0080ff" alt="repo-language-count">
<p>
<p align="center">
		<em>Developed with the software and tools below.</em>
</p>
<p align="center">
	<img src="https://img.shields.io/badge/GNU%20Bash-4EAA25.svg?style=flat&logo=GNU-Bash&logoColor=white" alt="GNU%20Bash">
	<img src="https://img.shields.io/badge/HTML5-E34F26.svg?style=flat&logo=HTML5&logoColor=white" alt="HTML5">
	<img src="https://img.shields.io/badge/YAML-CB171E.svg?style=flat&logo=YAML&logoColor=white" alt="YAML">
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/Docker-2496ED.svg?style=flat&logo=Docker&logoColor=white" alt="Docker">
	<img src="https://img.shields.io/badge/Flask-000000.svg?style=flat&logo=Flask&logoColor=white" alt="Flask">
	<img src="https://img.shields.io/badge/JSON-000000.svg?style=flat&logo=JSON&logoColor=white" alt="JSON">
</p>
<hr>


##  Overview

The full_year_project is a web-based educational platform aimed at cybersecurity training through interactive challenges. It uses a Flask backend for server operations, user session management, and gamification elements. Docker containerization ensures seamless deployment and integration with an SQL database, which stores user data and challenge content. User experience is prioritized by providing dynamic HTML templates for account management, quiz performance summaries, and secure authentication processes, including password resets supported by a detailed password policy configuration. This platform offers a scalable and secure environment for users to engage in cybersecurity training, demonstrating progress through challenges and quizzes.

---

##  Features

|    | Feature             | Description                                                        |
|----|---------------------|--------------------------------------------------------------------|
| ⚙️  | **Architecture**    | *Multi-container Docker setup with Flask backend and MSSQL database.* |
| 🔩 | **Code Quality**    | *Clean, with structured Flask-oriented modules for maintainability.*  |
| 🔌 | **Integrations**    | *Flask integrations with HTML templates and email, plus Docker.*    |
| 🧩 | **Modularity**      | *Code is structured in modular files, though could be componentized.*|
| ⚡️  | **Performance**     | *Performance insights are limited without load tests or telemetry.* |
| 🛡️ | **Security**        | *Password policies enforced, yet broader security audit required.*  |
| 📦 | **Dependencies**    | *Flask, pymssql, python-dotenv, Flask-Mail, matplotlib, etc.*      |
| 🚀 | **Scalability**     | *Dockerized service suggests container scalability potential.*      |


---

##  Repository Structure

```sh
└── full_year_project/
    ├── Dockerfile
    ├── README.md
    ├── app_configuration.py
    ├── backend.py
    ├── common_functions.py
    ├── database
    │   ├── Challenges_Wexplanations.csv
    │   ├── Dockerfile
    │   ├── Solutions_Wexplanations.csv
    │   ├── challanges.csv
    │   ├── create_table.py
    │   ├── entrypoint.sh
    │   ├── initialization.sql
    │   └── jsonChallenges.json
    ├── docker-compose.yml
    ├── password_config.json
    ├── passwords.txt
    ├── requirements.txt
    ├── static
    │   ├── 6037795.jpg
    │   ├── ComunicationLTD.png
    │   ├── security_image.jpeg
    │   ├── security_img.png
    │   ├── style.css
    │   └── website1.css
    └── templates
        ├── cardGeneral.html
        ├── change_password.html
        ├── game_finish.html
        ├── login.html
        ├── password_reset.html
        ├── password_reset_token.html
        ├── questions_answers.html
        ├── register.html
        ├── set_new_pwd.html
        ├── user_dashboard.html
        └── user_summarise.html
```

---

##  Modules

<details closed><summary>.</summary>

| File                                                                                                      | Summary                                                                                                                                                                                                                                                                                            |
| ---                                                                                                       | ---                                                                                                                                                                                                                                                                                                |
| [password_config.json](https://github.com/eranbabayov/full_year_project/blob/master/password_config.json) | Defines password policies and messages for validation within the authentication system of the project's architecture.                                                                                                                                                                              |
| [docker-compose.yml](https://github.com/eranbabayov/full_year_project/blob/master/docker-compose.yml)     | The `docker-compose.yml` orchestrates a multi-container setup, linking a web service to a database, exposing relevant ports, and defining the web’s runtime command.                                                                                                                               |
| [chalanges.py](https://github.com/eranbabayov/full_year_project/blob/master/chalanges.py)                 | The `chalanges.py` is central for challenge-management within a gamified platform, interfacing with the database and user interactions.                                                                                                                                                            |
| [Dockerfile](https://github.com/eranbabayov/full_year_project/blob/master/Dockerfile)                     | The Dockerfile sets up a container for the main web application, installing dependencies and exposing port 5000 for the Python-based backend service.                                                                                                                                              |
| [common_functions.py](https://github.com/eranbabayov/full_year_project/blob/master/common_functions.py)   | The code manages user interactions and data for a gamified challenge platform, providing the backend logic and UI elements. Essential to user authentication, password management, and challenge content delivery within a Dockerized environment.                                                 |
| [app_configuration.py](https://github.com/eranbabayov/full_year_project/blob/master/app_configuration.py) | Configures Flask app with email capabilities and security parameters, defines password policy from JSON config.                                                                                                                                                                                    |
| [backend.py](https://github.com/eranbabayov/full_year_project/blob/master/backend.py)                     | The `backend.py` file serves as the application's web server logic, leveraging Flask for routing and session handling, and imports shared utilities and settings.                                                                                                                                  |
| [passwords.txt](https://github.com/eranbabayov/full_year_project/blob/master/passwords.txt)               | The repository contains the backend of a full-year project with a focus on challenge management, featuring Docker integration, application configuration, common utilities, and a database setup for storing challenges and solutions.                                                             |
| [requirements.txt](https://github.com/eranbabayov/full_year_project/blob/master/requirements.txt)         | The `full_year_project` repository includes a web application with a Flask backend, emphasizing cybersecurity education through challenges. Its structure implies user authentication, password management, and database interaction with Docker support. `requirements.txt` defines dependencies. |

</details>

<details closed><summary>templates</summary>

| File                                                                                                                          | Summary                                                                                                                                                          |
| ---                                                                                                                           | ---                                                                                                                                                              |
| [login.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/login.html)                               | This HTML template handles user login, displaying success messages and providing options for account creation and password resets within the web app's frontend. |
| [user_summarise.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/user_summarise.html)             | The `user_summarise.html` template visualizes a user's quiz performance, including scores, ranking, and statistical plots within the security training platform. |
| [game_finish.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/game_finish.html)                   | This HTML template displays a user's quiz score and navigation options post-game within a security education platform.                                           |
| [questions_answers.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/questions_answers.html)       | The `questions_answers.html` template supports the Q&A functionality within the full_year_project web application's user interface.                              |
| [register.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/register.html)                         | register.html` is the user registration interface, facilitating account creation within the web application's frontend.                                          |
| [set_new_pwd.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/set_new_pwd.html)                   | This HTML template facilitates resetting user passwords, vital for authentication and security within the project's web application framework.                   |
| [cardGeneral.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/cardGeneral.html)                   | This HTML template presents quiz questions and allows navigation between them as part of a security training web application.                                    |
| [password_reset.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/password_reset.html)             | This HTML template renders the password reset page within the web application, allowing users to request a password change via email.                            |
| [user_dashboard.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/user_dashboard.html)             | The `user_dashboard.html` serves as the user interface for account management and activity overview within the web platform's architecture.                      |
| [password_reset_token.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/password_reset_token.html) | Provides user interface for token-based password reset as part of a web application's authentication flow.                                                       |
| [change_password.html](https://github.com/eranbabayov/full_year_project/blob/master/templates/change_password.html)           | Handles web app backend logic; integrates with database, manages user authentication, and serves challenge content.                                              |

</details>

<details closed><summary>database</summary>

| File                                                                                                             | Summary                                                                                                                                                                                                          |
| ---                                                                                                              | ---                                                                                                                                                                                                              |
| [entrypoint.sh](https://github.com/eranbabayov/full_year_project/blob/master/database/entrypoint.sh)             | Initializes database and ensures persistence for SecurityPerformance in a Dockerized environment, augmenting repository's data layer automation.                                                                 |
| [Dockerfile](https://github.com/eranbabayov/full_year_project/blob/master/database/Dockerfile)                   | The Dockerfile establishes a containerized SQL Server for data storage within the project's database layer.                                                                                                      |
| [create_table.py](https://github.com/eranbabayov/full_year_project/blob/master/database/create_table.py)         | Initializes database with challenges and solutions, cleanses input CSVs, and populates SQL tables, supporting the project's data storage layer.                                                                  |
| [initialization.sql](https://github.com/eranbabayov/full_year_project/blob/master/database/initialization.sql)   | The code implements a web-based learning platform focusing on security education, integrating backend logic, database interaction, and front-end presentation, with Docker support for containerized deployment. |
| [jsonChallenges.json](https://github.com/eranbabayov/full_year_project/blob/master/database/jsonChallenges.json) | Central component of web-based challenge platform, integrates backend logic, security features, and data management within a Dockerized environment.                                                             |

</details>

---

##  Getting Started

***Requirements***

Ensure you have the following dependencies installed on your system:

* **HTML**: `version x.y.z`

###  Installation

1. Clone the full_year_project repository:

```sh
git clone https://github.com/eranbabayov/full_year_project
```

2. Change to the project directory:

```sh
cd full_year_project
```

3. Install the dependencies:

```sh
> INSERT-INSTALL-COMMANDS
```

###  Running full_year_project

Use the following command to run full_year_project:

```sh
> INSERT-RUN-COMMANDS
```
---

##  Contributing

Contributions are welcome! Here are several ways you can contribute:

- **[Submit Pull Requests](https://github.com/eranbabayov/full_year_project/blob/main/CONTRIBUTING.md)**: Review open PRs, and submit your own PRs.
- **[Join the Discussions](https://github.com/eranbabayov/full_year_project/discussions)**: Share your insights, provide feedback, or ask questions.
- **[Report Issues](https://github.com/eranbabayov/full_year_project/issues)**: Submit bugs found or log feature requests for Full_year_project.

<details closed>
    <summary>Contributing Guidelines</summary>

1. **Fork the Repository**: Start by forking the project repository to your GitHub account.
2. **Clone Locally**: Clone the forked repository to your local machine using a Git client.
   ```sh
   git clone https://github.com/eranbabayov/full_year_project
   ```
3. **Create a New Branch**: Always work on a new branch, giving it a descriptive name.
   ```sh
   git checkout -b new-feature-x
   ```
4. **Make Your Changes**: Develop and test your changes locally.
5. **Commit Your Changes**: Commit with a clear message describing your updates.
   ```sh
   git commit -m 'Implemented new feature x.'
   ```
6. **Push to GitHub**: Push the changes to your forked repository.
   ```sh
   git push origin new-feature-x
   ```
7. **Submit a Pull Request**: Create a PR against the original project repository. Clearly describe the changes and their motivations.

Once your PR is reviewed and approved, it will be merged into the main branch.

</details>

---

##  License

This project is protected under the [MIT](https://opensource.org/license/mit/) License.


---
