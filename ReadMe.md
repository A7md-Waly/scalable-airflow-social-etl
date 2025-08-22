# Social Media Analytics Pipeline

A comprehensive **data pipeline** that collects data from **X (Twitter)** and **YouTube**, processes it, and stores it in a **PostgreSQL database**. The pipeline is orchestrated using **Apache Airflow** running in Docker containers.

## Project Structure

```
SOCIAL_MEDIA_ANALYTICS/
├── dags/
│   └── Social_Media.py          # Main Airflow DAG
├── Output/
│   └── sample_data/
│       └── social_posts.json    # Sample output data
├── sql/
│   └── init_tables.sql          # Social media schema
├── src/
│   └── collectors/
│       ├── test_x_api.py        # X (Twitter) API collector
│       └── test_youtube_api.py  # YouTube API collector
├── ReadMe.md                    # This file
├── requirements.txt             # Python dependencies
└──docker-compose.yml           # Docker services configuration
```

## Prerequisites

### 1. Software Requirements
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop)
- **VS Code** (recommended IDE)
- **Git** for version control
- **Python 3.8+** (for local development)

Verify Docker installation:
```bash
docker --version
docker compose version
```

### 2. API Keys Setup
You'll need API credentials from both platforms:

#### X (Twitter) API
1. Visit [X Developer Portal](https://developer.twitter.com/)
2. Create a new project/app
3. Generate a **Bearer Token**

#### YouTube Data API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable **YouTube Data API v3**
4. Create an **API Key**

## Quick Start Guide

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd SOCIAL_MEDIA_ANALYTICS
```

### Step 2: Configure Environment Variables
Create a `.env` file in the root directory:
```bash
# API Configuration
X_BEARER_TOKEN=your_x_bearer_token_here
YOUTUBE_API_KEY=your_youtube_api_key_here

# Database Configuration (optional - uses Docker defaults)
POSTGRES_USER=airflow
POSTGRES_PASSWORD=airflow
POSTGRES_DB=airflow
```

### Step 3: Start Docker Services
```bash
# Start all services in background
docker compose up -d

# Check if all containers are running
docker ps
```

This will start:
- 🌐 **Airflow Webserver** → http://localhost:8080
- 📊 **Airflow Scheduler** → Background process
- 🗄️ **PostgreSQL Database** → Port 5432

### Step 4: Access Airflow UI
1. Open your browser and go to: **http://localhost:8080**
2. Login credentials:
   - **Username**: `airflow`
   - **Password**: `airflow`

### Step 5: Configure Airflow Variables
In Airflow UI, go to **Admin** → **Variables** and add:

| Key | Value |
|-----|-------|
| `X_BEARER_TOKEN` | Your X Bearer Token |
| `YT_API_KEY` | Your YouTube API Key |

### Step 6: Set up PostgreSQL Connection
1. In Airflow UI → **Admin** → **Connections**
2. Click **+** to add new connection:
   - **Connection Id**: `postgres_default`
   - **Connection Type**: `Postgres`
   - **Host**: `postgres`
   - **Schema**: `airflow`
   - **Login**: `airflow`
   - **Password**: `airflow`
   - **Port**: `5432`

### Step 7: Initialize Database Tables
```bash
# Get PostgreSQL container name
docker ps | grep postgres

# Execute initialization script
docker exec -it <postgres_container_name> psql -U airflow -d airflow -f /opt/airflow/sql/init_tables.sql
```

### Step 8: Run the Pipeline
1. In Airflow UI, find the DAG named `social_media_pipeline_dag`
2. Toggle it **ON** (switch on the left)
3. Click **Trigger DAG** to run manually

## Data Output

The pipeline collects and stores:
- **X (Twitter) Posts**: Tweet content, engagement metrics, user info
- **YouTube Videos**: Video metadata, view counts, channel information

Sample output format can be found in `Output/sample_data/social_posts.json`

## Development & Testing

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Test X API collector
python src/collectors/test_x_api.py

# Test YouTube API collector
python src/collectors/test_youtube_api.py
```

### Monitoring Pipeline
- **Airflow UI**: Monitor DAG runs and task status
- **Database**: Connect with tools like DBeaver to view stored data
  - Host: `localhost:5432`
  - Database: `airflow`
  - User: `airflow`
  - Password: `airflow`

## Troubleshooting

### Common Issues

**Docker doesn't start**
```bash
# Make sure Docker Desktop is running
docker info
```

**Airflow UI not accessible**
```bash
# Check if webserver container is running
docker ps | grep webserver

# Check logs
docker logs <airflow_webserver_container_name>
```

**API Keys not working**
- Verify your API keys are valid and have proper permissions
- Check Airflow Variables are set correctly
- Review API rate limits

**Database connection issues**
```bash
# Test PostgreSQL connection
docker exec -it <postgres_container> psql -U airflow -d airflow -c "\dt"
```

**Pipeline fails**
- Check Airflow task logs in the UI
- Verify API endpoints are accessible
- Ensure database tables exist

## Security Best Practices

- Never commit API keys to version control
- Use Airflow Variables or environment variables for sensitive data
- Keep your Docker images updated
- Monitor API usage and costs

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

---

**Happy Data Pipelining!**
