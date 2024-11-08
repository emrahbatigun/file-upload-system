
# File Upload System

A secure, scalable, and Dockerized file upload system built with Django, designed for handling and validating `.txt` files. This project emphasizes data security and provides a structured, IP-restricted file upload process with SSL encryption, AWS S3 integration, and RDS for secure storage.

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Security Measures](#security-measures)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Environment Variables](#environment-variables)
- [Docker Setup](#docker-setup)
- [AWS S3 Configuration](#aws-s3-configuration)
- [AWS RDS Configuration](#aws-rds-configuration)
- [SSL Configuration](#ssl-configuration)
- [Usage](#usage)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)

---

## Features

- **User Authentication**: Secure login and registration using Django’s authentication.
- **File Validation**: Accepts `.txt` files only, supports utf-8 characters, and validates file content.
- **Dockerized Setup**: Streamlined environment setup and deployment.
- **AWS Integration**: Uses S3 for secure, scalable file storage, accessible only from the EC2 instance.
- **AWS RDS**: Uses a private RDS instance accessible only from the EC2 instance’s IP with a secured connection peer.
- **IP-Restricted Access**: Ensures only specific IP addresses can access S3 and RDS, limiting exposure.
- **SSL Encryption**: Data transmitted securely through SSL, preventing data interception.
- **Environment Variables**: Sensitive data stored securely via environment variables.
- **Detailed Testing Suite**: Automated tests ensure system reliability, validating functionality and security.

---

## Project Structure

- **`file_upload_system/`**: Main Django project files (settings, URLs).
- **`users/`**: Handles user authentication (registration, login).
- **`files/`**: File upload and management module.
- **`templates/`**: HTML templates for frontend.
- **`static/`**: Static files (CSS, JavaScript).
- **`tests/`**: Automated test scripts for various components.

---

## Security Measures

1. **SSL (Secure Sockets Layer)**: Encrypts data transmitted between the server and clients, safeguarding sensitive information.
2. **IP Restriction for S3 Bucket**: Limits S3 bucket access to requests coming from your EC2 instance's IP address only, reducing exposure to external threats.
3. **Private RDS Instance with Peer Connection**: AWS RDS database is configured to accept requests only from the EC2 instance's IP, with a direct connection peer setup for secure communication.
4. **Environment Variables**: Stores sensitive credentials (e.g., AWS keys, Django secret key) securely in `.env` files.
5. **File Validation**: Ensures only `.txt` files are uploaded, preventing malicious file types.
6. **Access Control**: Authentication ensures only logged-in users can upload, view, or download files.

---

## Prerequisites

- **Docker** & **Docker Compose**
- **AWS Account** (for S3, RDS, and EC2 setup)
- **SSL Certificate** (for secure connections)
- **Python 3.10** installed locally (for running and testing)

---

## Setup Instructions

### Step 1: Clone the Repository

```bash
git clone https://github.com/emrahbatigun/file-upload-system.git
cd file-upload-system
```

### Step 2: Set Up Environment Variables

Create a `.env` file in the root directory, specifying the necessary environment variables:

```dotenv
AWS_ACCESS_KEY=
AWS_SECRET_ACCESS_KEY=
AWS_REGION_NAME=
AWS_BUCKET_NAME=
AWS_ENCRYPTION_TYPE=
AWS_ENCRYPTION_KEY_ID=
DJANGO_SECRET_KEY=
SSL_PATH=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
SERVER_IP=
```

> **Note**: Ensure `.env` is added to `.gitignore` to avoid committing sensitive information.

---

## Docker Setup

### Step 1: Build and Run Containers

Use Docker Compose to build and run the application:

```bash
docker-compose up --build
```

This setup includes the following services:

- **app**: The main Django application server, configured to:
  - Run database migrations.
  - Collect static files.
  - Start the Django development server on port 8000.

- **db**: PostgreSQL database for managing user data and file records.

### Step 2: Dockerfile Details

The `Dockerfile` uses a lightweight **Python 3.10 Alpine** image as the base, minimizing the image size. It installs necessary dependencies, including `gcc`, `musl-dev`, `linux-headers`, and `mariadb-dev` for building and running Python and database packages. Key configurations include:

- **Environment Variables**: Disables `.pyc` file creation (`PYTHONDONTWRITEBYTECODE=1`) and enables unbuffered output (`PYTHONUNBUFFERED=1`) for cleaner logs.
- **Dependency Installation**: Installs Python dependencies from `requirements.txt`.
- **Static Files**: Collects static files to a dedicated `static-data` volume.
- **Port Exposure**: Exposes port `8000` for the Django development server.

### Step 3: Docker Compose Configuration

In the `docker-compose.yml` file:

- **Service Definition**:
  - `app`: Builds from the `Dockerfile`, loads environment variables from `.env`, and maps port `8000` to allow external access.
  - The `static-data` volume stores collected static files, ensuring persistence across container restarts.

### Step 2: Access the Application

Once the containers are running, access the application at `https://ec2-ip`.

---

## AWS S3 Configuration

1. **Create an S3 Bucket** for secure file storage.
2. **IP Restriction**: In the S3 bucket permissions, allow access only from the EC2 instance's IP.
3. **Set Bucket Policy**:

   ```json
   {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::bucket-name/*",
            "Condition": {
                "NotIpAddress": {
                    "aws:SourceIp": [
                        "IP_1",
                        "IP_2"
                    ]
                },
                "StringNotEquals": {
                    "s3:x-amz-server-side-encryption": "encryption-type"
                }
            }
        },
        {
            "Effect": "Deny",
            "Principal": "*",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::bucket-name/*",
            "Condition": {
                "NotIpAddress": {
                    "aws:SourceIp": [
                        "IP_1",
                        "IP_2"
                    ]
                }
            }
        }
    ]
   }
   ```

4. **Add Environment Variables**: Include your AWS credentials in the `.env` file or configure the IAM roles and permission without using credentials.

---

## AWS RDS Configuration

1. **Create an RDS Instance** in a private subnet within your VPC.
2. **Set Security Group Rules** to allow inbound connections only from your EC2 instance’s IP.
3. **Peer Connection**: Establish a direct connection peer between the EC2 instance and the RDS instance for secure, efficient communication.
4. **Database URL**: Use the RDS endpoint in your `DB_HOST` in the `.env` file to connect Django to the RDS instance securely.
5. **Subnet and Security**: Configure RDS to operate within a private subnet, ensuring it is not publicly accessible.

> This configuration ensures that only requests from the EC2 instance can access the RDS instance through a dedicated peer connection, providing an additional layer of security.

---

## SSL Configuration

1. **Obtain an SSL Certificate** from AWS Certificate Manager or a trusted SSL provider.
2. **Configure SSL on EC2**: Set up SSL termination to encrypt communication between clients and your EC2 instance.

---

## Usage

1. **Sign Up / Login**: Register or log in to access the upload feature.
2. **File Upload**: Upload `.txt` files. Validation ensures only `.txt` files with utf-8 characters are accepted.
3. **File Management**: View and manage uploaded files. Only the owner can list,view or download their files.

---

## Testing

The application includes an extensive suite of tests for validation and security.

### Running Tests

To run the tests, use the following command:

```bash
docker-compose run web pytest
```

### Test Files Explanation

Each test file in the `tests/` directory is designed to validate specific components of the application:

- **`test_authentication.py`**: Tests user registration, login, and authentication flows, ensuring secure access control with validations for successful signup, password confirmation, email uniqueness, and logout functionality.

- **`test_file_upload.py`**: Ensures `.txt` file validation, utf-8 character support, secure file handling, and size restrictions (0.5KB to 2KB). Verifies proper error handling for unsupported file types and invalid file contents.

- **`test_s3_integration.py`**: Validates the functionality of uploading files to S3 with IP restrictions and verifies file download, ensuring that only authenticated users with appropriate permissions can access files.

- **`test_environment_variables.py`**: Confirms that sensitive data is accessed via environment variables and not hardcoded, ensuring better security practices for sensitive information.

- **`test_rds_integration.py`**: Validates secure connectivity and restricted access between Django and the private RDS instance with peer connection, ensuring a secure setup for database interactions.

- **`test_api.py`**: Contains tests for the file-related API endpoints, including file upload and download functionalities, file content retrieval, and listing of uploaded files. Ensures appropriate responses for authenticated and unauthenticated users, and validates error messages for various edge cases, such as file size or type issues.

- **`test_integration.py`**: Tests integration scenarios, such as the upload and download cycle and file content viewing, to validate that each process completes smoothly from end to end, with logs stored for each access. Ensures that the upload, download, and file view operations log user actions appropriately.

- **`test_models.py`**: Tests the `File` and `FileAccessLog` models, including creation, string representation, and logging. Ensures correct instantiation of files and logs, and verifies that string representations provide useful information.

- **`test_performance.py`**: Tests performance for large file upload and download operations, ensuring that these actions complete within a reasonable time limit (under 2 seconds), demonstrating efficient handling of larger files.

- **`test_serializers.py`**: Tests the `FileUploadSerializer` to confirm that it properly validates file input, catching errors when no file is provided and verifying correct handling of valid file inputs.

- **`test_views.py`**: Contains tests for user authentication views, including signup, signin, and logout. Covers edge cases, such as password mismatches, email uniqueness, required field validation, and proper redirection after signup or logout, ensuring smooth user management.

> **Note**: Regular testing is recommended before deploying updates to ensure system integrity and to detect any issues with authentication, file handling, or performance in the application.


---

## Deployment

For production deployment, make sure to set `DEBUG=False` in your `.env` file and configure SSL. Follow these steps:

1. **Push Changes to EC2**: Deploy the updated code to your EC2 instance.
2. **Run Docker Containers**: Use Docker Compose to build and start the containers.
3. **Verify IP Restriction and SSL**: Ensure only requests from the specified IP can access S3 and RDS, and SSL is active for secure connections.

---

## CI/CD Pipeline

This project includes a CI/CD setup to automate testing and deployment. The pipeline performs the following steps:

1. **Build**: Builds the Docker image for deployment.
2. **Testing**: Runs the full test suite to ensure application stability. If tests fail, it exits.
3. **Deployment**: Deploys the updated application if all tests pass.

Normally testing comes first but as we use advanced security steps, I used this order.

---
