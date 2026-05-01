# temporal-keda-worker

A minimal Temporal worker for validating **KEDA autoscaling** on [Porter](https://porter.run) with Temporal Cloud.

This repo is specifically designed to test that the KEDA 2.19.0 TLS fix works correctly when using API Key authentication with Temporal Cloud.

---

## Project Structure

```
.
├── worker.py          # Entry point — connects to Temporal Cloud and starts the worker
├── config.py          # Reads all config from environment variables
├── workflows.py       # Minimal workflow definition
├── activities.py      # Minimal activity definition
├── enqueue_tasks.py   # Script to push tasks into the queue (triggers scaling)
├── requirements.txt
├── Dockerfile
├── .env.example
└── .gitignore
```

---

## Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `TEMPORAL_ENDPOINT` | ✅ | — | gRPC endpoint, e.g. `your-ns.a1b2c.tmprl.cloud:7233` |
| `TEMPORAL_NAMESPACE` | ✅ | — | Temporal namespace, e.g. `your-ns.a1b2c` |
| `TEMPORAL_API_KEY` | ✅ | — | API key from a Temporal Cloud Service Account |
| `TEMPORAL_TASK_QUEUE` | ❌ | `keda-test-queue` | Task queue name to poll |

---

## Running Locally

```bash
# 1. Clone and set up
cp .env.example .env
# Fill in your values in .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the worker
export $(cat .env | xargs)
python worker.py
```

---

## Docker

```bash
# Build
docker build -t temporal-keda-worker .

# Run
docker run \
  -e TEMPORAL_ENDPOINT=your-namespace.a1b2c.tmprl.cloud:7233 \
  -e TEMPORAL_NAMESPACE=your-namespace.a1b2c \
  -e TEMPORAL_API_KEY=your-api-key \
  -e TEMPORAL_TASK_QUEUE=keda-test-queue \
  temporal-keda-worker
```

---

## Triggering Autoscaling (Enqueue Tasks)

Run this locally to push workflows into the queue and trigger KEDA to scale up:

```bash
export $(cat .env | xargs)
python enqueue_tasks.py --count 10
```

With `targetQueueSize: 1` in your Porter autoscaling config and 10 tasks enqueued,
KEDA should scale your worker up to the configured maximum replicas.

---

## Deploying on Porter

1. Push this repo to GitHub
2. In Porter → **New Application → Deploy from GitHub**
3. Select this repo, Porter will auto-detect the `Dockerfile`
4. Set the environment variables (`TEMPORAL_ENDPOINT`, `TEMPORAL_NAMESPACE`, `TEMPORAL_API_KEY`, `TEMPORAL_TASK_QUEUE`) in Porter's **Environment** tab
5. In the **Resources** tab, enable **Autoscaling → Temporal**
6. Configure the Temporal integration and set `Task queue name` to match `TEMPORAL_TASK_QUEUE`

---

## Validating the KEDA 2.19.0 TLS Fix

If the fix is working, you should see in KEDA operator logs:
- ✅ No `connection reset by peer` errors
- ✅ No `tls: certificate required` errors
- ✅ `ScaledObject` status shows `READY=True`

The previous bug (fixed in 2.19.0 via PR #7367) caused KEDA to fail connecting
to Temporal Cloud when using API Key auth because TLS RootCAs were not initialized correctly.
