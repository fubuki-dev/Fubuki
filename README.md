![logo](https://raw.githubusercontent.com/fubuki-dev/Fubuki/main/assets/logo.png)
# Fubuki: Next generation hybrid web framework
Fubuki is a simple and flexible hybrid web framework. It is lightweight yet powerful, supporting rapid development. Fubuki is influenced by Laravel's features, while providing Flask-like ease of use in areas like routing. It also supports regular expressions in routes, allowing you to store arguments.

## Features

- Simple and intuitive API
- Middleware support
- Serving static files
- Template engine support
- Efficient routing
- Flexible development with hybrid architecture
- Features influenced by Laravel
- LiteStar-like easy routing
- Supports regular expressions and stores them in route arguments
- ASGI, RSGI support ()

## Installation

To install Fubuki, use the following command:

```sh
pip install fubuki
```

## Usage

### Creating a Project (WIP)

To create a new Fubuki project, run the following command:

```sh
fubuki create_project <project_name>
```

### Directory Structure

The directory structure of a new project is as follows:

```
<project_name>/
├── app/
│   ├── __init__.py
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── home_controller.py
│   ├── middlewares/
│   │   ├── __init__.py
│   │   └── logging_middleware.py
│   ├── static/
│   │   └── styles.css
│   ├── templates/
│   │   └── welcome.html
│   ├── routes.py
├── cli.py
├── app.py
└── main.py
```

### Adding a Controller

To add a controller, create a new Python file in the `app/controllers` directory and define the routes as follows:

```python
from fubuki import Controller, route
from fubuki.response import JSONResponse

class MyController(Controller):
    @route("/my_path")
    async def my_route(request: Request):
        return JSONResponse({"message": "Hello, World!"})
```

### Configuring the Application

To add controllers to the application, edit the `routes.py` file.

```python
from app.controllers.home_controller import UserController

def setup_routes(app):
    for controller_class in [MyController, UserController]:
        app.add_route(controller_class)
```

### Running the Application

To run the application, execute the `main.py` file.

```sh
python main.py
```

## Contributing

Contributions are welcome! You can submit bug reports, feature requests, and pull requests on the GitHub repository.

## License

This project is licensed under the MIT License. For more details, see the [LICENSE](LICENSE) file.

## Author

- Name: AmaseCocoa
- Fediverse: [@AmaseCocoa@misskey.io](https://misskey.io/@AmaseCocoa) 
