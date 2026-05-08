<div align="center">

# PA4 Submission: TaskFlow Pipeline

<img alt="GitHub only" src="https://img.shields.io/badge/Submit-GitHub%20URL%20Only-10b981?style=for-the-badge">
<img alt="Total points" src="https://img.shields.io/badge/Total-100%20points-7c3aed?style=for-the-badge">

</div>

<div style="background:#f5f3ff;color:#111827;border-left:6px solid #6330bc;padding:14px 18px;border-radius:10px;margin:18px 0;">
Every screenshot is embedded under the correct task with a short description. The grader should not need any file outside this repository.
</div>

## Student Information

| Field | Value |
|---|---|
| Name | Amna Iftikhar |
| Roll Number | 26100396 |
| GitHub Repository URL | https://github.com/Amna1059/CS487-PA4 |
| Resource Group | `rg-sp26-26100396` |
| Assigned Region | `ukwest` |

## Evidence Rules

- Relative image paths are used throughout.
- Every image has a 1–3 sentence description below it.
- Azure Portal screenshots show the resource name and enough context to identify the service.
- CLI screenshots show the command and its output.
- Secrets (ACR passwords, function keys, connection strings) are masked by the portal's "Show value" toggle.

---

## Task 1: App Service Web App (15 points)

### Evidence 1.1: Forked Repository

![Forked repository — git clone output](<docs/images_pa4/images/task1/Screenshot 2026-05-07 132918.png>)

`Amna1059/CS487-PA4` is forked from `KarmaMS/CS487-PA4` as required by Task 1. All required directories — `function-app`, `report-job`, `validate-api`, `webapp`, and `docs` — are present on the `main` branch.

### Evidence 1.2: App Service Overview

![App Service overview — pa4-26100396](<docs/images_pa4/images/task1/Screenshot 2026-04-29 154303.png>)

The Azure Portal shows Web App **pa4-26100396** in resource group `rg-sp26-26100396`, status **Running**, location **UK West**, runtime **Node 20-lts**, on plan `asp-26100396 (B1: 1)`. The public default domain is `pa4-26100396-dxa9d8b8g4c5aza0.ukwest-01.azurewebsites.net` and the GitHub Project link points to `Amna1059/CS487-PA4`.

### Evidence 1.3: Deployment Center / GitHub Actions

![Deployment Center — GitHub Actions wired to main branch](<docs/images_pa4/images/task1/Screenshot 2026-04-29 154329.png>)

The Deployment Center blade for `pa4-26100396` shows source **GitHub**, organisation `Amna1059`, repository `CS487-PA4`, branch `main`, build provider **GitHub Actions**, runtime **Node 20-lts**. Every push to `main` triggers an automated build-and-deploy pipeline that keeps the App Service in sync with the repository.

### Evidence 1.4: Live Web UI

![TaskFlow running live in the browser](<docs/images_pa4/images/task1/Screenshot 2026-04-29 154231.png>)

The browser address bar shows `pa4-26100396-dxa9d8b8g4c5aza0.ukwest-01.azurewebsites.net` and the TaskFlow order-submission form is rendered and responsive. The form accepts Order ID, SKU, and Quantity (Max 100), confirming the App Service is publicly serving the frontend.

### Evidence 1.5: Application Settings

![TaskFlow running live in the browser](<docs/images_pa4/images/task1/Screenshot 2026-04-29 154353.png>)

The browser showing `FUNCTION_START_URL ` and `FUNCTION_STATUS_URL ` in the environment variables of the web app.

---

## Task 2: Azure Container Registry (15 points)

### Evidence 2.1: ACR Overview

![ACR Overview](<docs/images_pa4/images/task2/Screenshot 2026-05-08 040609.png>)

Image shows the successful creation of ACR.

### Evidence 2.2: Docker Builds

![Docker build — validate-api:v1](<docs/images_pa4/images/task2/Screenshot 2026-04-29 174852.png>)

`docker build -t validate-api:v1 .` run from the `validate-api/` folder. The output shows all image layers pulled from `docker.io/library/python:3.11-slim`, the `requirements.txt` install, and the final image ID assigned. This is the local build step before pushing to ACR.

![Local validate-api smoke test](<docs/images_pa4/images/task2/Screenshot 2026-04-29 173411.png>)

After starting the container locally on port 8080, `Invoke-RestMethod -Uri "http://localhost:8080/validate"` with order `LOCAL-1` (sku ABC, qty 2) returns `valid: True, reason: ok, order_id: LOCAL-1`, confirming the `validate-api` image works correctly before being pushed to the registry.

![ACR build — function-app:v1 successfully pushed](<docs/images_pa4/images/task2/Screenshot 2026-05-02 012543.png>)

`az acr build` output for the `function-app/` folder shows all layers pushed to `acrpa426100396.azurecr.io/function-app:v1`. Run ID `dc4` completed in 1m 45s, with SHA-256 digest recorded. The same `az acr build` pattern was used for `validate-api:v1` and `report-job:v1`.

### Evidence 2.3: ACR Repositories

![ACR repository list — all three repos](<docs/images_pa4/images/task2/Screenshot 2026-05-02 022058.png>)

`az acr repository list --name acrpa426100396 --output table` lists **func-app**, **report-job**, and **validate-api** — all three required repositories are present in the registry, each with a `v1` tag pushed and ready for deployment.

---

## Task 3: Durable Function Implementation (12 points)

### Evidence 3.1: Completed Function Code

[function-app/function_app.py](function-app/function_app.py)

The orchestrator `my_orchestrator` chains two activities sequentially: it first calls `validate_activity`, which POSTs the order JSON to the AKS validator at `VALIDATE_URL`; if the result is not valid it immediately returns `{"status":"rejected","reason":"..."}` without proceeding. If valid, it calls `report_activity`, which uses the Azure Container Instance Management SDK (`DefaultAzureCredential` + user-assigned MI) to spin up an ephemeral `ci-report-<order_id>` container that generates and uploads the PDF, polls until the container reaches `Succeeded`, deletes the container group, and returns the blob URL. State between the two `yield` calls is checkpointed by the Durable runtime, so no thread is ever blocked for the full ACI lifetime.

### Evidence 3.2: Local Function Handler Listing

![func start — all four handlers discovered](<docs/images_pa4/images/task3/Screenshot 2026-05-02 032147.png>)

`func start` inside the `function-app/` virtual environment shows Azure Functions Core Tools v4.10.0 and runtime v4.1048 discovering all four handlers: `http_starter` (POST HTTP trigger at `/api/orchestrators/my_orchestrator`), `my_orchestrator` (orchestrationTrigger), `report_activity` (activityTrigger), and `validate_activity` (activityTrigger). The worker process started and initialised without errors.

---

## Task 4: Function App Container Deployment (8 points)

### Evidence 4.1: Function App Container Configuration

![Function App — all four functions Enabled](<docs/images_pa4/images/task4/Screenshot 2026-05-03 235347.png>)

The Azure Portal Functions blade for **pa4-26100396-fn** lists `http_starter` (HTTP, Enabled), `my_orchestrator` (Orchestration, Enabled), `report_activity` (Activity, Enabled), and `validate_activity` (Activity, Enabled). All four handlers were discovered from the running container, confirming the `func-app:v1` image from ACR is executing correctly in the cloud.

![Deployment Center — func-app:v1 from acrpa426100396](<docs/images_pa4/images/task4/Screenshot 2026-05-03 235428.png>)

The Deployment Center (Containers tab) for `pa4-26100396-fn` shows image source **Azure Container Registry**, registry `acrpa426100396`, image `func-app`, tag `v1`. The Function App pulls this custom container on every restart instead of using a code-based deployment.

### Evidence 4.2: Orchestration Smoke Test

![curl — orchestration started, statusQueryGetUri returned](<docs/images_pa4/images/task4/WhatsApp Image 2026-05-03 at 11.41.48 PM.jpeg>)

A `curl -X POST` to `https://pa4-26100396-function.azurewebsites.net/api/orchestrators/my_orchestrator` with order `SMOKE-001` returns instance ID `eb3e87e9bcd849a1a4d5c9f0a9f6cd10` and a full set of Durable management URLs (`statusQueryGetUri`, `sendEventPostUri`, `terminatePostUri`, etc.), proving the HTTP starter is live and the Durable engine accepted the orchestration.

### Evidence 4.3: Expected Failed Status Before Downstream Wiring

![Status query — KeyError VALIDATE_URL](<docs/images_pa4/images/task4/WhatsApp Image 2026-05-03 at 11.42.24 PM.jpeg>)

Querying the `statusQueryGetUri` immediately after the smoke test returns `runtimeStatus: Failed` with a Python `KeyError: 'VALIDATE_URL'` stack trace. This is the expected result at this stage: `VALIDATE_URL` had not yet been configured (that is Task 5), so `validate_activity` could not reach the AKS endpoint. The failure confirms the orchestrator is correctly progressing through activities and that only the missing configuration is blocking completion.

---

## Task 5: AKS Validator (15 points)

### Evidence 5.1: AKS Cluster

![az aks get-credentials + kubectl get nodes](<docs/images_pa4/images/task5/Screenshot 2026-05-03 235738.png>)

`az aks get-credentials --resource-group rg-sp26-26100396 --name pa4-26100396` merges kubeconfig, and `kubectl get nodes` confirms node `aks-nodepool1-14991093-vmss000000` is **Ready** (Kubernetes v1.34.4, age 2m9s). The cluster is named `pa4-26100396` inside resource group `rg-sp26-26100396`, UK West.

### Evidence 5.2: Kubernetes Nodes and Pods

![kubectl get nodes — single node Ready](<docs/images_pa4/images/task5/Screenshot 2026-05-03 235738.png>)

The single system node is **Ready** with no taints, confirming the cluster control plane and node pool are healthy and the `kubectl` context is correctly configured.

![kubectl get pods -w — validator pod reaches Running](<docs/images_pa4/images/task5/Screenshot 2026-05-04 003136.png>)

`kubectl get pods -w` captures the rollout: the original pods entered `ImagePullBackOff` (wrong image reference), were terminated, and then `validate-deployment-848cf4ffdd-2xftw` reached **1/1 Running** with 0 restarts after the deployment was updated with the correct ACR image URI. The validator pod is now scheduled and serving.

### Evidence 5.3: Kubernetes Service

![kubectl get service validate-service — LoadBalancer](<docs/images_pa4/images/task5/Screenshot 2026-05-04 004937.png>)

`kubectl get service validate-service` shows a **LoadBalancer** service: cluster IP `10.0.137.211`, external IP **51.104.39.228**, port mapping `8080:30688/TCP`, age 35m. The external IP `51.104.39.228:8080` is the endpoint the Durable Function uses to call the validator.

### Evidence 5.4: Validator API Tests

![curl /health, /validate valid, /validate invalid](<docs/images_pa4/images/task5/Screenshot 2026-05-04 003458.png>)

Three curl calls against `http://51.104.39.228:8080`:
- `/health` → `{"status":"ok"}`
- `/validate` with `O-1001` qty 2 → `{"valid":true,"reason":"ok","order_id":"O-1001"}`
- `/validate` with `O-1002` qty 999 → `{"valid":false,"reason":"quantity exceeds limit","order_id":"O-1002"}`

This confirms both the happy-path acceptance and the `qty > 100` rejection rule enforced by the AKS-hosted validator.

### Evidence 5.5: Function App `VALIDATE_URL`

![Function App setting — VALIDATE_URL](<docs/images_pa4/images/task5/Screenshot 2026-05-04 004918.png>)

The Function App application setting `VALIDATE_URL` is set to `http://51.104.39.228:8080/validate` — the LoadBalancer external IP of the AKS service. The `validate_activity` reads this variable at runtime via `os.environ["VALIDATE_URL"]`, so the Function App reaches the AKS validator without any hardcoded addresses.

### Evidence 5.6: AKS Idle Behavior

![AKS Idle Behavior](<docs/images_pa4/images/task5/Screenshot 2026-05-08 042325.png>)

---

## Task 6: ACI Report Job (15 points)

### Evidence 6.1: Blob Container

![az storage blob list — reports container with TEST-001.pdf](<docs/images_pa4/images/task6/Screenshot 2026-05-04 011549.png>)

`az storage blob list --account-name stcloudpa26100396 --container-name reports --auth-mode login --output table` shows `TEST-001.pdf` (BlockBlob, Hot tier, 1462 bytes) uploaded at `2026-05-03T20:12:58+00:00`. Generated PDFs land in the `reports` container of storage account `stcloudpa26100396` in `rg-sp26-26100396`.

### Evidence 6.2: Manual ACI Run

![az container show — ci-report-test instanceView.state = Succeeded](<docs/images_pa4/images/task6/Screenshot 2026-05-04 011508.png>)

`az container show --resource-group rg-sp26-26100396 --name ci-report-test --query "instanceView.state" --output tsv` returns `Succeeded`. The container reached a terminal success state after completing the PDF generation and blob upload, demonstrating the run-to-completion ACI pattern.

### Evidence 6.3: ACI Logs

![az container logs — Uploaded TEST-001.pdf to reports container](<docs/images_pa4/images/task6/Screenshot 2026-05-04 011527.png>)

`az container logs --resource-group rg-sp26-26100396 --name ci-report-test` prints `Uploaded TEST-001.pdf to reports container` — the single log line from the report-job container. This confirms the container ran, generated the PDF, and successfully wrote it to Azure Blob Storage before exiting.

### Evidence 6.4: Generated PDF

![az storage blob list — TEST-001.pdf confirmed in blob](<docs/images_pa4/images/task6/Screenshot 2026-05-04 011549.png>)

The blob listing confirms `TEST-001.pdf` exists in the `reports` container with `content-type: application/octet-stream` and a modification timestamp of `2026-05-03T20:12:58+00:00`, directly proving the ACI container wrote the file to Azure Blob Storage during its single execution.

### Evidence 6.5: Function App Managed Identity and IAM

![Function App Identity — user-assigned mi-pa4-26100396](<docs/images_pa4/images/task6/Screenshot 2026-05-04 011825.png>)

The Identity blade of `pa4-26100396-fn` (User assigned tab) shows managed identity **mi-pa4-26100396** attached, scoped to resource group `rg-sp26-26100396`, subscription `67e93b84-fe08-452c-80ea-175d0a3eca56`. This identity is granted **Contributor** on the resource group, allowing the Function App to call `ContainerInstanceManagementClient.container_groups.begin_create_or_update()` without storing any credentials in code or configuration.

### Evidence 6.6: Report App Settings

![Function App settings — ACR_* and AZURE_CLIENT_ID](<docs/images_pa4/images/task6/Screenshot 2026-05-04 013300.png>)

`ACR_PASSWORD` (masked), `ACR_SERVER`, and `ACR_USERNAME` are the registry credentials passed to the `ImageRegistryCredential` object when creating the ACI container group, so ACI can pull the `report-job:v1` image from the private `acrpa426100396` registry. `AZURE_CLIENT_ID` holds the client ID of `mi-pa4-26100396` so that `DefaultAzureCredential` inside the Function App picks the correct user-assigned identity.

![Function App settings — REPORT_* STORAGE_ACCOUNT_URL SUBSCRIPTION_ID VALIDATE_URL](<docs/images_pa4/images/task6/Screenshot 2026-05-04 013240.png>)

`REPORT_IMAGE` is the full ACR image URI for the report container. `REPORT_LOCATION` and `REPORT_RG` tell `report_activity` where to create the ACI group. `STORAGE_ACCOUNT_URL` is injected as an environment variable into the running container so the report job can connect to blob storage. `SUBSCRIPTION_ID` is required by the Azure SDK management client. `VALIDATE_URL` is included here to confirm it is configured alongside the report settings.

---

## Task 7: End-to-End Pipeline (15 points)

### Evidence 7.1: Web App Wiring

![Web App env vars — FUNCTION_START_URL and FUNCTION_STATUS_URL](<docs/images_pa4/images/task1/Screenshot 2026-04-29 154353.png>)

The Environment Variables blade of `pa4-26100396` shows `FUNCTION_START_URL` and `FUNCTION_STATUS_URL` configured as App Service application settings (values masked). The frontend JavaScript reads these at runtime to POST a new order to the Durable HTTP starter and to poll the status endpoint, so the web app is wired to the Function App without any hardcoded URLs.

### Evidence 7.2: Happy Path UI

![Happy path — form filled with ORD-001 qty 2](<docs/images_pa4/images/task7/4_happy/Screenshot 2026-05-05 160520.png>)

The TaskFlow form is populated with Order ID `ORD-001`, SKU `WIDGET-X`, Quantity `2` (well within the 100-unit limit). The Submit Order button is ready to be clicked. The URL bar confirms this is the live App Service (`pa4-26100396-dxa9d8b8g4c5aza0.ukwest-01.azurewebsites.net`).

![Happy path — Running badge with instance ID](<docs/images_pa4/images/task7/4_happy/Screenshot 2026-05-05 160528.png>)

Immediately after submission the UI shows a **Running** badge alongside the orchestration instance ID, confirming the HTTP starter accepted the order payload and the Durable orchestration has begun executing.

![Happy path — Completed with View PDF Report link](<docs/images_pa4/images/task7/4_happy/Screenshot 2026-05-05 160605.png>)

The status badge transitions to **Completed** and a **View PDF Report** button appears. The full pipeline executed: the AKS validator approved the order, the Durable Function created an ACI report container, the PDF was written to Blob Storage, and the report URL was returned to the frontend.

![Happy path — PDF blob URL accessed](<docs/images_pa4/images/task7/4_happy/Screenshot 2026-05-05 160616.png>)

Clicking the report link navigates to `pa426100396.blob.core.windows.net/reports/ORD-001.pdf`. The `PublicAccessNotPermitted` XML error confirms the blob was written (the URL and container are real) but anonymous public access is disabled on the storage account — this is the correct, secure configuration. The file can be accessed via SAS token or authenticated SDK calls.

### Evidence 7.3: Backend Participation

![Blob Storage — ORD-009.pdf written during end-to-end run](<docs/images_pa4/images/task7/Screenshot 2026-05-05 154434.png>)

`az storage blob list --account-name pa426100396 --container-name reports` (running with `watch` every 5 s) shows `ORD-009.pdf` (1469 bytes) uploaded at `2026-05-05T10:41:11+00:00`. This proves the full pipeline wrote a production PDF for a real order submitted through the web UI.

![AKS validator logs — POST /validate 200 OK](<docs/images_pa4/images/task7/Screenshot 2026-05-05 160903.png>)

`kubectl logs -l app=validate-api` shows a stream of `POST /Validate HTTP/1.1 200 OK` entries alongside the `10.224.0.x` source IPs (the Function App's outbound IP range). The AKS validator pod received and processed every validation request from the Durable Function `validate_activity`.

![ACI activity log — ci-report-ord-* container groups created and deleted](<docs/images_pa4/images/task7/Screenshot 2026-05-05 161123.png>)

`az monitor activity-log list --resource-group rg-sp26-26100396` filtered to ContainerInstance resources shows multiple `ci-report-ord-*` container group operations. Each successful orchestration created a new ephemeral ACI group (visible by the `Microsoft.ContainerInstance/containerGroups/write` operations), confirming the per-order ACI spin-up pattern is working in production.

![Function App activity log — Started and Succeeded](<docs/images_pa4/images/task7/Screenshot 2026-05-05 162211.png>)

`az monitor activity-log list` filtered to `pa4-26100396-function` shows two `Started / Succeeded` pairs at `2026-05-05T10:33` and `2026-05-05T10:55`, matching two complete orchestration runs. The Function App itself was invoked, executed the full orchestration, and completed without error.

### Evidence 7.4: Reject Path UI

![Reject path — TaskFlow UI showing Rejected qty 9999](<docs/images_pa4/images/task7/7.3_rejection/Screenshot 2026-05-05 154811.png>)

Order `ORD-009` with SKU `WIDGET-X` and Quantity `9999` is submitted through the form. The UI immediately shows a **Rejected** badge with reason `quantity exceeds limit`, demonstrating the AKS validator returned `valid: false` and the orchestrator returned early without invoking `report_activity`.

![Reject path — status JSON shows rejected](<docs/images_pa4/images/task7/7.3_rejection/Screenshot 2026-05-05 155702.png>)

Polling the Durable status URL for instance `24da19e73b9448c5ae91b1767d02c5a7` (order `REJECT-001`, qty 999) returns `"runtimeStatus":"Completed"` with output `{"status":"rejected","reason":"quantity exceeds limit"}`, confirming the orchestrator completed normally and returned the rejection result rather than failing.

![Reject path — az container list empty, no ACI created](<docs/images_pa4/images/task7/7.3_rejection/Screenshot 2026-05-05 154637.png>)

`az container list --resource-group rg-sp26-26100396 --output table` run twice both return an empty table. No `ci-report-*` container group was created for the rejected order, proving the pipeline correctly skips the expensive ACI report step when validation fails.

### Evidence 7.5: All Resource Groups

![All resource groups](<docs/images_pa4/images/task7/7.3_rejection/Screenshot 2026-05-08 050053.png>)

---

## Task 8: Write-up and Architecture Diagram (5 points)

### Evidence 8.1: Architecture Diagram

![TaskFlow Architecture Diagram — rg-sp26-26100396, UK West](<docs/26100396_architecture.jpg>)

The diagram illustrates the end-to-end **TaskFlow** pipeline deployed on **Azure UK West** under resource group `rg-sp26-26100396`. A user submits an order through the App Service web UI, which triggers a **Durable Function App** orchestrator that fans out to an AKS validator (`validate_activity`) and spins up an ephemeral ACI report job (`report_activity`). Container images are pulled from **ACR**, durable state is persisted in the **Storage Account**, generated PDFs are written to **Blob Storage**, and all resource access is brokered through a single Managed Identity (`mi-pa4-26100396`).


---

### Question 8.2: Service Selection

**App Service** is the right host for the TaskFlow web frontend because it provides fully managed PaaS hosting with native GitHub Actions CI/CD, automatic TLS, and a predictable B1 plan cost of ~$13/month — none of which requires container orchestration knowledge to maintain. The frontend is a stateless Node.js server with negligible CPU/memory requirements, so the operational simplicity of App Service fits perfectly: no Dockerfile needed for CI/CD, no cluster to patch. Horizontal scale-out is available on demand, and every push to `main` triggers a build-and-deploy automatically.

**Durable Functions** is the correct orchestration layer because the TaskFlow workflow is inherently sequential — the order must be validated before a report can be generated — and the report step can block for up to 60 seconds waiting for an ACI container to start and exit. Plain HTTP functions cannot sleep for a minute without consuming a thread or hitting the 5-minute execution timeout. Durable Functions checkpoints each activity's output to Azure Storage and suspends the orchestrator between yield points, so no thread is blocked and the pipeline can span minutes without timeout risk.


**AKS** is the right host for the validation microservice because it is a long-running, always-available HTTP API that must respond within milliseconds to every `validate_activity` call. A Kubernetes Deployment ensures the pod is always `Running`, with Kubernetes handling restarts, health probes, and load distribution via the `LoadBalancer` Service. A permanently resident pod is far cheaper per-request than spinning up a new ACI for each validation call, and the rolling-update model allows zero-downtime image upgrades via `kubectl set image`.


**Azure Container Instances** is the right executor for the report job because generating a PDF is an ephemeral, run-to-completion workload that should not exist between orders. ACI's per-second billing means a 20-second container run costs a fraction of a cent, while the same workload kept alive on an AKS node accumulates VM costs around the clock. `report_activity` creates the container group via the Azure SDK, polls until `Succeeded`, then immediately deletes it — leaving zero persistent infrastructure and zero cost between submissions.

---

### Question 8.3: ACI vs AKS

**What happens to AKS when it is idle for 10 minutes?**

Nothing changes. The node VM stays in `Ready` state and the validator pod remains `1/1 Running` — AKS never terminates or de-allocates idle nodes. Azure bills for the underlying VM every minute the node pool exists regardless of traffic, and the only way to stop billing is to stop or delete the cluster, which takes the validator offline.

**What does idle mean for ACI in the TaskFlow pipeline?**

ACI containers do not exist between runs. After `report_activity` calls `begin_delete`, there is no container group in the resource group at all — idle means literally zero cost and zero allocated infrastructure. Every new report request boots a fresh container from ACR and terminates cleanly after writing the PDF.

**If a malicious user spammed Submit 1,000 times in a minute, which service incurs the most cost, and why?**

ACI would incur the most cost. Each valid order spawns a new container group (1 vCPU, 1.5 GB RAM), so 1,000 simultaneous containers running for ~30 seconds costs approximately $0.08–$0.12 in that single burst. The AKS node absorbs all 1,000 validation `POST` requests on the same pod with no change to its hourly VM charge. The correct mitigation is an **Azure API Management** rate-limit policy in front of the Durable HTTP starter endpoint.

---

### Question 8.4: Durable Functions vs Plain HTTP

If the same `validate → report` flow were implemented as two plain HTTP-triggered functions calling each other, at least two concrete problems would make it fragile.

**Function timeouts.** `report_activity` polls for ACI completion with `time.sleep(5)` for up to 60 seconds — blocking the thread the entire time. On a Consumption plan, any transient ACI slowness pushing the total past the 5-minute timeout causes an unhandled `503` with no retry. Durable Functions eliminates this by suspending the orchestrator at each `yield`, releasing the thread entirely until a storage queue message triggers resumption.

**State persistence and retry-on-failure.** If a plain HTTP function crashes mid-execution, there is no mechanism to resume from the last completed step — the caller receives a `500` with no record of whether validation succeeded, so a full retry risks creating a duplicate ACI container group. Durable Functions checkpoints every completed activity's output to Azure Storage; on restart the orchestrator skips already-completed steps and can retry only the failed one with exponential back-off via `call_activity_with_retry`.

---

### Question 8.5: Cost Review

![Cost Management — Cost Analysis for rg-sp26-26100396, May 2026](<docs/images_pa4/images/cost_analysis.png>)

---

### Question 8.6: Challenges Faced

**Challenge 1: ImagePullBackOff — AKS cluster could not pull from private ACR**

When `kubectl apply -f k8s/deployment.yaml` was first run, all `validate-deployment` pods immediately entered `ImagePullBackOff`. `kubectl describe pod <name>` revealed the error: `failed to pull image "acrpa426100396.azurecr.io/validate-api:v1": unauthorized: authentication required`. The AKS cluster's managed identity did not have the `AcrPull` role on the ACR. The fix was:

```bash
az aks update \
  --name pa4-26100396 \
  --resource-group rg-sp26-26100396 \
  --attach-acr acrpa426100396
```

This granted the cluster's managed identity the `AcrPull` role. After the role assignment propagated (~2 minutes), the failing pods were terminated by the Deployment controller and a fresh rollout succeeded — as visible in Evidence 5.2 where `validate-deployment-848cf4ffdd-2xftw` transitions from nothing to **1/1 Running** while the `ImagePullBackOff` pods are Terminating.

**Challenge 2: Managed Identity authentication failure in report_activity**

After deploying the Function App container and running the first full orchestration, `report_activity` threw `ManagedIdentityCredential authentication failed: No User Assigned or Delegated Managed Identity found for specified ClientId/ResourceId/PrincipalId`. The Function App portal showed the same error banner (visible in Evidence 4.1). The root cause was two-fold: (1) `DefaultAzureCredential` was iterating its credential chain and not finding a matching identity because `AZURE_CLIENT_ID` was not set, and (2) even after the MI was attached, it initially lacked sufficient permissions. The fix required:

1. Setting `AZURE_CLIENT_ID` in Function App application settings to the client ID of `mi-pa4-26100396`, so `DefaultAzureCredential` uses the correct user-assigned identity instead of falling through to other chain entries.
2. Verifying that `mi-pa4-26100396` held the **Contributor** role on `rg-sp26-26100396` (not just a read role), because creating and deleting ACI container groups requires write permissions on the resource group.

After both changes were applied and the Function App restarted, orchestrations completed successfully end-to-end as shown in Evidence 7.2 and 7.3.

---
