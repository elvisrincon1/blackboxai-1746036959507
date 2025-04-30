
Built by https://www.blackbox.ai

---

```markdown
# Plataforma de Afiliados

## Project Overview
Plataforma de Afiliados is a web-based application that enables users to manage affiliate marketing processes. The platform consists of different user roles: *Master*, *Supervisor*, and *Afiliado*, each with specific functionalities for managing users and products. Users can log in to their respective panels to perform actions such as creating users, uploading products, and managing product availability.

## Installation
To get started with the Plataforma de Afiliados, follow these simple steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/username/plataforma-afiliados.git
   ```
2. Navigate to the project directory:
   ```bash
   cd plataforma-afiliados
   ```
3. Open the `index.html` file in your preferred web browser. You can simply double-click the file or open it through your browser's file menu.

## Usage
- **Access the Login Page:** Open `index.html` to access the login page.
- **Login as User:**
  - For *Master*: username `master`, password `master123`
  - For *Supervisor*: username `supervisor`, password `supervisor123`
  - For *Afiliado*: username `afiliado`, password `afiliado123`
  
  Each role will redirect to its designated panel after a successful login.

## Features
- **User Management:**
  - Create new users with specified roles in the Master panel.
  - Manage affiliate accounts in the Supervisor panel.
  
- **Product Management:**
  - Upload and publish products in Master and Supervisor panels.
  - View available products in different categories for affiliates.

- **User-Friendly Interface:** Designed using Tailwind CSS for a streamlined and responsive experience.

## Dependencies
The project uses the following external libraries:
- [Tailwind CSS](https://tailwindcss.com/) for styling.
- [Font Awesome](https://fontawesome.com/) for icons.
- Google Fonts for typography (`Inter` font).

## Project Structure
Here's an overview of the file structure for the project:

```
plataforma-afiliados/
├── index.html       # Login page for the platform
├── master.html      # Master user panel for managing users and products
├── supervisor.html   # Supervisor panel for managing affiliates and products
└── afiliado.html    # Affiliate panel for accessing available products
```

The HTML files are structured with responsive designs, and each panel implements JavaScript functionalities for interactive features like form submissions and button actions.

## License
This project is open-source and available under the MIT License.
```