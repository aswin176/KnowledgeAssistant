# Setup Guide

## System Requirements

- **OS**: macOS, Linux, or Windows with WSL2
- **RAM**: 8 GB minimum (16 GB recommended for Ollama)
- **Disk**: 10 GB free space
- **Docker**: 24.0+ with Compose V2

## Step 1: Clone and Configure

```bash
git clone <repo-url> Eutridats
cd Eutridats
cp backend/.env.example backend/.env
```

Edit `backend/.env` to set secure passwords:

```env
SECRET_KEY=<generate-with-openssl-rand-hex-32>
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
NEO4J_PASSWORD=your-secure-password
ADMIN_PASSWORD=your-admin-password
```

## Step 2: Start Services

```bash
docker compose up -d
```

Wait for all services to be healthy:

```bash
docker compose ps
```

## Step 3: Pull LLM Model

```bash
docker exec eutridats-ollama ollama pull qwen3
```

Alternative models: `llama3.2`, `mistral`, `qwen2.5`. Update `OLLAMA_MODEL` in `.env`.

## Step 4: Initialize Data

```bash
docker exec eutridats-backend python scripts/seed_data.py
```

## Step 5: Access the Application

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | admin / admin123 |
| API Docs | http://localhost:8000/docs | Bearer token |
| Neo4j Browser | http://localhost:7474 | neo4j / eutridats_password |

## Local Development (Without Docker)

### Neo4j

Install Neo4j Desktop or run via Docker:

```bash
docker run -d --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/eutridats_password \
  neo4j:5.26-community
```

### Ollama

```bash
# macOS
brew install ollama
ollama serve &
ollama pull qwen3
```

### Backend

```bash
cd backend
poetry install
cp .env.example .env
poetry run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
cd backend
poetry run pytest tests/ -v
poetry run pytest tests/ --cov=app --cov-report=term-missing
```

## Importing Your Data

1. Prepare a CSV with columns: `name`, `email`, `company`, `city`, `skills`, `title`
2. Go to Import Data page or use the API:

```bash
curl -X POST http://localhost:8000/api/v1/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@contacts.csv"
```

Supported formats: `.csv`, `.xlsx`, `.json`, `.md`, `.pdf`, `.docx`

## Telegram Bot Setup

1. Create a bot via [@BotFather](https://t.me/BotFather)
2. Configure:

```bash
cp telegram/.env.example telegram/.env
# Set TELEGRAM_BOT_TOKEN
```

3. Run:

```bash
docker compose -f docker-compose.prod.yml --profile telegram up -d telegram
```


 > [frontend production 2/2] RUN npm run build:
0.334 
0.334 > eutridats-frontend@0.1.0 build
0.334 > next build
0.334 
0.772 Attention: Next.js now collects completely anonymous telemetry regarding usage.
0.772 This information is used to shape Next.js' roadmap and prioritize features.
0.772 You can learn more, including how to opt-out if you'd not like to participate in this anonymous program, by visiting the following URL:
0.772 https://nextjs.org/telemetry
0.772 
0.835    ▲ Next.js 15.5.20
0.835 
0.907    Creating an optimized production build ...
11.17 <w> [webpack.cache.PackFileCacheStrategy] Skipped not serializable cache item 'Compilation/modules|/app/node_modules/next/dist/build/webpack/loaders/css-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[2]!/app/node_modules/next/dist/build/webpack/loaders/postcss-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[3]!/app/src/app/globals.css': No serializer registered for PostCSSSyntaxError
11.17 <w> while serializing webpack/lib/cache/PackFileCacheStrategy.PackContentItems -> webpack/lib/NormalModule -> webpack/lib/ModuleBuildError -> PostCSSSyntaxError
11.47 Failed to compile.
11.47 
11.47 ./src/app/globals.css:54:24
11.47 Syntax error: /app/src/app/globals.css Unclosed string
11.47 
11.47   52 |   body {
11.47   53 |     @apply bg-background text-foreground font-sans antialiased;
11.47 > 54 |     font-family: "Inter", system-ui, sans-serif;
11.47      |                        ^
11.47   55 |   }
11.47   56 | }
11.47 
11.47 ./src/app/globals.css
11.47 Syntax error: /app/src/app/globals.css Unclosed string (54:24)
11.47 
11.47   52 |   body {
11.47   53 |     @apply bg-background text-foreground font-sans antialiased;
11.47 > 54 |     font-family: "Inter", system-ui, sans-serif;
11.47      |                        ^
11.47   55 |   }
11.47   56 | }
11.47 
11.47     at tryRunOrWebpackError (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:316119)
11.47     at __webpack_require_module__ (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:131532)
11.47     at __nested_webpack_require_161494__ (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:130967)
11.47     at /app/node_modules/next/dist/compiled/webpack/bundle5.js:29:131824
11.47     at symbolIterator (/app/node_modules/next/dist/compiled/neo-async/async.js:1:14444)
11.47     at done (/app/node_modules/next/dist/compiled/neo-async/async.js:1:14824)
11.47     at Hook.eval [as callAsync] (eval at create (/app/node_modules/next/dist/compiled/webpack/bundle5.js:14:9224), <anonymous>:15:1)
11.47     at Hook.CALL_ASYNC_DELEGATE [as _callAsync] (/app/node_modules/next/dist/compiled/webpack/bundle5.js:14:6378)
11.47     at /app/node_modules/next/dist/compiled/webpack/bundle5.js:29:130687
11.47     at symbolIterator (/app/node_modules/next/dist/compiled/neo-async/async.js:1:14402)
11.47 -- inner error --
11.47 Syntax error: /app/src/app/globals.css Unclosed string (54:24)
11.47 
11.47   52 |   body {
11.47   53 |     @apply bg-background text-foreground font-sans antialiased;
11.47 > 54 |     font-family: "Inter", system-ui, sans-serif;
11.47      |                        ^
11.47   55 |   }
11.47   56 | }
11.47 
11.47     at Object.<anonymous> (/app/node_modules/next/dist/build/webpack/loaders/css-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[2]!/app/node_modules/next/dist/build/webpack/loaders/postcss-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[3]!/app/src/app/globals.css:1:7)
11.47     at /app/node_modules/next/dist/compiled/webpack/bundle5.js:29:962717
11.47     at Hook.eval [as call] (eval at create (/app/node_modules/next/dist/compiled/webpack/bundle5.js:14:9002), <anonymous>:7:1)
11.47     at Hook.CALL_DELEGATE [as _call] (/app/node_modules/next/dist/compiled/webpack/bundle5.js:14:6272)
11.47     at /app/node_modules/next/dist/compiled/webpack/bundle5.js:29:131565
11.47     at tryRunOrWebpackError (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:316073)
11.47     at __webpack_require_module__ (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:131532)
11.47     at __nested_webpack_require_161494__ (/app/node_modules/next/dist/compiled/webpack/bundle5.js:29:130967)
11.47     at /app/node_modules/next/dist/compiled/webpack/bundle5.js:29:131824
11.47     at symbolIterator (/app/node_modules/next/dist/compiled/neo-async/async.js:1:14444)
11.47 
11.47 Generated code for /app/node_modules/next/dist/build/webpack/loaders/css-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[2]!/app/node_modules/next/dist/build/webpack/loaders/postcss-loader/src/index.js??ruleSet[1].rules[14].oneOf[10].use[3]!/app/src/app/globals.css
11.47 
11.47 Import trace for requested module:
11.47 ./src/app/globals.css
11.47 
11.51 
11.51 > Build failed because of webpack errors
------
failed to solve: process "/bin/sh -c npm run build" did not complete successfully: exit code: 1